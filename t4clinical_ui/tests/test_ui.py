from openerp.tests.common import SingleTransactionCase
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
#from openerp.addons.t4clinical_activity_types.tests.test_scenario import ActivityTypesTest
from pprint import pprint as pp
from faker import Faker
fake = Faker()
seed = fake.random_int(min=0, max=9999999)
def next_seed():
    global seed
    seed += 1
    return seed

class test_ui_data(SingleTransactionCase):

    def setUp(self):
        super(test_ui_data, self).setUp()

        #self.activity_pool = self.registry('t4.activity')

#     def test_workload(self):
#         #return
#         cr, uid = self.cr, self.uid
#         data = [
#             {'name': '46-', 'date_scheduled': (dt.today()+rd(minutes=48)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 10},
#             {'name': '45-30', 'date_scheduled': (dt.today()+rd(minutes=38)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 20},
#             {'name': '30-15', 'date_scheduled': (dt.today()+rd(minutes=18)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 30},
#             {'name': '15-0', 'date_scheduled': (dt.today()+rd(minutes=8)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 40},
#             {'name': '1-15', 'date_scheduled': (dt.today()-rd(minutes=8)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 50},
#             {'name': '16+', 'date_scheduled': (dt.today()-rd(minutes=18)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 60},
#         ]
#         #create activities
#         pos_env = self.create_pos_environment()
#         register_pool = self.registry('t4.clinical.adt.patient.register')
#         [d.update({'id': register_pool.create_activity(cr, pos_env['adt_user_id'], {'summary': d['name']}, self.data_patient())}) for d in data]
# 
#         #tests
#         activity_pool = self.registry('t4.activity')
#         activity_workload_pool = self.registry('t4.activity.workload')
#         for d in data:
#             activity_pool.schedule(cr, uid, d['id'], d['date_scheduled'])
#             activity_workload = activity_workload_pool.browse(cr, uid, d['id'])
#             print "expected: ", d['expected_value'], "  actual: ", activity_workload.proximity_interval, \
#                   "date_scheduled: ", activity_workload.date_scheduled
#             self.assertTrue(activity_workload.proximity_interval == d['expected_value'], 
#                             "workload_interval expected to be %s but is %s" 
#                             % (str(d['expected_value']), str(activity_workload.proximity_interval)))


    def test_wardboard_data(self):
        return
        cr, uid = self.cr, self.uid
        wardboard_model = self.registry('t4.clinical.wardboard')
        env_model = self.registry('t4.clinical.demo.env')
        api = self.registry('t4.clinical.api')
        config = {
            'bed_qty': 3,
            'patient_qty': 2,
        }
        #import pdb; pdb.set_trace()

        env_id = env_model.create(cr, uid, config)        
        env = env_model.browse(cr, uid, env_id)#env_model.build(cr, uid, env_id)  

        # patient data test
        patient_ids = wardboard_model.search(cr, uid, [['pos_id','=',env.pos_id.id]])
        assert len(patient_ids) == config['patient_qty'], "Wrong patient_qty in the POS: %s" % len(patient_ids)
        patients = api.patient_map(cr, uid, parent_location_ids=[env.pos_id.location_id.id])
        wardboard_ids = wardboard_model.search(cr, uid, [['patient_id','in',patients.keys()]])
        wardboards = wardboard_model.browse(cr, uid, wardboard_ids, [])
        print "================ PATIENT DATA =================="
        for wardboard in wardboards:
            patient = patients[wardboard.patient_id.id]
            pp(patient)
            assert patient['given_name'] or False == wardboard.patient_id.given_name
            assert patient['family_name'] or False == wardboard.patient_id.family_name
            assert patient['middle_names'] or False == wardboard.patient_id.middle_names, "wardboard: %s, patient: %s" % (patient['middle_names'], wardboard.patient_id.middle_names)
            assert patient['other_identifier'] or False == wardboard.patient_id.other_identifier
            assert patient['gender'] or False == wardboard.patient_id.gender
            assert patient['dob'] or False == wardboard.patient_id.dob
            assert patient['location_id'] or False == wardboard.location_id.id
            assert wardboard.ward_id.id in patient['parent_location_ids']
            assert patient['spell_activity_id'] == wardboard.spell_activity_id.id
            assert patient['pos_id'] == wardboard.pos_id.id
            assert patient['age'] == wardboard.age
            # TODO previous_spell_ids
        
        # EWS       
        
        data = [
            {'CASE': 0, 'PR': 65, 'RISK': 'None', 'RR': 18, 'O2_flag': 0, 'BT': 37.5, 'BPS': 120, 'SCORE': 0, 'AVPU': 'A', 'O2': 99, 'BPD': 80} ,
            {'CASE': 1, 'PR': 55, 'RISK': 'Low', 'RR': 11, 'O2_flag': 0, 'BT': 36.5, 'BPS': 115, 'SCORE': 1, 'AVPU': 'A', 'O2': 97, 'BPD': 70} ,
            {'CASE': 1, 'PR': 55, 'RISK': 'Low', 'RR': 11, 'O2_flag': 0, 'BT': 36.5, 'BPS': 115, 'SCORE': 2, 'AVPU': 'A', 'O2': 95, 'BPD': 70} ,
            {'CASE': 1, 'PR': 55, 'RISK': 'Low', 'RR': 11, 'O2_flag': 0, 'BT': 36.0, 'BPS': 115, 'SCORE': 3, 'AVPU': 'A', 'O2': 95, 'BPD': 70} ,
            {'CASE': 1, 'PR': 55, 'RISK': 'Low', 'RR': 11, 'O2_flag': 0, 'BT': 36.0, 'BPS': 110, 'SCORE': 4, 'AVPU': 'A', 'O2': 95, 'BPD': 70} ,
            {'CASE': 2, 'PR': 50, 'RISK': 'Medium', 'RR': 11, 'O2_flag': 0, 'BT': 36.0, 'BPS': 110, 'SCORE': 5, 'AVPU': 'A', 'O2': 95, 'BPD': 70} ,
            {'CASE': 2, 'PR': 110, 'RISK': 'Medium', 'RR': 24, 'O2_flag': 0, 'BT': 38.5, 'BPS': 110, 'SCORE': 6, 'AVPU': 'A', 'O2': 95, 'BPD': 70} ,
            {'CASE': 3, 'PR': 50, 'RISK': 'High', 'RR': 24, 'O2_flag': 0, 'BT': 38.5, 'BPS': 110, 'SCORE': 7, 'AVPU': 'A', 'O2': 93, 'BPD': 70} ,
            {'CASE': 3, 'PR': 50, 'RISK': 'High', 'RR': 24, 'O2_flag': 0, 'BT': 38.5, 'BPS': 100, 'SCORE': 8, 'AVPU': 'A', 'O2': 93, 'BPD': 70} ,
            {'CASE': 3, 'PR': 130, 'RISK': 'High', 'RR': 24, 'O2_flag': 0, 'BT': 38.5, 'BPS': 100, 'SCORE': 9, 'AVPU': 'A', 'O2': 93, 'BPD': 70} ,
            {'CASE': 3, 'PR': 130, 'RISK': 'High', 'RR': 25, 'O2_flag': 0, 'BT': 38.5, 'BPS': 100, 'SCORE': 10, 'AVPU': 'A', 'O2': 93, 'BPD': 70} ,
            {'CASE': 3, 'PR': 130, 'RISK': 'High', 'RR': 25, 'O2_flag': 0, 'BT': 35.5, 'BPS': 100, 'SCORE': 11, 'AVPU': 'A', 'O2': 91, 'BPD': 70} ,
            {'CASE': 3, 'PR': 130, 'RISK': 'High', 'RR': 25, 'O2_flag': 0, 'BT': 39.5, 'BPS': 100, 'SCORE': 12, 'AVPU': 'A', 'O2': 91, 'BPD': 70} ,
            {'CASE': 3, 'PR': 130, 'RISK': 'High', 'RR': 25, 'O2_flag': 0, 'BT': 35.0, 'BPS': 100, 'SCORE': 13, 'AVPU': 'A', 'O2': 91, 'BPD': 70} ,
            {'CASE': 3, 'PR': 130, 'RISK': 'High', 'RR': 25, 'O2_flag': 0, 'BT': 35.0, 'BPS': 90, 'SCORE': 14, 'AVPU': 'A', 'O2': 91, 'BPD': 70} ,
            {'CASE': 3, 'PR': 135, 'RISK': 'High', 'RR': 25, 'O2_flag': 0, 'BT': 35.0, 'BPS': 220, 'SCORE': 15, 'AVPU': 'A', 'O2': 91, 'BPD': 70} ,
            {'CASE': 3, 'PR': 135, 'RISK': 'High', 'RR': 24, 'O2_flag': 1, 'BT': 35.0, 'BPS': 220, 'SCORE': 16, 'AVPU': 'A', 'O2': 91, 'BPD': 70} ,
            {'CASE': 3, 'PR': 135, 'RISK': 'High', 'RR': 25, 'O2_flag': 1, 'BT': 35.0, 'BPS': 220, 'SCORE': 17, 'AVPU': 'A', 'O2': 91, 'BPD': 70} ,
            {'CASE': 2, 'PR': 65, 'RISK': 'Medium', 'RR': 18, 'O2_flag': 0, 'BT': 37.5, 'BPS': 120, 'SCORE': 3, 'AVPU': 'V', 'O2': 99, 'BPD': 80} ,
            {'CASE': 2, 'PR': 65, 'RISK': 'Medium', 'RR': 11, 'O2_flag': 0, 'BT': 37.5, 'BPS': 120, 'SCORE': 4, 'AVPU': 'P', 'O2': 99, 'BPD': 80} ,
            {'CASE': 3, 'PR': 135, 'RISK': 'High', 'RR': 25, 'O2_flag': 1, 'BT': 35.0, 'BPS': 220, 'SCORE': 20, 'AVPU': 'U', 'O2': 91, 'BPD': 70}
        ]
        
        data_field_map = {
             'AVPU': 'avpu_text',
             'BPD': 'blood_pressure_diastolic',
             'BPS': 'blood_pressure_systolic',
             'BT': 'body_temperature',
             'O2': 'indirect_oxymetry_spo2',
             'O2_flag': 'oxygen_administration_flag',
             'PR': 'pulse_rate',
             'RR': 'respiration_rate'
        }
        case_count = 5
        print "================ EWS DATA =================="
        nurse_user_id = api.user_map(cr,uid, group_xmlids=['group_t4clinical_nurse']).keys()[0]
        for patient_id in patients.keys():
            print "patient_id: %s" % patient_id
            mrsa_activity = api.create_complete(cr, uid, 't4.clinical.patient.mrsa', 
                                                {}, {'patient_id': patient_id, 'mrsa': fake.random_element([True, False])})
            diabetes_activity = api.create_complete(cr, uid, 't4.clinical.patient.diabetes', 
                                                {}, {'patient_id': patient_id, 'deabetes': fake.random_element([True, False])})
            pbpm_activity = api.create_complete(cr, uid, 't4.clinical.patient.pbp_monitoring', 
                                                {}, {'patient_id': patient_id, 'pbp_monitoring': fake.random_element([True, False])})
            weightm_activity = api.create_complete(cr, uid, 't4.clinical.patient.weight_monitoring', 
                                                {}, {'patient_id': patient_id, 'weight_monitoring': fake.random_element([True, False])})
            height_activity = api.create_complete(cr, uid, 't4.clinical.patient.observation.height', 
                                                {}, {'patient_id': patient_id, 'height': fake.random_int(120, 220)})
            o2level_ids = self.registry('t4.clinical.o2level').search(cr, uid, [])
            o2target_activity = api.create_complete(cr, uid, 't4.clinical.patient.o2target', 
                                                {}, {'patient_id': patient_id, 
                                                     'level_id': fake.random_element(o2level_ids)})
            
            previous_result = None
            for i in range(case_count): 
                case = fake.random_element(data)
                activities = api.activity_map(cr, uid, patient_ids=[patient_id],
                                                data_models=['t4.clinical.patient.observation.ews'],
                                                pos_ids=[env.pos_id.id],
                                                states=['new', 'scheduled'])
                assert len(activities) == 1, "More than 1 or None ews activities open!"
                activity_id = activities.keys()[0]
                ews_data = {v: case[k] for k, v in data_field_map.items()}
                api.assign(cr, uid, activity_id, nurse_user_id)
                activity = api.submit_complete(cr, nurse_user_id, activity_id, ews_data)
                print "score: %s" % activity.data_ref.score
                
                wardboard_ids = wardboard_model.search(cr, uid, [['id','=',patient_id],['pos_id','=',env.pos_id.id]])
                assert len(wardboard_ids) == 1
                wardboard = wardboard_model.browse(cr, uid, wardboard_ids[0])
                assert wardboard.clinical_risk == activity.data_ref.clinical_risk,\
                    "wardboard.clinical_risk: %s, activity.data_ref.clinical_risk: %s"\
                    %(wardboard.clinical_risk, activity.data_ref.clinical_risk)
                assert wardboard.clinical_risk == case['RISK'], "wardboard.clinical_risk: %s, case['RISK']: %s"\
                    % (wardboard.clinical_risk, case['RISK'])    
                # trend             
                if not previous_result:
                    assert wardboard.ews_trend_string == 'first'
                    
                else:
                    this_ews_trend = activity.data_ref.score - previous_result['score']
                    this_ews_trend_string = ((this_ews_trend < 0 and 'up') 
                                             or (this_ews_trend > 0 and 'down')
                                             or (this_ews_trend == 0 and 'same'))
                    assert wardboard.ews_trend == this_ews_trend,\
                        "wardboard.ews_trend: %s, activity.data_ref.score: %s, previous_result['score']: %s"\
                        % (wardboard.ews_trend, activity.data_ref.score, previous_result['score'])
                    assert wardboard.ews_trend_string == this_ews_trend_string,\
                        "wardboard.ews_trend_string: %s, this_ews_trend_string: %s"\
                        %(wardboard.ews_trend_string, this_ews_trend_string)
                previous_result = {'score':activity.data_ref.score}
            # other obs
            mrsa_activity_map = api.activity_rank_map(cr, uid, 
                                                        partition_by="patient_id, data_model, state", 
                                                        partition_order="sequence desc",
                                                        ranks=[1], pos_ids=[env.pos_id.id], 
                                                        patient_ids=[patient_id],
                                                        data_models=['t4.clinical.patient.mrsa'], 
                                                        states=['completed']
                                                      )
            print "create_complete mrsa_activity: %s" % mrsa_activity
            print "mrsa_activity_map: %s" % mrsa_activity_map         
            assert wardboard.mrsa == mrsa_activity.data_ref.mrsa and 'yes' or 'no'
            assert wardboard.diabetes == diabetes_activity.data_ref.diabetes and 'yes' or 'no'
            assert wardboard.pbp_monitoring == pbpm_activity.data_ref.pbp_monitoring and 'yes' or 'no'  
            assert wardboard.weight_monitoring == weightm_activity.data_ref.weight_monitoring and 'yes' or 'no' 
            assert wardboard.height == height_activity.data_ref.height
            assert wardboard.o2target.id == o2target_activity.data_ref.level_id.id