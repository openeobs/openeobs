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
        self.spell_id = 1
        self.normal_model = 'nh.test'
        self.exception_model = 'nh.clinical.patient.o2target'
        self.exception_model2 = 'nh.clinical.patient.move'
        self.start_date = datetime.now() + timedelta(days=5)
        self.end_date = datetime.now() + timedelta(days=5)

    def test_01_filter_with_normal_model_with_end_date_with_start_date(self):
        test_filter = build_activity_search_domain(
            self.spell_id, self.normal_model,
            self.start_date, self.end_date
        )
        self.assertEqual(len(test_filter), 5,
                         'Incorrect number of items in filter')
        spell_filter = test_filter[0]
        model_filter = test_filter[1]
        complete_filter = test_filter[2]
        start_filter = test_filter[3]
        end_filter = test_filter[4]
        self.assertEqual(
            str(spell_filter),
            "['parent_id', '=', 1]",
            'Incorrect spell activity filter created'
        )
        self.assertEqual(
            str(model_filter),
            "['data_model', '=', 'nh.test']",
            'Incorrect model filter created'
        )
        self.assertEqual(
            str(complete_filter),
            "['state', '=', 'completed']",
            'Incorrect complete filter created'
        )
        self.assertEqual(
            str(start_filter),
            "['date_terminated', '>=', '{0}']".format(
                datetime.strftime(self.start_date, dtf)
            ),
            'Incorrect date start filter created'
        )
        self.assertEqual(
            str(end_filter),
            "['date_terminated', '<=', '{0}']".format(
                datetime.strftime(self.end_date, dtf)
            ),
            'Incorrect date end filter created'
        )

    def test_02_filter_with_exception_model_w_end_date_w_start_date(self):
        test_filter = build_activity_search_domain(
            self.spell_id, self.exception_model,
            self.start_date, self.end_date
        )
        self.assertEqual(len(test_filter), 4,
                         'Incorrect number of items in filter')
        spell_filter = test_filter[0]
        model_filter = test_filter[1]
        start_filter = test_filter[2]
        end_filter = test_filter[3]
        self.assertEqual(
            str(spell_filter),
            "['parent_id', '=', 1]",
            'Incorrect spell activity filter created'
        )
        self.assertEqual(
            str(model_filter),
            "['data_model', '=', '{0}']".format(
                self.exception_model
            ),
            'Incorrect model filter created'
        )
        self.assertEqual(
            str(start_filter),
            "['date_terminated', '>=', '{0}']".format(
                datetime.strftime(self.start_date, dtf)
            ),
            'Incorrect date start filter created'
        )
        self.assertEqual(
            str(end_filter),
            "['date_terminated', '<=', '{0}']".format(
                datetime.strftime(self.end_date, dtf)
            ),
            'Incorrect date end filter created'
        )

    def test_03_filter_without_model_with_end_date_with_start_date(self):
        with self.assertRaises(ValueError):
            build_activity_search_domain(None, self.normal_model,
                                 self.start_date, self.end_date)

    def test_04_filter_with_normal_model_wout_end_date_with_start_date(self):
        test_filter = build_activity_search_domain(
            self.spell_id, self.normal_model,
            self.start_date, None
        )
        self.assertEqual(len(test_filter), 4,
                         'Incorrect number of items in filter')
        spell_filter = test_filter[0]
        model_filter = test_filter[1]
        complete_filter = test_filter[2]
        start_filter = test_filter[3]
        self.assertEqual(
            str(spell_filter),
            "['parent_id', '=', 1]",
            'Incorrect spell activity filter created'
        )
        self.assertEqual(
            str(model_filter),
            "['data_model', '=', 'nh.test']",
            'Incorrect model filter created'
        )
        self.assertEqual(
            str(complete_filter),
            "['state', '=', 'completed']",
            'Incorrect complete filter created'
        )
        self.assertEqual(
            str(start_filter),
            "['date_terminated', '>=', '{0}']".format(
                datetime.strftime(self.start_date, dtf)
            ),
            'Incorrect date start filter created'
        )

    def test_05_filter_with_normal_model_wout_end_date_wout_start_date(self):
        test_filter = build_activity_search_domain(
            self.spell_id,
            self.normal_model,
            None,
            None
        )
        self.assertEqual(
            len(test_filter),
            3,
            'Incorrect number of items in filter'
        )
        spell_filter = test_filter[0]
        model_filter = test_filter[1]
        complete_filter = test_filter[2]
        self.assertEqual(
            str(spell_filter),
            "['parent_id', '=', 1]",
            'Incorrect spell activity filter created'
        )
        self.assertEqual(
            str(model_filter),
            "['data_model', '=', 'nh.test']",
            'Incorrect model filter created'
        )
        self.assertEqual(
            str(complete_filter),
            "['state', '=', 'completed']",
            'Incorrect complete filter created'
        )

    def test_06_filter_with_normal_model_with_end_date_wout_start_date(self):
        test_filter = build_activity_search_domain(
            self.spell_id, self.normal_model, None, self.end_date)
        self.assertEqual(
            len(test_filter),
            4,
            'Incorrect number of items in filter'
        )
        spell_filter = test_filter[0]
        model_filter = test_filter[1]
        complete_filter = test_filter[2]
        end_filter = test_filter[3]
        self.assertEqual(
            str(spell_filter),
            "['parent_id', '=', 1]",
            'Incorrect spell activity filter created'
        )
        self.assertEqual(
            str(model_filter),
            "['data_model', '=', 'nh.test']",
            'Incorrect model filter created'
        )
        self.assertEqual(
            str(complete_filter),
            "['state', '=', 'completed']",
            'Incorrect complete filter created'
        )
        self.assertEqual(
            str(end_filter),
            "['date_terminated', '<=', '{0}']".format(
                datetime.strftime(self.end_date, dtf)
            ),
            'Incorrect date start filter created'
        )

    def test_07_filter_with_exception_model_w_end_date_wout_start_date(self):
        test_filter = build_activity_search_domain(
            self.spell_id, self.exception_model, None, self.end_date)
        self.assertEqual(
            len(test_filter),
            3,
            'Incorrect number of items in filter'
        )
        spell_filter = test_filter[0]
        model_filter = test_filter[1]
        end_filter = test_filter[2]
        self.assertEqual(
            str(spell_filter),
            "['parent_id', '=', 1]",
            'Incorrect spell activity filter created'
        )
        self.assertEqual(
            str(model_filter),
            "['data_model', '=', '{0}']".format(
                self.exception_model
            ),
            'Incorrect model filter created'
        )
        self.assertEqual(
            str(end_filter),
            "['date_terminated', '<=', '{0}']".format(
                datetime.strftime(self.end_date, dtf)
            ),
            'Incorrect date start filter created'
        )

    def test_08_filter_with_exception_model_wout_end_date_w_start_date(self):
        test_filter = build_activity_search_domain(
            self.spell_id, self.exception_model2, self.start_date, None)
        self.assertEqual(
            len(test_filter),
            3,
            'Incorrect number of items in filter'
        )
        spell_filter = test_filter[0]
        model_filter = test_filter[1]
        start_filter = test_filter[2]
        self.assertEqual(
            str(spell_filter),
            "['parent_id', '=', 1]",
            'Incorrect spell activity filter created'
        )
        self.assertEqual(
            str(model_filter),
            "['data_model', '=', '{0}']".format(
                self.exception_model2
            ),
            'Incorrect model filter created'
        )
        self.assertEqual(
            str(start_filter),
            "['date_terminated', '>=', '{0}']".format(
                datetime.strftime(self.start_date, dtf)
            ),
            'Incorrect date start filter created'
        )

    def test_09_filter_with_exception_model_out_end_date_wout_start_date(self):
        test_filter = build_activity_search_domain(
            self.spell_id, self.exception_model, None, None)
        self.assertEqual(
            len(test_filter),
            2,
            'Incorrect number of items in filter'
        )
        spell_filter = test_filter[0]
        model_filter = test_filter[1]
        self.assertEqual(
            str(spell_filter),
            "['parent_id', '=', 1]",
            'Incorrect spell activity filter created'
        )
        self.assertEqual(
            str(model_filter),
            "['data_model', '=', '{0}']".format(
                self.exception_model
            ),
            'Incorrect model filter created'
        )

    def test_10_filter_without_model_without_end_date_with_start_date(self):
        with self.assertRaises(ValueError):
            build_activity_search_domain(self.spell_id, None, self.start_date, None)

    def test_11_filter_without_model_without_end_date_without_start_date(self):
        with self.assertRaises(ValueError):
            build_activity_search_domain(self.spell_id, None, None, None)

    def test_12_filter_without_model_with_end_date_without_start_date(self):
        with self.assertRaises(ValueError):
            build_activity_search_domain(self.spell_id, None, None, self.end_date)

    def test_13_filter_without_model_with_end_date_with_start_date(self):
        with self.assertRaises(ValueError):
            build_activity_search_domain(self.spell_id, None,
                                 self.start_date, self.end_date)

    def test_14_filter_without_spell_activity_id(self):
        with self.assertRaises(ValueError):
            build_activity_search_domain(None, None, None, None)
