# Generated by Django 2.2.20 on 2021-06-07 09:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('passage', '0012_passage_privacy_check'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='passage',
            name='privacy_check',
        ),
    ]
