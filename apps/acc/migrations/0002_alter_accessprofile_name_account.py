# Generated by Django 5.0.4 on 2024-09-05 19:11

import datetime
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acc', '0001_initial'),
        ('org', '0001_initial'),
        ('res', '0005_resource_accounts_provider_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accessprofile',
            name='name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('guid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('code', models.CharField(blank=True, max_length=9)),
                ('delete_mark', models.BooleanField(default=False)),
                ('name', models.CharField(blank=True, max_length=50)),
                ('technical', models.BooleanField(default=False, help_text='Technical account')),
                ('create_date', models.DateField(default=datetime.date.today, help_text='Create date', null=True)),
                ('end_date', models.DateField(blank=True, help_text='Expiry date', null=True)),
                ('disabled', models.BooleanField(default=False)),
                ('archive', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True)),
                ('employee', models.ForeignKey(help_text='Employee', on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='org.employee')),
                ('profiles', models.ManyToManyField(related_name='accounts', to='acc.accessprofile')),
                ('resource', models.ForeignKey(help_text='Resource', limit_choices_to={'accounts_provider': True}, on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='res.resource')),
            ],
            options={
                'verbose_name': 'Account',
            },
        ),
    ]