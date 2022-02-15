# Generated by Django 4.0.2 on 2022-02-15 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passage', '0018_extra_rdw_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camera',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='heavytraffichouraggregation',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='igorhouraggregation',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='igorhouraggregation',
            name='taxi_indicator',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='passage',
            name='automatisch_verwerkbaar',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='passage',
            name='brandstoffen',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='passage',
            name='extra_data',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='passage',
            name='kenteken_karakters_betrouwbaarheid',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='passage',
            name='maximum_massa_trekken_geremd',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='passage',
            name='maximum_massa_trekken_ongeremd',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='passage',
            name='taxi_indicator',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='passage',
            name='wam_verzekerd',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='passagehouraggregation',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='passagehouraggregation',
            name='taxi_indicator',
            field=models.BooleanField(null=True),
        ),
    ]
