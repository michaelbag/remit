# Generated by Django 5.0.4 on 2024-06-02 09:47

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0026_alter_interfacetype_guid_alter_service_guid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='guid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]