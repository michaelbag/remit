# Generated by Django 5.0.3 on 2024-05-16 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0018_remove_service_is_group_alter_service_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='interface',
            name='dns',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='interface',
            name='ipv4_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='interface',
            name='ipv4_gateway',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='interface',
            name='ipv4_network_mask',
            field=models.IntegerField(default=0),
        ),
    ]