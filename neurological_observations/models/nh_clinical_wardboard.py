# -*- coding: utf-8 -*-
from openerp.addons.nh_eobs.wardboard import nh_clinical_wardboard
from openerp.osv import orm, fields


class NhClinicalWardboardNeuro(orm.Model):

    _name = 'nh.clinical.wardboard'
    _inherit = 'nh.clinical.wardboard'

    _columns = {
        'neuro_ids': fields.function(
            nh_clinical_wardboard._get_data_ids_multi,
            multi='neuro_ids',
            type='many2many',
            relation='nh.clinical.patient.observation.neurological',
            string='Neurological Obs'
        )
    }
