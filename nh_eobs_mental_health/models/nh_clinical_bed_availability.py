# -*- coding: utf-8 -*-
from openerp import models, fields, api


class NhClinicalBedAvailability(models.Model):

    _inherit = 'nh.clinical.bed_availability'

    patient_status_selection = [
        ('in ward', 'In Ward'),
        ('off ward', 'Off Ward')
    ]

    patient_status = fields.Selection(
        selection=patient_status_selection,
        string='Patient Status'
    )

    @api.model
    def search_read(self, *args, **kwargs):
        bed_availability_records = super(NhClinicalBedAvailability, self).search_read(*args, **kwargs)
        for record in bed_availability_records:
            record['patient_status'] = self._get_patient_status(record)
        return bed_availability_records

    def _get_patient_status(self, location):
        # if location['usage'] == 'bed' and location['patient_ids']:
        #     patient_model = self.env['nh.clinical.patient']
        #     patient = patient_model.browse(location['patient_ids'][0])
        #
        #     spell_model = self.env['nh.clinical.spell']
        #     spell_activity = spell_model.get_spell_activity_by_patient_id(
        #         patient.id)
        #
        #     obs_stop_model = self.env['nh.clinical.pme.obs_stop']
        #     obs_stop_open = obs_stop_model.get_open_activity(spell_activity.id)
        #
        #     return 'Off Ward' if obs_stop_open else 'In Ward'
        return 'in ward'
