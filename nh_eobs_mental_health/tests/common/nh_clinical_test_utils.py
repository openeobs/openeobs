# -*- coding: utf-8 -*-

from openerp.models import AbstractModel


class NhClinicalTestUtils(AbstractModel):

    _name = 'nh.clinical.test_utils'
    _inherit = 'nh.clinical.test_utils'

    # Setup methods
    def create_patient_and_spell_and_complete_clinical_review(self):
        self.activity_model = self.env['nh.activity']
        self.patient_model = self.env['nh.clinical.patient']
        self.spell_model = self.env['nh.clinical.spell']
        self.clinical_review_model = \
            self.env['nh.clinical.notification.clinical_review']
        self.clinical_review_frequency_model = \
            self.env['nh.clinical.notification.clinical_review_frequency']
        self.user_model = self.env['res.users']
        self.category_model = self.env['res.partner.category']

        self.nurse_role = self.category_model.search([('name', '=', 'Nurse')])[
            0]

        self.nurse = self.user_model.create({
            'name': 'Jon',
            'login': 'iknownothing',
            'password': 'atall',
            'category_id': [[4, self.nurse_role.id]],
        })

        self.patient = self.patient_model.create({
            'given_name': 'Jon',
            'family_name': 'Snow',
            'patient_identifier': 'he_knows_nothing'
        })

        self.spell_activity_id = self.spell_model.create_activity(
            {},
            {
                'patient_id': self.patient.id,
                'pos_id': 1
            }
        )
        self.activity_model.start(self.spell_activity_id)

        self.clinical_review_notification_activity_id = \
            self.clinical_review_model.sudo(self.nurse).create_activity(
                {
                    'parent_id': self.spell_activity_id,
                    'patient_id': self.patient.id
                },
                {
                    'patient_id': self.patient.id,
                }
            )
        self.clinical_review_notification_activity = \
            self.activity_model.sudo(self.nurse).browse(
                self.clinical_review_notification_activity_id
            )
        self.activity_model.sudo(self.nurse).complete(
            self.clinical_review_notification_activity_id
        )

    def start_pme(self, spell=None, reason=None):
        if not spell:
            spell = self.spell
        if not reason:
            reason_model = \
                self.env['nh.clinical.patient_monitoring_exception.reason']
            reason = reason_model.create({'display_text': 'reason one'})
        wardboard_model = self.env['nh.clinical.wardboard']
        self.wardboard = wardboard_model.browse(spell.id)
        self.wardboard.start_patient_monitoring_exception(
            reason, spell.id, spell.activity_id.id
        )

    def end_pme(self):
        self.wardboard.end_patient_monitoring_exception()

    def find_and_complete_clinical_review(self, ews_id=None):
        if not ews_id:
            ews_id = self.ews_activity.id
        clinical_review = self.activity_model.search([
            ['creator_id', '=', ews_id],
            ['data_model', '=', 'nh.clinical.notification.clinical_review'],
            ['state', 'not in', ['completed', 'cancelled']]
        ])
        if clinical_review:
            self.activity_model.sudo(self.doctor).complete(clinical_review.id)
