# Generated by Django 5.0.4 on 2025-07-29 18:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org', '0012_alter_department_created_alter_employee_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 29, 21, 54, 15, 734228), editable=False),
        ),
        migrations.AlterField(
            model_name='employee',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 29, 21, 54, 15, 734228), editable=False),
        ),
        migrations.AlterField(
            model_name='organization',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 29, 21, 54, 15, 734228), editable=False),
        ),
    ]
