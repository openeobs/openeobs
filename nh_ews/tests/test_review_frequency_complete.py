from openerp.tests.common import SingleTransactionCase
import __builtin__


class MockSuperWithComplete(object):

    def complete(*args, **kwargs):
        return True


class TestReviewFrequencyComplete(SingleTransactionCase):

    trigger_notifications_calls = 0
    OBSERVATION = 'nh.clinical.patient.observation.ews'
    FREQ = 1440

    @classmethod
    def setUpClass(cls):
        super(TestReviewFrequencyComplete, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        cls.review_freq_pool = \
            cls.registry('nh.clinical.notification.frequency')
        cls.activity_pool = cls.registry('nh.activity')
        cls.assess_pool = cls.registry('nh.clinical.notification.assessment')
        cls.notification_pool = cls.registry('nh.clinical.notification')
        cls.nhclinical_api = cls.registry('nh.clinical.api')
        cls.observation_pool = \
            cls.registry('nh.clinical.patient.observation.ews')
        patient_pool = cls.registry('nh.clinical.patient')
        cls.patient = patient_pool.create(cr, uid, {
            'given_name': 'Test',
            'patient_identifier': '123456789101112',
            'family_name': 'McTesterson'
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
        cls.review_freq = cls.review_freq_pool.new(cr, uid, {
            'patient_id': cls.patient,
            'frequency': cls.FREQ,
            'observation': cls.OBSERVATION
        })
        cls.assessment = cls.assess_pool.new(cr, uid, {
            'patient_id': cls.patient
        })

    def setUp(self):
        super(TestReviewFrequencyComplete, self).setUp()
        cr, uid = self.cr, self.uid

        self.trigger_notifications_calls = 0

        def mock_activity_browse(*args, **kwargs):
            context = kwargs.get('context')

            if len(args) > 3 and args[3] == 'rev_freq_browse':
                activity_dict = {
                    'data_ref': self.review_freq
                }

                creator_switch = {
                    'test_rev_freq_no_creator_parent':
                        self.activity_pool.new(cr, uid, {
                            'data_ref': self.observation_pool.browse(
                                cr, uid, self.observation_child
                            )
                        }),
                    'test_rev_freq_no_parent_clinical_risk':
                        self.activity_pool.new(cr, uid, {
                            'data_ref': self.observation_pool.browse(
                                cr, uid, self.observation_child
                            ),
                            'creator_id': self.activity_pool.new(cr, uid, {
                                'data_ref': self.observation_pool.browse(
                                    cr, uid, self.observation_parent
                                )
                            })
                        }),
                    'test_rev_freq_low_parent_not_assess':
                        self.activity_pool.new(cr, uid, {
                            'data_ref': self.observation_pool.browse(
                                cr, uid, self.observation_child
                            ),
                            'creator_id': self.activity_pool.new(cr, uid, {
                                'data_ref': self.observation_pool.browse(
                                    cr, uid, self.low_observation_parent
                                )
                            })
                        }),
                    'test_rev_freq_assess_not_ews':
                        self.activity_pool.new(cr, uid, {
                            'data_ref': self.assessment,
                            'creator_id': self.activity_pool.new(cr, uid, {
                                'data_ref': self.assessment
                            })
                        }),
                    'test_rev_freq_triggers_notifications':
                        self.activity_pool.new(cr, uid, {
                            'data_ref': self.assessment,
                            'creator_id': self.activity_pool.new(cr, uid, {
                                'data_ref': self.observation_pool.browse(
                                    cr, uid, self.low_observation_parent
                                )
                            })
                        })
                }

                if context:
                    creator = creator_switch.get(context)
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
                if args[0]._name == 'nh.clinical.notification.frequency':
                    return MockSuperWithComplete()
            return self.original_super(*args, **kwargs)

        def mock_trigger_notifications(*args, **kwargs):
            self.trigger_notifications_calls += 1
            context = kwargs.get('context')
            if context and context == 'test_rev_freq_triggers_notifications':
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
        super(TestReviewFrequencyComplete, self).tearDown()
        self.activity_pool._revert_method('browse')
        self.nhclinical_api._revert_method('trigger_notifications')

    def test_does_not_trigger_on_no_creator(self):
        """
        Test that no notifications are triggered on the Review Frequency task
        having no creator (for whatever reason)
        """
        self.review_freq_pool.complete(self.cr, self.uid, 'rev_freq_browse')
        self.assertEqual(self.trigger_notifications_calls, 0)

    def test_does_not_trigger_on_no_creator_parent(self):
        """
        Test taht not notifications are triggered on the task that triggered
        the review frequency task having no parent (so just a task triggering
        the Review Frequency task)
        """
        self.review_freq_pool.complete(
            self.cr, self.uid, 'rev_freq_browse',
            context='test_rev_freq_no_creator_parent')

        self.assertEqual(self.trigger_notifications_calls, 0)

    def test_does_not_trigger_on_no_clinical_risk_of_parent(self):
        """
        Test that no notifications are triggered if the task that triggered the
        task that triggered the Review Frequency task was not an EWS
        observation
        """
        self.review_freq_pool.complete(
            self.cr, self.uid, 'rev_freq_browse',
            context='test_rev_freq_no_parent_clinical_risk')

        self.assertEqual(self.trigger_notifications_calls, 0)

    def test_does_not_trigger_on_parent_ews_not_low_risk(self):
        """
        Test that no notifications are triggered if the EWS task that triggered
        the task that triggered the Review Frequency task didn't have a low
        clinical risk
        """
        self.review_freq_pool.complete(
            self.cr, self.uid, 'rev_freq_browse',
            context='test_rev_freq_no_parent_clinical_risk')

        self.assertEqual(self.trigger_notifications_calls, 0)

    def test_does_not_trigger_if_creator_not_assessment(self):
        """
        Test that no notifications are triggered if the task that triggered
        the Review Frequency task is not an Assess Patient task
        """
        self.review_freq_pool.complete(
            self.cr, self.uid, 'rev_freq_browse',
            context='test_rev_freq_low_parent_not_assess')

        self.assertEqual(self.trigger_notifications_calls, 0)

    def test_does_not_trigger_parents_assess_and_not_ews(self):
        """
        Test that no notifications are triggered if the tasks that led to the
        Review Frequency task are not EWS -> Assess Patient
        """
        self.review_freq_pool.complete(
            self.cr, self.uid, 'rev_freq_browse',
            context='test_rev_freq_assess_not_ews')

        self.assertEqual(self.trigger_notifications_calls, 0)

    def test_does_trigger_parents_assess_and_low_ews(self):
        """
        Test that notifications are triggered if the tasks that led to the
        Review Frequency task are not EWS (Low Risk) -> Assess Patient
        """
        self.review_freq_pool.complete(
            self.cr, self.uid, 'rev_freq_browse',
            context='test_rev_freq_triggers_notifications')

        self.assertEqual(self.trigger_notifications_calls, 1)
        self.assertEqual(trigger_params.get('notifications'),
                         [{'model': 'medical_team', 'groups': ['nurse']}])
        self.assertEqual(trigger_params.get('creator_id'), 'rev_freq_browse')
        self.assertEqual(trigger_params.get('patient_id'), self.patient)
        self.assertEqual(trigger_params.get('model'), self.OBSERVATION)
        self.assertEqual(trigger_params.get('group'), 'nurse')
