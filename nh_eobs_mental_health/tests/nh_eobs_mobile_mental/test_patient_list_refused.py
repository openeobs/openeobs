from openerp.tests.common import SingleTransactionCase


class TestPatientListRefused(SingleTransactionCase):
    """
    Test that the override of process patient list is working correctly
    """

    @classmethod
    def setUpClass(cls):
        super(TestPatientListRefused, cls).setUpClass()
        cls.spell_model = cls.registry('nh.clinical.spell')
        cls.mobile_model = cls.registry('nh.eobs.mobile.mental')
        cls.ews_model = cls.registry('nh.clinical.patient.observation.ews')

        def patch_spell_search(*args, **kwargs):
            return [1, 2]

        def patch_spell_read(*args, **kwargs):
            return [
                {
                    'patient_id': (1, 'Patient One'),
                    'obs_stop': False
                }, {
                    'patient_id': (2, 'Patient Two'),
                    'obs_stop': False
                }
            ]

        def patch_calculate_ews_class(*args, **kwargs):
            return 'level-none'

        def patch_is_patient_refusal_in_effect(*args, **kwargs):
            patient_id = args[3]
            if patient_id == 1:
                return True
            return False

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
        cls.ews_model._patch_method(
            'is_patient_refusal_in_effect', patch_is_patient_refusal_in_effect)
        cls.patients = cls.mobile_model.process_patient_list(
            cls.cr, cls.uid, cls.patient_list, context={'test': 'obs_stopped'})

    @classmethod
    def tearDownClass(cls):
        cls.spell_model._revert_method('search')
        cls.spell_model._revert_method('read')
        cls.mobile_model._revert_method('calculate_ews_class')
        cls.ews_model._revert_method('is_patient_refusal_in_effect')
        super(TestPatientListRefused, cls).tearDownClass()

    def test_refused_deadline_string(self):
        """
        Test that the deadline string is set to 'Observations stopped' when
        the obs_stop flag is set to true
        """
        self.assertEqual(
            self.patients[0].get('deadline_time'), 'Refused - soon')

    def test_non_refused_deadline_string(self):
        """
        Test that the deadline string is set to 'Observations stopped' when
        the obs_stop flag is set to true
        """
        self.assertEqual(self.patients[1].get('deadline_time'), 'now')
