import os
import sys
import csv
import django

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.apps import apps

def export_db_to_csv():
    export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    models_to_export = [
        'users.User',
        'users.UserSubscriptionHistory',
        'packing.TripType',
        'packing.PackingTemplate',
        'packing.PackingTemplateCategory',
        'packing.PackingTemplateItem',
        'packing.Trip',
        'closet.ItemCategoryType',
        'closet.ItemCategory',
        'closet.ClosetItem',
    ]
    
    print("🚀 Starting export of database to CSV files...")
    
    for model_string in models_to_export:
        try:
            model = apps.get_model(model_string)
            model_name = model.__name__
            csv_file_path = os.path.join(export_dir, f"{model_name}.csv")
            
            print(f"📦 Exporting {model_string}...")
            
            # Get all fields of the model
            fields = model._meta.fields
            field_names = [f.name for f in fields]
            
            queryset = model.objects.all()
            total_records = queryset.count()
            
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(field_names)
                
                # Write data rows
                for obj in queryset:
                    row = []
                    for field in fields:
                        val = getattr(obj, field.name)
                        # Handle foreign keys by getting their primary key
                        if val is not None and hasattr(val, 'pk'):
                            val = val.pk
                        row.append(val)
                    writer.writerow(row)
                    
            print(f"  ✅ Successfully exported {total_records} records to {csv_file_path}")
            
        except Exception as e:
            print(f"  ❌ Error exporting {model_string}: {e}")

    print("\n🎉 All exports completed! Check the 'exports/' directory.")

if __name__ == '__main__':
    export_db_to_csv()
