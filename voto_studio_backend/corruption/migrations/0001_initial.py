# Generated by Django 2.1.7 on 2019-02-19 16:36

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.utils.timezone
import voto_studio_backend.changes.models
import voto_studio_backend.forms.models
import voto_studio_backend.search.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CorruptionCase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permissions_dict', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of Creation')),
                ('tracked', models.BooleanField(default=True, verbose_name='Tracked')),
                ('source', models.URLField(blank=True, max_length=2048, null=True, verbose_name='Source')),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('statistics', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, null=True, verbose_name='Statistics')),
                ('location_id_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier Name')),
                ('location_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier')),
                ('rels_dict', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Relationships Dictionary')),
                ('order', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_studio_backend.changes.models.get_order_default, verbose_name='Media Content Order')),
                ('title', models.CharField(default=str, max_length=64, verbose_name='Title')),
                ('brief_description', models.CharField(blank=True, max_length=140, null=True, verbose_name='Description')),
                ('long_description', models.TextField(blank=True, default='<p></p>', verbose_name='Long Description')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, voto_studio_backend.forms.models.InfoMixin, voto_studio_backend.search.models.IndexingMixin),
        ),
        migrations.CreateModel(
            name='FinancialItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permissions_dict', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of Creation')),
                ('tracked', models.BooleanField(default=True, verbose_name='Tracked')),
                ('source', models.URLField(blank=True, max_length=2048, null=True, verbose_name='Source')),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('statistics', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, null=True, verbose_name='Statistics')),
                ('location_id_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier Name')),
                ('location_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier')),
                ('rels_dict', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Relationships Dictionary')),
                ('order', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_studio_backend.changes.models.get_order_default, verbose_name='Media Content Order')),
                ('title', models.CharField(default=str, max_length=64, verbose_name='Title')),
                ('brief_description', models.CharField(blank=True, max_length=140, null=True, verbose_name='Description')),
                ('amount', models.FloatField(blank=True, default=float, verbose_name='Amount')),
                ('corruption_related', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, voto_studio_backend.forms.models.InfoMixin, voto_studio_backend.search.models.IndexingMixin),
        ),
        migrations.CreateModel(
            name='InformativeSnippet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permissions_dict', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of Creation')),
                ('tracked', models.BooleanField(default=True, verbose_name='Tracked')),
                ('source', models.URLField(blank=True, max_length=2048, null=True, verbose_name='Source')),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('statistics', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, null=True, verbose_name='Statistics')),
                ('location_id_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier Name')),
                ('location_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier')),
                ('rels_dict', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Relationships Dictionary')),
                ('order', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_studio_backend.changes.models.get_order_default, verbose_name='Media Content Order')),
                ('title', models.CharField(default=str, max_length=64, verbose_name='Title')),
                ('brief_description', models.CharField(blank=True, max_length=140, null=True, verbose_name='Description')),
                ('long_description', models.TextField(blank=True, default='<p></p>', verbose_name='Long Description')),
                ('twitter_feed', models.URLField(blank=True, null=True, verbose_name='Twitter Feed URL')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, voto_studio_backend.forms.models.InfoMixin, voto_studio_backend.search.models.IndexingMixin),
        ),
    ]
