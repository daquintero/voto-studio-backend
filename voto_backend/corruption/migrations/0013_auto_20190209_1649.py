# Generated by Django 2.1.5 on 2019-02-09 16:49

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corruption', '0012_auto_20190208_1638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corruptioncase',
            name='statistics',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True, verbose_name='Statistics'),
        ),
        migrations.AlterField(
            model_name='financialitem',
            name='statistics',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True, verbose_name='Statistics'),
        ),
        migrations.AlterField(
            model_name='informativesnippet',
            name='statistics',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True, verbose_name='Statistics'),
        ),
    ]
