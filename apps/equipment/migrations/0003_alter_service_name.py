# Generated by Django 5.0.4 on 2024-05-12 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0002_remove_service_id_service_code_service_delete_mark_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='name',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
