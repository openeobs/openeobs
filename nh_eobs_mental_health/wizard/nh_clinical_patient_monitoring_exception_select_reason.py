# -*- coding: utf-8 -*-
from openerp import models, fields, api

class PatientMonitoringExceptionReasonDisplayModel(models.TransientModel):
    _name = 'nh.clinical.patient_monitoring_exception.select_reason'

    reasons = fields.Many2one(
        comodel_name='nh.clinical.patient_monitoring_exception.reason'
    )
    spell_has_open_escalation_tasks = fields.Boolean()
    patient_name = fields.Char(readonly=True)

    @api.multi
    def start_patient_monitoring_exception(self):
        """
        Create a new patient monitoring exception with the passed reason.
        :return:
        """
        if len(self.reasons) > 1:
            raise ValueError(
                "More than one reason was selected. "
                "There should only be one reason per patient monitoring "
                "exception."
            )
        selected_reason_id = self.reasons[0].id
        spell_id = self.env.context['spell_id']
        pme_model = self.env['nh.clinical.patient_monitoring_exception']
        pme_model.create_activity(
            {},
            {'reason': selected_reason_id, 'spell': spell_id}
        )
        wardboard_model = self.env['nh.clinical.wardboard']
        wardboard_model.toggle_obs_stop_flag(spell_id)
