# Generated by Django 4.0.2 on 2022-05-11 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passage', '0024_alter_passagehouraggregation_voertuig_soort'),
    ]

    operations = [
        migrations.AddField(
            model_name='camera',
            name='camera_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='vma_linknr',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='igorhouraggregation',
            name='camera_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='igorhouraggregation',
            name='camera_naam',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='igorhouraggregation',
            name='vma_linknr',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
