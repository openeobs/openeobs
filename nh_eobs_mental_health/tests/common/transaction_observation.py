from openerp.tests.common import TransactionCase
import logging

_logger = logging.getLogger(__name__)


class TransactionObservationCase(TransactionCase):
    """
    A class to handle the common setUp requirements of the Clinical Risk tests
    """

    def setUp(self):
        _logger.info('TransactionObservaitionCase setup')
        super(TransactionObservationCase, self).setUp()
        cr, uid = self.cr, self.uid
        self.location_pool = self.registry('nh.clinical.location')
        self.pos_pool = self.registry('nh.clinical.pos')
        self.group_pool = self.registry('res.groups')
        self.category_pool = self.registry('res.partner.category')
        self.user_pool = self.registry('res.users')
        self.context_pool = self.registry('nh.clinical.context')
        self.api_pool = self.registry('nh.eobs.api')
        self.activity_pool = self.registry('nh.activity')
        self.ews_pool = self.registry('nh.clinical.patient.observation.ews')
        self.obs_data = None
        self.expected_score = None
        self.expected_risk = None
        self.expected_freq = None

        _logger.info('Searching for hospital')
        hosp_id_search = self.location_pool.search(
            cr, uid, [['code', '=', 'SLAM'], ['usage', '=', 'hospital']]
        )
        if hosp_id_search:
            self.hospital_id = hosp_id_search[0]
        else:
            _logger.info('Creating hospital')
            self.hospital_id = self.location_pool.create(
                cr, uid, {
                    'name': 'Test Hospital',
                    'code': 'SLAM',
                    'usage': 'hospital'
                }
            )

        _logger.info('Searching for POS')
        pos_id_search = self.pos_pool.search(
            cr, uid, [['location_id', '=', self.hospital_id]]
        )
        if pos_id_search:
            self.pos_id = pos_id_search[0]
        else:
            _logger.info('Creating POS')
            self.pos_id = self.pos_pool.create(
                cr, uid, {
                    'name': 'Test POS',
                    'location_id': self.hospital_id
                }
            )

        _logger.info('Searching for nurse & adt group')
        nurse_group_ids = self.group_pool.search(
            cr, uid, [['name', 'in', ['NH Clinical Nurse Group']]])

        adt_id_search = self.user_pool.search(
            cr, uid, [['login', 'like', 'adt']]
        )
        if adt_id_search:
            self.adt_id = adt_id_search[0]
        else:
            _logger.info('Setting ADT user to UID')
            self.adt_id = uid

        _logger.info('Setting POS for ADT and UID')
        self.user_pool.write(cr, uid, uid, {'pos_id': self.pos_id})
        self.user_pool.write(cr, uid, self.adt_id, {
            'pos_id': self.pos_id,
            'pos_ids': [[6, 0, [self.pos_id]]]
        })

        _logger.info('Searching for ward')
        ward_id_search = self.location_pool.search(
            cr, uid, [
                ['usage', '=', 'ward'],
                ['parent_id', '=', self.hospital_id]
            ]
        )
        if ward_id_search:
            self.eobs_ward_id = ward_id_search[0]
        else:
            _logger.info('Creating ward')
            self.eobs_ward_id = self.location_pool.create(
                cr, uid, {
                    'name': 'Test Ward',
                    'usage': 'ward',
                    'parent_id': self.hospital_id,
                    'code': 'TESTWARD'
                }
            )

            self.eobs_ward_2_id = self.location_pool.create(
                cr, uid, {
                    'name': 'Test Ward 2',
                    'usage': 'ward',
                    'parent_id': self.hospital_id,
                    'code': 'TESTWARD2'
                }
            )

        _logger.info('Searching for bed')
        bed_ids_search = self.location_pool.search(
            cr, uid, [
                ['usage', '=', 'bed'],
                ['parent_id', '=', self.eobs_ward_id]
            ]
        )
        if bed_ids_search and len(bed_ids_search) >= 10:
            self.bed_ids = bed_ids_search[:10]
        else:
            _logger.info('Creating bed')
            bed_id = self.location_pool.create(
                cr, uid, {
                    'name': 'Test Bed 1',
                    'parent_id': self.eobs_ward_id,
                    'usage': 'bed',
                    'code': 'TESTWARDBED1'
                }
            )
            bed_2_id = self.location_pool.create(
                cr, uid, {
                    'name': 'Test Bed 2',
                    'parent_id': self.eobs_ward_2_id,
                    'usage': 'bed',
                    'code': 'TESTWARDBED2'
                }
            )
            self.bed_ids = [bed_id, bed_2_id]

        # create nurse
        _logger.info('Searching for nurse user')
        nurse_ids_search = self.user_pool.search(
            cr, uid, [
                ['login', '=', 'testnurse']
            ]
        )
        if nurse_ids_search:
            self.user_id = nurse_ids_search[0]
        else:
            _logger.info('Creating nurse user')
            nurse_dict = {
                'name': 'Test Nurse',
                'login': 'testnurse',
                'password': 'testnurse',
                'groups_id':
                    [[4, group_id] for group_id in nurse_group_ids],
                'pos_id': self.pos_id,
                'location_ids': [[6, 0, self.bed_ids]]
            }
            _logger.info('nurse data: {0}'.format(nurse_dict))
            try:
                self.user_id = self.user_pool.create(cr, uid, nurse_dict)
            except Exception as e:
                _logger.info('nurse failed {0}'.format(e))

        # register, admit and place patient
        _logger.info('Creating patient')
        self.patient_id = self.api_pool.register(
            cr, self.adt_id, 'TESTHN001',
            {
                'family_name': 'Testersen',
                'given_name': 'Test'
            }
        )
        self.patient_2_id = self.api_pool.register(
            cr, self.adt_id, 'TESTHN002',
            {
                'family_name': 'Testersen',
                'given_name': 'Test'
            }
        )
        _logger.info('Admitting patient')
        self.api_pool.admit(
            cr, self.adt_id, 'TESTHN001', {'location': 'SLAM'}
        )
        self.api_pool.admit(
            cr, self.adt_id, 'TESTHN002', {'location': 'SLAM'}
        )
        _logger.info('Finding spell')
        self.spell_id = self.activity_pool.search(
            cr, uid, [['data_model', '=', 'nh.clinical.spell'],
                      ['patient_id', '=', self.patient_id]])[0]

        self.spell_2_id = self.activity_pool.search(
            cr, uid, [['data_model', '=', 'nh.clinical.spell'],
                      ['patient_id', '=', self.patient_2_id]])[0]

        _logger.info('Finding placement')
        placement_id = self.activity_pool.search(
            cr, uid, [
                ['data_model', '=', 'nh.clinical.patient.placement'],
                ['patient_id', '=', self.patient_id],
                ['state', '=', 'scheduled']
            ]
        )

        placement_2_id = self.activity_pool.search(
            cr, uid, [
                ['data_model', '=', 'nh.clinical.patient.placement'],
                ['patient_id', '=', self.patient_2_id],
                ['state', '=', 'scheduled']
            ]
        )
        _logger.info('Submitting placement')
        self.activity_pool.submit(
            cr, uid, placement_id[0], {'location_id': self.bed_ids[0]}
        )
        self.activity_pool.submit(
            cr, uid, placement_2_id[0], {'location_id': self.bed_ids[1]}
        )
        _logger.info('completing placement')
        self.activity_pool.complete(cr, uid, placement_id[0])
        self.activity_pool.complete(cr, uid, placement_2_id[0])
        self.get_obs()

    def get_obs(self, patient_id=None):
        _logger.info('Searching for scheduled EWS for patient')
        if not patient_id:
            patient_id = self.patient_id
        ews_activity_search = self.activity_pool.search(
            self.cr,
            self.uid,
            [
                ['data_model', '=', 'nh.clinical.patient.observation.ews'],
                ['patient_id', '=', patient_id],
                ['state', '=', 'scheduled']
            ]
        )
        if ews_activity_search:
            self.ews_activity_id = ews_activity_search[0]
        else:
            raise ValueError('Could not find EWS Activity ID')

        _logger.info('Assigning EWS to user')
        self.api_pool.assign(
            self.cr,
            self.user_id,
            self.ews_activity_id,
            {'user_id': self.user_id}
        )

    def complete_obs(self, obs_data):
        # policy triggered by activity completion
        _logger.info('Completing observation with {0}'.format(obs_data))
        self.api_pool.complete(
            self.cr,
            self.user_id,
            self.ews_activity_id,
            obs_data
        )
        self.ews_activity = self.activity_pool.browse(
            self.cr,
            self.uid,
            self.ews_activity_id
        )

        _logger.info('Searching for next EWS')
        next_ews_domain = [
            ('creator_id', '=', self.ews_activity.id),
            ('state', 'not in', ['complete', 'cancelled']),
            ('data_model', '=', self.ews_pool._name)
        ]
        self.ews_activity_ids = self.activity_pool.search(self.cr, self.uid,
                                                          next_ews_domain)

        _logger.info('Searching for triggered activities')
        triggered_ids_domain = [
            ('creator_id', '=', self.ews_activity_id),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', '!=', 'nh.clinical.patient.observation.ews')
        ]
        self.triggered_ids = self.activity_pool.search(
            self.cr, self.uid, triggered_ids_domain
        )
