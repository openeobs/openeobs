from openerp.tests.common import SingleTransactionCase
import __builtin__


class MockSuperWithComplete(object):

    def complete(*args, **kwargs):
        return True


class TestReviewFrequencyComplete(SingleTransactionCase):

    calls_to_write = 0
    OBSERVATION_TYPE = 'nh.clinical.patient.observation.height'
    SUBMITTED_FREQ = 1440

    @classmethod
    def setUpClass(cls):
        super(TestReviewFrequencyComplete, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        cls.review_freq_pool = \
            cls.registry('nh.clinical.notification.frequency')
        cls.activity_pool = cls.registry('nh.activity')
        cls.notification_pool = cls.registry('nh.clinical.notification')
        cls.observation_pool = cls.registry(cls.OBSERVATION_TYPE)
        patient_pool = cls.registry('nh.clinical.patient')
        cls.patient = patient_pool.create(cr, uid, {
            'given_name': 'Test',
            'patient_identifier': '123456789101112',
            'family_name': 'McTesterson'
        })
        cls.observation = cls.observation_pool.create(cr, uid, {
            'patient_id': cls.patient
        })

    def setUp(self):
        super(TestReviewFrequencyComplete, self).setUp()
        cr, uid = self.cr, self.uid

        def mock_activity_browse(*args, **kwargs):
            if len(args) > 3 and args[3] == 'rev_freq_browse':
                review_freq = self.review_freq_pool.new(cr, uid, {
                    'patient_id': self.patient,
                    'frequency': self.SUBMITTED_FREQ,
                    'observation': self.OBSERVATION_TYPE
                })
                return self.activity_pool.new(cr, uid, {
                    'data_ref': review_freq
                })
            elif len(args) > 3 and args[3] == 'act_browse':
                return self.activity_pool.new(cr, uid, {
                    'data_ref': self.observation_pool.browse(cr, uid,
                                                             self.observation)
                })
            else:
                return mock_activity_browse.origin(*args, **kwargs)

        def mock_activity_search(*args, **kwargs):
            context = kwargs.get('context')
            if context:
                if context == 'test_rev_freq_search_domain':
                    global search_domain
                    search_domain = args[3]
                if context == 'test_rev_freq_update':
                    return ['act_browse']
            return []

        def mock_notification_complete(*args, **kwargs):
            if len(args) > 1 and hasattr(args[1], '_name'):
                if args[1]._name == 'nh.clinical.notification.frequency':
                    return MockSuperWithComplete()
            else:
                return self.original_super(*args, **kwargs)

        def mock_observation_write(*args, **kwargs):
            context = kwargs.get('context')
            self.calls_to_write += 1
            if context and context == 'test_rev_freq_update':
                global update_dict
                update_dict = args[4]
            return True

        self.activity_pool._patch_method('browse', mock_activity_browse)
        self.activity_pool._patch_method('search', mock_activity_search)
        self.observation_pool._patch_method('write', mock_observation_write)

        self.original_super = super
        __builtin__.super = mock_notification_complete

    def tearDown(self):
        __builtin__.super = self.original_super
        super(TestReviewFrequencyComplete, self).tearDown()
        self.activity_pool._revert_method('browse')
        self.activity_pool._revert_method('search')
        self.observation_pool._revert_method('write')

    def test_uses_submitted_data_for_obs_search(self):
        """
        Test that the complete method uses the submitted patient_id and
        observation parameters to search for the most recent open observation
        """
        self.review_freq_pool.complete(self.cr, self.uid, 'rev_freq_browse',
                                       context='test_rev_freq_search_domain')
        self.assertEqual(search_domain, [
            ('patient_id', '=', self.patient),
            ('data_model', '=', self.OBSERVATION_TYPE),
            ('state', 'not in', ['completed', 'cancelled'])
        ])

    def test_updates_frequency_for_latest_observation(self):
        """
        Test that the complete method updates the frequency of the observation
        with the frequency submitted
        """
        self.review_freq_pool.complete(self.cr, self.uid, 'rev_freq_browse',
                                       context='test_rev_freq_update')
        self.assertEqual(update_dict, {'frequency': self.SUBMITTED_FREQ})

    def test_does_not_update_if_no_obs_found(self):
        """
        Test that the complete method does not update the frequency if there
        are no observations found
        """
        self.calls_to_write = 0
        self.review_freq_pool.complete(self.cr, self.uid, 'rev_freq_browse',
                                       context='test_rev_freq_no_update')
        self.assertEqual(self.calls_to_write, 0)
