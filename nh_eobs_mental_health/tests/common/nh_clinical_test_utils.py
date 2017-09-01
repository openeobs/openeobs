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
            'patient_identifier': 'he_knows_nothing',
            'other_identifier': 'nothing_he_knows'
        })

        self.spell_activity_id = self.spell_model.create_activity(
            {},
            {
                'patient_id': self.patient.id,
                'pos_id': 1
            }
        )
        activity = self.activity_model.browse(self.spell_activity_id)
        activity.start()

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
        self.clinical_review_notification_activity.sudo(self.nurse).complete()

    # TODO rename this to `start_obs_stop`.
    def start_pme(self, spell=None, reason=None):
        """
        Start a patient monitoring exception for the patient created using
        test utils methods.
        :param spell:
        :param reason:
        :type reason: `nh.clinical.patient_monitoring_exception.reason`
        :return:
        """
        if not spell:
            spell = self.spell
        if not reason:
            reason_model = \
                self.env['nh.clinical.patient_monitoring_exception.reason']
            reason = reason_model.create({'display_text': 'reason one'})
        wardboard_model = self.env['nh.clinical.wardboard']
        self.wardboard = wardboard_model.browse(spell.id)
        self.wardboard.start_obs_stop(
            reason, spell.id, spell.activity_id.id)

    def end_pme(self):
        self.wardboard.end_obs_stop()

    def find_and_complete_clinical_review(self, ews_id=None):
        if not ews_id:
            ews_id = self.ews_activity.id
        clinical_review = self.activity_model.search([
            ['creator_id', '=', ews_id],
            ['data_model', '=', 'nh.clinical.notification.clinical_review'],
            ['state', 'not in', ['completed', 'cancelled']]
        ])
        if clinical_review:
            clinical_review.sudo(self.doctor).complete()
            # self.activity_model.sudo(self.doctor)
            # .complete(clinical_review.id)
        return clinical_review

    def find_and_complete_clinical_review_freq(self, review_id=None):
        clinical_review_freq = self.activity_model.search([
            ['creator_id', '=', review_id],
            ['data_model', '=',
             'nh.clinical.notification.clinical_review_frequency'],
            ['state', 'not in', ['completed', 'cancelled']]
        ])
        if clinical_review_freq:
            clinical_review_freq.sudo(self.doctor).complete()

    def create_activity_obs_stop(self):
        obs_stop_model = self.env['nh.clinical.pme.obs_stop']
        pme_reason_acute_ed = self.browse_ref('nh_eobs.acute_hospital_ed')
        activity_id_obs_stop = obs_stop_model.create_activity(
            {
                'parent_id': self.spell_activity.id,
                'spell_activity_id': self.spell_activity.id
            },
            {
                'reason': pme_reason_acute_ed.id,
                'spell': self.spell.id
            }
        )
        activity_obs_stop = self.activity_model.browse(activity_id_obs_stop)
        return activity_obs_stop

    def create_activity_rapid_tranq(self, reason_id=None):
        rapid_tranq_model = self.env['nh.clinical.pme.rapid_tranq']

        vals_data_activity = {
            'parent_id': self.spell_activity.id,
            'spell_activity_id': self.spell_activity.id
        }
        vals_data_ref = {'spell': self.spell.id}
        if reason_id:
            vals_data_ref['reason'] = reason_id

        activity_id_rapid_tranq = rapid_tranq_model.create_activity(
            vals_data_activity,
            vals_data_ref
        )

        activity_rapid_tranq = \
            self.activity_model.browse(activity_id_rapid_tranq)
        return activity_rapid_tranq
