from openerp import models, api


class NhClinicalPatient(models.Model):

    _inherit = 'nh.clinical.patient'

    @api.one
    def serialise(self):
        patient_dict = super(NhClinicalPatient, self).serialise()[0]

        last_ews = self.get_latest_completed_ews(limit=1)

        patient_dict['refusal_in_effect'] = self.get_refusal_in_effect(
            last_ews),
        patient_dict['rapid_tranq'] = self.get_rapid_tranq_status()
        return patient_dict

    def get_refusal_in_effect(self, last_ews):
        # If `last_ews` is falsey it is assumed that there is no last EWS
        # which means that the patient must not have had any EWS performed yet
        # and therefore cannot have refused any.
        if not last_ews:
            return False
        ews_model = self.env['nh.clinical.patient.observation.ews']
        return ews_model.is_refusal_in_effect(last_ews.activity_id.id)

    def get_rapid_tranq_status(self):
        spell_model = self.env['nh.clinical.spell']
        spell_activity = spell_model.get_spell_activity_by_patient_id(self.id)
        return spell_activity.data_ref.rapid_tranq
