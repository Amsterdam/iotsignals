from datetime import timedelta, datetime

import pytest
import time_machine
from django.core.management import call_command
from django.utils import timezone

from passage.models import HulptabelCameragebiedenTaxidashboard, TaxiHourAggregation, Camera, Passage
from .factories import PassageFactory, HulptabelCameragebiedenTaxidashboardFactory
import factory

@pytest.mark.django_db
class TestTaxiHourAggregation:
    @time_machine.travel(datetime.today() + timedelta(days=1), tick=False)
    @pytest.mark.parametrize("taxi_indicator", [True, False, None])
    @pytest.mark.parametrize("electric", [1, 0, None])

    def test_aggregation(
        self, taxi_indicator, electric
    ):
        HulptabelCameragebiedenTaxidashboardFactory.create_batch(
            size=10,
            gebiedstype="test",
            gebied="test",
            camera_id=factory.Sequence(lambda n: f'Name{n%2}') #2 different camera_ID's
        )
        helper_table_row = HulptabelCameragebiedenTaxidashboard.objects.all().first()
        print(helper_table_row)
        #helper_table_row = Camera.objects.filter().first()
        yesterday = timezone.now() - timedelta(days=1)
        # create ten passages for the correct day
        PassageFactory.create_batch(
            size=10,
            passage_at=yesterday,
            camera_naam=factory.Sequence(lambda n: f'Name{n%2}'), #2 different camera_names's
            taxi_indicator=taxi_indicator,
            electric=electric,
            kenteken_hash=factory.Sequence(lambda n: f'Name{n%2}'), #2 different hashes's
        )

        #check size base test tables
        assert TaxiHourAggregation.objects.count() == 0
        assert Passage.objects.count() == 10
        assert HulptabelCameragebiedenTaxidashboard.objects.count() == 10

        #Make aggregation
        call_command(
            'passage_taxi_hour_aggregation',
            from_date=yesterday.date(),
        )
        expected_date = yesterday.date()
        expected_hour = yesterday.hour

        assert Passage.objects.count() == 10
        assert HulptabelCameragebiedenTaxidashboard.objects.count() == 10


        # (implicitly) assert there is one result for today by using get
        if (electric is None and taxi_indicator is not True):
            assert TaxiHourAggregation.objects.count() == 0
        if (taxi_indicator is True and electric is True ):
            assert TaxiHourAggregation.objects.count() == 1
            result = TaxiHourAggregation.objects.filter(passage_at_date=expected_date)\
                .filter(electric=1).get()
            assert result.passage_at_date == expected_date
            assert result.hh == expected_hour
            assert result.unieke_passages == 2
            assert result.eletric == 1

            # check helper table data
            helper_fields = [
                'gebiedstype',
                'gebied',
            ]
            for attr in helper_fields:
                assert getattr(result, attr) == getattr(helper_table_row, attr)

        if (taxi_indicator is True and electric is False):
            assert TaxiHourAggregation.objects.count() == 1
            result = TaxiHourAggregation.objects.filter(passage_at_date=expected_date) \
                    .filter(electric=0).get()
            assert result.passage_at_date == expected_date
            assert result.hh == expected_hour
            assert result.unieke_passages == 2
            assert result.eletric == 0
            # check helper table data
            helper_fields = [
                'gebiedstype',
                'gebied',
            ]
            for attr in helper_fields:
                assert getattr(result, attr) == getattr(helper_table_row, attr)

