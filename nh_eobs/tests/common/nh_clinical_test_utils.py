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
        self.nurse = self.create_nurse()
        self.hca = self.create_hca()
        self.create_and_register_patient()

        self.api_model.admit(
            self.hospital_number, {'location': 'WA'}
        )

        self.spell = self.spell_model.search(
            [('patient_id', '=', self.patient_id)]
        )[0]
        self.spell_activity_id = self.spell.activity_id.id
        self.spell_activity = self.spell_model.browse(self.spell_activity_id)

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

    def place_patient(self, location_id=None):
        if not location_id:
            location_id = self.bed.id
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
            self.placement.id, {'location_id': location_id}
        )
        self.activity_pool.complete(
            self.env.cr, self.env.uid, self.placement.id
        )

    def transfer_patient(self, location_code, hospital_number=None):
        if not hospital_number:
            hospital_number = self.hospital_number
        api_model = self.env['nh.eobs.api']
        api_model.transfer(hospital_number, {
            'location': location_code
        })

    def nursing_shift_change(self):
        ward = self.ward
        other_hca = self.create_hca(ward.id)
        other_nurse = self.create_nurse(ward.id)
        self.allocating_pool = self.env['nh.clinical.allocating']
        self.allocation_pool = self.env['nh.clinical.staff.allocation']
        wizard = self.allocation_pool.create({'ward_id': ward.id})
        wizard.submit_ward()
        wizard.deallocate()
        wizard.write({'user_ids': [[6, 0, [other_hca.id, other_nurse.id]]]})
        wizard.submit_users()
        allocating_ids = wizard.allocating_ids
        allocating_ids.write({
            'nurse_id': other_nurse.id,
            'hca_ids': [[6, 0, [other_hca.id]]],
            'location_id': self.bed.id
        })
        wizard.complete()
        return {
            'nurse': other_nurse,
            'hca': other_hca
        }
