# Generated by Django 5.0.4 on 2024-09-05 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acc', '0002_alter_accessprofile_name_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='profiles',
            field=models.ManyToManyField(blank=True, related_name='accounts', to='acc.accessprofile'),
        ),
    ]