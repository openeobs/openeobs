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
                               'cancel_others': True,
                               'context': 'eobs',
                               'create_data': {
                                   'suggested_location_id': 'activity.data_ref.location_id.id'
                               }}]}


class nh_clinical_patient_transfer(orm.Model):
    _name = 'nh.clinical.patient.transfer'
    _inherit = 'nh.clinical.patient.transfer'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement', 
                               'type': 'schedule', 
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id': 'activity.data_ref.location_id.id'
                               },
                               'case': 1
                               }
                              , {'model': 'nh.clinical.patient.placement',
                                 'type': 'schedule',
                                 'context': 'eobs',
                                 'cancel_others': True,
                                 'create_data': {
                                    'suggested_location_id':
                                       "location_pool.get_closest_parent_id(cr, uid, 'ward', "
                                       "activity.data_ref.origin_loc_id.id, context=context) if "
                                       "activity.data_ref.origin_loc_id.usage != 'ward' else "
                                       "activity.data_ref.origin_loc_id.id"
                                 },
                                 'case': 2
                                 }
                              ]
               }
    
    
class nh_clinical_adt_spell_update(orm.Model):
    _name = 'nh.clinical.adt.spell.update'
    _inherit = 'nh.clinical.adt.spell.update'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement', 
                               'type': 'schedule', 
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id': 'activity.data_ref.location_id.id'
                               }
                               }]}
    

class nh_clinical_patient_discharge(orm.Model):
    _name = 'nh.clinical.patient.discharge'
    _inherit = 'nh.clinical.patient.discharge'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement',
                               'type': 'schedule',
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id':
                                       "location_pool.get_closest_parent_id(cr, uid, 'ward', "
                                       "activity.data_ref.location_id.id, context=context) if "
                                       "activity.data_ref.location_id.usage != 'ward' else "
                                       "activity.data_ref.location_id.id"
                               }
                               }]}