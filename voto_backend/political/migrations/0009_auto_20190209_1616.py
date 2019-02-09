# Generated by Django 2.1.5 on 2019-02-09 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('political', '0008_auto_20190209_1612'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='individual',
            name='organizations',
        ),
        migrations.AddField(
            model_name='organization',
            name='individuals',
            field=models.ManyToManyField(blank=True, to='political.Individual'),
        ),
    ]
