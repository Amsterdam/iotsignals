# Generated by Django 4.0.4 on 2022-06-24 08:53

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passage', '0030_update_camera_helpertable'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeavyTrafficHourAggregationV2',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('passage_at_date', models.DateField()),
                ('passage_at_year', models.SmallIntegerField()),
                ('passage_at_month', models.SmallIntegerField()),
                ('passage_at_day', models.SmallIntegerField()),
                ('passage_at_week', models.SmallIntegerField()),
                ('passage_at_day_of_week', models.CharField(max_length=20)),
                ('passage_at_hour', models.SmallIntegerField(db_index=True)),
                ('camera_id', models.CharField(blank=True, max_length=255, null=True)),
                ('camera_naam', models.CharField(blank=True, max_length=255, null=True)),
                ('camera_kijkrichting', models.FloatField(blank=True, null=True)),
                ('camera_locatie', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('rijrichting', models.SmallIntegerField(blank=True, null=True)),
                ('rijrichting_correct', models.CharField(blank=True, max_length=10, null=True)),
                ('straat', models.CharField(blank=True, max_length=255, null=True)),
                ('cordon', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('cordon_order_kaart', models.IntegerField(blank=True, null=True)),
                ('cordon_order_naam', models.CharField(blank=True, max_length=255, null=True)),
                ('massa_ledig_voertuig', models.CharField(blank=True, max_length=255, null=True)),
                ('toegestane_maximum_massa_voertuig', models.CharField(blank=True, max_length=255, null=True)),
                ('voertuig_soort', models.CharField(blank=True, max_length=64, null=True)),
                ('inrichting', models.CharField(blank=True, max_length=255, null=True)),
                ('europese_voertuigcategorie', models.CharField(blank=True, max_length=2, null=True)),
                ('europese_voertuigcategorie_toevoeging', models.CharField(blank=True, max_length=1, null=True)),
                ('versit_klasse', models.CharField(blank=True, max_length=255, null=True)),
                ('brandstoffen', models.JSONField(blank=True, null=True)),
                ('co2_uitstoot_gecombineerd', models.FloatField(blank=True, null=True)),
                ('co2_uitstoot_gewogen', models.FloatField(blank=True, null=True)),
                ('milieuklasse_eg_goedkeuring_zwaar', models.CharField(blank=True, max_length=255, null=True)),
                ('count', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'passage_heavytraffichouraggregation_v2',
            },
        ),
    ]
