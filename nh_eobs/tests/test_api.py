from openerp.tests.common import SingleTransactionCase
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf

from faker import Faker

fake = Faker()


class TestAPI(SingleTransactionCase):
    
    @classmethod
    def setUpClass(cls):
        super(TestAPI, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        
        cls.users_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.partner_pool = cls.registry('res.partner')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.extapi = cls.registry('nh.eobs.api')
        cls.apidemo = cls.registry('nh.clinical.api.demo')
        cls.follow_pool = cls.registry('nh.clinical.patient.follow')
        cls.unfollow_pool = cls.registry('nh.clinical.patient.unfollow')

        cls.apidemo.build_unit_test_env(cr, uid, bed_count=4, context='eobs')

        cls.wu_id = cls.location_pool.search(cr, uid, [('code', '=', 'U')])[0]
        cls.wt_id = cls.location_pool.search(cr, uid, [('code', '=', 'T')])[0]
        cls.pos_id = cls.location_pool.read(cr, uid, cls.wu_id, ['pos_id'])['pos_id'][0]
        cls.pos_location_id = cls.pos_pool.read(cr, uid, cls.pos_id, ['location_id'])['location_id'][0]

        cls.wmu_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMU')])[0]
        cls.wmt_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMT')])[0]
        cls.nu_id = cls.users_pool.search(cr, uid, [('login', '=', 'NU')])[0]
        cls.nt_id = cls.users_pool.search(cr, uid, [('login', '=', 'NT')])[0]
        cls.hu_id = cls.users_pool.search(cr, uid, [('login', '=', 'HU')])[0]
        cls.ht_id = cls.users_pool.search(cr, uid, [('login', '=', 'HT')])[0]
        cls.adt_id = cls.users_pool.search(cr, uid, [('groups_id.name', 'in', ['NH Clinical ADT Group']), ('pos_id', '=', cls.pos_id)])[0]

    def test_01_check_activity_access(self):
        cr, uid = self.cr, self.uid

        u_activity_ids = self.activity_pool.search(cr, uid, [('state', 'not in', ['completed', 'cancelled']), ('location_id', 'child_of', self.wu_id), ('location_id.usage', '=', 'bed')])
        t_activity_ids = self.activity_pool.search(cr, uid, [('state', 'not in', ['completed', 'cancelled']), ('location_id', 'child_of', self.wt_id), ('location_id.usage', '=', 'bed')])

        for u_act_id in u_activity_ids:
            self.assertTrue(self.extapi.check_activity_access(cr, self.nu_id, u_act_id), msg='Nurse U should have access to Ward U Activities')
            self.assertFalse(self.extapi.check_activity_access(cr, self.nt_id, u_act_id), msg='Nurse T should not have access to Ward U Activities')

        for t_act_id in t_activity_ids:
            self.assertTrue(self.extapi.check_activity_access(cr, self.nt_id, t_act_id), msg='Nurse T should have access to Ward T Activities')
            self.assertFalse(self.extapi.check_activity_access(cr, self.nu_id, t_act_id), msg='Nurse U should not have access to Ward T Activities')

    def test_02_get_activities(self):
        cr, uid = self.cr, self.uid

        u_activity_ids = self.activity_pool.search(cr, uid, [('state', 'not in', ['completed', 'cancelled']), ('location_id', 'child_of', self.wu_id), ('location_id.usage', '=', 'bed')])
        t_activity_ids = self.activity_pool.search(cr, uid, [('state', 'not in', ['completed', 'cancelled']), ('location_id', 'child_of', self.wt_id), ('location_id.usage', '=', 'bed')])

        u_api_activities = self.extapi.get_activities(cr, self.nu_id, [])
        t_api_activities = self.extapi.get_activities(cr, self.nt_id, [])

        for a in u_api_activities:
            self.assertTrue(a['id'] in u_activity_ids, msg='Get activities returned an activity the Nurse is not responsible for')
        for a in t_api_activities:
            self.assertTrue(a['id'] in t_activity_ids, msg='Get activities returned an activity the Nurse is not responsible for')

        patient_id = u_api_activities[0]['patient_id']
        follow_activity_id = self.follow_pool.create_activity(cr, uid, {'user_id': self.nt_id}, {'patient_ids': [[4, patient_id]]})
        self.activity_pool.complete(cr, uid, follow_activity_id)
        t_api_activities = self.extapi.get_activities(cr, self.nt_id, [])
        self.assertTrue(patient_id in [a['patient_id'] for a in t_api_activities], msg="Get activities not returning followed patient activities")

        unfollow_activity_id = self.unfollow_pool.create_activity(cr, uid, {}, {'patient_ids': [[4, patient_id]]})
        self.activity_pool.complete(cr, uid, unfollow_activity_id)
        t_api_activities = self.extapi.get_activities(cr, self.nt_id, [])
        self.assertTrue(patient_id not in [a['patient_id'] for a in t_api_activities], msg="Get activities not returning followed patient activities")

    def test_03_cancel_activity(self):
        cr, uid = self.cr, self.uid

        u_activity_ids = self.activity_pool.search(cr, uid, [('state', 'not in', ['completed', 'cancelled']), ('location_id', 'child_of', self.wu_id), ('location_id.usage', '=', 'bed')])

        self.extapi.cancel(cr, self.nu_id, u_activity_ids[0], None)
        state = self.activity_pool.read(cr, uid, u_activity_ids[0], ['state'])['state']
        self.assertTrue(state == 'cancelled', msg='Activity state did not change to cancelled after cancel')

    def test_04_assign_unassign_activity(self):
        cr, uid = self.cr, self.uid

        u_activity_ids = self.activity_pool.search(cr, uid, [('state', 'not in', ['completed', 'cancelled']), ('location_id', 'child_of', self.wu_id), ('location_id.usage', '=', 'bed')])

        self.extapi.assign(cr, self.nu_id, u_activity_ids[0], None)
        user_id = self.activity_pool.read(cr, uid, u_activity_ids[0], ['user_id'])['user_id'][0]
        self.assertTrue(user_id == self.nu_id, msg='Activity user_id does not match the nurse id after assign')
        self.extapi.unassign(cr, self.nu_id, u_activity_ids[0])
        user_id = self.activity_pool.read(cr, uid, u_activity_ids[0], ['user_id'])['user_id']
        self.assertFalse(user_id, msg='Activity user_id is not None after unassign')

    def test_05_get_patients(self):
        cr, uid = self.cr, self.uid

        u_patient_ids = self.patient_pool.search(cr, uid, [('current_location_id', 'child_of', self.wu_id), ('current_location_id.usage', '=', 'bed')])
        t_patient_ids = self.patient_pool.search(cr, uid, [('current_location_id', 'child_of', self.wt_id), ('current_location_id.usage', '=', 'bed')])

        u_api_patients = self.extapi.get_patients(cr, self.nu_id, [])
        t_api_patients = self.extapi.get_patients(cr, self.nt_id, [])

        for a in u_api_patients:
            self.assertTrue(a['id'] in u_patient_ids, msg='Get patients returned a patient the Nurse is not responsible for')
        for a in t_api_patients:
            self.assertTrue(a['id'] in t_patient_ids, msg='Get patients returned a patient the Nurse is not responsible for')

    def test_06_patient_update(self):
        cr, uid = self.cr, self.uid

        patient_ids = self.patient_pool.search(cr, uid, [('current_location_id', 'child_of', self.pos_location_id)])
        pnhs = {}
        for pid in patient_ids:
            pnhs[pid] = 'NHS'+str(pid)
            phn = self.patient_pool.read(cr, uid, pid, ['other_identifier'])['other_identifier']
            self.extapi.update(cr, self.adt_id, phn, {'patient_identifier': pnhs[pid]})

        for pid in patient_ids:
            check_nhs = self.patient_pool.read(cr, uid, pid, ['patient_identifier'])['patient_identifier']
            self.assertTrue(check_nhs == pnhs[pid], msg='NHS number does not match after patient update')

    def test_07_patient_register(self):
        cr, uid = self.cr, self.uid
        
        dob = (dt.now()+td(days=-7300)).strftime(dtf)
        patient_data = {
            'patient_identifier': 'TESTNHS001',
            'family_name': "Al'Thor",
            'given_name': 'Rand',
            'dob': dob,
            'gender': 'M',
            'sex': 'M'
        }
        
        self.extapi.register(cr, self.adt_id, 'TESTP0001', patient_data)
        
        check_patient_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0001')])
        self.assertTrue(check_patient_id)
        check_patient = self.patient_pool.read(cr, uid, check_patient_id[0], [])
        self.assertTrue(check_patient['patient_identifier'] == patient_data['patient_identifier'], msg='NHS number does not match after patient register')
        self.assertTrue(check_patient['family_name'] == patient_data['family_name'], msg='Family name does not match after patient register')
        self.assertTrue(check_patient['given_name'] == patient_data['given_name'], msg='Name does not match after patient register')
        self.assertTrue(check_patient['dob'] == patient_data['dob'], msg='Date of birth does not match after patient register')
        self.assertTrue(check_patient['gender'] == patient_data['gender'], msg='Gender does not match after patient register')
        self.assertTrue(check_patient['sex'] == patient_data['sex'], msg='Sex does not match after patient register')

    def test_08_patient_admit_update_and_cancel(self):
        cr, uid = self.cr, self.uid

        dob = (dt.now()+td(days=-7300)).strftime(dtf)
        patient_data = {
            'patient_identifier': 'TESTNHS002',
            'family_name': 'Aybara',
            'given_name': 'Perrin',
            'dob': dob,
            'gender': 'M',
            'sex': 'M'
        }

        self.extapi.register(cr, self.adt_id, 'TESTP0002', patient_data)
        patient_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0002')])[0]

        doctors_data = [
            {
                'type': 'c',
                'code': 'c01',
                'title': 'dr',
                'family_name': 'Damodred',
                'given_name': 'Moiraine'
            },
            {
                'type': 'r',
                'code': 'r01',
                'title': 'dr',
                'family_name': "Al'Vere",
                'given_name': 'Egwene'
            }
        ]
        doa = dt.now().strftime(dtf)
        admit_data = {
            'location': 'U',
            'start_date': doa,
            'doctors': doctors_data
        }

        self.extapi.admit(cr, self.adt_id, 'TESTP0002', admit_data)

        # check there is an open spell for that patient with start_date doa
        spell_activity_id = self.activity_pool.search(cr, uid, [('data_model', '=', 'nh.clinical.spell'), ('patient_id', '=', patient_id)])
        self.assertTrue(spell_activity_id, msg='No spell found after admission')
        spell = self.activity_pool.browse(cr, uid, spell_activity_id[0])
        self.assertTrue(spell.data_ref.start_date == doa, msg='Date of admission does not match')
        # check there is an open placement activity with suggested location ward U for this patient
        placement_activity_id = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 'nh.clinical.patient.placement'),
            ('patient_id', '=', patient_id),
            ('state', 'not in', ['completed', 'cancelled'])])
        self.assertTrue(placement_activity_id, msg='No placement found after admission')
        placement_activity = self.activity_pool.browse(cr, uid, placement_activity_id[0])
        self.assertTrue(placement_activity.data_ref.suggested_location_id.id == self.wu_id, msg='Placement activity does not have the correct location after admission')
        # check there are doctors matching the doctors_data info and they are related to the patient spell
        for rdoctor in spell.data_ref.ref_doctor_ids:
            self.assertTrue(rdoctor.title.name == 'dr', msg='Doctor title does not match')
            self.assertTrue(rdoctor.code == 'r01', msg='Doctor code does not match')
            self.assertTrue(rdoctor.name == "Al'Vere, Egwene", msg='Doctor name does not match')
        for cdoctor in spell.data_ref.con_doctor_ids:
            self.assertTrue(cdoctor.title.name == 'dr', msg='Doctor title does not match')
            self.assertTrue(cdoctor.code == 'c01', msg='Doctor code does not match')
            self.assertTrue(cdoctor.name == "Damodred, Moiraine", msg='Doctor name does not match')

        update_data = {
            'location': 'T',
            'start_date': doa,
            'doctors': False
        }

        self.extapi.admit_update(cr, self.adt_id, 'TESTP0002', update_data)

        # check there is an open spell for that patient with start_date doa
        spell_activity_id = self.activity_pool.search(cr, uid, [('data_model', '=', 'nh.clinical.spell'), ('patient_id', '=', patient_id)])
        self.assertTrue(spell_activity_id, msg='No spell found after admission update')
        spell = self.activity_pool.browse(cr, uid, spell_activity_id[0])
        self.assertTrue(spell.data_ref.start_date == doa, msg='Date of admission does not match')
        # check there is an open placement activity with suggested location ward T for this patient
        placement_activity_id = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 'nh.clinical.patient.placement'),
            ('patient_id', '=', patient_id),
            ('state', 'not in', ['completed', 'cancelled'])])
        self.assertTrue(placement_activity_id, msg='No placement found after admission update')
        placement_activity = self.activity_pool.browse(cr, uid, placement_activity_id[0])
        self.assertTrue(placement_activity.data_ref.suggested_location_id.id == self.wt_id, msg='Placement activity does not have the correct location after admission update')
        # check doctor info in the spell matches the admission update
        self.assertFalse(spell.data_ref.con_doctor_ids, msg='Consultant doctors not updated after admission update')
        self.assertFalse(spell.data_ref.ref_doctor_ids, msg='Referring doctors not updated after admission update')

        self.extapi.cancel_admit(cr, self.adt_id, 'TESTP0002')

        # check the spell was cancelled and there are no open activities related to it
        spell_state = self.activity_pool.read(cr, uid, spell_activity_id[0], ['state'])['state']
        self.assertTrue(spell_state == 'cancelled', msg='Patient spell was not cancelled after admission cancel')
        self.assertFalse(
            self.activity_pool.search(cr, uid, [('parent_id', '=', spell_activity_id[0]), ('state', 'not in', ['completed', 'cancelled'])]),
            msg='Activities related to the cancelled spell remain open after admission cancel')

    def test_09_patient_discharge_and_cancel(self):
        cr, uid = self.cr, self.uid

        dob = (dt.now()+td(days=-7300)).strftime(dtf)
        patient_data = {
            'patient_identifier': 'TESTNHS003',
            'family_name': "Machera",
            'given_name': 'Elyas',
            'dob': dob,
            'gender': 'M',
            'sex': 'M'
        }

        self.extapi.register(cr, self.adt_id, 'TESTP0003', patient_data)

        patient_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0003')])
        self.assertTrue(patient_id)
        doa = dt.now().strftime(dtf)
        admit_data = {
            'location': 'U',
            'start_date': doa,
            'doctors': False
        }

        self.extapi.admit(cr, self.adt_id, 'TESTP0003', admit_data)

        dod = dt.now().strftime(dtf)
        self.extapi.discharge(cr, self.adt_id, 'TESTP0003', {'discharge_date': dod})

        # check there is a completed spell for that patient with discharge date dod
        spell_activity_id = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 'nh.clinical.spell'),
            ('patient_id', '=', patient_id[0]),
            ('state', '=', 'completed')])
        self.assertTrue(spell_activity_id, msg='No completed spell found after discharge')
        spell = self.activity_pool.browse(cr, uid, spell_activity_id[0])
        self.assertTrue(spell.date_terminated == dod, msg='Date of discharge does not match')

        self.extapi.cancel_discharge(cr, self.adt_id, 'TESTP0003')

        # check the spell is back open
        spell = self.activity_pool.browse(cr, uid, spell_activity_id[0])
        self.assertTrue(spell.state not in ['completed', 'cancelled'], msg='Spell was not reopened after cancel discharge')
        # check there is an open placement activity with suggested location ward U for this patient
        placement_activity_id = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 'nh.clinical.patient.placement'),
            ('patient_id', '=', patient_id[0]),
            ('state', 'not in', ['completed', 'cancelled'])])
        self.assertTrue(placement_activity_id, msg='No placement found after cancel discharge')
        placement_activity = self.activity_pool.browse(cr, uid, placement_activity_id[0])
        self.assertTrue(placement_activity.data_ref.suggested_location_id.id == self.wu_id, msg='Placement activity does not have the correct location after cancel discharge')

    def test_10_patient_transfer_and_cancel(self):
        cr, uid = self.cr, self.uid

        dob = (dt.now()+td(days=-7300)).strftime(dtf)
        patient_data = {
            'patient_identifier': 'TESTNHS004',
            'family_name': 'Trakand',
            'given_name': 'Morgase',
            'dob': dob,
            'gender': 'F',
            'sex': 'F'
        }

        self.extapi.register(cr, self.adt_id, 'TESTP0004', patient_data)

        patient_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0004')])[0]
        self.assertTrue(patient_id)
        doa = dt.now().strftime(dtf)
        admit_data = {
            'location': 'T',
            'start_date': doa,
            'doctors': False
        }

        self.extapi.admit(cr, self.adt_id, 'TESTP0004', admit_data)

        self.extapi.transfer(cr, self.adt_id, 'TESTP0004', {'location': 'U'})
        # check there is an open spell for that patient
        spell_activity_id = self.activity_pool.search(cr, uid, [('data_model', '=', 'nh.clinical.spell'),
                                                                ('patient_id', '=', patient_id)])
        self.assertTrue(spell_activity_id, msg='No spell found after transfer')
        # check there is an open placement activity with suggested location ward U for this patient
        placement_activity_id = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 'nh.clinical.patient.placement'),
            ('patient_id', '=', patient_id),
            ('state', 'not in', ['completed', 'cancelled'])])
        self.assertTrue(placement_activity_id, msg='No placement found after transfer')
        placement_activity = self.activity_pool.browse(cr, uid, placement_activity_id[0])
        self.assertTrue(placement_activity.data_ref.suggested_location_id.id == self.wu_id, msg='Placement activity does not have the correct location after transfer')

        self.extapi.cancel_transfer(cr, self.adt_id, 'TESTP0004')
        # check there is an open spell for that patient
        spell_activity_id = self.activity_pool.search(cr, uid, [('data_model', '=', 'nh.clinical.spell'), ('patient_id', '=', patient_id)])
        self.assertTrue(spell_activity_id, msg='No spell found after cancel transfer')
        # check there is an open placement activity with suggested location ward T for this patient
        placement_activity_id = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 'nh.clinical.patient.placement'),
            ('patient_id', '=', patient_id),
            ('state', 'not in', ['completed', 'cancelled'])])
        self.assertTrue(placement_activity_id, msg='No placement found after cancel transfer')
        placement_activity = self.activity_pool.browse(cr, uid, placement_activity_id[0])
        self.assertTrue(placement_activity.data_ref.suggested_location_id.id == self.wt_id, msg='Placement activity does not have the correct location after cancel transfer')

    def test_11_patient_merge(self):
        cr, uid = self.cr, self.uid

        dob = (dt.now()+td(days=-7300)).strftime(dtf)
        patient_data = {
            'patient_identifier': 'TESTNHS005',
            'family_name': "al'Meara",
            'given_name': 'Nynaeve',
            'dob': dob,
            'gender': 'F',
            'sex': 'F'
        }
        patient2_data = {
            'family_name': 'Merrilin',
            'given_name': 'Thomdril',
            'gender': 'M',
            'sex': 'M'
        }

        self.extapi.register(cr, self.adt_id, 'TESTP0005', patient_data)
        self.extapi.register(cr, self.adt_id, 'TESTP0006', patient2_data)

        patient_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0005')])
        patient2_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0006')])
        self.assertTrue(patient_id)
        self.assertTrue(patient2_id)
        doa = dt.now().strftime(dtf)
        admit_data = {
            'location': 'T',
            'start_date': doa,
            'doctors': False
        }

        self.extapi.admit(cr, self.adt_id, 'TESTP0005', admit_data)

        spell_activity_id = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 'nh.clinical.spell'),
            ('patient_id', '=', patient_id[0])])
        other_activity_ids = self.activity_pool.search(cr, uid, [('patient_id', '=', patient_id[0])])
        spell2_activity_id = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 'nh.clinical.spell'),
            ('patient_id', '=', patient2_id[0])])
        self.assertFalse(spell2_activity_id, msg='Spell found for patient not admitted')
        self.extapi.merge(cr, self.adt_id, 'TESTP0006', {'from_identifier': 'TESTP0005'})

        spell2_activity_id = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 'nh.clinical.spell'),
            ('patient_id', '=', patient2_id[0])])
        self.assertTrue(spell2_activity_id, msg='Spell not found for patient after patient merge')
        self.assertTrue(spell2_activity_id[0] == spell_activity_id[0], msg='Spell id does not match after patient merge')
        for activity in self.activity_pool.browse(cr, uid, other_activity_ids):
            self.assertTrue(activity.patient_id.id == patient2_id[0], msg='Patient not updated on activities after merge')
        patient2 = self.patient_pool.browse(cr, uid, patient2_id[0])
        self.assertTrue(patient2.family_name == 'Merrilin', msg='Patient family name does not match after merge')
        self.assertTrue(patient2.given_name == 'Thomdril', msg='Patient given name does not match after merge')
        self.assertTrue(patient2.gender == 'M', msg='Patient gender does not match after merge')
        self.assertTrue(patient2.sex == 'M', msg='Patient sex does not match after merge')
        self.assertTrue(patient2.patient_identifier == 'TESTNHS005', msg='Patient NHS number does not match after merge')
        self.assertTrue(patient2.other_identifier == 'TESTP0006', msg='Patient hospital number does not match after merge')
        self.assertTrue(patient2.dob == dob, msg='Patient date of birth does not match after merge')
        patient = self.patient_pool.browse(cr, uid, patient_id[0])
        self.assertFalse(patient.active, msg='First patient remains active after merge')

    def test_12_submit_complete_activity_and_get_activities_for_patient_or_spell(self):
        cr, uid = self.cr, self.uid

        dob = (dt.now()+td(days=-7300)).strftime(dtf)
        patient_data = {
            'patient_identifier': 'TESTNHS007',
            'family_name': 'Mandragoran',
            'given_name': 'Lan',
            'dob': dob,
            'gender': 'M',
            'sex': 'M'
        }

        self.extapi.register(cr, self.adt_id, 'TESTP0007', patient_data)

        patient_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0007')])
        self.assertTrue(patient_id)
        doa = dt.now().strftime(dtf)
        admit_data = {
            'location': 'U',
            'start_date': doa,
            'doctors': False
        }

        self.extapi.admit(cr, self.adt_id, 'TESTP0007', admit_data)

        placement_activity_id = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 'nh.clinical.patient.placement'),
            ('patient_id', '=', patient_id[0]),
            ('state', 'not in', ['completed', 'cancelled'])])
        self.assertTrue(placement_activity_id, msg='No placement found after admission')
        bed_ids = self.location_pool.search(cr, uid, [('usage', '=', 'bed'), ('id', 'child_of', self.wu_id), ('is_available', '=', True)])
        self.assertTrue(bed_ids, msg='No available beds in ward U after admission')
        self.extapi.complete(cr, self.wmu_id, placement_activity_id[0], {'location_id': bed_ids[0]})

        ews_activity_id = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 'nh.clinical.patient.observation.ews'),
            ('patient_id', '=', patient_id[0]),
            ('state', 'not in', ['completed', 'cancelled'])])
        self.assertTrue(ews_activity_id, msg='No observation found after placement')
        ews_data = {
            'respiration_rate': 40,
            'indirect_oxymetry_spo2': 99,
            'oxygen_administration_flag': False,
            'body_temperature': 37.0,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 55,
            'avpu_text': 'A'
        }
        self.extapi.complete(cr, self.nu_id, ews_activity_id[0], ews_data)
        
        ews_activities = self.extapi.get_activities_for_patient(cr, uid, patient_id[0], 'ews')
        self.assertTrue(ews_activities, msg='No EWS found after ews activity submit/complete')
        self.assertTrue(ews_activities[0]['respiration_rate'] == ews_data['respiration_rate'], msg='respiration rate does not match')
        self.assertTrue(ews_activities[0]['indirect_oxymetry_spo2'] == ews_data['indirect_oxymetry_spo2'], msg='O2 saturation does not match')
        self.assertTrue(ews_activities[0]['oxygen_administration_flag'] == ews_data['oxygen_administration_flag'], msg='oxygen flag does not match')
        self.assertTrue(ews_activities[0]['body_temperature'] == ews_data['body_temperature'], msg='body temperature does not match')
        self.assertTrue(ews_activities[0]['blood_pressure_systolic'] == ews_data['blood_pressure_systolic'], msg='systolic does not match')
        self.assertTrue(ews_activities[0]['blood_pressure_diastolic'] == ews_data['blood_pressure_diastolic'], msg='diastolic rate does not match')
        self.assertTrue(ews_activities[0]['pulse_rate'] == ews_data['pulse_rate'], msg='pulse rate does not match')
        self.assertTrue(ews_activities[0]['avpu_text'] == ews_data['avpu_text'], msg='avpu does not match')

    def test_13_create_activity_for_patient(self):
        cr, uid = self.cr, self.uid

        dob = (dt.now()+td(days=-7300)).strftime(dtf)
        patient_data = {
            'patient_identifier': 'TESTNHS008',
            'family_name': 'Trakand',
            'given_name': 'Elayne',
            'dob': dob,
            'gender': 'F',
            'sex': 'F'
        }

        self.extapi.register(cr, self.adt_id, 'TESTP0008', patient_data)

        patient_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0008')])
        self.assertTrue(patient_id)
        doa = dt.now().strftime(dtf)
        admit_data = {
            'location': 'T',
            'start_date': doa,
            'doctors': False
        }

        self.extapi.admit(cr, self.adt_id, 'TESTP0008', admit_data)

        placement_activity_id = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 'nh.clinical.patient.placement'),
            ('patient_id', '=', patient_id[0]),
            ('state', 'not in', ['completed', 'cancelled'])])
        self.assertTrue(placement_activity_id, msg='No placement found after admission')
        bed_ids = self.location_pool.search(cr, uid, [('usage', '=', 'bed'), ('id', 'child_of', self.wt_id), ('is_available', '=', True)])
        self.assertTrue(bed_ids, msg='No available beds in ward T after admission')
        self.extapi.complete(cr, self.wmt_id, placement_activity_id[0], {'location_id': bed_ids[0]})

        ews_data = {
            'respiration_rate': 40,
            'indirect_oxymetry_spo2': 99,
            'oxygen_administration_flag': False,
            'body_temperature': 37.0,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 55,
            'avpu_text': 'A'
        }

        # FIXME: Should the completing user be nu_id (which was originally there but fails) or nt_id?
        ews_id = self.extapi.create_activity_for_patient(cr, self.nt_id, patient_id[0], 'ews')
        self.extapi.complete(cr, self.nt_id, ews_id, ews_data)

        ews_activities = self.extapi.get_activities_for_patient(cr, uid, patient_id[0], 'ews')
        self.assertTrue(ews_activities, msg='No EWS found after ews activity submit/complete')
        self.assertTrue(ews_activities[0]['respiration_rate'] == ews_data['respiration_rate'], msg='respiration rate does not match')
        self.assertTrue(ews_activities[0]['indirect_oxymetry_spo2'] == ews_data['indirect_oxymetry_spo2'], msg='O2 saturation does not match')
        self.assertTrue(ews_activities[0]['oxygen_administration_flag'] == ews_data['oxygen_administration_flag'], msg='oxygen flag does not match')
        self.assertTrue(ews_activities[0]['body_temperature'] == ews_data['body_temperature'], msg='body temperature does not match')
        self.assertTrue(ews_activities[0]['blood_pressure_systolic'] == ews_data['blood_pressure_systolic'], msg='systolic does not match')
        self.assertTrue(ews_activities[0]['blood_pressure_diastolic'] == ews_data['blood_pressure_diastolic'], msg='diastolic rate does not match')
        self.assertTrue(ews_activities[0]['pulse_rate'] == ews_data['pulse_rate'], msg='pulse rate does not match')
        self.assertTrue(ews_activities[0]['avpu_text'] == ews_data['avpu_text'], msg='avpu does not match')

    def test_14_start_and_stop_following(self):
        cr, uid = self.cr, self.uid

        dob = (dt.now()+td(days=-7300)).strftime(dtf)
        patient_data = {
            'patient_identifier': 'TESTNHS009',
            'family_name': 'Cauthon',
            'given_name': 'Matrim',
            'dob': dob,
            'gender': 'M',
            'sex': 'M'
        }

        self.extapi.register(cr, self.adt_id, 'TESTP0009', patient_data)

        patient_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0009')])
        self.assertTrue(patient_id)
        patient_id = patient_id[0]
        doa = dt.now().strftime(dtf)
        admit_data = {
            'location': 'T',
            'start_date': doa,
            'doctors': False
        }

        self.extapi.admit(cr, self.adt_id, 'TESTP0009', admit_data)

        placement_activity_id = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 'nh.clinical.patient.placement'),
            ('patient_id', '=', patient_id),
            ('state', 'not in', ['completed', 'cancelled'])])
        self.assertTrue(placement_activity_id, msg='No placement found after admission')
        bed_ids = self.location_pool.search(cr, uid, [('usage', '=', 'bed'), ('id', 'child_of', self.wt_id), ('is_available', '=', True)])
        self.assertTrue(bed_ids, msg='No available beds in ward T after admission')
        self.extapi.complete(cr, self.wmt_id, placement_activity_id[0], {'location_id': bed_ids[0]})

        self.assertTrue(self.extapi.follow_invite(cr, self.nt_id, [patient_id], self.nu_id), msg="Error calling follow_invite")
        follow_id = self.follow_pool.search(cr, uid, [
            ['activity_id.state', 'not in', ['completed', 'cancelled']],
            ['patient_ids', 'in', [patient_id]],
            ['activity_id.user_id', '=', self.nu_id]])
        self.assertTrue(follow_id, msg="Cannot find the Follow patient activity")
        patients = self.extapi.get_patients(cr, self.nt_id, [])
        self.extapi.get_invited_users(cr, uid, patients)
        self.assertTrue(all([self.nu_id in [u['id'] for u in p['invited_users']] if p['id'] == patient_id else True for p in patients]), msg="Get invited users: The invited user was not found within the result")
        follow = self.follow_pool.browse(cr, uid, follow_id[0])
        assigned_activities = self.extapi.get_assigned_activities(cr, self.nu_id, activity_type='nh.clinical.patient.follow')
        self.assertTrue(follow.activity_id.id in [aa['id'] for aa in assigned_activities], msg="Get assigned activities not returning the follow activity just created.")
        self.activity_pool.complete(cr, self.nu_id, follow.activity_id.id)
        check_patient = self.patient_pool.browse(cr, uid, patient_id)
        self.assertTrue(self.nu_id in [user.id for user in check_patient.follower_ids], msg="The user should be a follower after completing patient follow")

        followed_patients = self.extapi.get_followed_patients(cr, self.nu_id)
        self.assertTrue(followed_patients, msg="Get followed patients: No results while following a patient")
        self.assertTrue(any([patient['id'] == patient_id for patient in followed_patients]), msg="Get followed patients: Followed patient not found within the result")
        self.extapi.get_patient_followers(cr, uid, followed_patients)
        self.assertTrue(all([self.nu_id in [f['id'] for f in patient['followers']] for patient in followed_patients]), msg="Get patient followers: The user following was not found within the result")

        self.assertTrue(self.extapi.remove_followers(cr, self.nt_id, [patient_id]), msg="Error calling remove_followers")
        check_patient = self.patient_pool.browse(cr, uid, patient_id)
        self.assertTrue(self.nu_id not in [user.id for user in check_patient.follower_ids], msg="The user should not be a follower after calling remove followers")
        
    def test_15_get_share_users(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Get HCAs list of users.
        hca_result = self.extapi.get_share_users(cr, self.hu_id)
        self.assertFalse(hca_result, msg="HCA share users: Non expected user returned")

        # Scenario 2: Get Nurse list of users.
        nurse_result = self.extapi.get_share_users(cr, self.nu_id)
        self.assertTrue(self.nt_id not in [u['id'] for u in nurse_result], msg="Nurse share users: Non expected user returned")
        self.assertTrue(self.ht_id not in [u['id'] for u in nurse_result], msg="Nurse share users: Non expected user returned")
        self.assertTrue(self.hu_id in [u['id'] for u in nurse_result], msg="Nurse share users: User missing from result")

        # Scenario 3: Get Ward Manager list of users.
        wm_result = self.extapi.get_share_users(cr, self.wmu_id)
        self.assertTrue(self.wmt_id not in [u['id'] for u in wm_result], msg="Ward Manager share users: Non expected user returned")
        self.assertTrue(self.nu_id in [u['id'] for u in wm_result], msg="Ward Manager share users: User missing from result")
        self.assertTrue(self.nt_id not in [u['id'] for u in wm_result], msg="Ward Manager share users: Non expected user returned")
        self.assertTrue(self.ht_id not in [u['id'] for u in wm_result], msg="Ward Manager share users: Non expected user returned")
        self.assertTrue(self.hu_id in [u['id'] for u in wm_result], msg="Ward Manager share users: User missing from result")