# Generated by Django 2.1.7 on 2019-03-31 20:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('political', '0025_remove_organization_laws'),
    ]

    operations = [
        migrations.RenameField(
            model_name='individual',
            old_name='corruption_related_funds',
            new_name='related_funds',
        ),
        migrations.RenameField(
            model_name='organization',
            old_name='corruption_related_funds',
            new_name='related_funds',
        ),
        migrations.RemoveField(
            model_name='individual',
            name='non_corruption_related_funds',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='non_corruption_related_funds',
        ),
    ]
