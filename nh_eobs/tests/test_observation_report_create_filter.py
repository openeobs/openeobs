__author__ = 'colinwren'
from openerp.tests.common import TransactionCase
from datetime import datetime, timedelta
import logging
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from openerp.addons.nh_eobs.report.print_observation_report import ObservationReport as obs_report

_logger = logging.getLogger(__name__)

class TestObservationReport(TransactionCase):

    def setUp(self):
        super(TestObservationReport, self).setUp()
        self.spell_id = 1
        self.normal_model = 'nh.test'
        self.exception_model = 'nh.clinical.patient.o2target'
        self.exception_model2 = 'nh.clinical.patient.move'
        self.start_date = datetime.now() + timedelta(days=5)
        self.end_date = datetime.now() + timedelta(days=5)

    def test_1_create_search_filter_with_normal_model_with_end_date_with_start_date(self):
        test_filter = obs_report.create_search_filter(self.spell_id, self.normal_model, self.start_date, self.end_date)
        self.assertEqual(len(test_filter), 5, 'Incorrect number of items in filter')
        spell_filter = test_filter[0]
        model_filter = test_filter[1]
        complete_filter = test_filter[2]
        start_filter = test_filter[3]
        end_filter = test_filter[4]
        self.assertEqual(str(spell_filter), "['parent_id', '=', 1]", 'Incorrect spell activity filter created')
        self.assertEqual(str(model_filter), "['data_model', '=', 'nh.test']", 'Incorrect model filter created')
        self.assertEqual(str(complete_filter), "['state', '=', 'completed']", 'Incorrect complete filter created')
        self.assertEqual(str(start_filter), "['date_started', '>=', '{0}']".format(datetime.strftime(self.start_date, dtf)), 'Incorrect date start filter created')
        self.assertEqual(str(end_filter), "['date_terminated', '<=', '{0}']".format(datetime.strftime(self.end_date, dtf)), 'Incorrect date end filter created')

    def test_2_create_search_filter_with_exception_model_with_end_date_with_start_date(self):
        test_filter = obs_report.create_search_filter(self.spell_id, self.exception_model, self.start_date, self.end_date)
        self.assertEqual(len(test_filter), 4, 'Incorrect number of items in filter')
        spell_filter = test_filter[0]
        model_filter = test_filter[1]
        start_filter = test_filter[2]
        end_filter = test_filter[3]
        self.assertEqual(str(spell_filter), "['parent_id', '=', 1]", 'Incorrect spell activity filter created')
        self.assertEqual(str(model_filter), "['data_model', '=', '{0}']".format(self.exception_model), 'Incorrect model filter created')
        self.assertEqual(str(start_filter), "['date_started', '>=', '{0}']".format(datetime.strftime(self.start_date, dtf)), 'Incorrect date start filter created')
        self.assertEqual(str(end_filter), "['date_terminated', '<=', '{0}']".format(datetime.strftime(self.end_date, dtf)), 'Incorrect date end filter created')

    def test_3_create_search_filter_without_model_with_end_date_with_start_date(self):
        with self.assertRaises(ValueError):
            test_filter = obs_report.create_search_filter(None, self.normal_model, self.start_date, self.end_date)

    def test_4_create_search_filter_with_normal_model_without_end_date_with_start_date(self):
        test_filter = obs_report.create_search_filter(self.spell_id, self.normal_model, self.start_date, None)
        self.assertEqual(len(test_filter), 4, 'Incorrect number of items in filter')
        spell_filter = test_filter[0]
        model_filter = test_filter[1]
        complete_filter = test_filter[2]
        start_filter = test_filter[3]
        self.assertEqual(str(spell_filter), "['parent_id', '=', 1]", 'Incorrect spell activity filter created')
        self.assertEqual(str(model_filter), "['data_model', '=', 'nh.test']", 'Incorrect model filter created')
        self.assertEqual(str(complete_filter), "['state', '=', 'completed']", 'Incorrect complete filter created')
        self.assertEqual(str(start_filter), "['date_started', '>=', '{0}']".format(datetime.strftime(self.start_date, dtf)), 'Incorrect date start filter created')

    def test_5_create_search_filter_with_normal_model_without_end_date_without_start_date(self):
        test_filter = obs_report.create_search_filter(self.spell_id, self.normal_model, None, None)
        self.assertEqual(len(test_filter), 3, 'Incorrect number of items in filter')
        spell_filter = test_filter[0]
        model_filter = test_filter[1]
        complete_filter = test_filter[2]
        self.assertEqual(str(spell_filter), "['parent_id', '=', 1]", 'Incorrect spell activity filter created')
        self.assertEqual(str(model_filter), "['data_model', '=', 'nh.test']", 'Incorrect model filter created')
        self.assertEqual(str(complete_filter), "['state', '=', 'completed']", 'Incorrect complete filter created')

    def test_6_create_search_filter_with_exception_model_without_end_date_with_start_date(self):
        test_filter = obs_report.create_search_filter(self.spell_id, self.exception_model2, self.start_date, None)
        self.assertEqual(len(test_filter), 3, 'Incorrect number of items in filter')
        spell_filter = test_filter[0]
        model_filter = test_filter[1]
        start_filter = test_filter[2]
        self.assertEqual(str(spell_filter), "['parent_id', '=', 1]", 'Incorrect spell activity filter created')
        self.assertEqual(str(model_filter), "['data_model', '=', '{0}']".format(self.exception_model2), 'Incorrect model filter created')
        self.assertEqual(str(start_filter), "['date_started', '>=', '{0}']".format(datetime.strftime(self.start_date, dtf)), 'Incorrect date start filter created')

    def test_7_create_search_filter_with_exception_model_without_end_date_without_start_date(self):
        test_filter = obs_report.create_search_filter(self.spell_id, self.exception_model, None, None)
        self.assertEqual(len(test_filter), 2, 'Incorrect number of items in filter')
        spell_filter = test_filter[0]
        model_filter = test_filter[1]
        self.assertEqual(str(spell_filter), "['parent_id', '=', 1]", 'Incorrect spell activity filter created')
        self.assertEqual(str(model_filter), "['data_model', '=', '{0}']".format(self.exception_model), 'Incorrect model filter created')

    def test_8_create_search_filter_without_model_without_end_date_with_start_date(self):
        with self.assertRaises(ValueError):
            test_filter = obs_report.create_search_filter(self.spell_id, None, self.start_date, None)

    def test_9_create_search_filter_without_model_without_end_date_without_start_date(self):
        with self.assertRaises(ValueError):
            test_filter = obs_report.create_search_filter(self.spell_id, None, None, None)

    def test_10_create_search_filter_without_spell_activity_id(self):
        with self.assertRaises(ValueError):
            test_filter = obs_report.create_search_filter(None, None, None, None)