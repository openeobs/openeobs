from openerp.osv import orm


class nh_clinical_patient_placement(orm.Model):
    _name = 'nh.clinical.patient.placement'
    _inherit = 'nh.clinical.patient.placement'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.observation.ews', 
                               'type': 'recurring',
                               'cancel_others': True,
                               'context': 'eobs'}]}


class nh_clinical_patient_admission(orm.Model):
    _name = 'nh.clinical.patient.admission'
    _inherit = 'nh.clinical.patient.admission'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement', 
                               'type': 'schedule', 
                               'context': 'eobs',
                               'create_data': {
                                   'suggested_location_id': 'data_ref.suggested_location_id.id'
                               }}]}


class nh_clinical_adt_patient_transfer(orm.Model):
    _name = 'nh.clinical.adt.patient.transfer'
    _inherit = 'nh.clinical.adt.patient.transfer'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement', 
                               'type': 'schedule', 
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id': 'data_ref.location_id.id'
                               }
                              }]}
    
    
class nh_clinical_adt_spell_update(orm.Model):
    _name = 'nh.clinical.adt.spell.update'
    _inherit = 'nh.clinical.adt.spell.update'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement', 
                               'type': 'schedule', 
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id': 'data_ref.suggested_location_id.id'
                               }
                              }]}
    

class nh_clinical_adt_patient_cancel_discharge(orm.Model):
    _name = 'nh.clinical.adt.patient.cancel_discharge'
    _inherit = 'nh.clinical.adt.patient.cancel_discharge'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement', 
                               'type': 'schedule', 
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id': 'data_ref.last_location_id.parent_id.id'
                               }
                              }]}


class nh_clinical_adt_patient_cancel_transfer(orm.Model):
    _name = 'nh.clinical.adt.patient.cancel_transfer'
    _inherit = 'nh.clinical.adt.patient.cancel_transfer'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement', 
                               'type': 'schedule', 
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id': 'data_ref.last_location_id.id'
                               }
                              }]}