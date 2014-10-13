from openerp.osv import orm


class nh_clinical_patient_placement(orm.Model):
    _name = 'nh.clinical.patient.placement'
    _inherit = 'nh.clinical.patient.placement'


    _POLICY = {'activities': [{'model': 'nh.clinical.patient.observation.ews', 'type': 'recurring'}]}