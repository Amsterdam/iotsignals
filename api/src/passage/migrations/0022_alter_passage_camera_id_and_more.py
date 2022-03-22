# Generated by Django 4.0.2 on 2022-03-22 09:17

import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passage', '0021_alter_passage_passage_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passage',
            name='camera_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='passage',
            name='camera_kijkrichting',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='passage',
            name='camera_locatie',
            field=django.contrib.gis.db.models.fields.PointField(null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='passage',
            name='camera_naam',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='passage',
            name='kenteken_land',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='passage',
            name='kenteken_land_betrouwbaarheid',
            field=models.SmallIntegerField(null=True, validators=[django.core.validators.MaxValueValidator(1000), django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='passage',
            name='kenteken_nummer_betrouwbaarheid',
            field=models.SmallIntegerField(null=True, validators=[django.core.validators.MaxValueValidator(1000), django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='passage',
            name='rijrichting',
            field=models.SmallIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='passage',
            name='rijstrook',
            field=models.SmallIntegerField(null=True),
        ),
    ]
