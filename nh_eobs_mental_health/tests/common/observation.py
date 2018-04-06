from openerp.tests.common import SingleTransactionCase


class ObservationCase(SingleTransactionCase):
    """
    A class to handle the common setUp requirements of the Clinical Risk tests
    """

    @classmethod
    def setUpClass(cls):
        super(ObservationCase, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.group_pool = cls.registry('res.groups')
        cls.user_pool = cls.registry('res.users')
        cls.context_pool = cls.registry('nh.clinical.context')
        cls.api_pool = cls.registry('nh.eobs.api')
        cls.activity_pool = cls.registry('nh.activity')
        cls.ews_pool = cls.registry('nh.clinical.patient.observation.ews')
        cls.obs_data = None
        cls.expected_score = None
        cls.expected_risk = None
        cls.expected_freq = None

        hosp_id_search = cls.location_pool.search(
            cr, uid, [['code', '=', 'SLAM'], ['usage', '=', 'hospital']]
        )
        if hosp_id_search:
            cls.hospital_id = hosp_id_search[0]
        else:
            cls.hospital_id = cls.location_pool.create(
                cr, uid, {
                    'name': 'Test Hospital',
                    'code': 'SLAM',
                    'usage': 'hospital'
                }
            )

        pos_id_search = cls.pos_pool.search(
            cr, uid, [['location_id', '=', cls.hospital_id]]
        )
        if pos_id_search:
            cls.pos_id = pos_id_search[0]
        else:
            cls.pos_id = cls.pos_pool.create(
                cr, uid, {
                    'name': 'Test POS',
                    'location_id': cls.hospital_id
                }
            )

        nurse_group_ids = cls.group_pool.search(
            cr, uid, [['name', 'in', ['NH Clinical Nurse Group']]])

        adt_id_search = cls.user_pool.search(
            cr, uid, [['login', 'like', 'adt']]
        )
        if adt_id_search:
            cls.adt_id = adt_id_search[0]
        else:
            cls.adt_id = uid

        cls.user_pool.write(cr, uid, uid, {'pos_id': cls.pos_id})
        cls.user_pool.write(cr, uid, cls.adt_id, {
            'pos_id': cls.pos_id,
            'pos_ids': [[6, 0, [cls.pos_id]]]
        })

        ward_id_search = cls.location_pool.search(
            cr, uid, [
                ['usage', '=', 'ward'],
                ['parent_id', '=', cls.hospital_id]
            ]
        )
        if ward_id_search:
            cls.eobs_ward_id = ward_id_search[0]
        else:
            cls.eobs_ward_id = cls.location_pool.create(
                cr, uid, {
                    'name': 'Test Ward',
                    'usage': 'ward',
                    'parent_id': cls.hospital_id,
                    'code': 'TESTWARD'
                }
            )

        bed_ids_search = cls.location_pool.search(
            cr, uid, [
                ['usage', '=', 'bed'],
                ['parent_id', '=', cls.eobs_ward_id]
            ]
        )
        if bed_ids_search and len(bed_ids_search) >= 10:
            cls.bed_ids = bed_ids_search[:10]
        else:
            cls.bed_ids = cls.location_pool.create(
                cr, uid, {
                    'name': 'Test Bed 1',
                    'parent_id': cls.eobs_ward_id,
                    'usage': 'bed',
                    'code': 'TESTWARDBED1'
                }
            )

        # create nurse
        cls.user_id = cls.user_pool.create(
            cr, uid, {
                'name': 'Test Nurse',
                'login': 'testnurse',
                'password': 'testnurse',
                'groups_id': [[4, group_id] for group_id in nurse_group_ids],
                'pos_id': cls.pos_id,
                'location_ids': [[6, 0, [cls.bed_ids]]]
            }
        )

        # register, admit and place patient
        cls.patient_id = cls.api_pool.register(cr, cls.adt_id, 'TESTHN001', {
            'family_name': 'Testersen',
            'given_name': 'Test'
        })
        cls.api_pool.admit(
            cr, cls.adt_id, 'TESTHN001', {'location': 'SLAM'}
        )
        cls.spell_id = cls.activity_pool.search(
            cr, uid, [['data_model', '=', 'nh.clinical.spell'],
                      ['patient_id', '=', cls.patient_id]])[0]

        placement_id = cls.activity_pool.search(
            cr, uid, [
                ['data_model', '=', 'nh.clinical.patient.placement'],
                ['patient_id', '=', cls.patient_id],
                ['state', '=', 'scheduled']
            ]
        )
        if hasattr(cls.bed_ids, '__iter__'):
            location_id = cls.bed_ids[0]
        else:
            location_id = cls.bed_ids
        cls.activity_pool.submit(
            cr, uid, placement_id[0], {'location_id': location_id})
        cls.activity_pool.complete(cr, uid, placement_id[0])

    def get_obs(self):
        ews_activity_search = self.activity_pool.search(
            self.cr,
            self.uid,
            [
                ['data_model', '=', 'nh.clinical.patient.observation.ews'],
                ['patient_id', '=', self.patient_id],
                ['state', '=', 'scheduled']
            ]
        )
        if ews_activity_search:
            self.ews_activity_id = ews_activity_search[0]
        else:
            raise ValueError('Could not find EWS Activity ID')

        self.api_pool.assign(
            self.cr,
            self.user_id,
            self.ews_activity_id,
            {'user_id': self.user_id}
        )

    def setUp(self):
        super(ObservationCase, self).setUp()
        self.get_obs()

    def complete_obs(self, obs_data):
        # policy triggered by activity completion
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

        next_ews_domain = [
            ('creator_id', '=', self.ews_activity.id),
            ('state', 'not in', ['complete', 'cancelled']),
            ('data_model', '=', self.ews_pool._name)
        ]
        self.ews_activity_ids = self.activity_pool.search(self.cr, self.uid,
                                                          next_ews_domain)

        triggered_ids_domain = [
            ('creator_id', '=', self.ews_activity_id),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', '!=', 'nh.clinical.patient.observation.ews')
        ]
        self.triggered_ids = self.activity_pool.search(
            self.cr, self.uid, triggered_ids_domain
        )
