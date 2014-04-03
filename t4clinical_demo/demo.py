# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from openerp.addons.t4clinical_base.activity import except_if
import logging        
_logger = logging.getLogger(__name__)

from faker import Faker
fake = Faker()


class t4_clinical_pos(orm.Model):
    """
    POS Configuration
    """
    _inherit = 't4.clinical.pos'
    
    _defaults = {
         'ews_init_frequency': 30,
     }
    
    
class demo(orm.AbstractModel):
    _name = 'demo'
    
    def get_ward_data(self, parent_id=False, qty=5):
        data = []
        n = 0
        while n <= qty:
            code = "W"+str(fake.random_int(min=1000001, max=9999999))
            while code in [d['code'] for d in data]: 
                code = "W"+str(fake.random_int(min=1000001, max=9999999))
            data.append({
                    'name': code, 
                    'code': code,
                    'type': 'poc', 
                    'usage': 'ward', 
                    'parent_id': parent_id        
                   })
            n += 1
        return data

    def get_bed_data(self, ward_ids=[], qty=5):
        data = []
        n = 0
        while n <= qty:
            code = "B"+str(fake.random_int(min=1000001, max=9999999))
            while code in [d['code'] for d in data]: 
                code = "B"+str(fake.random_int(min=1000001, max=9999999))
            parent_id = ward_ids[fake.random_int(min=0, max=len(ward_ids)-1)]
            data.append({
                    'name': code, 
                    'code': code,
                    'type': 'poc', 
                    'usage': 'bed', 
                    'parent_id': parent_id        
                   })
            n += 1
        return data
    
    def get_register_data(self, qty=5):
        data = []
        n = 0
        while n <= qty:
            gender = fake.random_element(array=('M','F'))
            other_identifier = str(fake.random_int(min=1000001, max=9999999))
            while other_identifier in [d['other_identifier'] for d in data]: 
                other_identifier = str(fake.random_int(min=1000001, max=9999999))
            data.append({
                    'family_name': fake.last_name(), 
                    'given_name': fake.first_name(),
                    'other_identifier': other_identifier, 
                    'dob': fake.date_time_between(start_date="-80y", end_date="-10y").strftime("%Y-%m-%d %H:%M:%S"), 
                    'gender': gender, 
                    'sex': gender         
                   })
            n += 1
            
        return data
    
    def get_admit_data(self, register_data=[], qty=5):
        data = []
        n = 0
        for r in register_data:
            if n > qty:
                break
            t = {}
            t.update({'other_identifier':r['other_identifier']})
            t.update({'code': str(fake.random_int(min=10001, max=99999)), 
                      'location': 'W'+fake.random_element(array=('8','9')), 
                      'start_date': fake.date_time_between(start_date="-1w", end_date="-1h").strftime("%Y-%m-%d %H:%M:%S")
                      })
            data.append(t)
            n += 1
        return data
        
    def get_placement_data(self, cr, uid, qty=5):
        data = []
        # must be get_available location_ids(type, usage)
        locations = ['B'+str(n) for n in range(1,8)]
        location_ids = self.pool['t4.clinical.location'].search(cr, uid, [('code','in',locations)])
        n = 0
        for location_id in location_ids:
            if n > qty:
                break
            data.append({'location_id': location_id})
            n += 1
        return data
    
    
    def get_ews_data(self, cr, uid, patient_ids):
        data = []
        # must be get_available location_ids(type, usage)
        locations = ['B'+str(n) for n in range(1,8)]
        location_ids = self.pool['t4.clinical.location'].search(cr, uid, [('code','in',locations)])
        n = 0
        for patient_id in patient_ids:
                data.append({
                            'patient_id': patient_id,
                            'respiration_rate': fake.random_int(min=10, max=23),
                            'indirect_oxymetry_spo2': fake.random_int(min=95, max=100),
                            #'oxygen_administration_flag': False,
                            'body_temperature': float(fake.random_int(min=36, max=41)),
                            'blood_pressure_systolic': fake.random_int(min=115, max=150),
                            'blood_pressure_diastolic': fake.random_int(min=60, max=100),
                            'pulse_rate': fake.random_int(min=60, max=80),
                            'avpu_text': fake.random_element(array=('A','V','P','U'))                         
                         })
        return data   

    
    def scenario1(self, cr, uid, rollback=True):
        register_data = self.get_register_data(10)
        admit_data = self.get_admit_data(register_data, 5)       
        register_pool = self.pool['t4.clinical.adt.patient.register']
        admit_pool = self.pool['t4.clinical.adt.patient.admit']
        activity_pool = self.pool['t4.clinical.activity']
        placement_pool = self.pool['t4.clinical.patient.placement']
        api_pool = self.pool['t4.clinical.api']
 
        
        for rd in register_data:
            register_pool.create_activity(cr, uid, {}, rd)
        for ad in admit_data:
            admit_pool.create_activity(cr, uid, {}, ad)    
        placement_data = self.get_placement_data(cr, uid, qty=5)
        placement_activity_ids = activity_pool.search(cr, uid, [('data_model','=',placement_pool._name)])
        n = 0
        patient_ids = []
        #import pdb; pdb.set_trace()
        for placement_activity_id in placement_activity_ids:
            placement_activity = activity_pool.browse(cr, uid, placement_activity_id)
            patient_ids.append(placement_activity.patient_id.id)
            if n >=len(placement_data):
                break
            activity_pool.submit(cr, uid, placement_activity_id,  placement_data[n])
            activity_pool.start(cr, uid, placement_activity_id) 
            #activity_pool.complete(cr, uid, placement_activity_id) 
            n += 1
        ews_pool = self.pool['t4.clinical.patient.observation.ews']
        for n in range(1,10):
            ews_data = self.get_ews_data(cr, uid, patient_ids)
            for ews in ews_data:
                        # activity frequency
                api_pool.set_activity_trigger(cr, uid, ews['patient_id'],'t4.clinical.patient.observation.ews','minute', 15, context=None)  
                ews_activity_id = ews_pool.create_activity(cr, uid, {}, {'patient_id': ews['patient_id']})
                activity_pool.schedule(cr, uid, ews_activity_id, 
                   date_scheduled=fake.date_time_between(start_date="-1w", end_date="-1h").strftime("%Y-%m-%d %H:%M:%S"))
                activity_pool.submit(cr, uid, ews_activity_id, ews)
                activity_pool.start(cr, uid, ews_activity_id)
                activity_pool.complete(cr, uid, ews_activity_id)
        except_if(rollback, msg="Rollback")
        return True
    
    
    
    def scenario2(self, cr, uid, rollback=True):
        REGISTER_QTY = 10
        ADMIT_QTY = 5
        DISCHARGE_QTY = 3
        EWS_QTY = 3
        WARD_QTY = 1
        BED_QTY = 2
        
        ews_pool = self.pool['t4.clinical.patient.observation.ews']
        register_pool = self.pool['t4.clinical.adt.patient.register']
        admit_pool = self.pool['t4.clinical.adt.patient.admit']
        activity_pool = self.pool['t4.clinical.activity']
        placement_pool = self.pool['t4.clinical.patient.placement']
        discharge_pool = self.pool['t4.clinical.patient.discharge']
        spell_pool = self.pool['t4.clinical.spell']
        location_pool = self.pool['t4.clinical.location']
        user_pool = self.pool['res.users']    
        patient_pool = self.pool['t4.clinical.patient']
        
        pos = self.pool['t4.clinical.pos'].browse(cr, uid, 1) # UHG
        # Create Locations        
        ward_data = self.get_ward_data(pos.location_id.id, WARD_QTY)
        ward_ids = []
        for d in ward_data:
            ward_ids.append(location_pool.create(cr, uid, d))
        
        bed_data = self.get_bed_data(ward_ids, BED_QTY)
        bed_ids = []
        for d in bed_data:
            bed_ids.append(location_pool.create(cr, uid, d))        
        
        # Assign locations to users
        user_ids = user_pool.search(cr, uid, [])#[('login','=','nurse')])
        for user_id in user_ids:
            idx1 = fake.random_int(min=0, max=len(ward_ids)-1)
            idx2 = fake.random_int(min=0, max=len(ward_ids)-1)
            start, end = idx1 <= idx2 and (idx1, idx2) or (idx2, idx1)
            vals = {'location_ids': [[6, False, ward_ids]]} #ward_ids[start: end]
            user_pool.write(cr, uid, user_id, vals)
        
              
        # Register Patients
        register_data = self.get_register_data(REGISTER_QTY)
        for d in register_data:
            register_activity_id = register_pool.create_activity(cr, uid, {}, d)
            activity_pool.complete(cr, uid, register_activity_id)

        # Patient Address
        for patient_id in patient_pool.search(cr, uid, []):
            data = {}    
            data['street'] = fake.street_address()
            data['street2'] = fake.street_name()
            data['city'] = fake.city()
            data['zip'] = fake.postcode()
            data['mobile'] = fake.phone_number()
            patient_pool.write(cr, uid, patient_id, data)
  
        # Admit Patients
        admit_data = self.get_admit_data(register_data, ADMIT_QTY)
        for d in admit_data:
            admit_activity_id = admit_pool.create_activity(cr, uid, {}, d) 
            activity_pool.complete(cr, uid, admit_activity_id)
        
        # Complete Placements
        domain = [['data_model','=','t4.clinical.patient.placement'],['state','in',['draft','scheduled']]]
        placement_activity_ids = activity_pool.search(cr, uid, domain)
        for placement_activity in activity_pool.browse(cr, uid, placement_activity_ids):
            available_bed_location_ids = location_pool.get_available_location_ids(cr, uid, ['bed'])
            only_created_available_beds = list(set(available_bed_location_ids) & set(bed_ids))
            bed_location_ids = location_pool.search(cr, uid, 
                                                    [['id', 'child_of', placement_activity.data_ref.location_id.id],
                                                     ['id','in', only_created_available_beds]])
            if bed_location_ids:
                location_id = bed_location_ids[fake.random_int(min=0, max=len(bed_location_ids)-1)]
                activity_pool.submit(cr, uid, placement_activity.id, {'location_id': location_id})
                activity_pool.complete(cr, uid, placement_activity.id)
                
                
        # EWS loops
        i = 0
        while i < EWS_QTY:
            ews_activity_ids = activity_pool.search(cr, uid,[['data_model','=','t4.clinical.patient.observation.ews'],
                                                             ['state','in',['draft','scheduled']]])
            for ews_activity in activity_pool.browse(cr, uid, ews_activity_ids):
                activity_pool.complete(cr, uid, ews_activity.id)
            i += 1
        
        # Discharge Patients
        spell_ids = spell_pool.search(cr, uid, [('state','=','started')])
        spell_to_discharge_ids = []
        while len(spell_to_discharge_ids)< DISCHARGE_QTY:
           spell_to_discharge_ids.append(spell_ids[fake.random_int(min=0, max=len(spell_ids)-1)])
           spell_to_discharge_ids = list(set(spell_to_discharge_ids))
        
        for spell in spell_pool.browse(cr, uid, spell_to_discharge_ids):
            discharge_activity_id = discharge_pool.create_activity(cr, uid, {}, {'patient_id': spell.patient_id.id})
            activity_pool.complete(cr, uid, discharge_activity_id)
            
            
        except_if(rollback, msg="Rollback")
        return True