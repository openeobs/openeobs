from openerp.tests.common import SavepointCase


class TestCompleteClinicalReview(SavepointCase):

    def setUp(self):
        super(TestCompleteClinicalReview, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.copy_instance_variables(self)

        self.clinical_review_model = \
            self.env['nh.clinical.notification.clinical_review']
        self.clinical_review_model.create({
            'patient_id': self.patient.id
        })
        self.clinical_review_activity_id = \
            self.clinical_review_model.create_activity(
                {
                    'parent_id': self.spell_activity.id,
                },
                {
                    'patient_id': self.patient.id
                }
            )

    def test_doctor_can_complete_clinical_review_task(self):
        self.api_model = self.env['nh.eobs.api']
        self.api_model.sudo(self.doctor).complete(
            self.clinical_review_activity_id, {})
