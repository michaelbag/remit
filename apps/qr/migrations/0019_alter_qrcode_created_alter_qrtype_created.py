# Generated by Django 5.0.4 on 2025-07-29 19:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qr', '0018_alter_qrcode_created_alter_qrtype_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qrcode',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 29, 22, 9, 21, 474615), editable=False),
        ),
        migrations.AlterField(
            model_name='qrtype',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 29, 22, 9, 21, 474615), editable=False),
        ),
    ]
