# -*- coding: utf-8 -*-
"""Contains models related to patient monitoring exceptions."""
from openerp import models, fields, api


class PatientMonitoringException(models.Model):
    """
    A 'patient monitoring exception' is a waiver on the regular monitoring of a
    patient. While a patient monitoring exception is in effect the system will
    not enforce observations on a patient in the usual way as there is some
    reason why the patient cannot be or should not be monitored.

    Patient monitoring exceptions are implemented as activity data related to
    an activity. When the activity is 'started' then the patient monitoring
    exception is in effect. When the activity is 'completed' then the patient
    monitoring exception ceases and normal monitoring resumes.
    """
    _name = 'nh.clinical.patient_monitoring_exception'
    _inherit = ['nh.activity.data']

    reason = fields.Many2one(
        'nh.clinical.patient_monitoring_exception.reason',
        required=True
    )
    spell = fields.Many2one('nh.clinical.spell')

    def get_activity_by_spell_activity(self, spell_activity):
        """
        Get a patient monitoring exception activity from the passed spell
        activity.

        :param spell_activity:
        :return:
        """
        activity_model = self.env['nh.activity']
        domain = [
            ('parent_id', '=', spell_activity.id),
            ('data_model', '=', self._name)
        ]
        return activity_model.search(domain)[0]


class PatientMonitoringExceptionReason(models.Model):
    """
    A 'patient monitoring exception reason' is any reason why a patient is
    currently not being monitored (i.e. regular observations are not being
    performed).
    """
    _name = 'nh.clinical.patient_monitoring_exception.reason'

    display_text = fields.Char(string='Reason')

    @api.multi
    def name_get(self):
        return [(rec.id, rec.display_text) for rec in self]
