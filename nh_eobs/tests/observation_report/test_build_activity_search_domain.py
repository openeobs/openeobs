# -*- coding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta
import logging

from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf

from openerp.addons.nh_eobs.report.helpers import build_activity_search_domain


_logger = logging.getLogger(__name__)


class TestObservationReport(TransactionCase):

    def setUp(self):
        super(TestObservationReport, self).setUp()
        self.spell_activity_id = 1
        self.normal_model = 'nh.test'
        self.exception_model = 'nh.clinical.patient.o2target'
        self.exception_model2 = 'nh.clinical.patient.move'
        self.start_date = datetime.now() + timedelta(days=5)
        self.end_date = datetime.now() + timedelta(days=5)

    def assert_domain(self, spell_activity_id, model, start_date, end_date, *args):
        test_domain = build_activity_search_domain(
            spell_activity_id, model, start_date, end_date
        )

        domain_parameters_total = 0

        if spell_activity_id:
            domain_parameters_total += 1
            expected_spell_domain = ('parent_id', '=', spell_activity_id)
            actual_spell_domain = test_domain[domain_parameters_total - 1]
            self.assertSequenceEqual(expected_spell_domain, actual_spell_domain,
            'Incorrect spell activity domain created.')

        if model:
            domain_parameters_total += 1
            expected_model_domain = ('data_model', '=', model)
            actual_model_domain = test_domain[domain_parameters_total - 1]
            self.assertSequenceEqual(expected_model_domain, actual_model_domain,
                                     'Incorrect model domain created.')

        domain_parameters_total += 1
        expected_state_domain = ('state', '=', 'completed')
        actual_state_domain = test_domain[domain_parameters_total - 1]
        self.assertSequenceEqual(expected_state_domain, actual_state_domain,
                                 'Incorrect state domain created.')

        if start_date:
            domain_parameters_total += 1
            expected_start_domain = ('date_terminated', '>=',
                                     datetime.strftime(start_date, dtf))
            actual_start_domain = test_domain[domain_parameters_total - 1]
            self.assertSequenceEqual(expected_start_domain, actual_start_domain,
                                     'Incorrect start domain created.')

        if end_date:
            domain_parameters_total += 1
            expected_end_domain = ('date_terminated', '<=',
                                   datetime.strftime(end_date, dtf))
            actual_end_domain = test_domain[domain_parameters_total - 1]
            self.assertSequenceEqual(expected_end_domain, actual_end_domain,
                                     'Incorrect end domain created.')

        self.assertEqual(len(test_domain), domain_parameters_total,
                         'Incorrect number of items in filter.')

    def test_01_with_normal_model(self):
        self.assert_domain(self.spell_activity_id, self.normal_model,
                           self.start_date, self.end_date)

    def test_02_with_exception_model(self):
        self.assert_domain(self.spell_activity_id, self.exception_model,
                           self.start_date, self.end_date)

    def test_03_without_model(self):
        with self.assertRaises(ValueError):
            build_activity_search_domain(None, self.normal_model,
                                         self.start_date, self.end_date)

    def test_04_without_end_date(self):
        self.assert_domain(self.spell_activity_id, self.normal_model,
                           self.start_date, None)

    def test_05_without_end_date_or_start_date(self):
        self.assert_domain(self.spell_activity_id, self.normal_model,
                           None, None)

    def test_06_without_start_date(self):
        self.assert_domain(self.spell_activity_id, self.normal_model,
                           None, self.end_date)

    def test_07_with_exception_model_and_without_start_date(self):
        self.assert_domain(self.spell_activity_id, self.exception_model,
                           None, self.end_date)

    def test_08_with_exception_model_and_without_end_date(self):
        self.assert_domain(self.spell_activity_id, self.exception_model,
                           self.start_date, None)

    def test_09_with_exception_model_and_without_start_date_or_end_date(self):
        self.assert_domain(self.spell_activity_id, self.normal_model,
                           self.start_date, None)

    def test_10_without_model_or_end_date(self):
        with self.assertRaises(ValueError):
            build_activity_search_domain(self.spell_activity_id, None, self.start_date, None)

    def test_11_without_model_or_end_date_or_start_date(self):
        with self.assertRaises(ValueError):
            build_activity_search_domain(self.spell_activity_id, None, None, None)

    def test_12_without_model_or_end_date_or_start_date(self):
        with self.assertRaises(ValueError):
            build_activity_search_domain(self.spell_activity_id, None, None, self.end_date)

    def test_13_without_model_or_end_date_or_start_date(self):
        with self.assertRaises(ValueError):
            build_activity_search_domain(self.spell_activity_id, None,
                                         self.start_date, self.end_date)

    def test_14_without_spell_activity_id(self):
        with self.assertRaises(ValueError):
            build_activity_search_domain(None, None, None, None)
