from openerp.tests.common import SingleTransactionCase
from openerp import SUPERUSER_ID
from pprint import pprint as pp
from faker import Faker
fake = Faker()
seed = fake.random_int(min=0, max=9999999)
def next_seed():
    global seed
    seed += 1
    return seed

class test_ui_data(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(test_ui_data, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        cls.apidemo = cls.registry('nh.clinical.api.demo')
        cls.apidemo.build_unit_test_env(cr, uid, context='eobs')

    def test_wardboard_data(self):
        #return
        cr, uid = self.cr, self.uid
        wardboard_model = self.registry('nh.clinical.wardboard')
        api = self.registry('nh.clinical.api')
        location = self.registry('nh.clinical.location')
        ews_pool = self.registry('nh.clinical.patient.observation.ews')

        # patient data test
        location_id = location.search(cr, uid, [['code', '=', 'U']])
        wu = location.browse(cr, uid, location_id[0])
        patients = api.patient_map(cr, uid, parent_location_ids=[wu.parent_id.id])
        wardboard_ids = wardboard_model.search(cr, uid, [['patient_id', 'in', patients.keys()]])
        wardboards = wardboard_model.browse(cr, uid, wardboard_ids, [])
        for wardboard in wardboards:
            patient = patients[wardboard.patient_id.id]
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

        # EWS       
        
        data = [
            {'CASE': 0, 'PR': 65, 'RISK': 'None', 'RR': 18, 'O2_flag': 0, 'BT': 37.5, 'BPS': 120, 'SCORE': 0, 'AVPU': 'A', 'O2': 99, 'BPD': 80},
            {'CASE': 1, 'PR': 55, 'RISK': 'Low', 'RR': 11, 'O2_flag': 0, 'BT': 36.5, 'BPS': 115, 'SCORE': 1, 'AVPU': 'A', 'O2': 97, 'BPD': 70},
            {'CASE': 1, 'PR': 55, 'RISK': 'Low', 'RR': 11, 'O2_flag': 0, 'BT': 36.5, 'BPS': 115, 'SCORE': 2, 'AVPU': 'A', 'O2': 95, 'BPD': 70},
            {'CASE': 1, 'PR': 55, 'RISK': 'Low', 'RR': 11, 'O2_flag': 0, 'BT': 36.0, 'BPS': 115, 'SCORE': 3, 'AVPU': 'A', 'O2': 95, 'BPD': 70},
            {'CASE': 1, 'PR': 55, 'RISK': 'Low', 'RR': 11, 'O2_flag': 0, 'BT': 36.0, 'BPS': 110, 'SCORE': 4, 'AVPU': 'A', 'O2': 95, 'BPD': 70},
            {'CASE': 2, 'PR': 50, 'RISK': 'Medium', 'RR': 11, 'O2_flag': 0, 'BT': 36.0, 'BPS': 110, 'SCORE': 5, 'AVPU': 'A', 'O2': 95, 'BPD': 70},
            {'CASE': 2, 'PR': 110, 'RISK': 'Medium', 'RR': 24, 'O2_flag': 0, 'BT': 38.5, 'BPS': 110, 'SCORE': 6, 'AVPU': 'A', 'O2': 95, 'BPD': 70},
            {'CASE': 3, 'PR': 50, 'RISK': 'High', 'RR': 24, 'O2_flag': 0, 'BT': 38.5, 'BPS': 110, 'SCORE': 7, 'AVPU': 'A', 'O2': 93, 'BPD': 70},
            {'CASE': 3, 'PR': 50, 'RISK': 'High', 'RR': 24, 'O2_flag': 0, 'BT': 38.5, 'BPS': 100, 'SCORE': 8, 'AVPU': 'A', 'O2': 93, 'BPD': 70},
            {'CASE': 3, 'PR': 130, 'RISK': 'High', 'RR': 24, 'O2_flag': 0, 'BT': 38.5, 'BPS': 100, 'SCORE': 9, 'AVPU': 'A', 'O2': 93, 'BPD': 70},
            {'CASE': 3, 'PR': 130, 'RISK': 'High', 'RR': 25, 'O2_flag': 0, 'BT': 38.5, 'BPS': 100, 'SCORE': 10, 'AVPU': 'A', 'O2': 93, 'BPD': 70},
            {'CASE': 3, 'PR': 130, 'RISK': 'High', 'RR': 25, 'O2_flag': 0, 'BT': 35.5, 'BPS': 100, 'SCORE': 11, 'AVPU': 'A', 'O2': 91, 'BPD': 70},
            {'CASE': 3, 'PR': 130, 'RISK': 'High', 'RR': 25, 'O2_flag': 0, 'BT': 39.5, 'BPS': 100, 'SCORE': 12, 'AVPU': 'A', 'O2': 91, 'BPD': 70},
            {'CASE': 3, 'PR': 130, 'RISK': 'High', 'RR': 25, 'O2_flag': 0, 'BT': 35.0, 'BPS': 100, 'SCORE': 13, 'AVPU': 'A', 'O2': 91, 'BPD': 70},
            {'CASE': 3, 'PR': 130, 'RISK': 'High', 'RR': 25, 'O2_flag': 0, 'BT': 35.0, 'BPS': 90, 'SCORE': 14, 'AVPU': 'A', 'O2': 91, 'BPD': 70},
            {'CASE': 3, 'PR': 135, 'RISK': 'High', 'RR': 25, 'O2_flag': 0, 'BT': 35.0, 'BPS': 220, 'SCORE': 15, 'AVPU': 'A', 'O2': 91, 'BPD': 70},
            {'CASE': 3, 'PR': 135, 'RISK': 'High', 'RR': 24, 'O2_flag': 1, 'BT': 35.0, 'BPS': 220, 'SCORE': 16, 'AVPU': 'A', 'O2': 91, 'BPD': 70},
            {'CASE': 3, 'PR': 135, 'RISK': 'High', 'RR': 25, 'O2_flag': 1, 'BT': 35.0, 'BPS': 220, 'SCORE': 17, 'AVPU': 'A', 'O2': 91, 'BPD': 70},
            {'CASE': 2, 'PR': 65, 'RISK': 'Medium', 'RR': 18, 'O2_flag': 0, 'BT': 37.5, 'BPS': 120, 'SCORE': 3, 'AVPU': 'V', 'O2': 99, 'BPD': 80},
            {'CASE': 2, 'PR': 65, 'RISK': 'Medium', 'RR': 11, 'O2_flag': 0, 'BT': 37.5, 'BPS': 120, 'SCORE': 4, 'AVPU': 'P', 'O2': 99, 'BPD': 80},
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
        nurse_user_id = api.user_map(cr, uid, group_xmlids=['group_nhc_nurse']).keys()[0]
        for patient_id in patients.keys():
            mrsa_activity = api.create_complete(cr, uid, 'nh.clinical.patient.mrsa',
                                                {}, {'patient_id': patient_id, 'mrsa': fake.random_element([True, False])})
            diabetes_activity = api.create_complete(cr, uid, 'nh.clinical.patient.diabetes', 
                                                {}, {'patient_id': patient_id, 'diabetes': fake.random_element([True, False])})
            pbpm_activity = api.create_complete(cr, uid, 'nh.clinical.patient.pbp_monitoring', 
                                                {}, {'patient_id': patient_id, 'pbp_monitoring': fake.random_element([True, False])})
            weightm_activity = api.create_complete(cr, uid, 'nh.clinical.patient.weight_monitoring', 
                                                {}, {'patient_id': patient_id, 'weight_monitoring': fake.random_element([True, False])})
            height_activity = api.create_complete(cr, uid, 'nh.clinical.patient.observation.height', 
                                                {}, {'patient_id': patient_id, 'height': fake.random_int(120, 220)})
            o2level_ids = self.registry('nh.clinical.o2level').search(cr, uid, [])
            if o2level_ids:
                o2target_activity = api.create_complete(cr, uid, 'nh.clinical.patient.o2target', 
                                                {}, {'patient_id': patient_id, 
                                                     'level_id': fake.random_element(o2level_ids)})
            
            previous_result = None
            for i in range(case_count): 
                case = fake.random_element(data)
                activities = api.activity_map(cr, uid, patient_ids=[patient_id],
                                              data_models=['nh.clinical.patient.observation.ews'],
                                              pos_ids=[wu.parent_id.pos_id.id],
                                              states=['new', 'scheduled'])
                if len(activities) < 1:
                    continue
                assert len(activities) == 1, "More than 1 ews activities open!"
                activity_id = activities.keys()[0]
                ews_data = {v: case[k] for k, v in data_field_map.items()}
                api.assign(cr, uid, activity_id, nurse_user_id)
                activity = api.submit_complete(cr, nurse_user_id, activity_id, ews_data)
                print "score: %s" % activity.data_ref.score
                
                wardboard_ids = wardboard_model.search(cr, SUPERUSER_ID, [['patient_id', '=', patient_id], ['pos_id', '=', wu.parent_id.pos_id.id]])
                assert len(wardboard_ids) == 1
                wardboard = wardboard_model.read(cr, SUPERUSER_ID, wardboard_ids[0], ['clinical_risk', 'ews_trend', 'ews_trend_string', 'ews_ids'])

                assert wardboard['clinical_risk'] == activity.data_ref.clinical_risk,\
                    "wardboard.clinical_risk: %s, activity.data_ref.clinical_risk: %s"\
                    %(wardboard['clinical_risk'], activity.data_ref.clinical_risk)
                assert wardboard['clinical_risk'] == case['RISK'], "wardboard.clinical_risk: %s, case['RISK']: %s"\
                    % (wardboard['clinical_risk'], case['RISK'])
                if len(wardboard['ews_ids']) == 1:
                    assert wardboard['ews_trend_string'] == 'first'
                elif not previous_result:
                    previous_result = {'score': ews_pool.read(cr, uid, wardboard['ews_ids'][-2], ['score'])['score']}
                else:
                    this_ews_trend = activity.data_ref.score - previous_result['score']
                    this_ews_trend_string = ((this_ews_trend > 0 and 'up')
                                             or (this_ews_trend < 0 and 'down')
                                             or (this_ews_trend == 0 and 'same'))
                    assert wardboard['ews_trend'] == this_ews_trend,\
                        "wardboard.ews_trend: %s, activity.data_ref.score: %s, previous_result['score']: %s"\
                        % (wardboard['ews_trend'], activity.data_ref.score, previous_result['score'])
                    assert wardboard['ews_trend_string'] == this_ews_trend_string,\
                        "wardboard.ews_trend_string: %s, this_ews_trend_string: %s"\
                        %(wardboard['ews_trend_string'], this_ews_trend_string)
                previous_result = {'score': activity.data_ref.score}
                ews_ids = wardboard['ews_ids']
                
                assert activity.data_ref.id in ews_ids, "ews.data_ref.id not in wardboard.ews_ids: id = %s, ews_ids = %s" % (activity.data_ref.id, ews_ids)
            # other obs
            wardboard = wardboard_model.read(cr, SUPERUSER_ID, wardboard_ids[0], ['height', 'mrsa', 'diabetes', 'pbp_monitoring', 'weight_monitoring'])
            assert wardboard['mrsa'] == mrsa_activity.data_ref.mrsa and 'yes' or 'no'
            assert wardboard['diabetes'] == diabetes_activity.data_ref.diabetes and 'yes' or 'no'
            assert wardboard['pbp_monitoring'] == pbpm_activity.data_ref.pbp_monitoring and 'yes' or 'no'
            assert wardboard['weight_monitoring'] == weightm_activity.data_ref.weight_monitoring and 'yes' or 'no'
