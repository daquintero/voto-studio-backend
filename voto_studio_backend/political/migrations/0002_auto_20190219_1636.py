# Generated by Django 2.1.7 on 2019-02-19 16:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('political', '0001_initial'),
        ('media', '0002_auto_20190219_1636'),
        ('corruption', '0003_auto_20190219_1636'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='promise',
            name='permitted_users',
            field=models.ManyToManyField(blank=True, related_name='political_promise_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='promise',
            name='resources',
            field=models.ManyToManyField(blank=True, to='media.Resource'),
        ),
        migrations.AddField(
            model_name='promise',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='promise',
            name='videos',
            field=models.ManyToManyField(blank=True, to='media.Video'),
        ),
        migrations.AddField(
            model_name='organization',
            name='financial_items',
            field=models.ManyToManyField(blank=True, to='corruption.FinancialItem'),
        ),
        migrations.AddField(
            model_name='organization',
            name='images',
            field=models.ManyToManyField(blank=True, to='media.Image'),
        ),
        migrations.AddField(
            model_name='organization',
            name='individuals',
            field=models.ManyToManyField(blank=True, to='political.Individual'),
        ),
        migrations.AddField(
            model_name='organization',
            name='organizations',
            field=models.ManyToManyField(blank=True, related_name='_organization_organizations_+', to='political.Organization'),
        ),
        migrations.AddField(
            model_name='organization',
            name='permitted_users',
            field=models.ManyToManyField(blank=True, related_name='political_organization_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='organization',
            name='resources',
            field=models.ManyToManyField(blank=True, to='media.Resource'),
        ),
        migrations.AddField(
            model_name='organization',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='organization',
            name='videos',
            field=models.ManyToManyField(blank=True, to='media.Video'),
        ),
        migrations.AddField(
            model_name='law',
            name='images',
            field=models.ManyToManyField(blank=True, to='media.Image'),
        ),
        migrations.AddField(
            model_name='law',
            name='permitted_users',
            field=models.ManyToManyField(blank=True, related_name='political_law_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='law',
            name='resources',
            field=models.ManyToManyField(blank=True, to='media.Resource'),
        ),
        migrations.AddField(
            model_name='law',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='law',
            name='videos',
            field=models.ManyToManyField(blank=True, to='media.Video'),
        ),
        migrations.AddField(
            model_name='individual',
            name='financial_items',
            field=models.ManyToManyField(blank=True, to='corruption.FinancialItem'),
        ),
        migrations.AddField(
            model_name='individual',
            name='images',
            field=models.ManyToManyField(blank=True, to='media.Image'),
        ),
        migrations.AddField(
            model_name='individual',
            name='individuals',
            field=models.ManyToManyField(blank=True, related_name='_individual_individuals_+', to='political.Individual'),
        ),
        migrations.AddField(
            model_name='individual',
            name='laws',
            field=models.ManyToManyField(blank=True, to='political.Law'),
        ),
        migrations.AddField(
            model_name='individual',
            name='permitted_users',
            field=models.ManyToManyField(blank=True, related_name='political_individual_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='individual',
            name='resources',
            field=models.ManyToManyField(blank=True, to='media.Resource'),
        ),
        migrations.AddField(
            model_name='individual',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='individual',
            name='videos',
            field=models.ManyToManyField(blank=True, to='media.Video'),
        ),
        migrations.AddField(
            model_name='electoralperiod',
            name='financial_items',
            field=models.ManyToManyField(blank=True, to='corruption.FinancialItem'),
        ),
        migrations.AddField(
            model_name='electoralperiod',
            name='images',
            field=models.ManyToManyField(blank=True, to='media.Image'),
        ),
        migrations.AddField(
            model_name='electoralperiod',
            name='individual',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='political.Individual'),
        ),
        migrations.AddField(
            model_name='electoralperiod',
            name='laws',
            field=models.ManyToManyField(blank=True, to='political.Law'),
        ),
        migrations.AddField(
            model_name='electoralperiod',
            name='permitted_users',
            field=models.ManyToManyField(blank=True, related_name='political_electoralperiod_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='electoralperiod',
            name='resources',
            field=models.ManyToManyField(blank=True, to='media.Resource'),
        ),
        migrations.AddField(
            model_name='electoralperiod',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='electoralperiod',
            name='videos',
            field=models.ManyToManyField(blank=True, to='media.Video'),
        ),
        migrations.AddField(
            model_name='controversy',
            name='financial_items',
            field=models.ManyToManyField(blank=True, to='corruption.FinancialItem'),
        ),
        migrations.AddField(
            model_name='controversy',
            name='images',
            field=models.ManyToManyField(blank=True, to='media.Image'),
        ),
        migrations.AddField(
            model_name='controversy',
            name='individual',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='political.Individual'),
        ),
        migrations.AddField(
            model_name='controversy',
            name='permitted_users',
            field=models.ManyToManyField(blank=True, related_name='political_controversy_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='controversy',
            name='resources',
            field=models.ManyToManyField(blank=True, to='media.Resource'),
        ),
        migrations.AddField(
            model_name='controversy',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='controversy',
            name='videos',
            field=models.ManyToManyField(blank=True, to='media.Video'),
        ),
        migrations.AddField(
            model_name='achievement',
            name='images',
            field=models.ManyToManyField(blank=True, to='media.Image'),
        ),
        migrations.AddField(
            model_name='achievement',
            name='individual',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='political.Individual'),
        ),
        migrations.AddField(
            model_name='achievement',
            name='permitted_users',
            field=models.ManyToManyField(blank=True, related_name='political_achievement_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='achievement',
            name='resources',
            field=models.ManyToManyField(blank=True, to='media.Resource'),
        ),
        migrations.AddField(
            model_name='achievement',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='achievement',
            name='videos',
            field=models.ManyToManyField(blank=True, to='media.Video'),
        ),
    ]
