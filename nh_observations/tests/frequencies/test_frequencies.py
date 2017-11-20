# -*- coding: utf-8 -*-
from openerp.addons.nh_observations import frequencies
from openerp.tests.common import SingleTransactionCase


class TestFrequencies(SingleTransactionCase):

    def test_as_list(self):
        expected = [
            frequencies.EVERY_15_MINUTES,
            frequencies.EVERY_30_MINUTES,
            frequencies.EVERY_HOUR,
            frequencies.EVERY_2_HOURS,
            frequencies.EVERY_4_HOURS,
            frequencies.EVERY_6_HOURS,
            frequencies.EVERY_8_HOURS,
            frequencies.EVERY_10_HOURS,
            frequencies.EVERY_12_HOURS,
            frequencies.EVERY_DAY,
            frequencies.EVERY_3_DAYS,
            frequencies.EVERY_WEEK
        ]
        actual = frequencies.as_list()
        self.assertEqual(expected, actual)

    def test_as_list_max(self):
        expected = [
            frequencies.EVERY_15_MINUTES,
            frequencies.EVERY_30_MINUTES,
            frequencies.EVERY_HOUR,
            frequencies.EVERY_2_HOURS,
            frequencies.EVERY_4_HOURS,
            frequencies.EVERY_6_HOURS,
            frequencies.EVERY_8_HOURS,
            frequencies.EVERY_10_HOURS,
            frequencies.EVERY_12_HOURS,
            frequencies.EVERY_DAY,
        ]
        actual = frequencies.as_list(max=1440)
        self.assertEqual(expected, actual)

    def test_minutes_only(self):
        expected = [
            frequencies.FIFTEEN_MINUTES,
            frequencies.THIRTY_MINUTES,
            frequencies.ONE_HOUR,
            frequencies.TWO_HOURS,
            frequencies.FOUR_HOURS,
            frequencies.SIX_HOURS,
            frequencies.EIGHT_HOURS,
            frequencies.TEN_HOURS,
            frequencies.TWELVE_HOURS,
            frequencies.ONE_DAY,
            frequencies.THREE_DAYS,
            frequencies.ONE_WEEK
        ]
        actual = frequencies.minutes_only()
        self.assertEqual(expected, actual)
