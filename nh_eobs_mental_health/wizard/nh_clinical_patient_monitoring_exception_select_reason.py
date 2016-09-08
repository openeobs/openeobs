# -*- coding: utf-8 -*-
from openerp import models, fields, api

class PatientMonitoringExceptionSelectReason(models.TransientModel):
    """
    A model used for displaying a drop down list of patient monitoring exception
    'reasons' so that the user can select one.

    'spell_has_open_escalation_tasks' is used as a flag in the view so that
    warning messages can be shown.

    'patient_name' allows the view to easily display the patient name.
    """
    _name = 'nh.clinical.patient_monitoring_exception.select_reason'

    reasons = fields.Many2one(
        comodel_name='nh.clinical.patient_monitoring_exception.reason'
    )
    spell_has_open_escalation_tasks = fields.Boolean()
    patient_name = fields.Char(readonly=True)

    @api.multi
    def start_patient_monitoring_exception(self):
        """
        As this model is only for the purposes of display in the UI this method
        is limited in that it simply receives the call from the view and passes
        on the necessary data in the model to
        :method:`~models.nh_clinical_wardboard.NHClinicalWardboard
        .start_patient_monitoring_exception` where most of the logic is
        implemented.
        """
        reasons = self.reasons
        spell_id = self.env.context['spell_id']
        spell_activity_id = self.env.context['spell_activity_id']
        wardboard_model = self.env['nh.clinical.wardboard']
        wardboard_model.start_patient_monitoring_exception(reasons,
                                                           spell_id,
                                                           spell_activity_id)
