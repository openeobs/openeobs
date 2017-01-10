# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import datetime

from openerp.tests.common import TransactionCase

from . import patient_refusal_event_fixtures


class TestGetRefusalEventsData(TransactionCase):

    datetime_format = '%d/%m/%Y %H:%M'

    def setUp(self):
        super(TestGetRefusalEventsData, self).setUp()
        self.report_model = self.env['report.nh.clinical.observation_report']

        self.mock_spell_activity_id = 1
        self.report_model.spell_activity_id = self.mock_spell_activity_id
        self.report_model._patch_method(
            'get_refusal_episodes',
            patient_refusal_event_fixtures.mock_get_refusal_episodes
        )

    def tearDown(self):
        self.report_model._revert_method('get_refusal_episodes')

    def call_test(self):
        self.refusal_events_data = self.report_model.get_refusal_events_data()

    def test_returns_list(self):
        self.call_test()
        self.assertTrue(isinstance(self.refusal_events_data, list))

    def test_number_of_report_entries(self):
        self.call_test()
        expected = \
            len(patient_refusal_event_fixtures.refusal_episodes)
        actual = len(self.refusal_events_data)
        self.assertEqual(expected, actual)

    def test_ordered_chronologically_descending(self):
        self.call_test()
        datetime_objects = \
            [datetime.strptime(episode['first_refusal'],
                               self.datetime_format)
             for episode in self.refusal_events_data]
        datetime_objects_sorted = deepcopy(datetime_objects)
        datetime_objects_sorted = sorted(datetime_objects_sorted, reverse=True)

        self.assertEqual(datetime_objects,
                         datetime_objects_sorted)
