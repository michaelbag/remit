# Generated by Django 5.0.4 on 2025-02-19 07:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0004_alter_equipment_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='equipments', to='equipment.equipmentmodel'),
        ),
    ]
