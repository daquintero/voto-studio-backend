# Generated by Django 2.1.5 on 2019-02-08 03:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('corruption', '0010_auto_20190208_0324'),
        ('political', '0002_auto_20190208_0246'),
    ]

    operations = [
        migrations.AddField(
            model_name='achievement',
            name='brief_description',
            field=models.CharField(blank=True, max_length=140, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='achievement',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='achievement',
            name='individual',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='political.Individual'),
        ),
        migrations.AddField(
            model_name='achievement',
            name='type',
            field=models.CharField(blank=True, choices=[('1', 'Economy'), ('2', 'Agriculture'), ('3', 'Employment'), ('4', 'Transport'), ('5', 'Energy'), ('6', 'Waste Management'), ('7', 'Indigenous Relations'), ('8', 'Health Services'), ('9', 'Pensions'), ('10', 'Security'), ('11', 'Emergency Services'), ('12', 'Education'), ('13', 'Poverty'), ('14', 'Business'), ('15', 'Industry'), ('16', 'Entertainment')], max_length=128, null=True, verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='controversy',
            name='brief_description',
            field=models.CharField(blank=True, max_length=140, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='controversy',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='controversy',
            name='financial_items',
            field=models.ManyToManyField(blank=True, to='corruption.FinancialItem'),
        ),
        migrations.AddField(
            model_name='controversy',
            name='individual',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='political.Individual'),
        ),
        migrations.AddField(
            model_name='controversy',
            name='type',
            field=models.CharField(blank=True, choices=[('1', 'Economy'), ('2', 'Agriculture'), ('3', 'Employment'), ('4', 'Transport'), ('5', 'Energy'), ('6', 'Waste Management'), ('7', 'Indigenous Relations'), ('8', 'Health Services'), ('9', 'Pensions'), ('10', 'Security'), ('11', 'Emergency Services'), ('12', 'Education'), ('13', 'Poverty'), ('14', 'Business'), ('15', 'Industry'), ('16', 'Entertainment')], max_length=128, null=True, verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='electoralperiod',
            name='attendance_percentage',
            field=models.FloatField(blank=True, default=float, null=True, verbose_name='Attendance Percentage'),
        ),
        migrations.AddField(
            model_name='electoralperiod',
            name='brief_description',
            field=models.CharField(blank=True, max_length=140, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='electoralperiod',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='electoralperiod',
            name='financial_items',
            field=models.ManyToManyField(blank=True, to='corruption.FinancialItem'),
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
            name='long_description',
            field=models.TextField(blank=True, default='<p></p>', verbose_name='Long Description'),
        ),
        migrations.AddField(
            model_name='electoralperiod',
            name='period',
            field=models.CharField(blank=True, choices=[('1419', '2014-2019'), ('0914', '2009-2014'), ('0409', '2004-2009'), ('9904', '1999-2004'), ('9499', '1994-1999')], max_length=128, null=True, verbose_name='Period'),
        ),
        migrations.AddField(
            model_name='electoralperiod',
            name='position',
            field=models.CharField(blank=True, choices=[('1', 'Presidente'), ('2', 'Diputado'), ('3', 'Representante'), ('4', 'Alcalde'), ('5', 'Gobernador')], max_length=128, null=True, verbose_name='Position'),
        ),
        migrations.AddField(
            model_name='electoralperiod',
            name='published_public_finances',
            field=models.BooleanField(default=False, verbose_name='Published Public Finances'),
        ),
        migrations.AddField(
            model_name='individual',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='law',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='brief_description',
            field=models.CharField(blank=True, max_length=140, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='organization',
            name='corruption_related_funds',
            field=models.FloatField(blank=True, default=float, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='email',
            field=models.CharField(default=str, max_length=64, verbose_name='Email Address'),
        ),
        migrations.AddField(
            model_name='organization',
            name='facebook_username',
            field=models.CharField(default=str, max_length=128, verbose_name='Facebook Username'),
        ),
        migrations.AddField(
            model_name='organization',
            name='financial_items',
            field=models.ManyToManyField(blank=True, to='corruption.FinancialItem'),
        ),
        migrations.AddField(
            model_name='organization',
            name='long_description',
            field=models.TextField(blank=True, default='<p></p>', verbose_name='Long Description'),
        ),
        migrations.AddField(
            model_name='organization',
            name='name',
            field=models.CharField(default=str, max_length=64, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='organization',
            name='non_corruption_related_funds',
            field=models.FloatField(blank=True, default=float, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='organizations',
            field=models.ManyToManyField(blank=True, related_name='_organization_organizations_+', to='political.Organization'),
        ),
        migrations.AddField(
            model_name='organization',
            name='phone_number',
            field=models.CharField(default=str, max_length=64, verbose_name='Phone Number'),
        ),
        migrations.AddField(
            model_name='organization',
            name='twitter_username',
            field=models.CharField(default=str, max_length=15, verbose_name='Twitter Username'),
        ),
        migrations.AddField(
            model_name='organization',
            name='type',
            field=models.CharField(blank=True, choices=[('1', 'Governmental'), ('2', 'Political Party'), ('3', 'Company')], max_length=128, null=True, verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='organization',
            name='website',
            field=models.URLField(blank=True, max_length=2048, null=True, verbose_name='Website'),
        ),
        migrations.AddField(
            model_name='promise',
            name='brief_description',
            field=models.CharField(blank=True, max_length=140, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='promise',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='promise',
            name='fulfilled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='promise',
            name='individual',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='political.Individual'),
        ),
        migrations.AddField(
            model_name='promise',
            name='type',
            field=models.CharField(blank=True, choices=[('1', 'Economy'), ('2', 'Agriculture'), ('3', 'Employment'), ('4', 'Transport'), ('5', 'Energy'), ('6', 'Waste Management'), ('7', 'Indigenous Relations'), ('8', 'Health Services'), ('9', 'Pensions'), ('10', 'Security'), ('11', 'Emergency Services'), ('12', 'Education'), ('13', 'Poverty'), ('14', 'Business'), ('15', 'Industry'), ('16', 'Entertainment')], max_length=128, null=True, verbose_name='Type'),
        ),
    ]