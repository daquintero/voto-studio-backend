# Generated by Django 2.1.7 on 2019-02-20 19:55

import django.contrib.postgres.fields.jsonb
from django.db import migrations
import voto_studio_backend.changes.models


class Migration(migrations.Migration):

    dependencies = [
        ('corruption', '0003_auto_20190219_1636'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corruptioncase',
            name='statistics',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_studio_backend.changes.models.Statistics(), null=True, verbose_name='Statistics'),
        ),
        migrations.AlterField(
            model_name='financialitem',
            name='statistics',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_studio_backend.changes.models.Statistics(), null=True, verbose_name='Statistics'),
        ),
        migrations.AlterField(
            model_name='informativesnippet',
            name='statistics',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_studio_backend.changes.models.Statistics(), null=True, verbose_name='Statistics'),
        ),
    ]
