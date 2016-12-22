# -*- coding: utf-8 -*-

from openerp.models import AbstractModel


class NhClinicalTestUtils(AbstractModel):

    _name = 'nh.clinical.test_utils'
    _inherit = 'nh.clinical.test_utils'

    # Setup methods
    def admit_and_place_patient(self):
        self.admit_patient()
        self.place_patient()

    def admit_patient(self):
        self.spell_model = self.env['nh.clinical.spell']
        self.api_model = self.env['nh.eobs.api']

        self.search_for_hospital_and_pos()
        self.create_locations()
        self.create_nurse()
        self.create_doctor()
        self.create_and_register_patient()

        self.api_model.admit(
            self.hospital_number, {'location': 'WA'}
        )

        self.spell = self.spell_model.search(
            [('patient_id', '=', self.patient_id)]
        )[0]
        self.spell_activity_id = self.spell.activity_id.id

    def create_and_register_patient(self):
        self.api_model = self.env['nh.eobs.api']
        self.patient_model = self.env['nh.clinical.patient']

        self.hospital_number = 'TESTHN001'
        self.patient_id = self.api_model.sudo().register(
            self.hospital_number,
            {
                'family_name': 'Testersen',
                'given_name': 'Test'
            }
        )
        self.patient = self.patient_model.browse(self.patient_id)

    def place_patient(self):
        self.activity_model = self.env['nh.activity']
        self.activity_pool = self.pool['nh.activity']

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

    def discharge_patient(self, hospital_number=None):
        if not hospital_number:
            hospital_number = self.hospital_number
        api_model = self.env['nh.eobs.api']
        api_model.discharge(hospital_number, {
            'location': 'DISL'
        })

    def transfer_patient(self, location_code, hospital_number=None):
        if not hospital_number:
            hospital_number = self.hospital_number
        api_model = self.env['nh.eobs.api']
        api_model.transfer(hospital_number, {
            'location': location_code
        })
