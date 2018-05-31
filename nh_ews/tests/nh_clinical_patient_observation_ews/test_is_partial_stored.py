from openerp.addons.nh_ews.tests.common \
    import clinical_risk_sample_data as sample_obs_data
from openerp.tests.common import SavepointCase


class TestIsPartialStored(SavepointCase):
    """
    Test that the `is_partial` field is re-computed and stored when it should
    be. The `_is_partial` method is used as a reference for when an observation
    actually is partial which can be compared to the value in the database.
    """
    def setUp(self):
        super(TestIsPartialStored, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.copy_instance_variables(self)
        self.ews_model = self.env['nh.clinical.patient.observation.ews']

        self.nasal_cannula_device = \
            self.browse_ref('nh_clinical.nhc_device_type_nasal_cannula')
        self.cpap_device = self.browse_ref('nh_clinical.nhc_device_type_cpap')

    def call_test(self, create_obs_data=None, write_obs_data=None,
                  expected_creation_partial_state=None,
                  expected_write_partial_state=None):
        # The field will always be computed on creation.
        ews_activity = \
            self.test_utils_model.create_and_complete_ews_obs_activity(
                self.patient.id, self.spell.id,
                obs_data=create_obs_data
            )
        ews = ews_activity.data_ref
        self.assertEqual(expected_creation_partial_state, ews.is_partial)
        # The write tests whether the field was re-computed.
        ews.write(write_obs_data)
        self.assertEqual(expected_write_partial_state, ews.is_partial)

    def test_updated_to_full_after_adding_device(self):
        data = sample_obs_data.PARTIAL_OXYGEN_ADMINISTRATION_NO_DEVICE
        self.call_test(
            create_obs_data=data,
            write_obs_data={
                'device_id': self.nasal_cannula_device.id,
                'concentration': 18
            },
            expected_creation_partial_state=True,
            expected_write_partial_state=False
        )

    def test_updated_to_full_after_adding_missing_respiration_rate(self):
        data = sample_obs_data.PARTIAL_NO_RESPIRATION_RATE
        self.call_test(
            create_obs_data=data,
            write_obs_data={'respiration_rate': 1},
            expected_creation_partial_state=True,
            expected_write_partial_state=False
        )

    def test_updated_to_partial_after_removing_device_id(self):
        data = sample_obs_data.FULL_OXYGEN_ADMINISTRATION
        self.call_test(
            create_obs_data=data,
            write_obs_data={'device_id': None},
            expected_creation_partial_state=False,
            expected_write_partial_state=True
        )

    def test_updated_to_full_after_adding_device_and_flow_rate(self):
        data = sample_obs_data.PARTIAL_OXYGEN_ADMINISTRATION_NO_DEVICE
        self.call_test(
            create_obs_data=data,
            write_obs_data={
                'device_id': self.nasal_cannula_device.id,
                'flow_rate': 18
            },
            expected_creation_partial_state=True,
            expected_write_partial_state=False
        )

    def test_updated_to_full_after_adding_cpap_peep(self):
        data = sample_obs_data.PARTIAL_OXYGEN_ADMINISTRATION_NO_DEVICE
        data['device_id'] = self.cpap_device.id
        data['flow_rate'] = 18
        self.call_test(
            create_obs_data=data,
            write_obs_data={
                'cpap_peep': 1
            },
            expected_creation_partial_state=True,
            expected_write_partial_state=False
        )
