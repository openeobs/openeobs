from openerp.tests.common import SingleTransactionCase


class TestWorkloadPatientNameGet(SingleTransactionCase):
    """
    Test that the patient's name is accurate on the workload view
    """

    @classmethod
    def setUpClass(cls):
        super(TestWorkloadPatientNameGet, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        cls.user_pool = cls.registry('res.users')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.workload_pool = cls.registry('nh.activity.workload')
        cls.activity_pool = cls.registry('nh.activity')

        wards = cls.location_pool.search(cr, uid, [['usage', '=', 'ward']])
        if not wards:
            raise ValueError('Could not find ward for test')
        ward = wards[0]
        beds = cls.location_pool.search(cr, uid, [
            ['usage', '=', 'bed'],
            ['parent_id', '=', ward]
        ])
        if not beds:
            raise ValueError('Could not find bed for test')

        patients = cls.patient_pool.search(cr, uid, [
            ['current_location_id', 'in', beds]
        ])
        if not patients:
            raise ValueError('Could not find patients for test')
        cls.patient = cls.patient_pool.read(cr, uid, patients[0])
        activities = cls.activity_pool.search(cr, uid, [
            ['patient_id', '=', patients[0]],
            ['state', 'not in', ['cancelled', 'completed']]
        ])
        if not activities:
            raise ValueError('No activities for test')
        cls.activity = activities[0]

    def test_workload_update_patient_name(self):
        """
        Test that after a patient's details are updated that the workload
        view reflects this
        """
        cr, uid = self.cr, self.uid
        before_workload = self.workload_pool.read(cr, uid, self.activity)
        self.assertEqual(
            before_workload.get('patient_id')[1],
            self.patient.get('display_name')
        )
        self.patient_pool.write(cr, uid, self.patient.get('id'), {
            'given_name': 'Colin',
            'family_name': 'Wren',
            'middle_names': False
        })
        after_workload = self.workload_pool.read(cr, uid, self.activity)
        self.assertEqual(
            after_workload.get('patient_id')[1],
            'Wren, Colin'
        )
