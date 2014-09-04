# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from openerp.addons.t4activity.activity import except_if
import logging        
from pprint import pprint as pp
_logger = logging.getLogger(__name__)

class t4_clinical_demo_placement(orm.TransientModel):    
    _name = 't4.clinical.demo.placement'
    
    _columns ={
#         'family_name':
#         'given_name':
#         'other_identifier':

#         'gender':
#         'sex':
        'bed_location_id':  fields.many2one('t4.clinical.location', 'Bed Location', domain=[['usage','=','bed']], required=True),
        'pos_id': fields.many2one('t4.clinical.pos', 'POS', required=True),
        
        'dob': fields.datetime('Date Of Birth'),
        'sex': fields.char('Sex', size=1),
        'gender': fields.char('Gender', size=1),
        'patient_identifier': fields.char('Patient Identifier', size=100,),
        'other_identifier': fields.char('Other Identifier', size=100,),
        'given_name': fields.char('Given Name', size=200),
        'middle_names': fields.char('Middle Name(s)', size=200),
        'family_name': fields.char('Family Name', size=200,),
   
        
    } 
    
    def default_get(self, cr, uid, fields, context=None):
        api_demo = self.pool['t4.clinical.api.demo']
        api = self.pool['t4.clinical.api']
        res = {}.fromkeys(fields)
        data = api_demo.demo_data(cr, uid, "t4.clinical.adt.patient.register")
        res.update(data)
        pos_id = self.pool['t4.clinical.pos'].search(cr, uid, [])[0]
        bed_id = api.location_map(cr, uid, usages=['bed'], pos_ids=[pos_id]).keys()[0]
        res.update({'pos_id': pos_id, 'bed_location_id': bed_id})
        return res    
    
    def submit(self, cr, uid, ids, context=None):
        api = self.pool['t4.clinical.api']
        api_demo = self.pool['t4.clinical.api.demo']
        data = self.read(cr, uid, ids[0], [])
        data_copy = data.copy()
        data_copy.pop('id')
        bed_location_id = data_copy.pop('bed_location_id')[0]
        pos_id = data_copy.pop('pos_id')[0]
        #data_copy.update({'pos_id': pos_id})

        adt_uid = api.user_map(cr, uid, group_xmlids=['group_t4clinical_adt'], pos_ids=[pos_id]).keys()
        adt_uid = adt_uid and adt_uid[0] or api_demo.create(cr, uid, 'res.users', 'user_adt', {'pos_id': pos_id})
        
        reg_activity_id = api_demo.create_activity(cr, adt_uid, 't4.clinical.adt.patient.register', None, {}, data_copy)
        reg_data = api.get_activity_data(cr, uid, reg_activity_id)
        #v.update({'other_identifier': reg_data['other_identifier']})
        admit_activity_id = api_demo.create_activity(cr, adt_uid, 't4.clinical.adt.patient.admit', None, {}, reg_data)
        api.complete(cr, uid, admit_activity_id)

        admission_activity_id = api.activity_map(cr, uid, 
                                                  data_models=['t4.clinical.patient.admission'],
                                                  creator_ids=[admit_activity_id]).keys()[0]
                        
        placement_activity_id = api.activity_map(cr, uid, 
                                                  data_models=['t4.clinical.patient.placement'],
                                                  creator_ids=[admission_activity_id]).keys()[0]   
        
        api.submit_complete(cr, uid, placement_activity_id, {'location_id': bed_location_id})
             
#         admit_activity_ids = [self.create_activity(cr, adt_uid, 't4.clinical.adt.patient.admit') for i in range(patient_admit_count)]
#         [api.complete(cr, uid, id) for id in admit_activity_ids]
#         temp_bed_ids = [i for i in bed_ids]
#         temp_placement_activity_ids = api.activity_map(cr, uid, 
#                                                   data_models=['t4.clinical.patient.placement'],
#                                                   pos_ids=[pos_id],
#                                                   states=['new', 'scheduled']).keys()
#                                                   
# 
#         
#         #import pdb; pdb.set_trace()
#         for i in range(patient_placement_count):
#             placement_activity_id = fake.random_element(temp_placement_activity_ids)
#             bed_location_id = fake.random_element(temp_bed_ids)
#             api.submit_complete(cr, uid, placement_activity_id, {'location_id': bed_location_id})
#             temp_placement_activity_ids.remove(placement_activity_id)
#             temp_bed_ids.remove(bed_location_id)