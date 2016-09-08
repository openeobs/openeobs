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
        Creates a new patient monitoring exception with the passed reason.

        Creates an activity with a reference to the monitoring exception, save
        the 'spell activity id' on the activity, and start it. It is difficult
        to retrieve the monitoring exception activity later to complete it if
        the spell activity id is not set.

        Toggles the 'obs stop' flag on the spell to True as there is now a
        patient monitoring exception in effect.
        """
        if len(self.reasons) > 1:
            raise ValueError(
                "More than one reason was selected. "
                "There should only be one reason per patient monitoring "
                "exception."
            )
        selected_reason_id = self.reasons[0].id
        spell_id = self.env.context['spell_id']
        spell_activity_id = self.env.context['spell_activity_id']

        pme_model = self.env['nh.clinical.patient_monitoring_exception']
        activity_id = pme_model.create_activity(
            {},
            {'reason': selected_reason_id, 'spell': spell_id}
        )
        activity_model = self.env['nh.activity']
        pme_activity = activity_model.browse(activity_id)
        pme_activity.spell_activity_id = spell_activity_id
        pme_model.start(activity_id)

        wardboard_model = self.env['nh.clinical.wardboard']
        wardboard_model.toggle_obs_stop_flag(spell_id)
