# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestNhClinicalWardboardStartPatientMonitoringException(TransactionCase):
    """
    Test :method:`start_patient_monitoring_exception` in
    :class:`NHClinicalWardboard<nh_eobs_mental_health.nh_clinical_wardboard>`.
    """
    def setUp(self):
        super(TestNhClinicalWardboardStartPatientMonitoringException, self) \
            .setUp()
        self.patient_model = self.env['nh.clinical.patient']
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.activity_pool = self.registry('nh.activity')
        self.reason_model = \
            self.env['nh.clinical.patient_monitoring_exception.reason']
        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.wizard_model = \
            self.env['nh.clinical.patient_monitoring_exception.select_reason']
        self.pme_model = self.env['nh.clinical.patient_monitoring_exception']

        self.patient = self.patient_model.create({
            'given_name': 'Jon',
            'family_name': 'Snow',
            'patient_identifier': 'a_patient_identifier'
        })

        self.spell_activity_id = self.spell_model.create_activity(
            {},
            {'patient_id': self.patient.id, 'pos_id': 1}
        )

        self.spell_activity = \
            self.activity_model.browse(self.spell_activity_id)

        # Fails in spell.get_patient_by_id() if not started.
        self.activity_pool.start(self.env.cr, self.env.uid,
                                 self.spell_activity_id)

        self.spell = self.spell_activity.data_ref

        self.wardboard = self.wardboard_model.new({
            'spell_activity_id': self.spell_activity_id,
            'patient_id': self.patient
        })

        a_reason = self.reason_model.create({'display_text': 'reason one'})

        self.wardboard.start_patient_monitoring_exception(
            a_reason, self.spell.id, self.spell_activity_id
        )
        self.wardboard.end_patient_monitoring_exception(cancellation=True)

    def test_cancels_open_patient_monitoring_exception_activity(self):
        spell_activity = self.activity_model.browse(self.spell_activity_id)
        pme_activity = \
            self.pme_model.get_activity_by_spell_activity(spell_activity)

        self.assertEqual(pme_activity.state, 'cancelled')

        cancel_reason_patient_monitoring_exception = self.browse_ref(
            'nh_eobs.cancel_reason_transfer'
        )
        self.assertEqual(pme_activity.cancel_reason_id,
                         cancel_reason_patient_monitoring_exception)
