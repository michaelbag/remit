# Generated by Django 5.0.4 on 2024-06-02 09:54

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0027_alter_equipment_guid'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='equipmenttype',
            options={'verbose_name': 'Equipment type'},
        ),
        migrations.AlterField(
            model_name='equipmentmodel',
            name='guid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='equipmenttype',
            name='guid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='equipmenttype',
            name='name',
            field=models.CharField(blank=True, max_length=32),
        ),
    ]