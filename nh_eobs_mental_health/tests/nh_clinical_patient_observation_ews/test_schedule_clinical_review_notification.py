from openerp.tests import SingleTransactionCase


class TestScheduleClinicalReviewNotification(SingleTransactionCase):
    """
    Test that the schedule_clinical_review_notification method only schedules
    the Clinical Review notification if there has been no full observations
    taken since the EWS that triggered it was completed.
    """

    def setUp(self):
        super(TestScheduleClinicalReviewNotification, self).setUp()
        self.activity_model = self.registry('nh.activity')
        self.ews_model = self.registry('nh.clinical.patient.observation.ews')
        self.clinical_review_model = \
            self.registry('nh.clinical.notification.clinical_review')
        cr, uid = self.cr, self.uid

        def patch_activity_get_child_acts(*args, **kwargs):
            context = kwargs.get('context', {})
            test = context.get('test')
            activities = []
            if test == 'full_ews':
                activities.append(self.ews_model.new(
                    cr, uid, {'state': 'completed'}))
            return activities

        def patch_activity_browse(*args, **kwargs):
            if args[1] == 'fake_id':
                return self.activity_model.new(cr, uid, {
                    'data_ref': self.ews_model.new(cr, uid, {})
                })
            return patch_activity_browse.origin(*args, **kwargs)

        def patch_create_activity(*args, **kwargs):
            global create_activity_called
            create_activity_called = True
            return True

        self.ews_model._patch_method(
            'get_child_activity', patch_activity_get_child_acts)
        self.activity_model._patch_method('browse', patch_activity_browse)
        self.clinical_review_model._patch_method(
            'create_activity', patch_create_activity)
        global create_activity_called
        create_activity_called = False

    def tearDown(self):
        self.ews_model._revert_method('get_child_activity')
        self.activity_model._revert_method('browse')
        self.clinical_review_model._revert_method('create_activity')
        super(TestScheduleClinicalReviewNotification, self).tearDown()

    def test_creates_notification_when_no_full_ews(self):
        """
        Test that if no full EWS have been done since the partial that
        triggered the schedule_clinical_review_notification call then the
        Clinical Review notification is created
        """
        self.ews_model.schedule_clinical_review_notification(
            self.cr, self.uid, *('fake_id',), context={'test': 'partial_ews'})
        self.assertTrue(create_activity_called)

    def test_dont_create_notification_when_full_ews(self):
        """
        Test that is a full EWS has been done since the partial that
        triggered the schedule_clinical_review_notification call then the
        Clinical Review notification is not created
        """
        self.ews_model.schedule_clinical_review_notification(
            self.cr, self.uid, *('fake_id',), context={'test': 'full_ews'})
        self.assertFalse(create_activity_called)
