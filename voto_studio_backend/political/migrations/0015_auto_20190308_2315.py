# Generated by Django 2.1.7 on 2019-03-08 23:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('political', '0014_auto_20190308_1809'),
    ]

    operations = [
        migrations.RenameField(
            model_name='achievement',
            old_name='last_publish_date',
            new_name='date_last_publish',
        ),
        migrations.RenameField(
            model_name='controversy',
            old_name='last_publish_date',
            new_name='date_last_publish',
        ),
        migrations.RenameField(
            model_name='individual',
            old_name='last_publish_date',
            new_name='date_last_publish',
        ),
        migrations.RenameField(
            model_name='law',
            old_name='last_publish_date',
            new_name='date_last_publish',
        ),
        migrations.RenameField(
            model_name='organization',
            old_name='last_publish_date',
            new_name='date_last_publish',
        ),
        migrations.RenameField(
            model_name='promise',
            old_name='last_publish_date',
            new_name='date_last_publish',
        ),
    ]
