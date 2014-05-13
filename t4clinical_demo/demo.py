# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from openerp.addons.t4activity.activity import except_if
import logging        
from pprint import pprint as pp
_logger = logging.getLogger(__name__)

from faker import Faker
fake = Faker()
seed = fake.random_int(min=1000001, max=9999999)
def next_seed():
    global seed
    seed += 1
    return seed

class t4_clinical_spell(orm.Model):
    """
    SPELL Configuration
    """
    _inherit = 't4.clinical.spell'
    
    _defaults = {
         'ews_frequency': 30,
     }
    
    
class demo(orm.AbstractModel):
    _name = 'demo'
    
    def create_ward(self, cr, uid, parent_id):
        fake.seed(next_seed()) 
        code = "W"+str(fake.random_int(min=1000001, max=9999999))
        data = {
                'name': code, 
                'code': code,
                'type': 'poc', 
                'usage': 'ward', 
                'parent_id': parent_id        
               }
        
        location_id = self.pool['t4.clinical.location'].create(cr, uid, data)
        return location_id

    def create_bed(self, cr, uid, parent_id):
        fake.seed(next_seed()) 
        code = "B"+str(fake.random_int(min=1000001, max=9999999))
        data = {
                'name': code, 
                'code': code,
                'type': 'poc', 
                'usage': 'bed', 
                'parent_id': parent_id        
               }
        location_id = self.pool['t4.clinical.location'].create(cr, uid, data)
        return location_id

    def create_pos(self, cr, uid):
        pos_pool = self.pool['t4.clinical.pos']
        location_pool = self.pool['t4.clinical.location']
        fake.seed(next_seed())
        # POS location 
        code = "POS"+str(fake.random_int(min=1, max=9))
        data = {'name': "POS Location (%s)" % code, 'code': code, 'type': 'pos', 'usage': 'hospital'}
        pos_location_id = location_pool.create(cr, uid, data)
        # Admission location
        data = {'name': "Admission Location (%s)" % code, 
                'code': "ADML-%s" % code, 
                'type': 'pos', 'usage': 'hospital', 'parent_id': pos_location_id}
        lot_admission_id = location_pool.create(cr, uid, data)
        # Discharge Location
        data = {'name': "Discharge Location (%s)" % code, 
                'code': "DISL-%s" % code, 
                'type': 'pos', 'usage': 'hospital', 'parent_id': pos_location_id}
        lot_discharge_id = location_pool.create(cr, uid, data)                
        # POS        
        data = {'name': "HOSPITAL"+str(fake.random_int(min=1, max=9)),
                'location_id': pos_location_id,
                'lot_admission_id': lot_admission_id,
                'lot_discharge_id': lot_discharge_id}
        pos_id = pos_pool.create(cr, uid, data)
        return pos_id
    
    def adt_patient_register(self, cr, uid):
        res = {}
        activity_pool = self.pool['t4.activity']
        register_pool = self.pool['t4.clinical.adt.patient.register']
        fake.seed(next_seed()) 
        gender = fake.random_element(array=('M','F'))
        other_identifier = str(fake.random_int(min=1000001, max=9999999))
        dob = fake.date_time_between(start_date="-80y", end_date="-10y").strftime("%Y-%m-%d %H:%M:%S")
        register_activity_id = register_pool.create_activity(cr, uid, {},{})
        register_submit_res = activity_pool.submit(cr, uid, register_activity_id,
                                                   {
                                                    'family_name': fake.last_name(), 
                                                    'given_name': fake.first_name(),
                                                    'other_identifier': other_identifier, 
                                                    'dob': dob, 
                                                    'gender': gender, 
                                                    'sex': gender         
                                                    })
        register_complete_res = activity_pool.complete(cr, uid, register_activity_id)
        res.update({'register_activity_id': register_activity_id})
        res.update(register_submit_res)
        res.update(register_complete_res)
        return res
    
    def adt_patient_update(self, cr, uid, patient_id):
        # FIXME! to be done via adt.patient.update 
        patient_pool = self.pool['t4.clinical.patient']
        fake.seed(next_seed())
        data = {}
        data['street'] = fake.street_address()
        data['street2'] = fake.street_name()
        data['city'] = fake.city()
        data['zip'] = fake.postcode()
        data['mobile'] = fake.phone_number()
        patient_pool.write(cr, uid, patient_id, data)
        return {}
     
    def adt_patient_admit(self, cr, uid, patient_id, suggested_location_ids):
        res = {}
        patient_pool = self.pool['t4.clinical.patient']
        location_pool = self.pool['t4.clinical.location']
        admit_pool = self.pool['t4.clinical.adt.patient.admit']
        activity_pool = self.pool['t4.activity']
        fake.seed(next_seed())
        suggested_location_names = [location.name for location in location_pool.browse(cr, uid, suggested_location_ids)]
        patient = patient_pool.browse(cr, uid, patient_id)
        data = {}
        data['other_identifier'] = patient.other_identifier
        data['code'] = str(fake.random_int(min=10001, max=99999))
        data['location'] = suggested_location_names[fake.random_int(min=0, max=len(suggested_location_ids)-1)]
        data['start_date'] = fake.date_time_between(start_date="-1w", end_date="-1h").strftime("%Y-%m-%d %H:%M:%S")
        admit_activity_id = admit_pool.create_activity(cr, uid, {}, {})
        admit_submit_res = activity_pool.submit(cr, uid, admit_activity_id, data)
        admit_complete_res = activity_pool.complete(cr, uid, admit_activity_id)
        res.update({'admit_activity_id': admit_activity_id})
        res.update(admit_submit_res)
        res.update(admit_complete_res)
        return res
    
    def complete_placement(self, cr, uid, placement_activity_id):
        res = {}
        patient_pool = self.pool['t4.clinical.patient']
        activity_pool = self.pool['t4.activity']
        location_pool = self.pool['t4.clinical.location']
        fake.seed(next_seed())
        placement_activity = activity_pool.browse(cr, uid, placement_activity_id)
        available_bed_location_ids = location_pool.get_available_location_ids(cr, uid, ['bed'])
        bed_location_domain = [['id','in', available_bed_location_ids]]
        suggested_location_id = placement_activity.data_ref.suggested_location_id.id
        if suggested_location_id:
             bed_location_domain.append(['id', 'child_of', suggested_location_id])
        bed_location_ids = location_pool.search(cr, uid, bed_location_domain)
        #import pdb; pdb.set_trace()
        if bed_location_ids:
            location_id = bed_location_ids[fake.random_int(min=0, max=len(bed_location_ids)-1)]
            placement_submit_res = activity_pool.submit(cr, uid, placement_activity.id, 
                                                        {'location_id': location_id,
                                                         'suggested_location_id': suggested_location_id})
            placement_complete_res = activity_pool.complete(cr, uid, placement_activity.id)
            res.update(placement_complete_res)
            res.update(placement_submit_res)
        else:
            _logger.warn("No available beds left. Placement id=%s can't be completed and stays in '%s'" % (placement_activity.id, placement_activity.state))        
        return res

    def complete_ews(self, cr, uid, ews_activity_id):
        res = {}
        data = {}
        activity_pool = self.pool['t4.activity']
        fake.seed(next_seed())
        data = {
                'respiration_rate': fake.random_int(min=10, max=23),
                'indirect_oxymetry_spo2': fake.random_int(min=95, max=100),
                #'oxygen_administration_flag': False,
                'body_temperature': float(fake.random_int(min=36, max=41)),
                'blood_pressure_systolic': fake.random_int(min=115, max=150),
                'blood_pressure_diastolic': fake.random_int(min=60, max=100),
                'pulse_rate': fake.random_int(min=60, max=80),
                'avpu_text': fake.random_element(array=('A','V','P','U'))                         
        }
        ews_submit_res = activity_pool.submit(cr, uid, ews_activity_id, data)
        ews_complete_res = activity_pool.complete(cr, uid, ews_activity_id)
        res.update(ews_submit_res)
        res.update(ews_complete_res)
        return res

    def adt_patient_discharge(self, cr, uid, patient_id):
        res = {}
        activity_pool = self.pool['t4.activity']
        discharge_pool = self.pool['t4.clinical.patient.discharge']
        discharge_activity_id = discharge_pool.create_activity(cr, uid, {}, {'patient_id': patient_id})
        discharge_complete_res = activity_pool.complete(cr, uid, discharge_activity_id)
        res.update(discharge_complete_res)
        return res
    
    def create_adt_user(self, cr, uid, pos_id):
        user_pool = self.pool['res.users']
        imd_pool = self.pool['ir.model.data']
        fake.seed(next_seed())
        adt_group = imd_pool.get_object(cr, uid, "t4clinical_base", "group_t4clinical_adt")   
        name = fake.first_name() 
        data = {
            'name': name,
            'login': name.lower(),
            'password': name.lower(),
            'groups_id': [(4, adt_group.id)],
            'pos_id': pos_id
        }
        user_id = user_pool.create(cr, uid, data)
        return user_id
    
    def create_nurse_user(self, cr, uid, location_ids):
        user_pool = self.pool['res.users']
        imd_pool = self.pool['ir.model.data']
        fake.seed(next_seed())
        nurse_group = imd_pool.get_object(cr, uid, "t4clinical_base", "group_t4clinical_nurse")   
        name = fake.first_name() 
        data = {
            'name': name,
            'login': name.lower(),
            'password': name.lower(),
            'groups_id': [(4, nurse_group.id)],
            'location_ids': [(4,location_id) for location_id in location_ids]
        }
        #import pdb; pdb.set_trace()
        user_id = user_pool.create(cr, uid, data)
        return user_id    
    
    
    def scenario2(self, cr, uid, rollback=True):
        REGISTER_QTY = 10
        ADMIT_QTY = 5
        DISCHARGE_QTY = 3
        EWS_QTY = 3
        WARD_QTY = 1
        BED_QTY = 2
        BED_PER_WARD = 2
        
        api_pool = self.pool['t4.clinical.api']
        ews_pool = self.pool['t4.clinical.patient.observation.ews']
        register_pool = self.pool['t4.clinical.adt.patient.register']
        admit_pool = self.pool['t4.clinical.adt.patient.admit']
        activity_pool = self.pool['t4.activity']
        placement_pool = self.pool['t4.clinical.patient.placement']
        discharge_pool = self.pool['t4.clinical.patient.discharge']
        spell_pool = self.pool['t4.clinical.spell']
        location_pool = self.pool['t4.clinical.location']
        user_pool = self.pool['res.users']    
        patient_pool = self.pool['t4.clinical.patient']
        pos_pool = self.pool['t4.clinical.pos']
        imd_pool = self.pool['ir.model.data']
        adt_user = imd_pool.get_object(cr, uid, "t4clinical_demo", "demo_user_adt_uhg")   
        
        # Create POS
        pos_id = self.create_pos(cr, uid)
        pos = pos_pool.browse(cr, uid, pos_id)
        
        # Create wards
        ward_location_ids = [self.create_ward(cr, uid, pos.location_id.id) for i in range(WARD_QTY)]
        
        # Create beds 
        bed_location_ids = []
        for ward_location_id in ward_location_ids:
            bed_location_ids.extend([self.create_bed(cr, uid, ward_location_id) for i in range(BED_PER_WARD)])
        
        # Create ADT user
        adt_user = user_pool.browse(cr, uid, self.create_adt_user(cr, uid, pos.id))
        
        # Create nurse users
        nurse_user_ids = [
             self.create_nurse_user(cr, uid, ward_location_ids),
             self.create_nurse_user(cr, uid, ward_location_ids)
         ]
              
        # Register Patients
        register_res = [self.adt_patient_register(cr, adt_user.id) for i in range(REGISTER_QTY)]
        patient_ids = [res['patient_id'] for res in register_res]
        
        # Patient Address
        update_res = [self.adt_patient_update(cr, adt_user.id, patient_id) for patient_id in patient_ids]
       
        # Admit Patients
        admit_res = [self.adt_patient_admit(cr, adt_user.id, patient_id, ward_location_ids) for patient_id in patient_ids[:ADMIT_QTY]]
        placement_activity_ids = [res['t4.clinical.patient.placement'] for res in admit_res[:ADMIT_QTY]]
        pp(admit_res)
        
        #Complete Placements
        placement_res = [self.complete_placement(cr, uid, activity_id) for activity_id in placement_activity_ids[:ADMIT_QTY]]
        pp(placement_res)
        
        # EWS
        def ews_ids():
            """ Generator """  
            spell_activity_ids = [a['t4.clinical.spell'] for a in admit_res]
            ews_domain = [['data_model','=','t4.clinical.patient.observation.ews'], 
                          ['state','in',['new','scheduled']],
                          ['parent_id','in',spell_activity_ids]]
            for i in range(1, EWS_QTY): 
                for ews_activity_id in activity_pool.search(cr, uid, ews_domain):
                    yield ews_activity_id
                
        
        ews_res = [self.complete_ews(cr, uid, ews_id) for ews_id in ews_ids()]
            
          

        # Discharge Patients
        discharge_res = [self.adt_patient_discharge(cr, adt_user.id, res['patient_id']) for res in register_res[:DISCHARGE_QTY]]
        pp(discharge_res)

            
        #import pdb; pdb.set_trace()
        except_if(rollback, msg="Rollback")
        
        return True   