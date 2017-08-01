# -*- coding: utf-8 -*-
from openerp import models, fields, api


class NhClinicalBedAvailability(models.Model):

    _inherit = 'nh.clinical.bed_availability'

    patient_status = fields.Char(
        string='Patient Status',
        compute='_get_patient_status'
    )

    @api.depends('location')
    def _get_patient_status(self):
        for record in self:
            patient_status = None
            # Originally tried just using `record.location.patient_ids` but
            # for some reason this destroyed performance, taking
            # ~10 minutes to create all the bed availability records.
            # Not sure why this is but read did not have the same problem.
            patient_ids = record.location.read(
                fields=['patient_ids'])[0]['patient_ids']
            if record.location.usage == 'bed' and patient_ids:
                if len(patient_ids) != 1:
                    raise ValueError("Multiple patient IDs found for bed.")
                patient_model = self.env['nh.clinical.patient']
                patient = patient_model.browse(patient_ids[0])

                spell_model = record.env['nh.clinical.spell']
                spell_activity = \
                    spell_model.get_spell_activity_by_patient_id(patient.id)

                obs_stop_model = record.env['nh.clinical.pme.obs_stop']
                obs_stop_activity = \
                    obs_stop_model.get_open_activity(spell_activity.id)

                if obs_stop_activity:
                    obs_stop = obs_stop_activity.data_ref
                    obs_stop_reason = obs_stop.reason.display_text
                    obs_stop_active_time = obs_stop.get_hours_active()
                    patient_status = 'Off Ward - {} ({} Hours)'.format(
                        obs_stop_reason, obs_stop_active_time)
                else:
                    patient_status = 'In Ward'
            record.patient_status = patient_status
