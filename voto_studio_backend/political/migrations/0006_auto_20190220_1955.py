# Generated by Django 2.1.7 on 2019-02-20 19:55

import django.contrib.postgres.fields.jsonb
from django.db import migrations
import voto_studio_backend.changes.models
import voto_studio_backend.political.models


class Migration(migrations.Migration):

    dependencies = [
        ('political', '0005_individual_experience'),
    ]

    operations = [
        migrations.AlterField(
            model_name='achievement',
            name='statistics',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_studio_backend.changes.models.Statistics(), null=True, verbose_name='Statistics'),
        ),
        migrations.AlterField(
            model_name='controversy',
            name='statistics',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_studio_backend.changes.models.Statistics(), null=True, verbose_name='Statistics'),
        ),
        migrations.AlterField(
            model_name='electoralperiod',
            name='statistics',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_studio_backend.changes.models.Statistics(), null=True, verbose_name='Statistics'),
        ),
        migrations.AlterField(
            model_name='individual',
            name='experience',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_studio_backend.political.models.Experience(), null=True),
        ),
        migrations.AlterField(
            model_name='individual',
            name='statistics',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_studio_backend.changes.models.Statistics(), null=True, verbose_name='Statistics'),
        ),
        migrations.AlterField(
            model_name='law',
            name='statistics',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_studio_backend.changes.models.Statistics(), null=True, verbose_name='Statistics'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='statistics',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_studio_backend.changes.models.Statistics(), null=True, verbose_name='Statistics'),
        ),
        migrations.AlterField(
            model_name='promise',
            name='statistics',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_studio_backend.changes.models.Statistics(), null=True, verbose_name='Statistics'),
        ),
    ]
