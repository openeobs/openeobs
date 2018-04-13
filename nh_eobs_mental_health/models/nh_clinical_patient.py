from openerp import models, api


class NhClinicalPatient(models.Model):

    _inherit = 'nh.clinical.patient'

    @api.one
    def serialise(self):
        """
        Override to add refusal and rapid tranq data to the patient dictionary.

        :return:
        :rtype: dict
        """
        patient_dict = super(NhClinicalPatient, self).serialise()[0]

        last_ews = self.get_latest_completed_ews(limit=1)

        patient_dict['refusal_in_effect'] = self.get_refusal_in_effect(
            last_ews)
        patient_dict['rapid_tranq'] = self.get_rapid_tranq_status()

        self.modify_deadline_for_patient_statuses_if_necessary(patient_dict)

        return patient_dict

    def get_refusal_in_effect(self, last_ews):
        """
        Get data about the patient's refusal status to add to the patient
        dictionary.

        :param last_ews:
        :return:
        :rtype: bool
        """
        # If `last_ews` is falsey it is assumed that there is no last EWS
        # which means that the patient must not have had any EWS performed yet
        # and therefore cannot have refused any.
        if not last_ews:
            return False
        ews_model = self.env['nh.clinical.patient.observation.ews']
        return ews_model.is_refusal_in_effect(last_ews.activity_id.id)

    def get_rapid_tranq_status(self):
        """
        Get data about the patient's rapid tranq status to add to the patient
        dictionary.

        :return:
        :rtype: bool
        """
        spell_model = self.env['nh.clinical.spell']
        spell_activity = spell_model.get_spell_activity_by_patient_id(self.id)
        return spell_activity.data_ref.rapid_tranq

    @api.multi
    def get_status_map_for_patient_ids(self):
        """
        Take a list of patient IDs and return the spells

        :return: dict containing patient ID to status flag mapping
        """
        spell_model = self.env['nh.clinical.spell']
        spell_ids = spell_model.search([
            ['patient_id', 'in', self._ids],
            ['state', 'not in', ['completed', 'cancelled']]
        ])
        spells = spell_model.read(spell_ids, [
            'obs_stop',
            'rapid_tranq',
            'patient_id'
        ])
        status_mapping = {}
        for spell in spells:
            patient_id = spell.get('patient_id')
            if patient_id:
                patient_status = status_mapping[patient_id[0]] = {}
                patient_status['obs_stop'] = spell.get('obs_stop')
                patient_status['rapid_tranq'] = spell.get('rapid_tranq')
        return status_mapping

    def modify_deadline_for_patient_statuses_if_necessary(self, patient_dict):
        status_map = self.get_status_map_for_patient_ids()
        patient_dict['rapid_tranq'] = status_map.get(self.id, {}).get(
            'rapid_tranq', False)
        if status_map.get(self.id, {}).get('obs_stop'):
            for deadline in patient_dict['deadlines']:
                deadline['datetime'] = 'Observations Stopped'
