# Generated by Django 5.0.4 on 2025-07-29 18:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acc', '0014_alter_accessprofile_created_alter_account_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accessprofile',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 29, 21, 54, 15, 734228), editable=False),
        ),
        migrations.AlterField(
            model_name='account',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 29, 21, 54, 15, 734228), editable=False),
        ),
    ]
