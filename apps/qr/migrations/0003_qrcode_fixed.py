# Generated by Django 5.0.4 on 2024-05-23 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qr', '0002_qrtype_fixed'),
    ]

    operations = [
        migrations.AddField(
            model_name='qrcode',
            name='fixed',
            field=models.BooleanField(default=False),
        ),
    ]
