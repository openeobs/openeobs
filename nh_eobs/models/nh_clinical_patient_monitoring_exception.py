# -*- coding: utf-8 -*-
from openerp import models, fields, api

class PatientMonitoringException(models.Model):
    """
    A 'patient monitoring exception' is any reason why a patient is currently
    not being monitored (i.e. regular observations are not being performed).

    Patient monitoring exceptions are implemented as activity data related to
    an activity. When the activity is 'started' then the patient monitoring
    exception is in effect. When the activity is 'completed' then the patient
    monitoring exception ceases and normal monitoring resumes.
    """
    _name = 'nh.clinical.patient_monitoring_exception'
    _inherit = ['nh.activity.data']

    reason = fields.Many2one('nh.clinical.patient_monitoring_exception_reason')
    spell = fields.Many2one('nh.clinical.spell')

class PatientMonitoringExceptionReason(models.Model):
    _name = 'nh.clinical.patient_monitoring_exception_reason'

    display_text = fields.Char(string='Reason')

    @api.multi
    def name_get(self):
        return [(rec.id, rec.display_text) for rec in self]

    def create_patient_monitoring_exception(self):
        wardboard_model = self.registry('nh.clinical.wardboard')
        return {}
