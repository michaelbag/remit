# Generated by Django 5.0.4 on 2024-06-05 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0002_remove_extsystem_token_extsystem_created_datetime_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extsystem',
            name='last_ping_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]