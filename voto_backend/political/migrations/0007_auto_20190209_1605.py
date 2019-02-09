# Generated by Django 2.1.5 on 2019-02-09 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('political', '0006_auto_20190209_0216'),
    ]

    operations = [
        migrations.AddField(
            model_name='individual',
            name='laws',
            field=models.ManyToManyField(blank=True, to='political.Law'),
        ),
        migrations.AlterField(
            model_name='achievement',
            name='type',
            field=models.CharField(blank=True, choices=[('1', 'Economy'), ('2', 'Agriculture'), ('3', 'Employment'), ('4', 'Transport'), ('5', 'Energy'), ('6', 'Waste Management'), ('7', 'Indigenous Relations'), ('8', 'Health Services'), ('9', 'Pensions'), ('10', 'Security'), ('11', 'Emergency Services'), ('12', 'Education'), ('13', 'Poverty'), ('14', 'Business'), ('15', 'Industry'), ('16', 'Entertainment'), ('17', 'None')], max_length=128, null=True, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='controversy',
            name='type',
            field=models.CharField(blank=True, choices=[('1', 'Economy'), ('2', 'Agriculture'), ('3', 'Employment'), ('4', 'Transport'), ('5', 'Energy'), ('6', 'Waste Management'), ('7', 'Indigenous Relations'), ('8', 'Health Services'), ('9', 'Pensions'), ('10', 'Security'), ('11', 'Emergency Services'), ('12', 'Education'), ('13', 'Poverty'), ('14', 'Business'), ('15', 'Industry'), ('16', 'Entertainment'), ('17', 'None')], max_length=128, null=True, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='law',
            name='category',
            field=models.CharField(blank=True, choices=[('1', 'Economy'), ('2', 'Agriculture'), ('3', 'Employment'), ('4', 'Transport'), ('5', 'Energy'), ('6', 'Waste Management'), ('7', 'Indigenous Relations'), ('8', 'Health Services'), ('9', 'Pensions'), ('10', 'Security'), ('11', 'Emergency Services'), ('12', 'Education'), ('13', 'Poverty'), ('14', 'Business'), ('15', 'Industry'), ('16', 'Entertainment'), ('17', 'None')], max_length=140, null=True, verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='promise',
            name='type',
            field=models.CharField(blank=True, choices=[('1', 'Economy'), ('2', 'Agriculture'), ('3', 'Employment'), ('4', 'Transport'), ('5', 'Energy'), ('6', 'Waste Management'), ('7', 'Indigenous Relations'), ('8', 'Health Services'), ('9', 'Pensions'), ('10', 'Security'), ('11', 'Emergency Services'), ('12', 'Education'), ('13', 'Poverty'), ('14', 'Business'), ('15', 'Industry'), ('16', 'Entertainment'), ('17', 'None')], max_length=128, null=True, verbose_name='Type'),
        ),
    ]
