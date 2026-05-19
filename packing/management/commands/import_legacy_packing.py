import re
import datetime
import traceback
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from users.models import User, UserSubscriptionHistory
from packing.models import (
    TripType, Trip, PackingTemplate, 
    PackingTemplateCategory, PackingTemplateItem
)
from closet.models import ClosetItem, ItemCategory, ItemCategoryType

class Command(BaseCommand):
    help = 'Import legacy data from Laravel SQL dump including closet items'

    def add_arguments(self, parser):
        parser.add_argument('sql_file', type=str, help='Path to the SQL dump file')

    def handle(self, *args, **options):
        sql_file_path = options['sql_file']
        
        self.stdout.write(self.style.SUCCESS(f'Starting import from {sql_file_path}...'))

        # Clear existing data
        self.stdout.write('Clearing existing packing and closet data...')
        Trip.objects.all().delete()
        PackingTemplateItem.objects.all().delete()
        PackingTemplateCategory.objects.all().delete()
        PackingTemplate.objects.all().delete()
        ClosetItem.objects.all().delete()
        UserSubscriptionHistory.objects.all().delete()

        # Mappings
        user_map = {}
        camp_map = {}
        category_map = {}
        camper_user_map = {}
        item_category_name_map = {}
        legacy_cat_id_name_map = {}

        camping_type, _ = TripType.objects.get_or_create(
            name='Camping', defaults={'code': 'CAMP'})
        clothing_main, _ = ItemCategoryType.objects.get_or_create(
            name='Clothing')
        
        def get_sub_cat(name):
            name = name or 'Miscellaneous'
            cat, _ = ItemCategory.objects.get_or_create(
                name=name,
                type=clothing_main, # Corrected field name
                defaults={'is_system': True}
            )
            return cat

        tables = [
            'users', 'camps', 'packing_categories', 'packing_items', 
            'camper_camps', 'campers', 'camper_closets', 'user_subscription_histories'
        ]
        data = {table: [] for table in tables}
        
        self.stdout.write('Parsing SQL file...')
        with open(sql_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                for table in tables:
                    pattern = f"INSERT INTO `{table}` VALUES"
                    if line.startswith(pattern):
                        vals_part = line[len(pattern):].strip()
                        if vals_part.endswith(';'): vals_part = vals_part[:-1]
                        if vals_part.startswith('(') and vals_part.endswith(')'):
                            rows = self.parse_values(vals_part)
                            data[table].extend(rows)
                        break

        # 1. Users
        self.stdout.write(f"Migrating Users ({len(data['users'])} rows)...")
        for row in data['users']:
            try:
                legacy_id = int(row[0])
                first_name = self.clean_val(row[1])
                last_name = self.clean_val(row[2])
                email = self.clean_val(row[3]).lower()
                is_sub = True if row[11] == '1' else False
                
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'full_name': f"{first_name} {last_name or ''}".strip(),
                        'role': 'parent',
                        'is_email_verified': True if row[4] != 'NULL' else False,
                        'is_subscribed': is_sub,
                    }
                )
                if not created and user.is_subscribed != is_sub:
                    user.is_subscribed = is_sub
                    user.save(update_fields=['is_subscribed'])
                    
                if created:
                    user.set_password('user@1234')
                    user.save()
                user_map[legacy_id] = user
            except Exception as e:
                self.stdout.write(f"  Error migrating user {row[0]}: {e}")

        # 2. Camps
        self.stdout.write(f"Migrating Camps ({len(data['camps'])} rows)...")
        for row in data['camps']:
            try:
                legacy_id = int(row[0])
                name = self.clean_val(row[1])
                address = self.clean_val(row[2])
                days = int(row[4]) if row[4] != 'NULL' else 7
                template = PackingTemplate.objects.create(
                    title=name,
                    description=address or f"Imported Camp (Days: {days})",
                    trip_type=camping_type,
                    is_system=True
                )
                template._legacy_days = days
                camp_map[legacy_id] = template
            except Exception as e:
                self.stdout.write(f"  Error migrating camp {row[0]}: {e}")

        # 3. Categories
        self.stdout.write(f"Migrating Categories ({len(data['packing_categories'])} rows)...")
        for row in data['packing_categories']:
            try:
                legacy_id = int(row[0])
                camp_id = int(row[1])
                name = self.clean_val(row[2])
                legacy_cat_id_name_map[legacy_id] = name
                if camp_id in camp_map:
                    category = PackingTemplateCategory.objects.create(
                        template=camp_map[camp_id],
                        name=name,
                        sort_order=int(row[11]) if row[11] != 'NULL' else 0
                    )
                    category_map[legacy_id] = category
            except Exception as e:
                self.stdout.write(f"  Error migrating category {row[0]}: {e}")

        # 4. Items
        self.stdout.write(f"Migrating Items ({len(data['packing_items'])} rows)...")
        for row in data['packing_items']:
            try:
                legacy_item_id = int(row[0])
                category_id = int(row[1])
                name = self.clean_val(row[2])
                if category_id in legacy_cat_id_name_map:
                    item_category_name_map[legacy_item_id] = legacy_cat_id_name_map[category_id]
                if category_id in category_map:
                    PackingTemplateItem.objects.create(
                        template=category_map[category_id].template,
                        category=category_map[category_id],
                        title=name,
                        quantity=int(row[3]) if row[3] != 'NULL' else 1,
                        note=self.clean_val(row[4]),
                        sort_order=int(row[15]) if row[15] != 'NULL' else 0
                    )
            except Exception as e:
                self.stdout.write(f"  Error migrating item {row[0]}: {e}")

        # 5. Campers -> Trip
        self.stdout.write(f"Migrating Campers ({len(data['campers'])} rows)...")
        camper_camp_map = {int(r[1]): int(r[2]) for r in data['camper_camps']}
        for row in data['campers']:
            try:
                legacy_camper_id = int(row[0])
                legacy_user_id = int(row[8])
                camper_user_map[legacy_camper_id] = legacy_user_id
                if legacy_user_id in user_map:
                    user = user_map[legacy_user_id]
                    camp_id = camper_camp_map.get(legacy_camper_id)
                    template = camp_map.get(camp_id)
                    created_at_str = self.clean_val(row[11])
                    try: start_date = datetime.datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S').date()
                    except: start_date = timezone.now().date()
                    days = getattr(template, '_legacy_days', 7) if template else 7
                    Trip.objects.create(
                        user=user, template=template, trip_type=camping_type,
                        name=f"{self.clean_val(row[1])} {self.clean_val(row[2]) or ''}".strip(),
                        location=self.clean_val(row[4]) or "Unknown",
                        start_date=start_date, end_date=start_date + datetime.timedelta(days=days),
                        status='Past'
                    )
            except Exception as e:
                self.stdout.write(f"  Error migrating camper {row[0]}: {e}")

        # 6. Closet Items
        self.stdout.write(f"Migrating Closet Items ({len(data['camper_closets'])} rows)...")
        closet_success = 0
        closet_fail = 0
        for row in data['camper_closets']:
            try:
                legacy_camper_id = int(row[7])
                legacy_user_id = camper_user_map.get(legacy_camper_id)
                if not legacy_user_id or legacy_user_id not in user_map:
                    closet_fail += 1
                    continue
                
                user = user_map[legacy_user_id]
                name = self.clean_val(row[1])
                legacy_item_id = int(row[6])
                cat_name = item_category_name_map.get(legacy_item_id, 'Miscellaneous')
                sub_cat = get_sub_cat(cat_name)
                color_str = self.clean_val(row[9])
                
                ClosetItem.objects.create(
                    user=user,
                    main_category=clothing_main,
                    sub_category=sub_cat,
                    name=name or f"Item {legacy_item_id}",
                    quantity=int(row[4]) if row[4] != 'NULL' else 1,
                    size=self.clean_val(row[5]) or "N/A",
                    color=[color_str] if color_str else [],
                    brand=None
                )
                closet_success += 1
            except Exception as e:
                closet_fail += 1
                if closet_fail < 10: # Log first few errors
                    self.stdout.write(f"  Closet Error: {e}")

        # 7. Import Subscription Histories
        sub_len = len(data['user_subscription_histories'])
        self.stdout.write(f"Migrating Subscription Histories ({sub_len} rows)...")
        sub_success = 0
        sub_fail = 0
        for row in data['user_subscription_histories']:
            try:
                legacy_user_id = int(row[1])
                if legacy_user_id in user_map:
                    user = user_map[legacy_user_id]
                    
                    start_time = None
                    start_str = self.clean_val(row[7])
                    if start_str:
                        try:
                            start_time = datetime.datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                        
                    expiry_time = None
                    expiry_str = self.clean_val(row[8])
                    if expiry_str:
                        try:
                            expiry_time = datetime.datetime.strptime(expiry_str, '%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    
                    status_val = True if row[13] == '1' else False
                    
                    UserSubscriptionHistory.objects.create(
                        user=user,
                        subscription_status=self.clean_val(row[2]),
                        device_type=self.clean_val(row[3]),
                        product_id=self.clean_val(row[4]),
                        purchase_token=self.clean_val(row[5]),
                        order_id=self.clean_val(row[6]),
                        start_time=start_time,
                        expiry_time=expiry_time,
                        price_currency_code=self.clean_val(row[9]),
                        price_amount=self.clean_val(row[10]),
                        country_code=self.clean_val(row[11]),
                        payment_state=self.clean_val(row[12]),
                        status=status_val
                    )
                    sub_success += 1
            except Exception as e:
                sub_fail += 1
                if sub_fail < 10:
                    self.stdout.write(f"  Subscription Error: {e}")

        self.stdout.write(self.style.SUCCESS(f'Import completed! Closet Success: {closet_success}, Sub Success: {sub_success}'))

    def parse_values(self, values_str):
        rows = []
        row_strs = re.split(r"\),\s*\(", values_str[1:-1])
        for row_str in row_strs:
            vals = []
            current_v = ""; in_s = False; esc = False
            for char in row_str:
                if esc: current_v += char; esc = False
                elif char == "\\": esc = True
                elif char == "'": in_s = not in_s; current_v += char
                elif char == "," and not in_s: vals.append(current_v.strip()); current_v = ""
                else: current_v += char
            vals.append(current_v.strip())
            rows.append(vals)
        return rows

    def clean_val(self, val):
        if val == 'NULL' or val is None: return None
        if val.startswith("'") and val.endswith("'"): val = val[1:-1]
        return val.replace("''", "'").replace("\\'", "'")
