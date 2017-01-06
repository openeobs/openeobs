from openerp.tools import test_reports

from . import observation_report_helpers


class TestObsReportNoDOB(observation_report_helpers.ObservationReportHelpers):

    def setUp(self):
        super(TestObsReportNoDOB, self).setUp()

        def new_patient_pool_mock_patient(*args, **kwargs):
            return [{
                'dob': False,
                'id': 1,
                'other_identifier': 'NHS1234123',
                'gender': 'Male',
                'full_name': 'Test Patient',
                'patient_identifier': 'HOS1234123'
            }]

        self.patient_pool._revert_method('read')
        self.patient_pool._patch_method('read', new_patient_pool_mock_patient)
    #
    # def tearDown(self):
    #     super(TestObsReportNoDOB, self).setUp()


    def test_observation_report_without_dob(self):
        """
        Test that when patient doesn't have DOB that it doesn't break report
        """

        report_model, cr, uid = self.report_model, self.cr, self.uid
        report_test = test_reports.try_report(
            cr, uid, report_model, [],
            data={
                'spell_id': self.spell_id,
                'start_time': None,
                'end_time': None
            })
        self.assertEqual(report_test, True,
                         'Unable to print Observation Report')
