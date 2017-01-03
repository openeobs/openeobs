# -*- coding: utf-8 -*-
from openerp.models import Model


class NhClinicalPatientObservationEws(Model):

    _name = 'nh.clinical.patient.observation.ews'
    _inherit = 'nh.clinical.patient.observation.ews'

    # TODO EOBS-811: Duplication between Python methods and SQL views
    def current_patient_refusal_was_triggered_by(self, refused_obs_activity):
        """
        Extends the :method:`current_patient_refusal_was_triggered_by` of
        :class:`nh_clinical_patient_observation` to take into account patient
        monitoring exceptions which are introduced in this module.

        :param refused_obs_activity:
        :type refused_obs_activity: 'nh.activity' record.
        :return:
        :rtype: bool
        """
        super_return = super(NhClinicalPatientObservationEws, self) \
            .current_patient_refusal_was_triggered_by(refused_obs_activity)

        spell_activity = refused_obs_activity.parent_id
        pme_model = self.env['nh.clinical.patient_monitoring_exception']
        if pme_model.started_after_date(
                spell_activity, refused_obs_activity.date_terminated):
            return False

        return super_return
