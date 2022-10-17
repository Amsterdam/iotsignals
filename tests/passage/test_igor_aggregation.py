from datetime import timedelta, datetime

import pytest
import time_machine
from django.core.management import call_command
from django.utils import timezone

from passage.management.commands.make_partitions import make_partitions
from passage.models import Camera, IGORHourAggregation
from .factories import PassageFactory


@pytest.mark.django_db
class TestIGORAggregation:
    @time_machine.travel(datetime.today() + timedelta(days=1), tick=False)
    @pytest.mark.parametrize("taxi_indicator", [True, False, None])
    @pytest.mark.parametrize("europese_voertuigcategorie", ["A", "B"])
    @pytest.mark.parametrize("kenteken_land", ["NL", "BE"])
    def test_aggregation(
        self, taxi_indicator, europese_voertuigcategorie, kenteken_land
    ):
        helper_table_row = Camera.objects.filter(cordon__in=['S100', 'A10']).first()

        yesterday = timezone.now() - timedelta(days=1)
        # create ten passages for the correct day
        PassageFactory.create_batch(
            size=10,
            passage_at=yesterday,
            camera_naam=helper_table_row.camera_naam,
            camera_kijkrichting=helper_table_row.camera_kijkrichting,
            rijrichting=helper_table_row.rijrichting,
            taxi_indicator=taxi_indicator,
            europese_voertuigcategorie=europese_voertuigcategorie,
            kenteken_land=kenteken_land,
        )
        # create some more for different days
        other_days = [
            yesterday - timedelta(days=1),
            yesterday - timedelta(days=2),
            yesterday - timedelta(days=3),
        ]

        for day in other_days:
            make_partitions([day])
            PassageFactory.create_batch(
                size=5,
                passage_at=day,
                camera_naam=helper_table_row.camera_naam,
                camera_kijkrichting=helper_table_row.camera_kijkrichting,
                rijrichting=helper_table_row.rijrichting,
            )

        assert IGORHourAggregation.objects.count() == 0
        call_command(
            'passage_igor_hour_aggregation',
            from_date=other_days[2].date(),
        )

        expected_timestamp = yesterday.replace(minute=0, second=0, microsecond=0)
        expected_date = yesterday.date()
        expected_year = yesterday.year
        expected_month = yesterday.month
        expected_day = yesterday.day
        expected_week = int(yesterday.strftime("%U"))
        expected_day_of_week = str(yesterday.isoweekday())
        expected_hour = yesterday.hour

        # (implicitly) assert there is one result for today by using get
        result = IGORHourAggregation.objects.filter(
            passage_at_timestamp=expected_timestamp
        ).get()
        for day in other_days:
            assert IGORHourAggregation.objects.filter(
                passage_at_timestamp=day.replace(minute=0, second=0, microsecond=0)
            ).exists()

        # check extracted datetime info
        assert result.passage_at_timestamp == expected_timestamp
        assert result.passage_at_date == expected_date
        assert result.passage_at_year == expected_year
        assert result.passage_at_month == expected_month
        assert result.passage_at_day == expected_day
        assert result.passage_at_week == expected_week
        assert result.passage_at_day_of_week == expected_day_of_week
        assert result.passage_at_hour == expected_hour

        assert result.taxi_indicator == taxi_indicator
        assert result.europese_voertuigcategorie == europese_voertuigcategorie
        assert result.kenteken_land == kenteken_land

        # check helper table data
        helper_fields = [
            'order_kaart',
            'order_naam',
            'cordon',
            'richting',
            'location',
            'geom',
            'azimuth',
            'camera_id',
            'camera_naam',
            'vma_linknr'
        ]
        for attr in helper_fields:
            assert getattr(result, attr) == getattr(helper_table_row, attr)

        # check the most important (calculated) attribute: intensity
        assert result.intensiteit == 10
