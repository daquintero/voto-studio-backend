# Generated by Django 2.1.5 on 2019-02-06 13:41

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
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of Creation')),
                ('tracked', models.BooleanField(default=True, verbose_name='Tracked')),
                ('location_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier')),
                ('location_id_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier Name')),
                ('name', models.CharField(blank=True, max_length=30, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, voto_backend.forms.models.InfoMixin, voto_backend.search.models.IndexingMixin),
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of Creation')),
                ('tracked', models.BooleanField(default=True, verbose_name='Tracked')),
                ('location_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier')),
                ('location_id_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier Name')),
                ('title', models.CharField(blank=True, default=str, max_length=20)),
                ('icon', models.CharField(blank=True, default=str, max_length=40)),
                ('file', models.FileField(blank=True, null=True, upload_to='resources_fs/')),
                ('voting_resource', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, voto_backend.forms.models.InfoMixin, voto_backend.search.models.IndexingMixin),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of Creation')),
                ('tracked', models.BooleanField(default=True, verbose_name='Tracked')),
                ('location_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier')),
                ('location_id_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier Name')),
                ('title', models.CharField(blank=True, default=str, max_length=30)),
                ('embed_url_src', models.URLField(blank=True, max_length=256)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, voto_backend.forms.models.InfoMixin, voto_backend.search.models.IndexingMixin),
        ),
    ]