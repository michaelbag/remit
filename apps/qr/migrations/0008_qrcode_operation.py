# Generated by Django 5.0.4 on 2025-07-05 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qr', '0007_qrcode_short_public_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='qrcode',
            name='operation',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]
