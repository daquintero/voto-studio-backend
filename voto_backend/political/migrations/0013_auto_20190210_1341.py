# Generated by Django 2.1.5 on 2019-02-10 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('political', '0012_auto_20190210_0524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controversy',
            name='brief_description',
            field=models.CharField(blank=True, max_length=2048, null=True, verbose_name='Description'),
        ),
    ]
