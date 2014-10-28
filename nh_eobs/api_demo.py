from openerp.osv import orm
from openerp import SUPERUSER_ID
import logging
from openerp.addons.nh_activity.activity import except_if
_logger = logging.getLogger(__name__)

from faker import Faker
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