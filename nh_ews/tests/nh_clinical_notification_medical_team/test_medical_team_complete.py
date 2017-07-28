from openerp.tests.common import SingleTransactionCase
import __builtin__


class MockSuperWithComplete(object):

    def complete(*args, **kwargs):
        return True


class TestMedicalTeamComplete(SingleTransactionCase):

    trigger_notifications_calls = 0
    OBSERVATION = 'nh.clinical.patient.observation.ews'
    FREQ = 1440

    @classmethod
    def setUpClass(cls):
        super(TestMedicalTeamComplete, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        cls.review_freq_pool = \
            cls.registry('nh.clinical.notification.frequency')
        cls.activity_pool = cls.registry('nh.activity')
        cls.assess_pool = cls.registry('nh.clinical.notification.assessment')
        cls.notification_pool = cls.registry('nh.clinical.notification')
        cls.medical_team_pool = \
            cls.registry('nh.clinical.notification.medical_team')
        cls.nhclinical_api = cls.registry('nh.clinical.api')
        cls.observation_pool = \
            cls.registry('nh.clinical.patient.observation.ews')
        patient_pool = cls.registry('nh.clinical.patient')
        cls.patient = patient_pool.create(cr, uid, {
            'given_name': 'Test',
            'patient_identifier': '123456789101112',
            'family_name': 'McTesterson',
            'other_identifier': '2131231231'
        })
        cls.observation_parent = cls.observation_pool.create(cr, uid, {
            'patient_id': cls.patient
        })
        cls.low_observation_parent = cls.observation_pool.create(cr, uid, {
            'patient_id': cls.patient,
            'respiration_rate': 11,
            'indirect_oxymetry_spo2': 100,
            'body_temperature': 38.0,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 80,
            'avpu_text': 'A',
            'oxygen_administration_flag': False
        })
        cls.observation_child = cls.observation_pool.create(cr, uid, {
            'patient_id': cls.patient
        })
        cls.review_freq = cls.review_freq_pool.create(cr, uid, {
            'patient_id': cls.patient,
            'frequency': cls.FREQ,
            'observation': cls.OBSERVATION
        })
        cls.review_freq_data = \
            cls.review_freq_pool.browse(cr, uid, cls.review_freq)
        cls.assessment = cls.assess_pool.new(cr, uid, {
            'patient_id': cls.patient
        })

        cls.medical_team = cls.medical_team_pool.new(cr, uid, {
            'patient_id': cls.patient
        })

    def setUp(self):
        super(TestMedicalTeamComplete, self).setUp()
        cr, uid = self.cr, self.uid

        self.trigger_notifications_calls = 0

        def mock_activity_browse(*args, **kwargs):
            context = kwargs.get('context')

            if len(args) > 3 and args[3] == 'medical_team_browse':
                activity_dict = {
                    'data_ref': self.medical_team
                }

                if context:
                    creator = self.activity_pool.new(cr, uid, {
                        'data_ref': self.review_freq_data,
                        'creator_id': self.activity_pool.new(cr, uid, {
                            'data_ref': self.observation_pool.browse(
                                cr, uid, self.review_freq
                            )
                        })
                    })
                    if creator:
                        activity_dict['creator_id'] = creator

                return self.activity_pool.new(cr, uid, activity_dict)
            elif len(args) > 3 and args[3] == 'act_browse':
                return self.activity_pool.new(cr, uid, {
                    'data_ref': self.observation_pool.browse(
                        cr, uid, self.observation_child)
                })
            else:
                return mock_activity_browse.origin(*args, **kwargs)

        def mock_notification_complete(*args, **kwargs):
            if len(args) > 1 and hasattr(args[0], '_name'):
                if args[0]._name == 'nh.clinical.notification.medical_team':
                    return MockSuperWithComplete()
            return self.original_super(*args, **kwargs)

        def mock_trigger_notifications(*args, **kwargs):
            self.trigger_notifications_calls += 1
            context = kwargs.get('context')
            test_name = 'test_medical_team_triggers_notifications'
            if context and context == test_name:
                global trigger_params
                trigger_params = args[3]
            return True

        self.activity_pool._patch_method('browse', mock_activity_browse)
        self.nhclinical_api._patch_method('trigger_notifications',
                                          mock_trigger_notifications)

        self.original_super = super
        __builtin__.super = mock_notification_complete

    def tearDown(self):
        __builtin__.super = self.original_super
        super(TestMedicalTeamComplete, self).tearDown()
        self.activity_pool._revert_method('browse')
        self.nhclinical_api._revert_method('trigger_notifications')

    def test_does_trigger_parents_assess_and_low_ews(self):
        """
        Test that notifications are triggered if the tasks that led to the
        Review Frequency task are not EWS (Low Risk) -> Assess Patient
        """
        self.medical_team_pool.complete(
            self.cr, self.uid, 'medical_team_browse',
            context='test_medical_team_triggers_notifications')

        self.assertEqual(self.trigger_notifications_calls, 1)
        self.assertEqual(
            trigger_params.get('notifications'),
            [{'model': 'doctor_assessment', 'groups': ['doctor']}]
        )
        self.assertEqual(
            trigger_params.get('creator_id'),
            'medical_team_browse'
        )
        self.assertEqual(trigger_params.get('patient_id'), self.patient)
        self.assertEqual(
            trigger_params.get('model'),
            'nh.clinical.notification.frequency'
        )
        self.assertEqual(trigger_params.get('group'), 'doctor')
