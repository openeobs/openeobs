from openerp.tests.common import TransactionCase


class TestCheckLocationIdsConstraint(TransactionCase):
    """
    Test the location_ids constraint added to res.user that ensures that the
    user is unassigned from any activities related to location_ids they are no
    longer allocated to
    """

    def setUp(self):
        super(TestCheckLocationIdsConstraint, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.allocation_pool = self.env['nh.clinical.staff.allocation']
        self.user_pool = self.env['res.users']
        self.patient_pool = self.env['nh.clinical.patient']
        self.allocating_pool = self.env['nh.clinical.allocating']
        self.activity_model = self.env['nh.activity']
        self.test_utils_model.create_locations()
        self.test_utils_model.create_users()
        self.test_utils_model.create_patient()
        self.test_utils_model.admit_patient()
        self.test_utils_model.placement = \
            self.test_utils_model.create_placement()
        self.test_utils_model.place_patient()
        self.shift_coordinator = \
            self.test_utils_model.create_shift_coordinator()
        items_needed = [
            'ward',
            'nurse',
            'bed',
            'other_bed',
            'patient'
        ]
        for item in items_needed:
            self.test_utils_model.copy_instance_variable_if_exists(self, item)
        self.other_patient = \
            self.test_utils_model.create_and_register_patient()
        self.other_spell = self.test_utils_model.admit_patient(
            hospital_number=self.other_patient.other_identifier,
            location_code=self.ward.code,
            patient_id=self.other_patient.id
        )
        self.other_spell_activity_id = self.other_spell.activity_id.id
        # TODO: Rename variable as it is a spell not an activity.
        self.other_spell_activity = self.other_spell.activity_id
        self.other_placement = self.test_utils_model.create_placement(
            patient_id=self.other_patient.id,
            location_id=self.ward.id
        )
        self.test_utils_model.place_patient(
            location_id=self.other_bed.id,
            placement_activity_id=self.other_placement
        )
        self.allocation_pool.responsibility_allocation_activity(
            self.nurse.id, [self.bed.id, self.other_bed.id])

        # Create activities for user to lock
        self.activity_1 = self.activity_model.create({
            'data_model': 'nh.activity',
            'summary': 'This is a test',
            'user_id': self.nurse.id,
            'location_id': self.bed.id
        })
        self.activity_2 = self.activity_model.create({
            'data_model': 'nh.activity',
            'summary': 'This is a test',
            'user_id': self.nurse.id,
            'location_id': self.other_bed.id
        })

        self.wizard = self.allocation_pool \
            .sudo(self.shift_coordinator) \
            .create({'ward_id': self.ward.id})

        self.wizard.submit_ward()
        self.wizard.deallocate()
        self.wizard.submit_users()
        self.wizard.complete()

    def test_user_unassigned_from_task_on_dropped_bed(self):
        """
        Test that the user is unassigned from a task they have linked to a
        location they have been deallocated from
        """
        self.assertFalse(self.activity_1.user_id.ids)

    def test_user_stays_assigned_to_task_on_kept_bed(self):
        """
        Test that the user stays assigned from a task they have linked to a
        location they have kept after deallocation
        """
        self.assertEqual(self.activity_2.user_id.ids, [self.nurse.id])
