# Generated by Django 4.0.2 on 2022-03-02 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passage', '0018_passage_aantal_assen_passage_aantal_staanplaatsen_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='passage',
            name='volgnummer',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
