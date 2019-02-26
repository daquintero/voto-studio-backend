# Generated by Django 2.1.7 on 2019-02-24 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('political', '0007_auto_20190221_1808'),
    ]

    operations = [
        migrations.AddField(
            model_name='individual',
            name='instagram_username',
            field=models.CharField(default=str, max_length=128, verbose_name='Instagram Username'),
        ),
        migrations.AddField(
            model_name='organization',
            name='instagram_username',
            field=models.CharField(default=str, max_length=128, verbose_name='Instagram Username'),
        ),
    ]