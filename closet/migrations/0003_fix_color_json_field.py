from django.db import migrations, models
import json

def convert_color_to_json(apps, schema_editor):
    ClosetItem = apps.get_model('closet', 'ClosetItem')
    for item in ClosetItem.objects.all():
        if isinstance(item.color, str):
            # Try to see if it's already a JSON list string
            try:
                val = json.loads(item.color)
                if not isinstance(val, list):
                    item.color = json.dumps([item.color])
                    item.save(update_fields=['color'])
            except (ValueError, json.JSONDecodeError):
                # It's a plain string, wrap it in a list
                item.color = json.dumps([item.color])
                item.save(update_fields=['color'])
        elif item.color is None:
            item.color = json.dumps([])
            item.save(update_fields=['color'])

class Migration(migrations.Migration):

    dependencies = [
        ('closet', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(convert_color_to_json),
        migrations.AlterField(
            model_name='closetitem',
            name='color',
            field=models.JSONField(blank=True, default=list, help_text='Store multiple color codes or names as a JSON array'),
        ),
    ]
