# Generated by Django 4.0.2 on 2022-05-11 14:14

from django.db import migrations

from passage.helpertable_importer import import_helper_table_into_camera


class Migration(migrations.Migration):

    dependencies = [
        ('passage', '0025_camera_camera_id_camera_vma_linknr_and_more'),
    ]

    operations = [
        migrations.RunPython(import_helper_table_into_camera, migrations.RunPython.noop)
    ]
