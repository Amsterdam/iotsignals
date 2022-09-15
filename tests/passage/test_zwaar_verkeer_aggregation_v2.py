from datetime import timedelta, datetime

import pytest
import time_machine
from django.core.management import call_command
from django.utils import timezone

from passage.models import (
    Camera,
    HeavyTrafficHourAggregationV2,
)
from .factories import PassageFactory


@pytest.mark.django_db
class TestZwaarVerkeerHourAggregationV2:
    @time_machine.travel(datetime.today() + timedelta(days=1), tick=False)
    @pytest.mark.parametrize(
        'voertuig_soort,is_bedrijfsvoertuig',
        [
            ('Personenauto', False),
            ('Vrachtwagen', False),
            ('Bedrijfsauto', True),
        ],
    )
    @pytest.mark.parametrize(
        'toegestane_maximum_massa_voertuig',
        [
            0,
            3500,
            3501,
            7500,
            7501,
            99999,
        ],
    )
    @pytest.mark.parametrize('rijrichting_correct', [True, False])
    def test_aggregation(
        self,
        voertuig_soort,
        is_bedrijfsvoertuig,
        toegestane_maximum_massa_voertuig,
        rijrichting_correct,
    ):
        helper_table_row = Camera.objects.filter(
            rijrichting_correct=rijrichting_correct
        ).first()

        yesterday = timezone.now() - timedelta(days=1)

        # create ten passages for the correct day and hour
        PassageFactory.create_batch(
            size=10,
            passage_at=yesterday,
            camera_id=helper_table_row.id,
            camera_naam=helper_table_row.camera_naam,
            camera_kijkrichting=helper_table_row.camera_kijkrichting,
            camera_locatie=helper_table_row.location,
            rijrichting=helper_table_row.rijrichting,
            voertuig_soort=voertuig_soort,
            toegestane_maximum_massa_voertuig=toegestane_maximum_massa_voertuig,
            # set the following to static because we group by these values
            massa_ledig_voertuig=999,
            inrichting='bla',
            europese_voertuigcategorie='M1',
            europese_voertuigcategorie_toevoeging='A',
            brandstoffen={},
            lengte=999,
            straat='Weesperplein',
        )

        # create some more for different days
        other_days = [
            yesterday + timedelta(days=1),
            yesterday + timedelta(days=2),
            yesterday + timedelta(days=3),
        ]
        other_days = []
        for day in other_days:
            PassageFactory.create_batch(
                size=5,
                passage_at=day,
                camera_naam=helper_table_row.camera_naam,
                camera_kijkrichting=helper_table_row.camera_kijkrichting,
                rijrichting=helper_table_row.rijrichting,
            )

        assert HeavyTrafficHourAggregationV2.objects.count() == 0
        call_command(
            'passage_zwaar_verkeer_hour_aggregation_v2',
            from_date=yesterday.date(),
        )

        # check the most important (calculated) attribute: count (number of passages)
        # based on the 'data leveringsovereenkomst', the following rules apply
        # if this type should not be included, the aggregation should not exist
        should_be_included = rijrichting_correct and (
            (is_bedrijfsvoertuig and toegestane_maximum_massa_voertuig > 3500)
            or toegestane_maximum_massa_voertuig > 7500
        )
        if not should_be_included:
            assert HeavyTrafficHourAggregationV2.objects.count() == 0
        else:
            expected_date = yesterday.date()
            expected_year = yesterday.year
            expected_month = yesterday.month
            expected_day = yesterday.day
            expected_week = int(yesterday.strftime("%U"))
            expected_day_of_week = str(yesterday.isoweekday())
            expected_hour = yesterday.hour

            # (implicitly) assert there is one result for this hour by using get
            result = HeavyTrafficHourAggregationV2.objects.get(
                passage_at_date=expected_date, passage_at_hour=expected_hour
            )
            assert result.count == 10

            for day in other_days:
                assert HeavyTrafficHourAggregationV2.objects.filter(
                    passage_at_timestamp=day.replace(minute=0, second=0, microsecond=0)
                ).exists()

            # check extracted datetime info
            assert result.passage_at_date == expected_date
            assert result.passage_at_year == expected_year
            assert result.passage_at_month == expected_month
            assert result.passage_at_day == expected_day
            assert result.passage_at_week == expected_week
            assert result.passage_at_day_of_week == expected_day_of_week
            assert result.passage_at_hour == expected_hour

            # check helper table data
            helper_fields = [
                'cordon_order_kaart',
                'cordon_order_naam',
                'cordon',
                'rijrichting_correct',
            ]
            for attr in helper_fields:
                if attr == 'cordon_order_kaart':
                    helper_attr = 'order_kaart'
                elif attr == 'cordon_order_naam':
                    helper_attr = 'order_naam'
                else:
                    helper_attr = attr

                assert getattr(result, attr) == getattr(helper_table_row, helper_attr)

    def _get_expected_dow(self, timestamp):
        """
        Get the expected day of week
        """
        dow = timestamp.weekday()
        if dow == 0:
            return '1 maandag'
        elif dow == 1:
            return '2 dinsdag'
        elif dow == 2:
            return '3 woensdag'
        elif dow == 3:
            return '4 donderdag'
        elif dow == 4:
            return '5 vrijdag'
        elif dow == 5:
            return '6 zaterdag'
        elif dow == 6:
            return '7 zondag'
        return 'onbekend'
