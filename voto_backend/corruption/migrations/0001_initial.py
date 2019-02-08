# Generated by Django 2.1.5 on 2019-02-06 13:41

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.utils.timezone
import voto_backend.forms.models
import voto_backend.search.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CorruptionCase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of Creation')),
                ('tracked', models.BooleanField(default=True, verbose_name='Tracked')),
                ('location_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier')),
                ('location_id_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier Name')),
                ('title', models.CharField(default=str, max_length=64, verbose_name='Title')),
                ('brief_description', models.CharField(blank=True, max_length=140, null=True, verbose_name='Description')),
                ('long_description', models.TextField(blank=True, default='<p></p>', verbose_name='Long Description')),
                ('statistics', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Statistics')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, voto_backend.forms.models.InfoMixin, voto_backend.search.models.IndexingMixin),
        ),
        migrations.CreateModel(
            name='InformativeSnippet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of Creation')),
                ('tracked', models.BooleanField(default=True, verbose_name='Tracked')),
                ('location_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier')),
                ('location_id_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier Name')),
                ('title', models.CharField(default=str, max_length=64, verbose_name='Title')),
                ('brief_description', models.CharField(blank=True, max_length=140, null=True, verbose_name='Description')),
                ('long_description', models.TextField(blank=True, default='<p></p>', verbose_name='Long Description')),
                ('source', models.URLField(blank=True, max_length=256, null=True, verbose_name='Source')),
                ('statistics', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Statistics')),
                ('twitter_feed', models.URLField(blank=True, null=True, verbose_name='Twitter Feed URL')),
                ('corruption_cases', models.ManyToManyField(blank=True, to='corruption.CorruptionCase')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, voto_backend.forms.models.InfoMixin, voto_backend.search.models.IndexingMixin),
        ),
    ]
