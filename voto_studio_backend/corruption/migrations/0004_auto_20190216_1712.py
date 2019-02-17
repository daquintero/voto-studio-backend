# Generated by Django 2.1.7 on 2019-02-16 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corruption', '0003_auto_20190216_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='informativesnippet',
            name='controversies',
            field=models.ManyToManyField(blank=True, related_name='informative_snippets', to='political.Controversy'),
        ),
        migrations.AlterField(
            model_name='informativesnippet',
            name='corruption_cases',
            field=models.ManyToManyField(blank=True, related_name='informative_snippets', to='corruption.CorruptionCase'),
        ),
        migrations.AlterField(
            model_name='informativesnippet',
            name='financial_items',
            field=models.ManyToManyField(blank=True, related_name='informative_snippets', to='corruption.FinancialItem'),
        ),
        migrations.AlterField(
            model_name='informativesnippet',
            name='individuals',
            field=models.ManyToManyField(blank=True, related_name='informative_snippets', to='political.Individual'),
        ),
        migrations.AlterField(
            model_name='informativesnippet',
            name='laws',
            field=models.ManyToManyField(blank=True, related_name='informative_snippets', to='political.Law'),
        ),
    ]
