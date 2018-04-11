from copy import deepcopy

from openerp.tests.common import SavepointCase

from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data


class TestGetO2Display(SavepointCase):

    def setUp(self):
        super(TestGetO2Display, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.copy_instance_variables(self)

        self.ews_model = self.env['nh.clinical.patient.observation.ews']

        self.obs_data = deepcopy(clinical_risk_sample_data.NO_RISK_DATA)

    def call_test(self, oxygen_administration_flag=None, expected=None):
        self.obs_data['patient_id'] = self.patient.id
        self.obs_data['oxygen_administration_flag'] = \
            oxygen_administration_flag
        ews = self.ews_model.create(self.obs_data)

        actual = ews.o2_display
        self.assertEqual(expected, actual)

    def test_oxygen_administration_flag_is_true_with_no_other_data(self):
        """
        Value should be an empty string when there is no data in the
        `flow_rate`, `concentration`, or `device_id` fields.
        """
        self.call_test(oxygen_administration_flag=True, expected='')

    def test_oxygen_administration_flag_is_false(self):
        """
        Value should be an empty string when no oxygen was administered.
        """
        self.call_test(oxygen_administration_flag=False, expected='')
