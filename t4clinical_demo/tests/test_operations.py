from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.osv import orm, fields, osv




admission_type_data = {'summary': 'Patient Admission', 'data_model': 't4.clinical.patient.admission'}

data_model_data = {'summary': 'Test Type', 'data_model': 'observation.test'}
submit_data = {'val1': 'submit_val1', 'val2': 'submit_val2'}

class TestOperations(common.SingleTransactionCase):
    def setUp(self):
        global cr, uid
        global activity_pool, spell_pool, admission_pool, height_weight_pool, move_pool, discharge_pool
        global user_pool, type_pool, location_pool, patient_pool, ews_pool, api_pool
        global donald_patient_id, w8_location_id, b1_location_id, admission_data, admission_activity_id, discharge_activity_id
        global nurse_user_id, nurse_employee_id
        global now, tomorrow
        
        cr, uid = self.cr, self.uid
        
        now = dt.today().strftime('%Y-%m-%d %H:%M:%S')
        tomorrow = (dt.today() + rd(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                
        activity_pool = self.registry('t4.clinical.activity')
        spell_pool = self.registry('t4.clinical.spell')
        admission_pool = self.registry('t4.clinical.patient.admission')
        move_pool = self.registry('t4.clinical.patient.move')
        height_weight_pool = self.registry('t4.clinical.patient.observation.height_weight')
        ews_pool = self.registry('t4.clinical.patient.observation.ews')
        discharge_pool = self.registry('t4.clinical.patient.discharge')
        user_pool = self.registry('res.users')
        location_pool = self.registry('t4.clinical.location')
        patient_pool = self.registry('t4.clinical.patient')
        api_pool = self.registry('t4.clinical.api')
        
        super(TestOperations, self).setUp()

    def xml2db_id(self, xmlid):
        imd_pool = self.registry('ir.model.data')
        imd_id = imd_pool.search(cr, uid, [('name','=', xmlid)])
        db_id = imd_id and imd_pool.browse(cr, uid, imd_id[0]).res_id or False
        return db_id
    
    def test_operations(self):
        """            
        """
        global cr, uid
        global activity_pool, spell_pool, admission_pool, height_weight_pool, move_pool, discharge_pool
        global user_pool, type_pool, location_pool, patient_pool, ews_pool, api_pool
        global donald_patient_id, w8_location_id, b1_location_id, admission_data, admission_activity_id, discharge_activity_id
        global nurse_user_id, nurse_employee_id
        global now, tomorrow
        
        # ids from demo & base data
        donald_patient_id = self.xml2db_id("demo_patient_donald")
        uhg_location_id = self.xml2db_id("demo_location_uhg")
        uhg_pos_id = self.xml2db_id("demo_pos_uhg")
        w8_location_id = self.xml2db_id("demo_location_w8")
        b1_location_id = self.xml2db_id("demo_location_b1")
        nurse_user_id = self.xml2db_id("demo_user_nurse")
        manager_user_id = self.xml2db_id("demo_user_manager")

        
        
        # activity frequency
        api_pool.set_activity_trigger(cr, uid, donald_patient_id, 
                                   't4.clinical.patient.observation.ews', 
                                   'minute', 15, context=None)        

        nurse_user = user_pool.browse(cr, uid, nurse_user_id)
        # base data tests
        self.assertTrue(w8_location_id in [l.id for l in nurse_user.location_ids], 'w8_location in nurse_user.locations')
        
        w8_location = location_pool.browse(cr, uid, w8_location_id)
        #import pdb; pdb.set_trace()
        self.assertTrue(w8_location.pos_id.id == uhg_pos_id, 'w8_location.pos == uhg_pos')
        
        b1_location = location_pool.browse(cr, uid, b1_location_id)
        self.assertTrue(b1_location.pos_id.id == uhg_pos_id, 'b1_location.pos == uhg_pos')
        
        # admission create
        admission_activity_id = self.create_activity_test(
                                     admission_pool,
                                     activity_vals      = {},
                                     data_vals      = {'location_id': w8_location_id, 'patient_id': donald_patient_id},
                                     patient_id     = donald_patient_id, 
                                     location_id    = w8_location_id, 
                                     user_id        = manager_user_id
                                     )
        
        # admission operations
        activity_pool.assign(cr, uid, admission_activity_id, manager_user_id)   
        activity_pool.start(cr, uid, admission_activity_id)
        activity_pool.complete(cr, uid, admission_activity_id)
        # admission test
        self.admission_complete_test(
                                     admission_activity_id,
                                     patient_id     = donald_patient_id, 
                                     location_id    = w8_location_id, 
                                     user_id        = manager_user_id
                                     )
         
         
        # placement
        placement_activity = activity_pool.browse_domain(cr, uid, 
                             [('parent_id','=',admission_activity_id), ('data_model','=','t4.clinical.patient.placement')])[0]
        activity_pool.start(cr, uid, placement_activity.id)
        #self.assertTrue(b1_location_id in location_pool.get_available_location_ids(cr, uid), 'location in get_available_bed_location_ids()')
        try:
            activity_pool.submit(cr, uid, placement_activity.id,{'location_id': b1_location_id})
        except: # not available
            pass
        else:
            self.assertTrue(b1_location_id not in location_pool.get_available_location_ids(cr, uid), 'location NOT in get_available_bed_location_ids()')
            #import pdb; pdb.set_trace()
            self.assertTrue(donald_patient_id in api_pool.get_not_palced_patient_ids(cr, uid), 'patient in get_not_palced_patient_ids()')
            
            activity_pool.complete(cr, uid, placement_activity.id)
            self.assertTrue(donald_patient_id not in api_pool.get_not_palced_patient_ids(cr, uid), 'patient not in get_not_palced_patient_ids()')
            # test spell has placement location set
            spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, placement_activity.data_ref.patient_id.id)
            spell_activity = activity_pool.browse(cr, uid, spell_activity_id)
            self.assertTrue(spell_activity.data_ref.location_id.id == b1_location_id, 'spell.location == placement.location')
             
            # tests
            #import pdb; pdb.set_trace()
            # placement location currently set to the patient location
            #self.assertTrue(placement_activity.location_id.id == b1_location_id, 'activity.location == b1_location_id')


            admission_activity = activity_pool.browse(cr, uid, admission_activity_id)
            spell_activity_id = admission_activity.parent_id.id
            
            height_weight_activity_id = self.create_activity_test(
                                         height_weight_pool,
                                         activity_vals      = {'parent_id': spell_activity_id},
                                         data_vals      = {'patient_id': donald_patient_id,'height': 180},#'weight': 80},
                                         patient_id     = donald_patient_id, 
                                         location_id    = b1_location_id, #implemented as latest placement location
                                         user_id        = nurse_user_id
                                         )          
            height_weight_activity = activity_pool.browse(cr, uid, height_weight_activity_id)
            # tests PARTIAL
            self.assertTrue(height_weight_activity.data_ref.is_partial, 'partial')
    
    
            # EWS
            #import pdb; pdb.set_trace()
            ews_activity_id = self.create_activity_test(
                                         ews_pool,
                                         activity_vals      = {},
                                         data_vals      = {'patient_id': donald_patient_id},
                                         patient_id     = donald_patient_id, 
                                         location_id    = b1_location_id, # patient placement location
                                         user_id        = nurse_user_id
                                         )        
            activity_pool.start(cr, uid, ews_activity_id)
            activity_pool.complete(cr, uid, ews_activity_id)  
             
            # discharge
            #import pdb; pdb.set_trace()
            discharge_activity_id = self.create_activity_test(
                                         discharge_pool,
                                         activity_vals      = {},
                                         data_vals      = {'patient_id': donald_patient_id},
                                         patient_id     = donald_patient_id, 
                                         location_id    = b1_location_id, # patient placement location
                                         user_id        = manager_user_id
                                         )        
            activity_pool.start(cr, uid, discharge_activity_id)
            activity_pool.complete(cr, uid, discharge_activity_id)



    def create_activity_test(self, data_pool, activity_vals={}, data_vals={}, patient_id=False, location_id=False, user_id=False):
        global cr, uid
        global activity_pool, spell_pool, admission_pool, height_weight_pool, move_pool, discharge_pool
        global user_pool, type_pool, location_pool, patient_pool, ews_pool, api_pool
        global donald_patient_id, w8_location_id, b1_location_id, admission_data, admission_activity_id, discharge_activity_id
        global nurse_user_id, nurse_employee_id
        global now, tomorrow       
#         def print_vars():
#             print "\n"
#             print "activity_create_test vars dump header"
#             print "data_pool: %s" % data_pool
#             print "activity_vals: %s" % activity_vals
#             print "data_vals: %s" % data_vals
#             print "patient_id: %s" % patient_id
#             print "location_id: %s" % location_id            
#             print "user_id: %s" % user_id
#             print "\n"
#         
#         print_vars()
            
            
        activity_id = data_pool.create_activity(cr, uid, activity_vals, data_vals)
        activity = activity_pool.browse(cr, uid, activity_id)
        
        data_domain = []
        data_vals and data_domain.extend([(k,'=',v) for k,v in data_vals.iteritems() if isinstance(v,(int, basestring, float, long))])
        
        activity_domain=[('data_model','=',data_pool._name)]
        patient_id and activity_domain.append(('patient_id','=',patient_id))
        location_id and activity_domain.append(('location_id','=',location_id))      
        user_id and activity_domain.append(('user_id','=',user_id))
        activity_ids = activity_pool.search(cr, uid, [['data_model','=',data_pool._name]])

        print "activity_ids: %s" % activity_ids
        print "activity_domain: %s" % activity_domain
        print "data_domain: %s" % data_domain
        print "user_id: %s" % user_id
        print "activity.location_id: %s" % activity.location_id
        print "location_ids child_of activity.location_id: %s" % location_pool.search(cr, uid, [('id','child_of',activity.location_id.id)])        
        print "activity.patient_id: %s" % activity.patient_id
        print "activity.user_ids: %s" % activity.user_ids
        print "\n"        
        self.assertTrue(activity_id in activity_ids, "activity_id in activity_ids")
        #import pdb; pdb.set_trace()
        user_id and self.assertTrue(user_id in [u.id for u in activity.user_ids], "user in activity.user")
        location_id and self.assertTrue(location_id == activity.location_id.id, 'location == activity.location')
        patient_id and self.assertTrue(patient_id == activity.patient_id.id, 'patient == get.patient')        
             
        return activity_id

    def admission_complete_test(self, admit_activity_id, patient_id=False, location_id=False, user_id=False):
        global cr, uid
        global activity_pool, spell_pool, admission_pool, height_weight_pool, move_pool, discharge_pool
        global user_pool, type_pool, location_pool, patient_pool, ews_pool, api_pool
        global donald_patient_id, w8_location_id, b1_location_id, admission_data, admission_activity_id, discharge_activity_id
        global nurse_user_id, nurse_employee_id
        global now, tomorrow
        
        admission_activity = activity_pool.browse(cr, uid, admission_activity_id)
        spell_activity = activity_pool.browse(cr, uid, admission_activity.parent_id.id)
        child_Activities = {activity.data_model: activity for activity in activity_pool.browse_domain(cr, uid, [('id','child_of',admission_activity.id)])}
        move_activity = child_Activities['t4.clinical.patient.move']
        placement_activity = child_Activities['t4.clinical.patient.placement'] 
        
        self.assertTrue(admission_activity.data_model == "t4.clinical.patient.admission", "admission_activity.data_model == admission")
        self.assertTrue(admission_activity.state == "completed", "admission_activity.state == completed")
        self.assertTrue(spell_activity.data_model == "t4.clinical.spell", "spell_activity.data_model == spell")
        self.assertTrue(spell_activity.state == "started", "spell_activity.state == started")
        self.assertTrue(move_activity.state == "completed", "move_activity.state == completed")
        self.assertTrue(placement_activity.state == "draft", "placement_activity.state == draft")
        if patient_id:
            self.assertTrue(patient_id == admission_activity.patient_id.id, 'patient == admission.patient') 
            #import pdb; pdb.set_trace()
            self.assertTrue(patient_id == spell_activity.patient_id.id, 'patient == spell.patient') 
            self.assertTrue(patient_id == move_activity.patient_id.id, 'patient == move.patient')
            self.assertTrue(patient_id == placement_activity.patient_id.id, 'patient == placement.patient')
        if location_id:
            self.assertTrue(location_id == admission_activity.location_id.id, 'location == admission.location')
            self.assertTrue(spell_activity.location_id.id, 'spell.location') 
            self.assertTrue(location_id == move_activity.location_id.id, 'location == move.location')
            self.assertTrue(placement_activity.location_id.id, 'placement.location')   
        if user_id:
            self.assertTrue(user_id in [u.id for u in admission_activity.user_ids], 'user in admission.users') 
            self.assertTrue([u.id for u in spell_activity.user_ids], 'spell.users') 
            self.assertTrue(user_id in [u.id for u in move_activity.user_ids], 'user in move.users')
            self.assertTrue([u.id for u in placement_activity.user_ids], 'placement.users')     
        if user_id:
            self.assertTrue(admission_activity.user_id.id == user_id, 'admission.user == user')