# Generated by Django 2.1.7 on 2019-03-08 23:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corruption', '0009_auto_20190308_2315'),
    ]

    operations = [
        migrations.RenameField(
            model_name='corruptioncase',
            old_name='date_last_publish',
            new_name='date_last_published',
        ),
        migrations.RenameField(
            model_name='financialitem',
            old_name='date_last_publish',
            new_name='date_last_published',
        ),
        migrations.RenameField(
            model_name='informativesnippet',
            old_name='date_last_publish',
            new_name='date_last_published',
        ),
    ]
