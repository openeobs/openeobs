# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestRestartsEWSTasks(TransactionCase):
    """
    Test that a new EWS task is generated when the observations are restarted
    """

    def setUp(self):
        super(TestRestartsEWSTasks, self).setUp()
        self.patient_model = self.env['nh.clinical.patient']
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.wizard_model = \
            self.env['nh.clinical.patient_monitoring_exception.select_reason']

        self.patient = self.patient_model.create({
            'given_name': 'Jon',
            'family_name': 'Snow',
            'patient_identifier': 'a_patient_identifier'
        })

        self.spell_activity_id = self.spell_model.create_activity(
            {'state': 'started'},  # Fails a search later without this.
            {'patient_id': self.patient.id, 'pos_id': 1}
        )

        self.wardboard = self.wardboard_model.new(
            {
                'spell_activity_id': self.spell_activity_id,
                'patient_id': self.patient
            }
        )

    def test_ews_task_created(self):
        """
        Test that when obs_stop flag is set to False then a new EWS observation
        is scheduled for 1 hours time.
        :return:
        """
        domain = [
            ('data_model', '=', 'nh.clinical.patient.observation.ews'),
            ('spell_activity_id', '=', self.wardboard.spell_activity_id.id)
        ]
        ews_activities_before = len(self.activity_model.search(domain))
        self.wardboard.create_new_ews(None)
        ews_activities_after = len(self.activity_model.search(domain))
        self.assertTrue(ews_activities_before + 1, ews_activities_after)

    def test_ews_due_in_one_hour(self):
        """
        Test that the newly created ews task is due one hour from creation.
        """
        time_before_ews_creation = datetime.now()
        expected_time_due = time_before_ews_creation + timedelta(hours=1)
        new_ews_id = self.wardboard.create_new_ews(None)
        actual_time_due_str = \
            self.activity_model.browse(new_ews_id).date_scheduled
        actual_time_due = datetime.strptime(actual_time_due_str, DTF)
        self.assertEqual(expected_time_due.year, actual_time_due.year)
        self.assertEqual(expected_time_due.month, actual_time_due.month)
        self.assertEqual(expected_time_due.day, actual_time_due.day)
        self.assertEqual(expected_time_due.hour, actual_time_due.hour)
        self.assertEqual(expected_time_due.minute, actual_time_due.minute)
