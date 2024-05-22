# Generated by Django 5.0.4 on 2024-05-13 17:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0014_alter_service_parent'),
        ('org', '0006_alter_employee_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='services', to='org.organization'),
        ),
    ]
