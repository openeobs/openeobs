import __builtin__

from openerp.tests import SingleTransactionCase


class FakeEWSSuper(object):
    """
    Fake super for the EWS class under test
    """

    def complete(*args, **kwargs):
        """
        Stubbed complete method that returns an activity_id

        :param cr: Odoo Cursor
        :param uid: User doing operation
        :param activity_id: Activity being completed
        :param context: Odoo Context
        :return: Stubbed out ID
        """
        return 1


class TestComplete(SingleTransactionCase):
    """
    Test that the complete method of the nh.clinical.patient.observation.ews
    model schedules a cron to call the 'schedule_clinical_review_notification'
    method in X days depending on the clinical risk of the patient.
    """

    def setUp(self):
        super(TestComplete, self).setUp()
        self.cron_model = self.env['ir.cron']
        ews_model_name = 'nh.clinical.patient.observation.ews'
        self.ews_model = self.env[ews_model_name]
        self.activity_model = self.env['nh.activity']
        self.api_model = self.env['nh.eobs.api']
        patient_model = self.env['nh.clinical.patient']
        patient = patient_model.new({
            'family_name': 'Testerson',
            'given_name': 'Testy',
            'other_identifier': '1337',
            'patient_identifier': '666'
        })

        refused_ews = self.activity_model.new({
            'data_ref': self.ews_model.new({
                'respiration_rate': 11,
                'partial_reason': 'refused',
                'patient_id': patient,
                'is_partial': True
            }),
            'data_model': ews_model_name
        })

        partial_ews = self.activity_model.new({
            'data_model': ews_model_name,
            'data_ref': self.ews_model.new({
                'respiration_rate': 11,
                'partial_reason': 'asleep',
                'patient_id': patient,
                'is_partial': True
            })
        })

        full_ews = self.activity_model.new({
            'data_model': ews_model_name,
            'data_ref': self.ews_model.new({
                'respiration_rate': 18,
                'indirect_oxymetry_spo2': 99,
                'oxygen_administration_flag': 0,
                'body_temperature': 37.5,
                'blood_pressure_systolic': 120,
                'blood_pressure_diastolic': 80,
                'pulse_rate': 65,
                'avpu_text': 'A',
                'patient_id': patient,
                'is_partial': False
            })
        })

        def patched_activity_browse(*args, **kwargs):
            context = kwargs.get('context', {})
            test = context.get('test')
            ews = {
                'refused': refused_ews,
                'partial': partial_ews,
                'full': full_ews
            }.get(test)
            if ews:
                return ews
            return patched_activity_browse.origin(*args, **kwargs)

        def patched_cron_create(*args, **kwargs):
            global cron_call
            cron_call = args[3]
            return 1

        def patched_get_patients(*args, **kwargs):
            context = kwargs.get('context', {})
            patient = context.get('patient', 'high')
            risk = {
                'no': 'None',
                'low': 'Low',
                'med': 'Medium',
                'high': 'High'
            }.get(patient)
            return [{
                'clinical_risk': risk
            }]

        def mock_ews_super(*args, **kwargs):
            if len(args) > 1 and hasattr(args[0], '_name'):
                if args[0]._name == 'nh.clinical.patient.observation.ews':
                    return FakeEWSSuper()
            return self.original_super(*args, **kwargs)

        self.cron_model._patch_method('create', patched_cron_create)
        self.activity_model._patch_method('browse', patched_activity_browse)
        self.api_model._patch_method('get_patients', patched_get_patients)

        self.original_super = super
        __builtin__.super = mock_ews_super

    def tearDown(self):
        __builtin__.super = self.original_super
        self.cron_model._revert_method('create')
        self.activity_model._revert_method('browse')
        self.api_model._revert_method('get_patients')
        super(TestComplete, self).tearDown()

    def call_test(self, context):
        ews_model = self.registry('nh.clinical.patient.observation.ews')
        global cron_call
        cron_call = None
        ews_model.complete(self.cr, self.uid, 1, context=context)

    def test_schedules_clinical_review_cron_in_7_day_no(self):
        """
        Test that completing a partial observation with the reason 'refused'
        for a patient with no clinical risk results in an ir.cron being set up
        to call schedule_clinical_review_notification in 7 days.
        """
        self.call_test(context={'test': 'refused', 'patient': 'no'})
        self.assertEqual(cron_call.get('interval_number'), 7)

    def test_schedules_clinical_review_cron_in_7_day_low(self):
        """
        Test that completing a partial observation with the reason 'refused'
        for a patient with low clinical risk results in an ir.cron being set up
        to call schedule_clinical_review_notification in 7 days.
        """
        self.call_test(context={'test': 'refused', 'patient': 'low'})
        self.assertEqual(cron_call.get('interval_number'), 7)

    def test_schedules_clinical_review_cron_in_1_day_med(self):
        """
        Test that completing a partial observation with the reason 'refused'
        for a patient with medium clinical risk results in an ir.cron being
        set up to call schedule_clinical_review_notification in 1 day.
        """
        self.call_test(context={'test': 'refused', 'patient': 'med'})
        self.assertEqual(cron_call.get('interval_number'), 1)

    def test_schedules_clinical_review_cron_in_1_day_high(self):
        """
        Test that completing a partial observation with the reason 'refused'
        for a patient with high clinical risk results in an ir.cron being
        set up to call schedule_clinical_review_notification in 1 day.
        """
        self.call_test(context={'test': 'refused', 'patient': 'high'})
        self.assertEqual(cron_call.get('interval_number'), 1)

    def test_schedules_clinical_review_cron_in_1_day_unknown(self):
        """
        Test that completing a partial observation with the reason 'refused'
        for a patient with unknown clinical risk results in an ir.cron being
        set up to call schedule_clinical_review_notification in 1 day.
        """
        self.call_test(context={'test': 'refused', 'patient': '?'})
        self.assertEqual(cron_call.get('interval_number'), 1)

    def test_dont_schedule_clinical_review_cron_if_full(self):
        """
        Test that completing a full observation for a patient results in
        no ir.cron being set up to call schedule_clinical_review_notification.
        """
        self.call_test(context={'test': 'full'})
        self.assertIsNone(cron_call)

    def test_dont_schedule_clinical_review_cron_if_not_refused(self):
        """
        Test that completing a partial observation with a reason that isn't
        refused results in no ir.cron being set up to called
        schedule_clinical_review_notification
        """
        self.call_test(context={'test': 'partial'})
        self.assertIsNone(cron_call)

    def test_cron_args(self):
        """
        Check the arguments sent to the ir.cron create call
        """
        self.call_test(context={'test': 'refused', 'patient': 'high'})
        self.assertEqual(cron_call.get('interval_type'), 'days')
        self.assertEqual(cron_call.get('priority'), 0)
        self.assertEqual(cron_call.get('args'), '(1,)')
        self.assertEqual(cron_call.get('numbercall'), 1)
        self.assertEqual(cron_call.get('model'),
                         'nh.clinical.patient.observation.ews')
        self.assertEqual(cron_call.get('function'),
                         'schedule_clinical_review_notification')
        self.assertEqual(cron_call.get('name'),
                         'Clinical Review Task for Activity:1')
