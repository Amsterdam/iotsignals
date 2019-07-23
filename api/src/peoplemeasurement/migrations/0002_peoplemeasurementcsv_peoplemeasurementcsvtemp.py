# Generated by Django 2.2.3 on 2019-07-23 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peoplemeasurement', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PeopleMeasurementCSV',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('camera', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField()),
                ('direction_index', models.CharField(max_length=30)),
                ('direction_name', models.CharField(max_length=30)),
                ('label', models.CharField(max_length=255)),
                ('value', models.FloatField(max_length=255)),
                ('processed', models.CharField(max_length=30)),
                ('csv_name', models.CharField(max_length=255, null=True)),
            ],
            options={
                'ordering': ('timestamp',),
            },
        ),
        migrations.CreateModel(
            name='PeopleMeasurementCSVTemp',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('camera', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField()),
                ('direction_index', models.CharField(max_length=30)),
                ('direction_name', models.CharField(max_length=30)),
                ('label', models.CharField(max_length=255)),
                ('value', models.FloatField(max_length=255)),
                ('processed', models.CharField(max_length=30)),
            ],
            options={
                'ordering': ('timestamp',),
            },
        ),
    ]
