# Generated by Django 5.0.3 on 2025-04-18 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0008_alter_equipment_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='name',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]
