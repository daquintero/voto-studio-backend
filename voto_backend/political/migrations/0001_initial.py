# Generated by Django 2.1.5 on 2019-02-08 02:44

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import voto_backend.changes.models
import voto_backend.forms.models
import voto_backend.search.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('corruption', '0009_auto_20190208_0244'),
        ('media', '0010_auto_20190207_1933'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of Creation')),
                ('tracked', models.BooleanField(default=True, verbose_name='Tracked')),
                ('location_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier')),
                ('location_id_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier Name')),
                ('source', models.URLField(blank=True, max_length=2048, null=True, verbose_name='Source')),
                ('statistics', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Statistics')),
                ('order', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_backend.changes.models.get_order_default, verbose_name='Media Content Order')),
                ('images', models.ManyToManyField(blank=True, to='media.Image')),
                ('resources', models.ManyToManyField(blank=True, to='media.Resource')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('videos', models.ManyToManyField(blank=True, to='media.Video')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, voto_backend.forms.models.InfoMixin, voto_backend.search.models.IndexingMixin),
        ),
        migrations.CreateModel(
            name='Controversy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of Creation')),
                ('tracked', models.BooleanField(default=True, verbose_name='Tracked')),
                ('location_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier')),
                ('location_id_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier Name')),
                ('source', models.URLField(blank=True, max_length=2048, null=True, verbose_name='Source')),
                ('statistics', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Statistics')),
                ('order', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_backend.changes.models.get_order_default, verbose_name='Media Content Order')),
                ('images', models.ManyToManyField(blank=True, to='media.Image')),
                ('resources', models.ManyToManyField(blank=True, to='media.Resource')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('videos', models.ManyToManyField(blank=True, to='media.Video')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, voto_backend.forms.models.InfoMixin, voto_backend.search.models.IndexingMixin),
        ),
        migrations.CreateModel(
            name='ElectoralPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of Creation')),
                ('tracked', models.BooleanField(default=True, verbose_name='Tracked')),
                ('location_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier')),
                ('location_id_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier Name')),
                ('source', models.URLField(blank=True, max_length=2048, null=True, verbose_name='Source')),
                ('statistics', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Statistics')),
                ('order', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_backend.changes.models.get_order_default, verbose_name='Media Content Order')),
                ('images', models.ManyToManyField(blank=True, to='media.Image')),
                ('resources', models.ManyToManyField(blank=True, to='media.Resource')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('videos', models.ManyToManyField(blank=True, to='media.Video')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, voto_backend.forms.models.InfoMixin, voto_backend.search.models.IndexingMixin),
        ),
        migrations.CreateModel(
            name='Individual',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of Creation')),
                ('tracked', models.BooleanField(default=True, verbose_name='Tracked')),
                ('location_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier')),
                ('location_id_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier Name')),
                ('source', models.URLField(blank=True, max_length=2048, null=True, verbose_name='Source')),
                ('statistics', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Statistics')),
                ('order', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_backend.changes.models.get_order_default, verbose_name='Media Content Order')),
                ('name', models.CharField(default=str, max_length=64, verbose_name='Name')),
                ('alias', models.CharField(default=str, max_length=64, verbose_name='Alias')),
                ('brief_description', models.CharField(blank=True, max_length=140, null=True, verbose_name='Description')),
                ('long_description', models.TextField(blank=True, default='<p></p>', verbose_name='Long Description')),
                ('email', models.CharField(default=str, max_length=64, verbose_name='Email Address')),
                ('phone_number', models.CharField(default=str, max_length=64, verbose_name='Phone Number')),
                ('website', models.URLField(blank=True, max_length=2048, null=True, verbose_name='Website')),
                ('twitter_username', models.CharField(default=str, max_length=15, verbose_name='Twitter Username')),
                ('facebook_username', models.CharField(default=str, max_length=128, verbose_name='Facebook Username')),
                ('type', models.CharField(blank=True, choices=[('1', 'Politician'), ('2', 'Business person'), ('3', 'Civilian')], max_length=128, null=True, verbose_name='Type')),
                ('total_amount', models.FloatField(blank=True, default=float, null=True)),
                ('financial_items', models.ManyToManyField(blank=True, to='corruption.FinancialItem')),
                ('images', models.ManyToManyField(blank=True, to='media.Image')),
                ('individuals', models.ManyToManyField(blank=True, related_name='_individual_individuals_+', to='political.Individual')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, voto_backend.forms.models.InfoMixin, voto_backend.search.models.IndexingMixin),
        ),
        migrations.CreateModel(
            name='Law',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of Creation')),
                ('tracked', models.BooleanField(default=True, verbose_name='Tracked')),
                ('location_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier')),
                ('location_id_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier Name')),
                ('source', models.URLField(blank=True, max_length=2048, null=True, verbose_name='Source')),
                ('statistics', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Statistics')),
                ('order', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_backend.changes.models.get_order_default, verbose_name='Media Content Order')),
                ('code', models.CharField(blank=True, max_length=128, null=True, verbose_name='Law Code')),
                ('brief_description', models.CharField(blank=True, max_length=128, null=True, verbose_name='Description')),
                ('long_description', models.TextField(blank=True, default='<p></p>', verbose_name='Long Description')),
                ('category', models.CharField(blank=True, choices=[('1', 'Economy'), ('2', 'Agriculture'), ('3', 'Employment'), ('4', 'Transport'), ('5', 'Energy'), ('6', 'Waste Management'), ('7', 'Indigenous Relations'), ('8', 'Health Services'), ('9', 'Pensions'), ('10', 'Security'), ('11', 'Emergency Services'), ('12', 'Education'), ('13', 'Poverty'), ('14', 'Business'), ('15', 'Industry'), ('16', 'Entertainment')], max_length=140, null=True, verbose_name='Category')),
                ('images', models.ManyToManyField(blank=True, to='media.Image')),
                ('resources', models.ManyToManyField(blank=True, to='media.Resource')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('videos', models.ManyToManyField(blank=True, to='media.Video')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, voto_backend.forms.models.InfoMixin, voto_backend.search.models.IndexingMixin),
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of Creation')),
                ('tracked', models.BooleanField(default=True, verbose_name='Tracked')),
                ('location_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier')),
                ('location_id_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier Name')),
                ('source', models.URLField(blank=True, max_length=2048, null=True, verbose_name='Source')),
                ('statistics', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Statistics')),
                ('order', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_backend.changes.models.get_order_default, verbose_name='Media Content Order')),
                ('images', models.ManyToManyField(blank=True, to='media.Image')),
                ('resources', models.ManyToManyField(blank=True, to='media.Resource')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('videos', models.ManyToManyField(blank=True, to='media.Video')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, voto_backend.forms.models.InfoMixin, voto_backend.search.models.IndexingMixin),
        ),
        migrations.CreateModel(
            name='Promise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of Creation')),
                ('tracked', models.BooleanField(default=True, verbose_name='Tracked')),
                ('location_id', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier')),
                ('location_id_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='Location Identifier Name')),
                ('source', models.URLField(blank=True, max_length=2048, null=True, verbose_name='Source')),
                ('statistics', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Statistics')),
                ('order', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=voto_backend.changes.models.get_order_default, verbose_name='Media Content Order')),
                ('images', models.ManyToManyField(blank=True, to='media.Image')),
                ('resources', models.ManyToManyField(blank=True, to='media.Resource')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('videos', models.ManyToManyField(blank=True, to='media.Video')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, voto_backend.forms.models.InfoMixin, voto_backend.search.models.IndexingMixin),
        ),
        migrations.AddField(
            model_name='individual',
            name='organizations',
            field=models.ManyToManyField(blank=True, to='political.Organization'),
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
    ]