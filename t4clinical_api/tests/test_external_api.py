from openerp.tests.common import SingleTransactionCase
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf


class TestExternalAPI(SingleTransactionCase):
    
    @classmethod
    def setUpClass(cls):
        super(TestExternalAPI, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        
        cls.users_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.partner_pool = cls.registry('res.partner')
        cls.activity_pool = cls.registry('t4.activity')
        cls.patient_pool = cls.registry('t4.clinical.patient')
        cls.location_pool = cls.registry('t4.clinical.location')
        cls.pos_pool = cls.registry('t4.clinical.pos')
        cls.extapi = cls.registry('t4.clinical.api.external')
        cls.apidemo = cls.registry('t4.clinical.api.demo')

        cls.apidemo.build_unit_test_env(cr, uid)

        cls.wu_id = cls.location_pool.search(cr, uid, [('code', '=', 'U')])[0]
        cls.wt_id = cls.location_pool.search(cr, uid, [('code', '=', 'T')])[0]
        cls.pos_id = cls.location_pool.read(cr, uid, cls.wu_id, ['pos_id'])['pos_id'][0]
        cls.pos_location_id = cls.pos_pool.read(cr, uid, cls.pos_id, ['location_id'])['location_id'][0]

        cls.nu_id = cls.users_pool.search(cr, uid, [('login', '=', 'NU')])[0]
        cls.nt_id = cls.users_pool.search(cr, uid, [('login', '=', 'NT')])[0]
        cls.adt_id = cls.users_pool.search(cr, uid, [('groups_id.name', 'in', ['T4 Clinical ADT Group']), ('pos_id', '=', cls.pos_id)])[0]

    def test_check_activity_access(self):
        cr, uid = self.cr, self.uid

        u_activity_ids = self.activity_pool.search(cr, uid, [('state', 'not in', ['completed', 'cancelled']), ('location_id', 'child_of', self.wu_id), ('location_id.usage', '=', 'bed')])
        t_activity_ids = self.activity_pool.search(cr, uid, [('state', 'not in', ['completed', 'cancelled']), ('location_id', 'child_of', self.wt_id), ('location_id.usage', '=', 'bed')])

        for u_act_id in u_activity_ids:
            self.assertTrue(self.extapi.check_activity_access(cr, self.nu_id, u_act_id), msg='Nurse U should have access to Ward U Activities')
            self.assertFalse(self.extapi.check_activity_access(cr, self.nt_id, u_act_id), msg='Nurse T should not have access to Ward U Activities')

        for t_act_id in t_activity_ids:
            self.assertTrue(self.extapi.check_activity_access(cr, self.nt_id, t_act_id), msg='Nurse T should have access to Ward T Activities')
            self.assertFalse(self.extapi.check_activity_access(cr, self.nu_id, t_act_id), msg='Nurse U should not have access to Ward T Activities')

    def test_get_activities(self):
        cr, uid = self.cr, self.uid

        u_activity_ids = self.activity_pool.search(cr, uid, [('state', 'not in', ['completed', 'cancelled']), ('location_id', 'child_of', self.wu_id), ('location_id.usage', '=', 'bed')])
        t_activity_ids = self.activity_pool.search(cr, uid, [('state', 'not in', ['completed', 'cancelled']), ('location_id', 'child_of', self.wt_id), ('location_id.usage', '=', 'bed')])

        u_api_activities = self.extapi.get_activities(cr, self.nu_id, [])
        t_api_activities = self.extapi.get_activities(cr, self.nt_id, [])

        for a in u_api_activities:
            self.assertTrue(a['id'] in u_activity_ids, msg='Get activities returned an activity the Nurse is not responsible for')
        for a in t_api_activities:
            self.assertTrue(a['id'] in t_activity_ids, msg='Get activities returned an activity the Nurse is not responsible for')

    def test_cancel_activity(self):
        cr, uid = self.cr, self.uid

        u_activity_ids = self.activity_pool.search(cr, uid, [('state', 'not in', ['completed', 'cancelled']), ('location_id', 'child_of', self.wu_id), ('location_id.usage', '=', 'bed')])

        self.extapi.cancel(cr, self.nu_id, u_activity_ids[0], None)
        state = self.activity_pool.read(cr, uid, u_activity_ids[0], ['state'])['state']
        self.assertTrue(state == 'cancelled', msg='Activity state did not change to cancelled after cancel')

    def test_assign_unassign_activity(self):
        cr, uid = self.cr, self.uid

        u_activity_ids = self.activity_pool.search(cr, uid, [('state', 'not in', ['completed', 'cancelled']), ('location_id', 'child_of', self.wu_id), ('location_id.usage', '=', 'bed')])

        self.extapi.assign(cr, self.nu_id, u_activity_ids[0], None)
        user_id = self.activity_pool.read(cr, uid, u_activity_ids[0], ['user_id'])['user_id'][0]
        self.assertTrue(user_id == self.nu_id, msg='Activity user_id does not match the nurse id after assign')
        self.extapi.unassign(cr, self.nu_id, u_activity_ids[0])
        user_id = self.activity_pool.read(cr, uid, u_activity_ids[0], ['user_id'])['user_id']
        self.assertFalse(user_id, msg='Activity user_id is not None after unassign')

    def test_get_patients(self):
        cr, uid = self.cr, self.uid

        u_patient_ids = self.patient_pool.search(cr, uid, [('current_location_id', 'child_of', self.wu_id), ('current_location_id.usage', '=', 'bed')])
        t_patient_ids = self.patient_pool.search(cr, uid, [('current_location_id', 'child_of', self.wt_id), ('current_location_id.usage', '=', 'bed')])

        u_api_patients = self.extapi.get_patients(cr, self.nu_id, [])
        t_api_patients = self.extapi.get_patients(cr, self.nt_id, [])

        for a in u_api_patients:
            self.assertTrue(a['id'] in u_patient_ids, msg='Get patients returned a patient the Nurse is not responsible for')
        for a in t_api_patients:
            self.assertTrue(a['id'] in t_patient_ids, msg='Get patients returned a patient the Nurse is not responsible for')

    def test_patient_update(self):
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

    def test_patient_register(self):
        cr, uid = self.cr, self.uid
        
        dob = (dt.now()+td(days=-7300)).strftime(dtf)
        patient_data = {
            'patient_identifier': 'TESTNHS0001',
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

    def test_patient_admit_update_and_cancel(self):
        cr, uid = self.cr, self.uid

        dob = (dt.now()+td(days=-7300)).strftime(dtf)
        patient_data = {
            'patient_identifier': 'TESTNHS0002',
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
        spell_activity_id = self.activity_pool.search(cr, uid, [('data_model', '=', 't4.clinical.spell'), ('patient_id', '=', patient_id)])
        self.assertTrue(spell_activity_id, msg='No spell found after admission')
        spell = self.activity_pool.browse(cr, uid, spell_activity_id[0])
        self.assertTrue(spell.data_ref.start_date == doa, msg='Date of admission does not match')
        # check there is an open placement activity with suggested location ward U for this patient
        placement_activity_id = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 't4.clinical.patient.placement'),
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
            self.assertTrue(rdoctor.doctor, msg='Doctor flag is False')
        for cdoctor in spell.data_ref.con_doctor_ids:
            self.assertTrue(cdoctor.title.name == 'dr', msg='Doctor title does not match')
            self.assertTrue(cdoctor.code == 'c01', msg='Doctor code does not match')
            self.assertTrue(cdoctor.name == "Damodred, Moiraine", msg='Doctor name does not match')
            self.assertTrue(cdoctor.doctor, msg='Doctor flag is False')

        update_data = {
            'location': 'T',
            'start_date': doa,
            'doctors': False
        }

        self.extapi.admit_update(cr, self.adt_id, 'TESTP0002', update_data)

        # check there is an open spell for that patient with start_date doa
        spell_activity_id = self.activity_pool.search(cr, uid, [('data_model', '=', 't4.clinical.spell'), ('patient_id', '=', patient_id)])
        self.assertTrue(spell_activity_id, msg='No spell found after admission update')
        spell = self.activity_pool.browse(cr, uid, spell_activity_id[0])
        self.assertTrue(spell.data_ref.start_date == doa, msg='Date of admission does not match')
        # check there is an open placement activity with suggested location ward T for this patient
        placement_activity_id = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 't4.clinical.patient.placement'),
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

    def test_patient_discharge_and_cancel(self):
        cr, uid = self.cr, self.uid

        dob = (dt.now()+td(days=-7300)).strftime(dtf)
        patient_data = {
            'patient_identifier': 'TESTNHS0003',
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
            ('data_model', '=', 't4.clinical.spell'),
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
            ('data_model', '=', 't4.clinical.patient.placement'),
            ('patient_id', '=', patient_id[0]),
            ('state', 'not in', ['completed', 'cancelled'])])
        self.assertTrue(placement_activity_id, msg='No placement found after cancel discharge')
        placement_activity = self.activity_pool.browse(cr, uid, placement_activity_id[0])
        self.assertTrue(placement_activity.data_ref.suggested_location_id.id == self.wu_id, msg='Placement activity does not have the correct location after cancel discharge')

    def test_patient_transfer_and_cancel(self):
        cr, uid = self.cr, self.uid

        dob = (dt.now()+td(days=-7300)).strftime(dtf)
        patient_data = {
            'patient_identifier': 'TESTNHS0004',
            'family_name': 'Trakand',
            'given_name': 'Morgase',
            'dob': dob,
            'gender': 'F',
            'sex': 'F'
        }

        self.extapi.register(cr, self.adt_id, 'TESTP0004', patient_data)

        patient_id = self.patient_pool.search(cr, uid, [('other_identifier', '=', 'TESTP0004')])
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
        spell_activity_id = self.activity_pool.search(cr, uid, [('data_model', '=', 't4.clinical.spell'), ('patient_id', '=', patient_id)])
        self.assertTrue(spell_activity_id, msg='No spell found after transfer')
        # check there is an open placement activity with suggested location ward U for this patient
        placement_activity_id = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 't4.clinical.patient.placement'),
            ('patient_id', '=', patient_id),
            ('state', 'not in', ['completed', 'cancelled'])])
        self.assertTrue(placement_activity_id, msg='No placement found after transfer')
        placement_activity = self.activity_pool.browse(cr, uid, placement_activity_id[0])
        self.assertTrue(placement_activity.data_ref.suggested_location_id.id == self.wu_id, msg='Placement activity does not have the correct location after transfer')

        self.extapi.cancel_transfer(cr, self.adt_id, 'TESTP0004')
        # check there is an open spell for that patient
        spell_activity_id = self.activity_pool.search(cr, uid, [('data_model', '=', 't4.clinical.spell'), ('patient_id', '=', patient_id)])
        self.assertTrue(spell_activity_id, msg='No spell found after cancel transfer')
        # check there is an open placement activity with suggested location ward T for this patient
        placement_activity_id = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 't4.clinical.patient.placement'),
            ('patient_id', '=', patient_id),
            ('state', 'not in', ['completed', 'cancelled'])])
        self.assertTrue(placement_activity_id, msg='No placement found after cancel transfer')
        placement_activity = self.activity_pool.browse(cr, uid, placement_activity_id[0])
        self.assertTrue(placement_activity.data_ref.suggested_location_id.id == self.wt_id, msg='Placement activity does not have the correct location after cancel transfer')