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
        self.spell_model = self.env['nh.clinical.spell']
        cr, uid = self.cr, self.uid

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

        def patch_patient_refusal_in_effect(*args, **kwargs):
            context = kwargs.get('context', {})
            if context.get('refusal_in_effect'):
                return True
            return patch_patient_refusal_in_effect.origin(*args, **kwargs)

        self.activity_model._patch_method('browse', patch_activity_browse)
        self.clinical_review_model._patch_method(
            'create_activity', patch_create_activity)
        self.spell_model._patch_method(
            'patient_monitoring_exception_in_effect',
            patch_patient_refusal_in_effect
        )
        global create_activity_called
        create_activity_called = False

    def tearDown(self):
        self.activity_model._revert_method('browse')
        self.clinical_review_model._revert_method('create_activity')
        self.spell_model._revert_method(
            'patient_monitoring_exception_in_effect')
        super(TestScheduleClinicalReviewNotification, self).tearDown()

    def test_create_when_patient_refusal_in_effect(self):
        """
        Test that if a patient monitoring exception has been started since the
        partial that triggered the schedule_clinical_review_notification call
        then the Clinical Review notification is not created.
        """
        self.ews_model.schedule_clinical_review_notification(
            self.cr, self.uid, 'fake_id', context={'refusal_in_effect': True}
        )
        self.assertFalse(create_activity_called)
