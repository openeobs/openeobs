from openerp.tests.common import TransactionCase


mocked_print_called = 0


class SettingsPoolMockBrowse(object):

    def __init__(self):
        self.locations_to_print = []


class TestUpdateFlags(TransactionCase):
    """
    Test that the report_printed flag is updated by observations being
    taken and reports being printed
    """

    def setUp(self):
        super(TestUpdateFlags, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.spell_model = self.env['nh.clinical.spell']
        self.location_model = self.env['nh.clinical.location']
        self.ews_model = self.env['nh.clinical.patient.observation.ews']
        self.test_utils.admit_and_place_patient()
        self.patient_id = self.test_utils.patient.id

    def test_flag_changed_by_observation_complete(self):
        """
        Test that the report_printed flag is set to False on completing
        an EWS observation
        """
        spell = self.spell_model.browse(
            self.spell_model.get_by_patient_id(
                self.patient_id
            )
        )
        spell.write({'report_printed': True})
        self.assertEqual(spell.report_printed, True,
                         'Flag not set correctly by write method')
        self.test_utils.create_and_complete_ews_obs_activity(
            self.patient_id, spell.id)
        self.assertEqual(spell.report_printed, False,
                         'Flag not updated by complete method properly')

    # def test_04_test_flag_changed_by_report_printing_method(self):
    #     # complete an observation and check flag is now False
    #     cr, uid = self.cr, self.uid
    #     spell_id = self.spell_pool.get_by_patient_id(
    # cr, uid, self.patient_id)
    #     ews_activity_id = self.ews_pool.create_activity(
    #         cr, uid,
    #         {'parent_id': self.spell_id},
    #         {'patient_id': self.patient_id})
    #     self.ews_pool.submit(cr, uid, ews_activity_id, self.ews_data)
    #     self.ews_pool.complete(cr, uid, ews_activity_id)
    #     pre_report_value = self.spell_pool.read(
    #         cr, uid, spell_id, ['report_printed'])['report_printed']
    #     self.assertEqual(pre_report_value, False,
    #                      'Flag not updated by complete method properly')
    #
    #     # run the report printing method in api and check that the
    #     # flag is set to True
    #     self.api_pool.print_report(cr, uid, spell_id)
    #     post_report_value = self.spell_pool.read(
    #         cr, uid, spell_id, ['report_printed'])['report_printed']
    #     self.assertEqual(post_report_value, True,
    #                      'Flag not updated by printing method properly')
    #
    # def test_05_test_flag_changed_by_printing_method_no_spell_defined(self):
    #     # complete an observation and check flag is now False
    #     cr, uid = self.cr, self.uid
    #     # clean up before test
    #     dirty_spell_ids = self.spell_pool.search(
    #         cr, uid, [['report_printed', '=', False]])
    #     self.spell_pool.write(
    #         cr, uid, dirty_spell_ids, {'report_printed': True})
    #
    #     # add demo data
    #     spell_id = self.spell_pool.get_by_patient_id(
    # cr, uid, self.patient_id)
    #     spell_id2 = self.spell_pool.get_by_patient_id(
    #         cr, uid, self.patient_id2)
    #     ews_activity_id = self.ews_pool.create_activity(
    #         cr, uid,
    #         {'parent_id': self.spell_id},
    #         {'patient_id': self.patient_id}
    #     )
    #     ews_activity_id2 = self.ews_pool.create_activity(
    #         cr, uid,
    #         {'parent_id': self.spell_id2},
    #         {'patient_id': self.patient_id2}
    #     )
    #     self.ews_pool.submit(cr, uid, ews_activity_id, self.ews_data)
    #     self.ews_pool.complete(cr, uid, ews_activity_id)
    #     self.ews_pool.submit(cr, uid, ews_activity_id2, self.ews_data2)
    #     self.ews_pool.complete(cr, uid, ews_activity_id2)
    #     pre_report_value = self.spell_pool.read(
    #         cr, uid, spell_id, ['report_printed'])['report_printed']
    #     self.assertEqual(pre_report_value, False,
    #                      'Flag not updated by complete method properly')
    #     pre_report_value = self.spell_pool.read(
    #         cr, uid, spell_id2, ['report_printed'])['report_printed']
    #     self.assertEqual(pre_report_value, False,
    #                      'Flag not updated by complete '
    #                      'method properly on second report')
    #
    #     # run the report printing method in api and check
    #     # that the flag is set to True
    #     self.api_pool.print_report(cr, uid)
    #     post_report_value = self.spell_pool.read(
    #         cr, uid, spell_id, ['report_printed'])['report_printed']
    #     self.assertEqual(post_report_value, True,
    #                      'Flag not updated by printing method properly')
    #     post_report_value = self.spell_pool.read(
    #         cr, uid, spell_id2, ['report_printed'])['report_printed']
    #     self.assertEqual(post_report_value, True,
    #                      'Flag not updated by printing method properly')
    #
    # def test_06_test_flag_not_change_by_wkhtmltopdf_error(self):
    #     # complete an observation and check flag is now False
    #     cr, uid = self.cr, self.uid
    #
    #     def mock_print(*args, **kwargs):
    #         global mocked_print_called
    #         mocked_print_called += 1
    #         if mocked_print_called == 2:
    #             raise osv.except_osv(
    #                 'Report (PDF)',
    #                 'Wkhtmltopdf failed (error code: -11). Message:'
    #             )
    #         return mock_print.origin(*args, **kwargs)
    #
    #     self.registry('report')._patch_method('_run_wkhtmltopdf', mock_print)
    #     # clean up before test
    #     dirty_spell_ids = self.spell_pool.search(
    #         cr, uid, [['report_printed', '=', False]])
    #     self.spell_pool.write(
    #         cr, uid, dirty_spell_ids, {'report_printed': True})
    #
    #     # add demo data
    #     spell_id = self.spell_pool.get_by_patient_id(
    #         cr, uid, self.patient_id)
    #     spell_id2 = self.spell_pool.get_by_patient_id(
    #         cr, uid, self.patient_id2)
    #     spell_id3 = self.spell_pool.get_by_patient_id(
    #         cr, uid, self.patient_id3)
    #     ews_activity_id = self.ews_pool.create_activity(
    #         cr, uid,
    #         {'parent_id': self.spell_id},
    #         {'patient_id': self.patient_id}
    #     )
    #     ews_activity_id2 = self.ews_pool.create_activity(
    #         cr, uid,
    #         {'parent_id': self.spell_id2},
    #         {'patient_id': self.patient_id2}
    #     )
    #     ews_activity_id3 = self.ews_pool.create_activity(
    #         cr, uid,
    #         {'parent_id': self.spell_id3},
    #         {'patient_id': self.patient_id3}
    #     )
    #     self.ews_pool.submit(cr, uid, ews_activity_id, self.ews_data)
    #     self.ews_pool.complete(cr, uid, ews_activity_id)
    #     self.ews_pool.submit(cr, uid, ews_activity_id2, self.ews_data2)
    #     self.ews_pool.complete(cr, uid, ews_activity_id2)
    #     self.ews_pool.submit(cr, uid, ews_activity_id3, self.ews_data2)
    #     self.ews_pool.complete(cr, uid, ews_activity_id3)
    #
    #     # Test that all false
    #     pre_report_value = self.spell_pool.read(
    #         cr, uid, spell_id, ['report_printed'])['report_printed']
    #     self.assertEqual(pre_report_value, False,
    #                      'Flag not updated by complete method properly')
    #     pre_report_value = self.spell_pool.read(
    #         cr, uid, spell_id2, ['report_printed'])['report_printed']
    #     self.assertEqual(pre_report_value, False,
    #                      'Flag not updated by complete method '
    #                      'properly on second report')
    #     pre_report_value = self.spell_pool.read(
    #         cr, uid, spell_id3, ['report_printed'])['report_printed']
    #     self.assertEqual(pre_report_value, False,
    #                      'Flag not updated by complete '
    #                      'method properly on second report')
    #
    #     # run the report printing method in api and check that the flag
    #     # is set to True
    #     self.api_pool.print_report(cr, uid)
    #     post_report_value = self.spell_pool.read(
    #         cr, uid, spell_id, ['report_printed'])['report_printed']
    #     self.assertEqual(post_report_value, True,
    #                      'Flag not updated by printing method properly')
    #     post_report_value = self.spell_pool.read(
    #         cr, uid, spell_id2, ['report_printed'])['report_printed']
    #     self.assertEqual(post_report_value, False,
    #                      'Flag not updated by printing method properly')
    #     post_report_value = self.spell_pool.read(
    #         cr, uid, spell_id3, ['report_printed'])['report_printed']
    #     self.assertEqual(post_report_value, True,
    #                      'Flag not updated by printing method properly')
    #
    #     # Test that only failed spell is returned for printing
    #     new_dirty_spell_ids = self.spell_pool.search(
    #         cr, uid, [['report_printed', '=', False]])
    #     self.assertEqual(
    #         new_dirty_spell_ids, [spell_id2],
    #         'Spells returned post failed print not correct')
    #
    #     self.registry('report')._revert_method('_run_wkhtmltopdf')
    #
    # def test_07_test_no_spell_domain_is_empty_when_no_non_
    # printed_spells(self):
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
    # def test_08_test_no_spell_domain_is_empty_when_no_non_
    # printed_spells(self):
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
    #     spell_id = self.spell_pool.get_by_patient_id(
    # cr, uid, self.patient_id)
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
    # def test_12_test_general_settings_view_updated_with_options(self):
    #     # Grab the view XML and make sure it has the overridden values
    #     cr, uid = self.cr, self.uid
    #     view_pool = self.registry('ir.ui.view')
    #     parent_view_id = view_pool.search(
    #         cr, uid, [
    #             ['model', '=', 'base.config.settings'],
    #             ['mode', '=', 'primary']
    #         ]
    #     )[0]
    #     child_view_ids = view_pool.read(
    #         cr, uid,
    #         parent_view_id,
    #         ['inherit_children_ids']
    #     )['inherit_children_ids']
    #     our_view_id = view_pool.search(
    #         cr, uid, [['name', '=', 'base.config.settings.nhclinical']])[0]
    #     self.assertTrue(
    #         our_view_id in child_view_ids,
    #         'View not in list of inherited views for general
    # settings screen')
    #
    # def test_13_test_gen_settings_loads_backup_enabld_wards_correctly(self):
    #     # Using the demo ward call the function to load the data
    #     cr, uid = self.cr, self.uid
    #     settings_pool = self.registry('base.config.settings')
    #     get_vals = settings_pool.get_default_all(cr, uid, [])
    #     self.assertEqual(
    #         get_vals['locations_to_print'][0],
    #         self.wu_id,
    #         'Ward U id not in location to print from settings')
    #
    # def test_14_gen_settings_set_location_removes_all_
    # wards_not_defined(self):
    #     cr, uid = self.cr, self.uid
    #     settings_pool = self.registry('base.config.settings')
    #     record = settings_pool.create(cr, uid, {'locations_to_print': []})
    #     settings_pool.set_locations(cr, uid, [record])
    #     get_vals = settings_pool.get_default_all(cr, uid, [])
    #     self.assertEqual(
    #         get_vals['locations_to_print'],
    #         [], 'Ward U not removed from backed up wards')
