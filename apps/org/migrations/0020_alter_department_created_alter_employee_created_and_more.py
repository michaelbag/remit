# Generated by Django 5.0.4 on 2025-07-29 19:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org', '0019_alter_department_created_alter_employee_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 29, 22, 20, 27, 315289), editable=False),
        ),
        migrations.AlterField(
            model_name='employee',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 29, 22, 20, 27, 315289), editable=False),
        ),
        migrations.AlterField(
            model_name='organization',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 29, 22, 20, 27, 315289), editable=False),
        ),
    ]
