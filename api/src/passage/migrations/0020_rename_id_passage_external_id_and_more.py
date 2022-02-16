# Generated by Django 4.0.2 on 2022-02-16 12:53

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('passage', '0019_alter_camera_id_alter_heavytraffichouraggregation_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='passage',
            old_name='id',
            new_name='external_id',
        ),
        migrations.AddConstraint(
            model_name='passage',
            constraint=models.UniqueConstraint(django.db.models.expressions.F('external_id'), django.db.models.expressions.F('camera_id'), django.db.models.expressions.F('passage_at'), name='unique_passage_camera'),
        ),
    ]
