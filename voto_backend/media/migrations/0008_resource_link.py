# Generated by Django 2.1.5 on 2019-02-07 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0007_auto_20190206_2113'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='link',
            field=models.URLField(blank=True, max_length=2048),
        ),
    ]
