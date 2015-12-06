# Part of Open eObs. See LICENSE file for full copyright and licensing details.
__author__ = 'colinwren'
__author__ = 'colinwren'
from openerp.tests.common import TransactionCase
from datetime import datetime, timedelta
import logging
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from openerp.addons.nh_eobs.report.helpers import data_dict_to_obj

_logger = logging.getLogger(__name__)

class TestObservationReport(TransactionCase):

    def setUp(self):
        super(TestObservationReport, self).setUp()
        self.spell_id = 1
        self.start_time = datetime.strftime(datetime.now() + timedelta(days=5), dtf)
        self.end_time = datetime.strftime(datetime.now() + timedelta(days=5), dtf)

    def test_01_data_obj_with_spell_with_start_time_with_end_time_with_ews_only(self):
        test_dict = {
            'spell_id': self.spell_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'ews_only': True
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(test_data_obj.spell_id, self.spell_id, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, self.start_time, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, self.end_time, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, True, 'Created data obj ews_only does not match')

    def test_02_data_obj_with_spell_with_start_time_with_end_time_without_ews_only(self):
        test_dict = {
            'spell_id': self.spell_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'ews_only': False
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(test_data_obj.spell_id, self.spell_id, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, self.start_time, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, self.end_time, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, None, 'Created data obj ews_only does not match')

    def test_03_data_obj_with_spell_with_start_time_without_end_time_with_ews_only(self):
        test_dict = {
            'spell_id': self.spell_id,
            'start_time': self.start_time,
            'end_time': None,
            'ews_only': True
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(test_data_obj.spell_id, self.spell_id, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, self.start_time, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, None, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, True, 'Created data obj ews_only does not match')

    def test_04_data_obj_with_spell_with_start_time_without_end_time_without_ews_only(self):
        test_dict = {
            'spell_id': self.spell_id,
            'start_time': self.start_time,
            'end_time': None,
            'ews_only': False
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(test_data_obj.spell_id, self.spell_id, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, self.start_time, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, None, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, None, 'Created data obj ews_only does not match')

    def test_05_data_obj_with_spell_without_start_time_with_end_time_with_ews_only(self):
        test_dict = {
            'spell_id': self.spell_id,
            'start_time': None,
            'end_time': self.end_time,
            'ews_only': True
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(test_data_obj.spell_id, self.spell_id, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, None, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, self.end_time, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, True, 'Created data obj ews_only does not match')

    def test_06_data_obj_with_spell_without_start_time_with_end_time_without_ews_only(self):
        test_dict = {
            'spell_id': self.spell_id,
            'start_time': None,
            'end_time': self.end_time,
            'ews_only': False
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(test_data_obj.spell_id, self.spell_id, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, None, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, self.end_time, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, None, 'Created data obj ews_only does not match')

    def test_07_data_obj_with_spell_without_start_time_without_end_time_with_ews_only(self):
        test_dict = {
            'spell_id': self.spell_id,
            'start_time': None,
            'end_time': None,
            'ews_only': True
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(test_data_obj.spell_id, self.spell_id, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, None, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, None, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, True, 'Created data obj ews_only does not match')

    def test_08_data_obj_with_spell_without_start_time_without_end_time_without_ews_only(self):
        test_dict = {
            'spell_id': self.spell_id,
            'start_time': None,
            'end_time': None,
            'ews_only': False
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(test_data_obj.spell_id, self.spell_id, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, None, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, None, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, None, 'Created data obj ews_only does not match')

    def test_09_data_obj_without_spell_without_start_time_without_end_time_with_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': None,
            'end_time': None,
            'ews_only': True
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(test_data_obj.spell_id, None, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, None, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, None, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, True, 'Created data obj ews_only does not match')

    def test_10_data_obj_without_spell_without_start_time_without_end_time_without_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': None,
            'end_time': None,
            'ews_only': False
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(test_data_obj.spell_id, None, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, None, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, None, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, None, 'Created data obj ews_only does not match')

    def test_11_data_obj_without_spell_without_start_time_without_end_time_without_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': None,
            'end_time': None,
            'ews_only': None
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(test_data_obj.spell_id, None, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, None, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, None, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, None, 'Created data obj ews_only does not match')

    def test_12_data_obj_with_empty_dictionary(self):
        test_data_obj = data_dict_to_obj({})
        self.assertEqual(test_data_obj.spell_id, None, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, None, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, None, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, None, 'Created data obj ews_only does not match')

    def test_13_data_obj_without_spell_with_start_time_with_end_time_with_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'ews_only': True
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(test_data_obj.spell_id, None, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, self.start_time, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, self.end_time, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, True, 'Created data obj ews_only does not match')

    def test_14_data_obj_without_spell_with_start_time_with_end_time_without_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'ews_only': None
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(test_data_obj.spell_id, None, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, self.start_time, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, self.end_time, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, None, 'Created data obj ews_only does not match')

    def test_15_data_obj_without_spell_with_start_time_without_end_time_without_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': self.start_time,
            'end_time': None,
            'ews_only': None
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(test_data_obj.spell_id, None, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, self.start_time, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, None, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, None, 'Created data obj ews_only does not match')

    def test_16_data_obj_without_spell_without_start_time_with_end_time_with_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': None,
            'end_time': self.end_time,
            'ews_only': True
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(test_data_obj.spell_id, None, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, None, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, self.end_time, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, True, 'Created data obj ews_only does not match')

    def test_17_data_obj_without_spell_without_start_time_with_end_time_without_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': None,
            'end_time': self.end_time,
            'ews_only': None
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(test_data_obj.spell_id, None, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, None, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, self.end_time, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, None, 'Created data obj ews_only does not match')

    def test_18_data_obj_without_spell_without_start_time_without_end_time_with_ews_only(self):
        test_dict = {
            'spell_id': None,
            'start_time': None,
            'end_time': None,
            'ews_only': True
        }
        test_data_obj = data_dict_to_obj(test_dict)
        self.assertEqual(test_data_obj.spell_id, None, 'Created Data Obj spell_id attribute does not match')
        self.assertEqual(test_data_obj.start_time, None, 'Created Data Obj start_time attr does not match')
        self.assertEqual(test_data_obj.end_time, None, 'Created data obj end_time attr does not match')
        self.assertEqual(test_data_obj.ews_only, True, 'Created data obj ews_only does not match')