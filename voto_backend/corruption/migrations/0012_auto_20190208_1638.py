# Generated by Django 2.1.5 on 2019-02-08 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corruption', '0011_auto_20190208_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corruptioncase',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='financialitem',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='informativesnippet',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]