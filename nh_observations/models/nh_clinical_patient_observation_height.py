# -*- coding: utf-8 -*-
from openerp import api
from openerp.osv import orm, fields


class NhClinicalPatientObservationHeight(orm.Model):
    """
    Represents the action of measuring a
    :class:`patient<base.nh_clinical_patient>` height.
    """
    _name = 'nh.clinical.patient.observation.height'
    _inherit = ['nh.clinical.patient.observation']
    _description = "Height"

    _required = ['height']
    _num_fields = ['height']
    _columns = {
        'height': fields.float('Height', digits=(1, 2)),
    }

    _form_description = [
        {
            'name': 'height',
            'type': 'float',
            'necessary': 'true',
            'label': 'Height (m)',
            'min': 0.1,
            'max': 3.0,
            'digits': [1, 1],
            'initially_hidden': False
        }
    ]

    @api.model
    def get_latest_height(self, patient_id):
        domain = [
            ('patient_id', '=', patient_id),
            ('state', '=', 'completed')
        ]
        order = 'date_terminated desc, id desc'
        records = self.search(domain, order=order)
        for record in records:
            if record.height:
                return record.height
        return None
