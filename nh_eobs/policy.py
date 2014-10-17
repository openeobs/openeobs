from openerp.osv import orm


class nh_clinical_patient_placement(orm.Model):
    _name = 'nh.clinical.patient.placement'
    _inherit = 'nh.clinical.patient.placement'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.observation.ews', 'type': 'recurring', 'context': 'eobs'}]}


class nh_clinical_patient_admission(orm.Model):
    _name = 'nh.clinical.patient.admission'
    _inherit = 'nh.clinical.patient.admission'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement', 'type': 'schedule', 'context': 'eobs',
                               'create_data': {
                                   'suggested_location_id': 'data_ref.suggested_location_id.id'
                               }}]}