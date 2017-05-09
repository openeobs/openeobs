# -*- coding: utf-8 -*-
from copy import deepcopy
from openerp import models, api
from openerp.osv import fields
from openerp.addons.nh_eobs.helpers import refresh_materialized_views
from openerp.addons.nh_odoo_fixes import validate


class NHClinicalPatientObservationBloodGlucose(models.Model):
    """
    Represents the action of measuring a
    :class:`patient<base.nh_clinical_patient>` blood glucose concentration.
    """
    _name = 'nh.clinical.patient.observation.blood_glucose'
    _inherit = ['nh.clinical.patient.observation']
    _required = ['blood_glucose']
    _num_fields = ['blood_glucose']
    _description = "Blood Glucose"
    _columns = {
        'blood_glucose': fields.float('Blood Glucose', digits=(2, 1)),
    }
    _form_description = [
        {
            'name': 'blood_glucose',
            'type': 'float',
            'label': 'Blood Glucose (mmol/L)',
            'min': 0.0,
            'max': 200.0,
            'digits': [2, 1],
            'initially_hidden': False
        }
    ]

    @api.constrains('blood_glucose')
    def _in_min_max_range(self):
        form_description = self.get_form_description(None)

        if self.blood_glucose is not None:
            field_definition = [
                field for field in form_description if
                field.get('name') == 'blood_glucose'
            ][0]
            field_min = field_definition.get('min')
            field_max = field_definition.get('max')

            validate.in_min_max_range(field_min, field_max, self.blood_glucose)

    @api.model
    def get_form_description(self, patient_id):
        """
        Override of `nh.clinical.patient.observation_scored` method.

        :param patient_id:
        :return:
        """
        form_description = deepcopy(self._form_description)
        return form_description

    @classmethod
    def get_data_visualisation_resource(cls):
        """
        Returns URL of JS file to plot data visualisation so can be loaded on
        mobile and desktop

        :return: URL of JS file to plot graph
        :rtype: str
        """
        return '/nh_blood_glucose/static/src/js/chart.js'

    @api.multi
    def get_formatted_obs(self, replace_zeros=True,
                          convert_datetimes_to_client_timezone=False):
        convert = convert_datetimes_to_client_timezone
        return super(NHClinicalPatientObservationBloodGlucose, self)\
            .get_formatted_obs(replace_zeros=replace_zeros,
                               convert_datetimes_to_client_timezone=convert)

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        return super(
            NHClinicalPatientObservationBloodGlucose, self).complete(
            cr, uid, activity_id, context)
