# Generated by Django 2.1.7 on 2019-02-19 16:36

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Change',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage_type', models.CharField(blank=True, choices=[('created', 'created'), ('updated', 'updated'), ('deleted', 'deleted')], max_length=128, verbose_name='Stage type')),
                ('description', models.CharField(blank=True, max_length=256, verbose_name='Change description')),
                ('object_id', models.PositiveIntegerField(null=True, verbose_name='Copy instance id')),
                ('base_id', models.PositiveIntegerField(null=True, verbose_name='Base instance id')),
                ('parent_object_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='Parent instance id')),
                ('one_to_one_models', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True, verbose_name="Fully describes base instance's one to one rels")),
                ('many_to_many_models', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True, verbose_name="Describes base instance's many to manys rels")),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of creation')),
                ('committed', models.BooleanField(default=False, verbose_name='Whether the change has been committed')),
                ('date_committed', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of commit')),
                ('reverted', models.BooleanField(default=False, verbose_name='Whether the change has been reverted')),
                ('date_reverted', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of revert')),
            ],
        ),
        migrations.CreateModel(
            name='ChangeGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=128, verbose_name='Short description of the change group')),
                ('date_created', models.DateTimeField(blank=True, verbose_name='Date when change group committed')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='ID of parent instance')),
                ('changes_committed', models.ManyToManyField(blank=True, to='changes.Change')),
                ('content_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
    ]
