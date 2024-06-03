# Generated by Django 5.0.4 on 2024-06-02 09:45

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org', '0007_employee_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='guid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='employee',
            name='guid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='organization',
            name='guid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]