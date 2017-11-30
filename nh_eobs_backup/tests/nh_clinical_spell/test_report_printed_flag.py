from openerp.tests.common import TransactionCase


class TestReportPrintedFlag(TransactionCase):
    """
    Test that the report_printed flag is set on the nh.clinical.spell model
    """

    def setUp(self):
        """
        Set up the tests
        """
        super(TestReportPrintedFlag, self).setUp()
        self.spell_model = self.env['nh.clinical.spell']
        self.test_utils = self.env['nh.clinical.test_utils']
        self.api_model = self.env['nh.eobs.api']
        self.test_utils.admit_and_place_patient()
        self.ews_data = {
            'respiration_rate': 40,
            'indirect_oxymetry_spo2': 99,
            'oxygen_administration_flag': False,
            'body_temperature': 37.0,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 55,
            'avpu_text': 'A'
        }

        def patch_add_report_to_database(*args, **kwargs):
            return True

        def patch_add_report_to_backup_location(*args, **kwargs):
            return True

        self.api_model._patch_method(
            'add_report_to_database',
            patch_add_report_to_database
        )
        self.api_model._patch_method(
            'add_report_to_backup_location',
            patch_add_report_to_backup_location
        )

    def tearDown(self):
        """
        Clean up after test
        """
        self.api_model._revert_method('add_report_to_database')
        self.api_model._revert_method('add_report_to_backup_location')
        super(TestReportPrintedFlag, self).tearDown()

    def test_report_printed_property(self):
        """
        Test that the report_printed flag is available on the spell
        """
        flag_present = 'report_printed' in self.spell_model
        self.assertEqual(
            flag_present,
            True,
            'Flag not set on Spell class properly'
        )

    def test_report_printed_default(self):
        """
        Test that the report_printed flag defaults to False
        """
        flag_value = self.spell_model._defaults['report_printed']
        self.assertEqual(
            flag_value,
            False,
            'Flag value not set correctly'
        )

    def test_report_printed(self):
        """
        Test that on printing the report while the report_printed flag is False
        that is sets the flag to True
        """
        self.test_utils.spell.report_printed = True
        self.test_utils.get_open_obs()
        self.test_utils.complete_obs(self.ews_data)
        self.api_model.print_report(self.test_utils.spell.id)
        self.assertTrue(self.test_utils.spell.report_printed)
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
    #     spell_id = self.spell_pool.get_by_patient_id(cr, uid, self.patient_id)
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