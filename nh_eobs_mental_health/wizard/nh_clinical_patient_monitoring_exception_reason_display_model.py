# -*- coding: utf-8 -*-
from openerp import models, fields

class PatientMonitoringExceptionReasonDisplayModel(models.TransientModel):
    _name = 'nh.clinical.patient_monitoring_exception_reason_display_model'

    reasons = fields.One2many('nh.clinical.patient_monitoring_exception_reason')