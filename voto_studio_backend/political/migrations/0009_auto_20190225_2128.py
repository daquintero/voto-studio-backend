# Generated by Django 2.1.7 on 2019-02-25 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('political', '0008_auto_20190224_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(default=str, max_length=2048, verbose_name='Name'),
        ),
    ]
