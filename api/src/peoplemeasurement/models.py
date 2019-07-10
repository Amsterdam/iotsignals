from django.db import models
from django.contrib.postgres.fields import JSONField

from datetimeutc.fields import DateTimeUTCField


class PeopleMeasurement(models.Model):
    """PeopleMeasurement

    This models describes data coming from various sensors, such as
    counting cameras, 3D cameras and wifi sensors. The information
    contains for example people counts, direction, speed, lat/long etc.
    """

    version = models.CharField(max_length=10)
    timestamp = models.DateTimeField(db_index=True)
    sensor = models.CharField(max_length=255)
    sensortype = models.CharField(max_length=255)
    latitude = models.CharField(max_length=15)
    longitude = models.CharField(max_length=15)
    count = models.IntegerField()
    details = JSONField(null=True)
