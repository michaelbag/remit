# Generated by Django 5.0.4 on 2024-06-05 19:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('equipment', '0001_initial'),
        ('org', '0001_initial'),
        ('res', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='interface',
            name='connected_to',
            field=models.ForeignKey(blank=True, limit_choices_to={'resource_category': 'network'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='res.resource'),
        ),
        migrations.AddField(
            model_name='interface',
            name='equipment',
            field=models.ForeignKey(limit_choices_to={'has_interfaces': True, 'is_group': False}, on_delete=django.db.models.deletion.CASCADE, related_name='interfaces', to='equipment.equipment'),
        ),
        migrations.AddField(
            model_name='interface',
            name='interface_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interfaces', to='equipment.interfacetype'),
        ),
        migrations.AddField(
            model_name='service',
            name='equipment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='equipment.equipment'),
        ),
        migrations.AddField(
            model_name='service',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='services', to='org.organization'),
        ),
        migrations.AddField(
            model_name='service',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='elements', to='equipment.service'),
        ),
        migrations.AddField(
            model_name='service',
            name='software',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='services', to='equipment.software'),
        ),
        migrations.AddField(
            model_name='softwareversion',
            name='software',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='equipment.software'),
        ),
        migrations.AddField(
            model_name='service',
            name='software_version',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='services', to='equipment.softwareversion'),
        ),
        migrations.AddField(
            model_name='equipmentmodel',
            name='supplier',
            field=models.ForeignKey(blank=True, limit_choices_to={'archive': False, 'delete_mark': False}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='models', to='equipment.supplier'),
        ),
    ]