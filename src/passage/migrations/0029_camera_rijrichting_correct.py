# Generated by Django 4.0.4 on 2022-06-24 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passage', '0028_alter_heavytraffichouraggregation_azimuth_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='camera',
            name='rijrichting_correct',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
