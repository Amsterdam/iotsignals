# Generated by Django 2.1.5 on 2019-01-21 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('passage', '0004_auto_20190121_1258'),
    ]

    operations = [
        migrations.RenameField(
            model_name='passage',
            old_name='tax_indicator',
            new_name='taxi_indicator',
        ),
    ]