# Generated by Django 2.1.7 on 2019-03-31 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corruption', '0013_remove_financialitem_corruption_related'),
    ]

    operations = [
        migrations.AddField(
            model_name='informativesnippet',
            name='informative_snippets',
            field=models.ManyToManyField(blank=True, related_name='_informativesnippet_informative_snippets_+', to='corruption.InformativeSnippet'),
        ),
    ]
