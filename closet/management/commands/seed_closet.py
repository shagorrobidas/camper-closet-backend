import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from closet.models import ItemCategoryType, ItemCategory, ClosetItem

fake = Faker()
User = get_user_model()


class Command(BaseCommand):
    help = 'Seed Closet Items for a specific user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user_id',
            type=str,
            default='e67cbf75-79ad-46a8-995c-c56bccc013c9',
            help='The ID of the user to seed items for'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='The number of closet items to create'
        )

    def handle(self, *args, **options):
        user_id = options['user_id']
        count = options['count']

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with ID "{user_id}" does not exist.')
            )
            return

        # Create Category Types (Main)
        types_data = [
            ("Clothes", "CL"),
            ("Toiletries", "TO"),
            ("Gear", "GE"),
        ]

        category_types = {}
        for name, code in types_data:
            obj, _ = ItemCategoryType.objects.get_or_create(
                name=name,
                defaults={'code': code}
            )
            category_types[name] = obj

        # Create Sub Categories
        sub_categories_data = {
            "Clothes": ["T-shirt", "Pant", "Shoes"],
            "Toiletries": ["Sunscreen", "Toothbrush"],
            "Gear": ["Sleeping Bag", "Backpack"],
        }

        sub_categories = []

        for main, subs in sub_categories_data.items():
            for sub in subs:
                obj, _ = ItemCategory.objects.get_or_create(
                    name=sub,
                    type=category_types[main],
                    defaults={
                        'user': None,
                        'is_system': True,
                        'is_custom': False
                    }
                )
                sub_categories.append(obj)

        # Sample Brands
        brands = [
            "Nike", "Adidas", "GAP", "Neutrogena", "Coleman", "Trekker"
        ]

        # Create Closet Items
        created_count = 20
        for i in range(count):
            sub_cat = random.choice(sub_categories)

            ClosetItem.objects.create(
                user=user,
                main_category=sub_cat.type,
                sub_category=sub_cat,
                name=f"{sub_cat.name} {fake.color_name()} {i+1}",
                image='closet_items/61507e01ee991-square_IqQlJuA.jpg',
                brand=random.choice(brands),
                color=random.choice(["Red", "Blue", "Black", "Green", "White"]),
                size=random.choice(["S", "M", "L", "XL"]),
                quantity=random.randint(1, 3),
                notes=fake.sentence(),
                is_scanned=random.choice([True, False]),
                is_favorite=random.choice([True, False]),
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ {created_count} ClosetItems created successfully for user {user.email}!'
            )
        )
