# Generated by Django 2.1.7 on 2019-03-04 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('political', '0011_auto_20190304_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='law',
            name='brief_description',
            field=models.CharField(blank=True, max_length=2048, null=True, verbose_name='Description'),
        ),
    ]