# Generated by Django 2.1.2 on 2018-11-06 08:58

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Passage',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False, unique=True)),
                ('versie', models.CharField(max_length=255)),
                ('datum_tijd', models.DateTimeField()),
                ('straat', models.CharField(max_length=255)),
                ('rijrichting', models.SmallIntegerField()),
                ('rijstrook', models.SmallIntegerField()),
                ('camera_id', models.CharField(max_length=255)),
                ('camera_naam', models.CharField(max_length=255)),
                ('camera_kijkrichting', models.CharField(max_length=255)),
                ('camera_locatie', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('kenteken_land', models.CharField(max_length=2)),
                ('kenteken_nummer_betrouwbaarheid', models.SmallIntegerField(validators=[django.core.validators.MaxValueValidator(1000), django.core.validators.MinValueValidator(1)])),
                ('kenteken_land_betrouwbaarheid', models.SmallIntegerField(validators=[django.core.validators.MaxValueValidator(1000), django.core.validators.MinValueValidator(1)])),
                ('kenteken_karakters_betrouwbaarheid', django.contrib.postgres.fields.jsonb.JSONField()),
                ('indicatie_snelheid', models.FloatField()),
                ('automatisch_verwerkbaar', models.BooleanField()),
                ('voertuig_soort', models.CharField(max_length=25)),
                ('merk', models.CharField(max_length=255)),
                ('inrichting', models.CharField(max_length=255)),
                ('datum_eerste_toelating', models.DateField()),
                ('datum_tenaamstelling', models.DateField()),
                ('toegestane_maximum_massa_voertuig', models.SmallIntegerField()),
                ('europese_voertuigcategorie', models.CharField(max_length=2)),
                ('europese_voertuigcategorie_toevoeging', models.CharField(max_length=1)),
                ('tax_indicator', models.BooleanField()),
                ('maximale_constructie_snelheid_bromsnorfiets', models.SmallIntegerField()),
                ('brandstoffen', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
        ),
    ]