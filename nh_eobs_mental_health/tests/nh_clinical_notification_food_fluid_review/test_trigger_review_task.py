# -*- coding: utf-8 -*-
from datetime import datetime

from openerp.tests.common import TransactionCase


class TestTriggerReviewTasksWhenObsStop(TransactionCase):
    def setUp(self):
        super(TestTriggerReviewTasksWhenObsStop, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

        self.food_and_fluid_review_model = \
            self.env['nh.clinical.notification.food_fluid_review']
        self.activity_model = self.env['nh.activity']

        self.f_and_f_review_activity_id = \
            self.food_and_fluid_review_model.create_activity(
                {'spell_activity_id': self.spell_activity.id},
                {'patient_id': self.patient.id})
        self.f_and_f_review_activity = self.activity_model.browse(
            self.f_and_f_review_activity_id)

        self.datetime_utils = self.env['datetime_utils']

        def mock_get_localised_time(*args, **kwargs):
            return self.date_time

        self.datetime_utils._patch_method('get_localised_time',
                                          mock_get_localised_time)

    def tearDown(self):
        self.datetime_utils._revert_method('get_localised_time')
        super(TestTriggerReviewTasksWhenObsStop, self) \
            .tearDown()

    def call_test(self, date_time=None, spell_activity_id=None):
        if not date_time:
            date_time = datetime(1989, 6, 6, 15, 0, 0)
        self.date_time = date_time

        self.food_and_fluid_review_model \
            .manage_review_tasks_for_active_periods()

    def test_triggered_when_patient_not_in_obs_stop(self):
        domain = [
            ('data_model', '=', 'nh.clinical.notification.food_fluid_review'),
            ('spell_activity_id', '=', self.spell_activity.id)
        ]
        open_food_and_fluid_review_tasks = self.activity_model.search(domain)
        tasks_num_before = len(open_food_and_fluid_review_tasks)

        self.call_test()

        open_food_and_fluid_review_tasks = self.activity_model.search(domain)
        tasks_num_after = len(open_food_and_fluid_review_tasks)

        self.assertEqual(tasks_num_before + 1, tasks_num_after)

    def test_not_triggered_when_patient_in_obs_stop(self):
        domain = [
            ('data_model', '=', 'nh.clinical.notification.food_fluid_review'),
            ('spell_activity_id', '=', self.spell_activity.id)
        ]
        open_food_and_fluid_review_tasks = self.activity_model.search(domain)
        tasks_num_before = len(open_food_and_fluid_review_tasks)

        pme_reason = self.test_utils.browse_ref('nh_eobs.awol')
        pme_model = self.env['nh.clinical.pme.obs_stop']
        activity_id = pme_model.create_activity(
            {'spell_activity_id': self.spell_activity.id},
            {'spell': self.spell.id, 'reason': pme_reason.id}
        )
        pme_activity = self.activity_model.browse(activity_id)
        pme = pme_activity.data_ref
        pme.start(pme_activity.id)

        self.call_test()

        open_food_and_fluid_review_tasks = self.activity_model.search(domain)
        tasks_num_after = len(open_food_and_fluid_review_tasks)

        self.assertEqual(tasks_num_before, tasks_num_after)
