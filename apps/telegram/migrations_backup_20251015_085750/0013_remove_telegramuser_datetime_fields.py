# Generated manually on 2025-01-14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('telegram', '0012_add_name_and_code_fields_to_broadcast'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='telegramuser',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='telegramuser',
            name='updated_at',
        ),
    ]
