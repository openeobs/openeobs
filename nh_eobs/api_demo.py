from openerp.osv import orm, osv
from openerp import SUPERUSER_ID
import logging
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from openerp.addons.nh_activity.activity import except_if
_logger = logging.getLogger(__name__)

from faker import Faker
from faker.providers import BaseProvider
fake = Faker()


class nh_clinical_api_demo(orm.AbstractModel):
    _name = 'nh.clinical.api.demo'
    _inherit = 'nh.clinical.api.demo'

    def build_unit_test_env(self, cr, uid, wards=None, bed_count=2, patient_admit_count=2, patient_placement_count=1,
                            ews_count=1, context=False, weight_count=0, blood_sugar_count=0, height_count=0, o2target_count=0,
                            users=None):
        """
        Create a default unit test environment for basic unit tests.
            2 WARDS - U and T
            2 beds per ward - U01, U02, T01, T02
            2 patients admitted per ward
            1 patient placed in bed per ward
            1 ews observation taken per patient
        The environment is customizable, the wards parameter must be a list of ward codes. All the other parameters are
        the number of beds, patients, placements and observations we want.

        users parameter expects a dictionary with the following format:
            {
                'ward_managers': {
                    'name': ['login', 'ward_code']
                },
                'nurses': {
                    'name': ['login', [list of locations]]
                },
                'hcas': {
                    'name': ['login', [list of locations]]
                },
                'doctors': {
                    'name': ['login', [list of locations]]
                }
            }
            if there is no data the default behaviour will be to add a ward manager per ward i.e. 'WMU' and 'WMT' and
            a nurse responsible for all beds in the ward i.e. 'NU' and 'NT'
        """
        if not wards:
            wards = ['U', 'T']
        assert patient_admit_count >= patient_placement_count
        assert bed_count >= patient_placement_count
        fake = self.next_seed_fake()
        api = self.pool['nh.clinical.api']
        activity_pool = self.pool['nh.activity']
        location_pool = self.pool['nh.clinical.location']
        context_pool = self.pool['nh.clinical.context']
        user_pool = self.pool['res.users']
        pos_id = self.create(cr, uid, 'nh.clinical.pos')
        pos_location_id = location_pool.search(cr, uid, [('pos_id', '=', pos_id)])[0]

        adt_uid = self.create(cr, uid, 'res.users', 'user_adt', {'pos_id': pos_id})

        if context:
            context_ids = context_pool.search(cr, uid, [['name', '=', context]])
            context = [[6, False, context_ids]] if context_ids else False

        # LOCATIONS
        ward_ids = [self.create(cr, uid, 'nh.clinical.location', 'location_ward', {'context_ids': context, 'parent_id': pos_location_id, 'name': 'Ward '+w, 'code': w}) for w in wards]
        i = 0
        bed_ids = {}
        bed_codes = {}
        for wid in ward_ids:
            bed_ids[wards[i]] = [self.create(cr, uid, 'nh.clinical.location', 'location_bed', {'context_ids': context, 'parent_id': wid, 'name': 'Bed '+str(n), 'code': wards[i]+str(n)}) for n in range(bed_count)]
            bed_codes[wards[i]] = [wards[i]+str(n) for n in range(bed_count)]
            i += 1

        # USERS
        if not users:
            users = {'ward_managers': {}, 'nurses': {}}
            for w in wards:
                users['ward_managers']['WM'+w] = ['WM'+w, w]
                users['nurses']['N'+w] = ['N'+w, bed_codes[w]]

        if users.get('ward_managers'):
            wm_ids = {}
            for wm in users['ward_managers'].keys():
                wid = location_pool.search(cr, uid, [('code', '=', users['ward_managers'][wm][1])])
                wm_ids[wm] = self.create(cr, uid, 'res.users', 'user_ward_manager', {'name': wm, 'login': users['ward_managers'][wm][0], 'location_ids': [[6, False, wid]]})

        if users.get('nurses'):
            n_ids = {}
            for n in users['nurses'].keys():
                lids = location_pool.search(cr, uid, [('code', 'in', users['nurses'][n][1])])
                n_ids[n] = self.create(cr, uid, 'res.users', 'user_nurse', {'name': n, 'login': users['nurses'][n][0], 'location_ids': [[6, False, lids]]})

        if users.get('hcas'):
            h_ids = {}
            for h in users['hcas'].keys():
                lids = location_pool.search(cr, uid, [('code', 'in', users['hcas'][h][1])])
                h_ids[h] = self.create(cr, uid, 'res.users', 'user_hca', {'name': h, 'login': users['hcas'][h][0], 'location_ids': [[6, False, lids]]})

        if users.get('doctors'):
            d_ids = {}
            for d in users['doctors'].keys():
                lids = location_pool.search(cr, uid, [('code', 'in', users['doctors'][d][1])])
                d_ids[d] = self.create(cr, uid, 'res.users', 'user_doctor', {'name': d, 'login': users['doctors'][d][0], 'location_ids': [[6, False, lids]]})

        for wcode in wards:
            admit_activity_ids = [self.create_activity(cr, adt_uid, 'nh.clinical.adt.patient.admit', None, {}, {'location': wcode}) for i in range(patient_admit_count)]
            [api.complete(cr, adt_uid, id) for id in admit_activity_ids]

        for wid in ward_ids:
            code = location_pool.read(cr, uid, wid, ['code'])['code']
            wmuid = user_pool.search(cr, uid, [('location_ids', 'in', [wid]), ('groups_id.name', 'in', ['NH Clinical Ward Manager Group'])])
            wmuid = uid if not wmuid else wmuid[0]
            placement_activity_ids = activity_pool.search(cr, uid, [
                ('data_model', '=', 'nh.clinical.patient.placement'),
                ('state', 'not in', ['completed', 'cancelled']), ('user_ids', 'in', [wmuid])])
            if not placement_activity_ids:
                continue
            for i in range(patient_placement_count):
                placement_activity_id = fake.random_element(placement_activity_ids)
                bed_location_id = fake.random_element(bed_ids[code])
                api.submit_complete(cr, wmuid, placement_activity_id, {'location_id': bed_location_id})
                placement_activity_ids.remove(placement_activity_id)
                bed_ids[code].remove(bed_location_id)

        for i in range(ews_count):
            ews_activity_ids = []
            for wid in ward_ids:
                ews_activity_ids += activity_pool.search(cr, uid, [
                    ('data_model', '=', 'nh.clinical.patient.observation.ews'),
                    ('state', 'not in', ['completed', 'cancelled']), ('location_id', 'child_of', wid)])
            for ews in activity_pool.browse(cr, uid, ews_activity_ids):
                nuid = user_pool.search(cr, uid, [('location_ids', 'in', [ews.location_id.id]), ('groups_id.name', 'in', ['NH Clinical Nurse Group'])])
                nuid = uid if not nuid else nuid[0]
                api.assign(cr, uid, ews.id, nuid)
                api.submit_complete(cr, nuid, ews.id, self.demo_data(cr, uid, 'nh.clinical.patient.observation.ews'))

        return True

    def build_eobs_uat_env(self, cr, uid, data, context=None):
        wards = data.get('wards') if data.get('wards') else 10
        beds = data.get('beds') if data.get('beds') else 10
        patients = data.get('patients') if data.get('patients') else 10
        begin_date = data.get('begin_date') if data.get('begin_date') else dt.now().strftime(dtf)
        fake = self.next_seed_fake()
        api = self.pool['nh.eobs.api']
        activity_pool = self.pool['nh.activity']
        patient_pool = self.pool['nh.clinical.patient']
        location_pool = self.pool['nh.clinical.location']
        context_pool = self.pool['nh.clinical.context']
        user_pool = self.pool['res.users']
        pos_pool = self.pool['nh.clinical.pos']
        pos_ids = pos_pool.search(cr, uid, [], context=context)
        if not pos_ids:
            pos_ids = [self.create(cr, uid, 'nh.clinical.pos')]
        pos_location_id = location_pool.search(cr, uid, [('pos_id', '=', pos_ids[0])])[0]

        adt_uid = user_pool.search(cr, uid, [['groups_id.name', 'in', ['NH Clinical ADT Group']]], context=context)
        if not adt_uid:
            adt_uid = self.create(cr, uid, 'res.users', 'user_adt', {'pos_id': pos_ids[0]})
        else:
            adt_uid = adt_uid[0]

        context_ids = context_pool.search(cr, uid, [['name', '=', 'eobs']], context=context)


        # LOCATIONS

        ward_ids = [self.create(cr, uid, 'nh.clinical.location', 'location_ward', {'context_ids': [[6, False, context_ids]], 'parent_id': pos_location_id, 'name': 'Ward '+str(w), 'code': str(w)}) if not location_pool.search(cr, uid, [['code', '=', str(w)], ['parent_id', '=', pos_location_id], ['usage', '=', 'ward']], context=context) else location_pool.search(cr, uid, [['code', '=', str(w)], ['parent_id', '=', pos_location_id], ['usage', '=', 'ward']], context=context)[0] for w in range(wards)]
        bed_ids = {}
        bed_codes = {}
        for w in range(wards):
            bed_ids[str(w)] = [self.create(cr, uid, 'nh.clinical.location', 'location_bed', {'context_ids': [[6, False, context_ids]], 'parent_id': ward_ids[w], 'name': 'Bed '+str(b), 'code': str(w)+str(b)}) if not location_pool.search(cr, uid, [['code', '=', str(w)+str(b)], ['parent_id.code', '=', str(w)], ['usage', '=', 'bed']], context=context) else location_pool.search(cr, uid, [['code', '=', str(w)+str(b)], ['parent_id.code', '=', str(w)], ['usage', '=', 'bed']], context=context)[0] for b in range(beds)]
            for b in range(beds):
                bed = location_pool.read(cr, uid, bed_ids[str(w)][b], ['is_available'], context=context)
                bed_codes[str(w)+str(b)] = {'available': bed['is_available'], 'ward': str(w)}

        # USERS

        wm_ids = {}
        n_ids = {}
        h_ids = {}
        d_ids = {}
        for w in range(wards):
            wm_ids[str(w)] = self.create(cr, uid, 'res.users', 'user_ward_manager', {'name': 'WM'+str(w), 'login': 'WM'+str(w), 'password': 'WM'+str(w), 'location_ids': [[6, False, [ward_ids[w]]]]}) if not user_pool.search(cr, uid, [['login', '=', 'WM'+str(w)]], context=context) else user_pool.search(cr, uid, [['login', '=', 'WM'+str(w)]], context=context)[0]
            n_ids[str(w)] = self.create(cr, uid, 'res.users', 'user_nurse', {'name': 'N'+str(w), 'login': 'N'+str(w), 'password': 'N'+str(w), 'location_ids': [[6, False, bed_ids[str(w)]]]}) if not user_pool.search(cr, uid, [['login', '=', 'N'+str(w)]], context=context) else user_pool.search(cr, uid, [['login', '=', 'N'+str(w)]], context=context)[0]
            h_ids[str(w)] = self.create(cr, uid, 'res.users', 'user_hca', {'name': 'H'+str(w), 'login': 'H'+str(w), 'password': 'H'+str(w), 'location_ids': [[6, False, bed_ids[str(w)]]]}) if not user_pool.search(cr, uid, [['login', '=', 'H'+str(w)]], context=context) else user_pool.search(cr, uid, [['login', '=', 'H'+str(w)]], context=context)[0]
            d_ids[str(w)] = self.create(cr, uid, 'res.users', 'user_doctor', {'name': 'D'+str(w), 'login': 'D'+str(w), 'password': 'D'+str(w), 'location_ids': [[6, False, bed_ids[str(w)]]]}) if not user_pool.search(cr, uid, [['login', '=', 'D'+str(w)]], context=context) else user_pool.search(cr, uid, [['login', '=', 'D'+str(w)]], context=context)[0]

        # PATIENT REGISTER

        patient_identifiers = []
        for p in range(patients):
            hospital_number = BaseProvider.numerify('#######')
            while patient_pool.search(cr, uid, [['other_identifier', '=', hospital_number]], context=context):
                hospital_number = BaseProvider.numerify('#######')
            nhs_number = BaseProvider.numerify('##########')
            while patient_pool.search(cr, uid, [['patient_identifier', '=', nhs_number]], context=context):
                nhs_number = BaseProvider.numerify('##########')
            gender = fake.random_element(['M', 'F'])
            data = {
                'patient_identifier': nhs_number,
                'family_name': fake.last_name(),
                'given_name': fake.first_name(),
                'dob': fake.date_time_between(start_date="-85y", end_date="now").strftime(dtf),
                'gender': gender,
                'sex': gender,
                'ethnicity': fake.random_element(patient_pool._ethnicity)[0]
            }
            api.register(cr, adt_uid, hospital_number, data, context=context)
            patient_identifiers.append(hospital_number)

        # PATIENT ADMIT


        count = 0
        for b in bed_codes.keys():
            if not bed_codes[b]['available']:
                continue
            if len(patient_identifiers) <= count:
                break
            data = {
                'location': bed_codes[b]['ward'],
                'start_date': begin_date
            }
            wm_uid = wm_ids[bed_codes[b]['ward']]
            api.admit(cr, adt_uid, patient_identifiers[count], data, context=context)
            placement_id = activity_pool.search(cr, uid, [['patient_id.other_identifier', '=', patient_identifiers[count]], ['data_model', '=', 'nh.clinical.patient.placement']], context=context)
            if not placement_id:
                osv.except_osv('Error!', 'The patient placement was not triggered after admission!')
            location_id = location_pool.search(cr, uid, [['usage', '=', 'bed'], ['code', '=', b], ['parent_id.usage', '=', 'ward'], ['parent_id.code', '=', bed_codes[b]['ward']]], context=context)
            if not location_id:
                osv.except_osv('Error!', 'Cannot complete placement. Location not found!')
            activity_pool.submit(cr, wm_uid, placement_id[0], {'date_started': begin_date, 'location_id': location_id[0]}, context=context)
            activity_pool.complete(cr, wm_uid, placement_id[0], context=context)
            activity_pool.write(cr, uid, placement_id[0], {'date_terminated': begin_date}, context=context)
            count += 1

        ews_activity_ids = activity_pool.search(cr, uid, [['patient_id.other_identifier', 'in', patient_identifiers], ['data_model', '=', 'nh.clinical.patient.observation.ews'], ['state', 'not in', ['completed', 'cancelled']]], context=context)
        activity_pool.write(cr, uid, ews_activity_ids, {'date_scheduled': begin_date}, context=context)

        current_date = dt.strptime(begin_date, dtf)
        while current_date < dt.now():
            ews_activity_ids = activity_pool.search(cr, uid, [['patient_id.other_identifier', 'in', patient_identifiers], ['data_model', '=', 'nh.clinical.patient.observation.ews'], ['state', 'not in', ['completed', 'cancelled']], ['date_scheduled', '<=', current_date.strftime(dtf)]], context=context)
            nearest_date = False
            for ews_id in ews_activity_ids:
                ews_data = {
                    'respiration_rate': fake.random_element([18]*90 + [11]*8 + [24]*2),
                    'indirect_oxymetry_spo2': fake.random_element([99]*90 + [95]*8 + [93]*2),
                    'oxygen_administration_flag': fake.random_element([False]*96 + [True]*4),
                    'blood_pressure_systolic': fake.random_element([120]*90 + [110]*8 + [100]*2),
                    'blood_pressure_diastolic': 80,
                    'avpu_text': fake.random_element(['A']*97 + ['V', 'P', 'U']),
                    'pulse_rate': fake.random_element([65]*90 + [50]*8 + [130]*2),
                    'body_temperature': fake.random_element([37.5]*93 + [36.0]*7),
                }
                ews_activity = activity_pool.browse(cr, uid, ews_id, context=context)
                n_uid = n_ids[ews_activity.location_id.parent_id.code]
                activity_pool.submit(cr, n_uid, ews_id, ews_data, context=context)
                activity_pool.complete(cr, n_uid, ews_id, context=context)
                ews_activity = activity_pool.browse(cr, uid, ews_id, context=context)
                overdue = fake.random_element([False, False, False, False, False, False, False, True, True, True])
                if overdue:
                    complete_date = current_date + td(days=1)
                else:
                    complete_date = current_date + td(minutes=ews_activity.data_ref.frequency-10)
                activity_pool.write(cr, uid, ews_id, {'date_terminated': complete_date.strftime(dtf)}, context=context)
                triggered_ews_id = activity_pool.search(cr, uid, [['creator_id', '=', ews_id], ['data_model', '=', 'nh.clinical.patient.observation.ews']], context=context)
                if not triggered_ews_id:
                    osv.except_osv('Error!', 'The NEWS observation was not triggered after previous submission!')
                triggered_ews = activity_pool.browse(cr, uid, triggered_ews_id[0], context=context)
                activity_pool.write(cr, uid, triggered_ews_id[0], {'date_scheduled': (complete_date + td(minutes=triggered_ews.data_ref.frequency)).strftime(dtf)}, context=context)
                if not nearest_date or complete_date + td(minutes=triggered_ews.data_ref.frequency) < nearest_date:
                    nearest_date = complete_date + td(minutes=triggered_ews.data_ref.frequency)
            current_date = nearest_date
        return True