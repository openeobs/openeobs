from openerp.tests.common import SingleTransactionCase


class TestPatientListObsStop(SingleTransactionCase):
    """
    Test that the override of process patient list is working correctly
    """

    @classmethod
    def setUpClass(cls):
        super(TestPatientListObsStop, cls).setUpClass()
        cls.spell_model = cls.registry('nh.clinical.spell')
        cls.mobile_model = cls.registry('nh.eobs.mobile.mental')

        def patch_spell_search(*args, **kwargs):
            return [1, 2]

        def patch_spell_read(*args, **kwargs):
            return [
                {
                    'patient_id': (1, 'Patient One'),
                    'obs_stop': False
                }, {
                    'patient_id': (2, 'Patient Two'),
                    'obs_stop': True
                }
            ]

        def patch_calculate_ews_class(*args, **kwargs):
            return 'level-none'

        cls.patient_list = [
            {
                'id': 1,
                'clinical_risk': 'low',
                'ews_trend': 'down',
                'next_ews_time': 'soon'
            },
            {
                'id': 2,
                'clinical_risk': 'low',
                'ews_trend': 'down',
                'next_ews_time': 'now'
            }
        ]

        cls.spell_model._patch_method('search', patch_spell_search)
        cls.spell_model._patch_method('read', patch_spell_read)
        cls.mobile_model._patch_method(
            'calculate_ews_class', patch_calculate_ews_class)

        cls.patients = cls.mobile_model.process_patient_list(
            cls.cr, cls.uid, cls.patient_list, context={'test': 'obs_stopped'})

    @classmethod
    def tearDownClass(cls):
        cls.spell_model._revert_method('search')
        cls.spell_model._revert_method('read')
        cls.mobile_model._revert_method('calculate_ews_class')
        super(TestPatientListObsStop, cls).tearDownClass()

    def test_obs_stopped_deadline_string(self):
        """
        Test that the deadline string is set to 'Observations stopped' when
        the obs_stop flag is set to true
        """
        self.assertEqual(
            self.patients[1].get('deadline_time'), 'Observations Stopped')

    def test_non_obs_stopped_deadline_string(self):
        """
        Test that the deadline string is set to 'Observations stopped' when
        the obs_stop flag is set to true
        """
        self.assertEqual(self.patients[0].get('deadline_time'), 'soon')
