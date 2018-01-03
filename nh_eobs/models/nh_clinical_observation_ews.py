# -*- coding: utf-8 -*-
from openerp.models import Model


class NhClinicalPatientObservationEws(Model):
    """
    Override to add refusal functionality.
    """
    _inherit = 'nh.clinical.patient.observation.ews'
