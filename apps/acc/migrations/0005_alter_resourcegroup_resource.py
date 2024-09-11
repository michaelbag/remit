# Generated by Django 5.0.4 on 2024-09-11 17:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acc', '0004_resourcegroup_accessprofile_groups'),
        ('res', '0005_resource_accounts_provider_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcegroup',
            name='resource',
            field=models.ForeignKey(help_text='Resource', limit_choices_to={'accounts_provider': True}, on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='res.resource'),
        ),
    ]
