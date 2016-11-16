# -*- coding: utf-8 -*-
def admit_and_place_patient(self):
    admit_patient(self)
    place_patient(self)


def admit_patient(self):
    try:
        self.api_model = self.env['nh.eobs.api']
    except KeyError:
        self.api_model = self.env['nh.clinical.api']
    self.spell_model = self.env['nh.clinical.spell']
    self.patient_model = self.env['nh.clinical.patient']
    self.location_model = self.env['nh.clinical.location']
    self.user_model = self.env['res.users']
    self.pos_model = self.env['nh.clinical.pos']
    self.activity_pool = self.registry['nh.activity']
    self.activity_model = self.env['nh.activity']
    self.ews_model = self.env['nh.clinical.patient.observation.ews']
    self.context_pool = self.env['nh.clinical.context']

    hospital_search = self.location_model.search(
        [('usage', '=', 'hospital')]
    )
    if hospital_search:
        self.hospital = hospital_search[0]
    else:
        raise ValueError('Could not find hospital ID')

    pos_search = self.pos_model.search(
        [('location_id', '=', self.hospital.id)]
    )
    if pos_search:
        self.pos = pos_search[0]
    else:
        raise ValueError('Could not find POS with location ID of hospital')

    self.user = self.user_model.browse(self.env.uid)
    self.user.write(
        {
            'pos_id': self.pos.id,
            'pos_ids': [[4, self.pos.id]]
        }
    )

    self.ward = self.location_model.create(
        {
            'name': 'Ward A',
            'code': 'WA',
            'usage': 'ward',
            'parent_id': self.hospital.id,
            'type': 'poc'
        }
    )

    self.location_model.create(
        {
            'name': 'Ward B',
            'code': 'WB',
            'usage': 'ward',
            'parent_id': self.hospital.id,
            'type': 'poc'
        }
    )

    self.eobs_context = self.context_pool.search(
        [['name', '=', 'eobs']]
    )[0]

    self.bed = self.location_model.create(
        {
            'name': 'a bed', 'code': 'a bed', 'usage': 'bed',
            'parent_id': self.ward.id, 'type': 'poc',
            'context_ids': [[4, self.eobs_context.id]]
        }
    )

    self.hospital_number = 'TESTHN001'

    self.patient_id = self.api_model.register(
        self.hospital_number,
        {
            'family_name': 'Testersen',
            'given_name': 'Test'
        }
    )
    self.patient = self.patient_model.browse(self.patient_id)

    self.api_model.admit(
        self.hospital_number, {'location': 'WA'}
    )

    self.spell = self.spell_model.search(
        [('patient_id', '=', self.patient_id)]
    )[0]
    self.spell_activity_id = self.spell.activity_id.id


def place_patient(self):
    self.placement = self.activity_model.search(
        [
            ('patient_id', '=', self.patient_id),
            ('data_model', '=', 'nh.clinical.patient.placement'),
            ('state', '=', 'scheduled')
        ]
    )[0]
    self.activity_pool.submit(
        self.env.cr, self.env.uid,
        self.placement.id, {'location_id': self.bed.id}
    )
    self.activity_pool.complete(
        self.env.cr, self.env.uid, self.placement.id
    )
