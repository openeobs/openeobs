# Part of Open eObs. See LICENSE file for full copyright and licensing details.
import logging
from datetime import datetime, timedelta

from openerp.addons.nh_eobs.report.helpers import data_dict_to_obj
from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf

_logger = logging.getLogger(__name__)


class TestObservationReport(TransactionCase):

    def setUp(self):
        super(TestObservationReport, self).setUp()
        self.spell_id = 1
        self.start_time = datetime.strftime(
            datetime.now() + timedelta(days=5), dtf)
        self.end_time = datetime.strftime(
            datetime.now() + timedelta(days=5), dtf)

    def test_01_data_obj_w_spell_w_start_time_w_end_time_w_ews_only(self):
        test_dict = {
            'spell_id': self.spell_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'ews_only': True
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(
            test_data_obj.spell_id,
            self.spell_id,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            self.start_time,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            self.end_time,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            True,
            'Created data obj ews_only does not match'
        )

    def test_02_data_obj_w_spell_w_start_time_w_end_time_wout_ews_only(self):
        test_dict = {
            'spell_id': self.spell_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'ews_only': False
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(
            test_data_obj.spell_id,
            self.spell_id,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            self.start_time,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            self.end_time,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            None,
            'Created data obj ews_only does not match'
        )

    def test_03_data_obj_w_spell_w_start_time_wout_end_time_w_ews_only(self):
        test_dict = {
            'spell_id': self.spell_id,
            'start_time': self.start_time,
            'end_time': None,
            'ews_only': True
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(
            test_data_obj.spell_id,
            self.spell_id,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            self.start_time,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            None,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            True,
            'Created data obj ews_only does not match'
        )

    def test_04_obj_w_spell_w_start_time_wout_end_time_wout_ews_only(self):
        test_dict = {
            'spell_id': self.spell_id,
            'start_time': self.start_time,
            'end_time': None,
            'ews_only': False
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(
            test_data_obj.spell_id,
            self.spell_id,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            self.start_time,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            None,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            None,
            'Created data obj ews_only does not match'
        )

    def test_05_data_obj_w_spell_wout_start_time_w_end_time_w_ews_only(self):
        test_dict = {
            'spell_id': self.spell_id,
            'start_time': None,
            'end_time': self.end_time,
            'ews_only': True
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(
            test_data_obj.spell_id,
            self.spell_id,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            None,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            self.end_time,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            True,
            'Created data obj ews_only does not match'
        )

    def test_06_obj_w_spell_wout_start_time_w_end_time_wout_ews_only(self):
        test_dict = {
            'spell_id': self.spell_id,
            'start_time': None,
            'end_time': self.end_time,
            'ews_only': False
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(
            test_data_obj.spell_id,
            self.spell_id,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            None,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            self.end_time,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            None,
            'Created data obj ews_only does not match'
        )

    def test_07_obj_w_spell_wout_start_time_wout_end_time_w_ews_only(self):
        test_dict = {
            'spell_id': self.spell_id,
            'start_time': None,
            'end_time': None,
            'ews_only': True
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(
            test_data_obj.spell_id,
            self.spell_id,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            None,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            None,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            True,
            'Created data obj ews_only does not match'
        )

    def test_08_obj_w_spell_wout_start_time_wout_end_time_wout_ews_only(self):
        test_dict = {
            'spell_id': self.spell_id,
            'start_time': None,
            'end_time': None,
            'ews_only': False
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(
            test_data_obj.spell_id,
            self.spell_id,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            None,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            None,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            None,
            'Created data obj ews_only does not match'
        )

    def test_09_obj_wut_spell_wout_start_time_wout_end_time_w_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': None,
            'end_time': None,
            'ews_only': True
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(
            test_data_obj.spell_id,
            None,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            None,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            None,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            True,
            'Created data obj ews_only does not match'
        )

    def test_10_obj_wt_spell_wt_start_time_wt_end_time_wout_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': None,
            'end_time': None,
            'ews_only': False
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(
            test_data_obj.spell_id,
            None,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            None,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            None,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            None,
            'Created data obj ews_only does not match'
        )

    def test_11_obj_wt_spell_wout_start_time_wout_end_time_wout_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': None,
            'end_time': None,
            'ews_only': None
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(
            test_data_obj.spell_id,
            None,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            None,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            None,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            None,
            'Created data obj ews_only does not match'
        )

    def test_12_data_obj_with_empty_dictionary(self):
        test_data_obj = data_dict_to_obj({})
        self.assertEqual(
            test_data_obj.spell_id,
            None,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            None,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            None,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            None,
            'Created data obj ews_only does not match'
        )

    def test_13_data_obj_wout_spell_w_start_time_w_end_time_w_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'ews_only': True
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(
            test_data_obj.spell_id,
            None,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            self.start_time,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            self.end_time,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            True,
            'Created data obj ews_only does not match'
        )

    def test_14_data_obj_wout_spell_w_start_time_w_end_time_out_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'ews_only': None
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(
            test_data_obj.spell_id,
            None,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            self.start_time,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            self.end_time,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            None,
            'Created data obj ews_only does not match'
        )

    def test_15_obj_wout_spell_w_start_time_wout_end_time_wout_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': self.start_time,
            'end_time': None,
            'ews_only': None
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(
            test_data_obj.spell_id,
            None,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            self.start_time,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            None,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            None,
            'Created data obj ews_only does not match'
        )

    def test_16_obj_wout_spell_wout_start_time_w_end_time_w_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': None,
            'end_time': self.end_time,
            'ews_only': True
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(
            test_data_obj.spell_id,
            None,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            None,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            self.end_time,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            True,
            'Created data obj ews_only does not match'
        )

    def test_17_obj_wout_spell_wout_start_time_w_end_time_wout_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': None,
            'end_time': self.end_time,
            'ews_only': None
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(
            test_data_obj.spell_id,
            None,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            None,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            self.end_time,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            None,
            'Created data obj ews_only does not match'
        )

    def test_18_obj_wout_spell_wout_start_time_wout_end_time_w_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': None,
            'end_time': None,
            'ews_only': True
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(
            test_data_obj.spell_id,
            None,
            'Created Data Obj spell_id attribute does not match'
        )
        self.assertEqual(
            test_data_obj.start_time,
            None,
            'Created Data Obj start_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.end_time,
            None,
            'Created data obj end_time attr does not match'
        )
        self.assertEqual(
            test_data_obj.ews_only,
            True,
            'Created data obj ews_only does not match'
        )
