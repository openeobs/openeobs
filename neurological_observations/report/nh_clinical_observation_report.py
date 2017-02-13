# -*- coding: utf-8 -*-
from openerp import models


class NhClinicalPatientObservationReport(models.Model):

    def get_report_data(self, data, ews_only=False):
        report_data = super(NhClinicalPatientObservationReport, self).get_report_data()
        report_data['neurological'] = self.get_neurological_observations(data)
        return report_data

    def get_neurological_observations(self, data):
        return []
