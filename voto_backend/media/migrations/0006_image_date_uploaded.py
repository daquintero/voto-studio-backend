# Generated by Django 2.1.5 on 2019-02-06 14:29

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0005_auto_20190206_1429'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='date_uploaded',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]