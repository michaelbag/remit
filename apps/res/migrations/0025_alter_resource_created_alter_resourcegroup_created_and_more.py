# Generated by Django 5.0.4 on 2025-07-29 19:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('res', '0024_alter_resource_created_alter_resourcegroup_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 29, 22, 23, 2, 283999), editable=False),
        ),
        migrations.AlterField(
            model_name='resourcegroup',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 29, 22, 23, 2, 283999), editable=False),
        ),
        migrations.AlterField(
            model_name='resourcetype',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 29, 22, 23, 2, 283999), editable=False),
        ),
    ]
