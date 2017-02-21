# -*- coding: utf-8 -*-
import __builtin__

from openerp.tests.common import TransactionCase, SingleTransactionCase


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

        self.spell_activity_id = self.activity_pool.new(
            cr, uid, {}
        )

        def mock_activity_browse(*args, **kwargs):
            if len(args) > 3 and args[3] == 'rev_freq_browse':
                review_freq = self.review_freq_pool.new(cr, uid, {
                    'patient_id': self.patient,
                    'frequency': self.SUBMITTED_FREQ,
                    'observation': self.OBSERVATION_TYPE
                })
                return self.activity_pool.new(cr, uid, {
                    'data_ref': review_freq,
                    'spell_activity_id': self.spell_activity_id
                })
            elif len(args) > 3 and args[3] == 'act_browse':
                return self.activity_pool.new(cr, uid, {
                    'data_ref': self.observation_pool.browse(
                        cr, uid, self.observation
                    ),
                    'spell_activity_id': self.spell_activity_id
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
        try:
            self.review_freq_pool.complete(
                self.cr, self.uid, 'rev_freq_browse',
                context='test_rev_freq_search_domain'
            )
        except ValueError:
            # Exception correctly thrown, catch it and do nothing, we just want
            # to see inspect the search domain that was used.
            pass
        self.assertEqual(search_domain, [
            ('spell_activity_id', '=', self.spell_activity_id.id),
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


class TestNoOpenObsFound(TransactionCase):
    """Test the scenario where no observations are found for """
    def setUp(self):
        super(TestNoOpenObsFound, self).setUp()
        self.notification_frequency_model = \
            self.env['nh.clinical.notification.frequency']
        self.activity_model = self.env['nh.activity']
        self.observation_model = self.env['nh.clinical.patient.observation']

        notification_frequency = self.notification_frequency_model.new()
        activity = self.activity_model.new({
            'patient_id': 1,
            'observation': 'foo'
        })
        activity.data_ref = notification_frequency

        def browse_stub(*args, **kwargs):
            return activity

        def search_stub(*args, **kwargs):
            return []

        self.activity_model._patch_method('browse', browse_stub)
        self.activity_model._patch_method('search', search_stub)

    def test_no_obs_found_raises_exception(self):
        with self.assertRaises(ValueError):
            fake_activity_id = 1
            self.notification_frequency_model.complete(fake_activity_id)

    def tearDown(self):
        self.activity_model._revert_method('browse')
        self.activity_model._revert_method('search')
        super(TestNoOpenObsFound, self).tearDown()
