# -*- coding: utf-8 -*-
from openerp import models, fields, api

class PatientMonitoringExceptionReasonDisplayModel(models.TransientModel):
    _name = 'nh.clinical.patient_monitoring_exception.select_reason'

    # reason_ids = fields.One2many(
    #     comodel_name='nh.clinical.patient_monitoring_exception_reason',
    #     inverse_name='display_model_id'
    # )
    reasons = fields.Many2one(
        comodel_name='nh.clinical.patient_monitoring_exception_reason'
    )

    @api.one
    def create_patient_monitoring_exception(self):
        """
        Create a new patient monitoring exception with the passed reason.
        :return:
        """
        print('Self is '.format(self))
        if len(self.reasons) > 1:
            raise ValueError(
                "More than one reason was selected. "
                "There should only be one reason per patient monitoring "
                "exception."
            )
        selected_reason = self.reasons[0]
        wardboard_model = self.env['nh.clinical.wardboard']