# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from openerp.osv import osv
from openerp.tests.common import TransactionCase
from datetime import datetime as dt
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
import base64
import os.path


mocked_print_called = 0


class SettingsPoolMockBrowse(object):

    def __init__(self):
        self.locations_to_print = []


class TestNHClinicalBackupProcedure(TransactionCase):

    def setUp(self):
        super(TestNHClinicalBackupProcedure, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.spell_model = self.env['nh.clinical.spell']
        self.test_utils.admit_and_place_patient()

        self.location_pool.write(
            cr, uid, self.wu_id, {'backup_observations': True})

        self.ews_data = {
            'respiration_rate': 40,
            'indirect_oxymetry_spo2': 99,
            'oxygen_administration_flag': False,
            'body_temperature': 37.0,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 55
        }
        self.ews_data2 = {
            'respiration_rate': 59,
            'indirect_oxymetry_spo2': 100,
            'oxygen_administration_flag': False,
            'body_temperature': 44.9,
            'blood_pressure_systolic': 300,
            'blood_pressure_diastolic': 280,
            'pulse_rate': 250,
            'avpu_text': 'U'
        }


    #
    # def test_07_test_no_spell_domain_is_empty_when_no_non_printed_spells(self):
    #     cr, uid = self.cr, self.uid
    #     loc_ids = self.location_pool.search(
    #         cr, uid, [
    #             ['usage', '=', 'ward'],
    #             ['backup_observations', '=', True]
    #         ]
    #     )
    #     dirty_spell_ids = self.spell_pool.search(
    #         cr, uid, [
    #             ['report_printed', '=', False],
    #             ['state', 'not in', ['completed', 'cancelled']],
    #             ['location_id', 'child_of', loc_ids]
    #         ]
    #     )
    #     self.spell_pool.write(
    #         cr, uid, dirty_spell_ids, {'report_printed': True})
    #
    #     test_empty = self.spell_pool.search(
    #         cr, uid, [
    #             ['report_printed', '=', False],
    #             ['state', 'not in', ['completed', 'cancelled']],
    #             ['location_id', 'child_of', loc_ids]
    #         ]
    #     )
    #     self.assertEqual(
    #         test_empty, [],
    #         'No Spell Domain returned spells when should be empty')
    #
    # def test_08_test_no_spell_domain_is_empty_when_no_non_printed_spells(self):
    #     cr, uid = self.cr, self.uid
    #     loc_ids = self.location_pool.search(
    #         cr, uid, [
    #             ['usage', '=', 'ward'],
    #             ['backup_observations', '=', True]
    #         ]
    #     )
    #     dirty_spell_ids = self.spell_pool.search(
    #         cr, uid, [
    #             ['report_printed', '=', False],
    #             ['state', 'not in', ['completed', 'cancelled']],
    #             ['location_id', 'child_of', loc_ids]
    #         ]
    #     )
    #     test_spell = dirty_spell_ids[0]
    #     self.spell_pool.write(
    #         cr, uid, dirty_spell_ids[1:], {'report_printed': True})
    #
    #     test_empty = self.spell_pool.search(
    #         cr, uid, [
    #             ['report_printed', '=', False],
    #             ['state', 'not in', ['completed', 'cancelled']],
    #             ['location_id', 'child_of', loc_ids]
    #         ]
    #     )
    #     self.assertEqual(
    #         test_empty, [test_spell],
    #         'No Spell Domain returned more than one spell')
    #
    # def test_09_test_report_added_to_database(self):
    #     # run the report printing method in api and check that report
    #     #  added to DB
    #     cr, uid = self.cr, self.uid
    #     attachment_id = self.api_pool.add_report_to_database(
    #         cr, uid,
    #         'nh.clinical.observation_report',
    #         'test_data',
    #         'test_report.pdf',
    #         'nh.clinical.observation_report_wizard',
    #         1
    #     )
    #
    #     attachment_data = self.ir_pool.read(
    #         cr, uid, attachment_id, ['datas'])[0]['datas']
    #     report_str = base64.decodestring(attachment_data)
    #
    #     self.assertEqual(
    #         report_str, 'test_data', 'Report not added to database properly')
    #
    # def test_10_test_report_added_to_file_system(self):
    #     # run the report printing method in api and check that file
    #     # was created on FS
    #     # /bcp/out
    #     self.api_pool.add_report_to_backup_location('/bcp/out',
    #                                                 'test_data',
    #                                                 'test_report')
    #     with open('/bcp/out/test_report.pdf', 'r') as report_file:
    #         file_content = report_file.read()
    #     self.assertEqual(
    #         file_content,
    #         'test_data',
    #         'Report not added to filesystem properly'
    #     )
    #
    # def test_11_test_report_filename_is_correct(self):
    #     # run the report pringing method in teh api and
    #     # check that the file is correctly named
    #     # ward_surname_nhs_number
    #     cr, uid = self.cr, self.uid
    #     spell_id = self.spell_pool.get_by_patient_id(cr, uid, self.patient_id)
    #     nhs_number = '1231231231'
    #     ward = None
    #     surname = 'Wren'
    #     file_name = '{w}_{s}_{n}'.format(w=ward, s=surname, n=nhs_number)
    #
    #     # do print_report
    #     self.api_pool.print_report(cr, uid, spell_id)
    #     # check backup file name
    #     backup_exists = os.path.isfile('/bcp/out/{0}.pdf'.format(file_name))
    #     self.assertEqual(
    #         backup_exists, True, 'Report incorrectly named on file system')
    #
    #
    #