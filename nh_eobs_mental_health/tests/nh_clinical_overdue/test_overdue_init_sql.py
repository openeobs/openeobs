from datetime import datetime

from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestOverdueInitSQL(TransactionCase):
    """
    Test that the override of the nh.clinical.doctor_activities SQL view is
    returning new activities
    """

    def setUp(self):
        super(TestOverdueInitSQL, self).setUp()
        self.patient_model = self.env['nh.clinical.patient']
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.location_model = self.env['nh.clinical.location']
        self.user_model = self.env['res.users']
        self.group_model = self.env['res.groups']
        self.pos_model = self.env['nh.clinical.pos']
        self.api_model = self.env['nh.eobs.api']

        # Create ward
        hosp_id_search = self.location_model.search(
            [['usage', '=', 'hospital']])
        hosp_id = hosp_id_search[0].id
        pos_id_search = self.pos_model.search([['location_id', '=', hosp_id]])
        pos_id = pos_id_search[0]
        ward = self.location_model.create({
            'code': 'TESTWARD_A',
            'usage': 'ward',
            'name': 'Test Ward',
            'parent_id': hosp_id
        })
        bed = self.location_model.create({
            'code': 'TESTWARD_AB1',
            'usage': 'bed',
            'name': 'Test Ward Bed 1',
            'parent_id': ward.id
        })
        # Create doctor user
        doctor_group_id = self.group_model.search(
            [['name', 'in', ['NH Clinical Doctor Group']]])
        doctor = self.user_model.create(
            {
                'name': 'Test Nurse',
                'login': 'testnurse',
                'password': 'testnurse',
                'groups_id': [[4, doctor_group_id.id]],
                'pos_id': pos_id.id,
                'location_ids': [[6, 0, [ward.id, bed.id]]]
            }
        )
        # Create patient
        admin_user = self.user_model.browse(self.uid)
        admin_user.write({
            'pos_id': pos_id.id,
            'pos_ids': [[6, 0, [pos_id.id]]]
        })
        # Place patient in ward
        self.registration_id = self.api_model.register('TESTHN001', {
            'family_name': 'Testersen',
            'given_name': 'Test'
        })
        self.registration_model = self.env['nh.clinical.adt.patient.register']
        self.registration = self.registration_model.browse(
            self.registration_id)
        self.patient = self.registration.patient_id
        self.patient_id = self.patient.id

        self.api_model.admit('TESTHN001', {'location': 'TESTWARD_A'})
        spell_activity_id = self.activity_model.search(
            [
                ['data_model', '=', 'nh.clinical.spell'],
                ['patient_id', '=', self.patient_id]
            ])[0]
        placement_id = self.activity_model.search(
            [
                ['data_model', '=', 'nh.clinical.patient.placement'],
                ['patient_id', '=', self.patient_id],
                ['state', '=', 'scheduled']
            ]
        )
        placement_act = placement_id[0]
        placement_act.submit({'location_id': bed.id})
        placement_act.complete()
        # Create activities for patient
        clinical_review_model = \
            self.env['nh.clinical.notification.clinical_review']
        due_date = datetime.now().strftime(DTF)
        self.clinical_review_id = clinical_review_model.create_activity({
            'creator_id': spell_activity_id.id,
            'parent_id': spell_activity_id.id,
            'date_scheduled': due_date,
            'date_deadline': due_date
        },
            {
                'patient_id': self.patient_id
            })

        clinical_review_frequency_model = \
            self.env['nh.clinical.notification.clinical_review_frequency']
        self.clinical_review_frequency_id = \
            clinical_review_frequency_model.create_activity(
                {
                    'creator_id': spell_activity_id.id,
                    'parent_id': spell_activity_id.id,
                    'date_scheduled': due_date,
                    'date_deadline': due_date
                },
                {
                    'patient_id': self.patient_id,
                    'observation': 'nh.clinical.patient.observation.ews'
                }
            )

        doc_assess_model = \
            self.env['nh.clinical.notification.doctor_assessment']
        self.doctor_assessment_id = doc_assess_model.create_activity({
            'creator_id': spell_activity_id.id,
            'parent_id': spell_activity_id.id,
            'date_scheduled': due_date,
            'date_deadline': due_date
        },
            {
                'patient_id': self.patient_id
            })

        self.overdue_tasks_model = self.env['nh.clinical.overdue']
        self.overdue_tasks = self.overdue_tasks_model.search_read(
            [['user_ids', 'in', [doctor.id]]])

    def test_doctor_assessment_for_doctor(self):
        """
        Test that the override returns the
        nh.clinical.notification.doctor_assessment task and that the group
        for the task is 'Doctor'
        """
        doctor_assessment = \
            [task for task in self.overdue_tasks
             if task.get('display_name') == 'Assessment Required']
        self.assertEqual(1, len(doctor_assessment))
        self.assertEqual(doctor_assessment[0].get('groups'), 'Doctor')

    def test_clinical_review_for_doctor(self):
        """
        Test that the override returns the
        nh.clinical.notification.clinical_review task and that the group
        for the task is 'Doctor'
        """
        clinical_review = \
            [task for task in self.overdue_tasks
             if task.get('display_name') == 'Clinical Review']
        self.assertEqual(1, len(clinical_review))
        self.assertEqual(clinical_review[0].get('groups'), 'Doctor')

    def test_clinical_review_frequency_for_doctor(self):
        """
        Test that the override returns the
        nh.clinical.notification.clinical_review_frequency task and that the
        group for the task is 'Doctor'.
        """
        clinical_review_frequency = \
            [task for task in self.overdue_tasks
             if task.get('display_name') == 'Clinical Review Frequency']
        self.assertEqual(1, len(clinical_review_frequency))
        self.assertEqual(clinical_review_frequency[0].get('groups'),
                         'Nurse, Doctor')
