# Generated by Django 2.1.5 on 2019-02-09 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('political', '0009_auto_20190209_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(default=str, max_length=2048, unique=True, verbose_name='Name'),
        ),
    ]
