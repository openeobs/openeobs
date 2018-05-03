from openerp.exceptions import ValidationError
from openerp.tests.common import SavepointCase


class TestCreate(SavepointCase):

    def setUp(self):
        super(TestCreate, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.copy_instance_variables(self)

        self.therapeutic_observation_model = \
            self.env['nh.clinical.patient.observation.therapeutic']
        self.therapeutic_level_model = \
            self.env['nh.clinical.therapeutic.level']

    def test_sets_patient_therapeutic_level_when_one_exists(self):
        expected_therapeutic_level = self.therapeutic_level_model.create({
            'patient': self.patient.id,
            'level': 1
        })
        therapeutic_observation = self.therapeutic_observation_model.create({
            'patient_id': self.patient.id,
            'patient_status': 'AW'
        })
        actual_therapeutic_level = therapeutic_observation.patient_level
        self.assertEqual(expected_therapeutic_level, actual_therapeutic_level)

    def test_still_creates_when_no_patient_therapeutic_level_exists(self):
        therapeutic_observation = self.therapeutic_observation_model.create({
            'patient_id': self.patient.id,
            'patient_status': 'AW'
        })
        self.assertFalse(therapeutic_observation.patient_level)

    def test_raises_when_location_field_value_is_over_100_characters(self):
        too_long_location = 'a' * 101
        with self.assertRaises(ValidationError):
            self.therapeutic_observation_model.create({
                'patient_id': self.patient.id,
                'patient_status': 'AW',
                'location': too_long_location
            })
