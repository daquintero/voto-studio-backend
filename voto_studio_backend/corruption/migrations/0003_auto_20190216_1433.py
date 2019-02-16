# Generated by Django 2.1.5 on 2019-02-16 14:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('corruption', '0002_auto_20190216_1433'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('media', '0001_initial'),
        ('political', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='informativesnippet',
            name='permitted_users',
            field=models.ManyToManyField(blank=True, related_name='corruption_informativesnippet_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='informativesnippet',
            name='resources',
            field=models.ManyToManyField(blank=True, to='media.Resource'),
        ),
        migrations.AddField(
            model_name='informativesnippet',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='informativesnippet',
            name='videos',
            field=models.ManyToManyField(blank=True, to='media.Video'),
        ),
        migrations.AddField(
            model_name='financialitem',
            name='images',
            field=models.ManyToManyField(blank=True, to='media.Image'),
        ),
        migrations.AddField(
            model_name='financialitem',
            name='permitted_users',
            field=models.ManyToManyField(blank=True, related_name='corruption_financialitem_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='financialitem',
            name='resources',
            field=models.ManyToManyField(blank=True, to='media.Resource'),
        ),
        migrations.AddField(
            model_name='financialitem',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='financialitem',
            name='videos',
            field=models.ManyToManyField(blank=True, to='media.Video'),
        ),
        migrations.AddField(
            model_name='corruptioncase',
            name='controversies',
            field=models.ManyToManyField(blank=True, to='political.Controversy'),
        ),
        migrations.AddField(
            model_name='corruptioncase',
            name='financial_items',
            field=models.ManyToManyField(blank=True, to='corruption.FinancialItem'),
        ),
        migrations.AddField(
            model_name='corruptioncase',
            name='images',
            field=models.ManyToManyField(blank=True, to='media.Image'),
        ),
        migrations.AddField(
            model_name='corruptioncase',
            name='permitted_users',
            field=models.ManyToManyField(blank=True, related_name='corruption_corruptioncase_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='corruptioncase',
            name='resources',
            field=models.ManyToManyField(blank=True, to='media.Resource'),
        ),
        migrations.AddField(
            model_name='corruptioncase',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='corruptioncase',
            name='videos',
            field=models.ManyToManyField(blank=True, to='media.Video'),
        ),
    ]
