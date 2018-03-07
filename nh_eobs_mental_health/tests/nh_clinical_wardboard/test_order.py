# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestOrder(TransactionCase):
    """
    Test the default order for wardboard records which is set on the `_order`
    class variable on the model.
    """
    def setUp(self):
        super(TestOrder, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.setup_ward()

        self.patients = []
        self.patient_ids = []
        self.beds = []
        for i in range(4):
            patient_number = i + 1
            patient = self.test_utils.create_patient()
            self.test_utils.admit_patient(
                hospital_number=patient.other_identifier,
                patient_id=patient.id)
            bed = self.test_utils.create_location(
                'bed', self.test_utils.ward.id)
            bed.name = 'Bed {}'.format(patient_number)
            self.test_utils.create_placement()
            self.test_utils.place_patient(location_id=bed.id)

            setattr(self, 'patient_{}'.format(patient_number), patient)
            setattr(self, 'patient_{}_bed'.format(patient_number), bed)

            self.patients.append(patient)
            self.patient_ids.append(patient.id)
            self.beds.append(bed)

        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.spell_model = self.env['nh.clinical.spell']

    def call_test(self, expected_patient_ids_order):
        records_dict = self.wardboard_model.search_read(
            [('patient_id', 'in', self.patient_ids)])
        actual_patient_ids_order = map(
            lambda wardboard: wardboard['patient_id'][0], records_dict)
        self.assertEqual(expected_patient_ids_order, actual_patient_ids_order)

    def _set_rapid_tranq_for_patient(self, patient_number):
        patient = getattr(self, 'patient_{}'.format(patient_number))
        spell = self.spell_model.search([
            ('patient_id', '=', patient.id)
        ])
        spell.ensure_one()
        spell.rapid_tranq = True

    def test_ordered_by_location_name_ascending(self):
        self.call_test(self.patient_ids)

    def test_patients_on_rapid_tranq_come_first(self):
        self._set_rapid_tranq_for_patient(3)

        expected_patient_ids = [
            self.patient_3.id,
            self.patient_1.id,
            self.patient_2.id,
            self.patient_4.id
        ]
        self.call_test(expected_patient_ids)

    def test_ordered_by_rapid_tranq_then_location_name_ascending(self):
        self._set_rapid_tranq_for_patient(3)
        self._set_rapid_tranq_for_patient(2)

        expected_patient_ids = [
            self.patient_2.id,
            self.patient_3.id,
            self.patient_1.id,
            self.patient_4.id
        ]
        self.call_test(expected_patient_ids)
