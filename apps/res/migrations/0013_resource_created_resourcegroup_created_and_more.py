# Generated by Django 5.0.4 on 2025-07-29 18:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('res', '0012_rename_modified_time_resource_modified_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 29, 21, 10, 39, 844995), editable=False),
        ),
        migrations.AddField(
            model_name='resourcegroup',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 29, 21, 10, 39, 844995), editable=False),
        ),
        migrations.AddField(
            model_name='resourcetype',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 29, 21, 10, 39, 844995), editable=False),
        ),
    ]
