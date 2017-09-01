from openerp.tests.common import TransactionCase
import uuid
import copy
from datetime import datetime


class TestLocalisedTriggerTime(TransactionCase):
    """
    Test that the review task is only triggered when it's 3pm and 6am in the
    'users' timezone
    """
    def setUp(self):
        super(TestLocalisedTriggerTime, self).setUp()
        # create users with different time zones
        users_model = self.env['res.users']
        self.review_model = \
            self.env['nh.clinical.notification.food_fluid_review']
        self.dateutils_model = self.env['datetime_utils']
        self.uk_user = users_model.create({
            'login': uuid.uuid4(),
            'password': 'pass',
            'name': 'GMT user',
            'tz': 'Europe/London'
        })

        def patch_get_current_time(*args, **kwargs):
            obj = args[0]
            hours = obj.env.context.get('hours', 6)
            if obj.env.context.get('summer'):
                return datetime(2017, 7, 7, hours, 0, 0, 0)
            return datetime(1988, 01, 12, hours, 0, 0, 0)

        self.dateutils_model._patch_method(
            'get_current_time', patch_get_current_time)

    def tearDown(self):
        self.dateutils_model._revert_method('get_current_time')
        super(TestLocalisedTriggerTime, self).tearDown()

    def test_non_dst_schedule_3pm(self):
        """
        Test that when not in DST that 3pm task is executed at 15:00 UTC
        """
        ctx = copy.deepcopy(self.env.context.copy())
        ctx.update({'hours': 15})
        self.assertTrue(
            self.review_model
            .sudo(self.uk_user)
            .with_context(ctx)
            .should_trigger_review()
        )

    def test_non_dst_schedule_6am(self):
        """
        Test that when not in DST that 6am task is executed at 06:00 UTC
        """
        self.assertTrue(
            self.review_model
            .sudo(self.uk_user)
            .should_trigger_review()
        )

    def test_dst_schedule_for_3pm(self):
        """
        Test that when in DST for UK (BST) that the task is triggered at
        14:00 UTC
        """
        ctx = copy.deepcopy(self.env.context.copy())
        ctx.update({'hours': 14, 'summer': True})
        self.assertTrue(
            self.review_model
            .sudo(self.uk_user)
            .should_trigger_review()
        )

    def test_dst_schedule_for_6am(self):
        """
        Test that when in DST for UK (BST) that the task is triggered at
        14:00 UTC
        """
        ctx = copy.deepcopy(self.env.context.copy())
        ctx.update({'hours': 5, 'summer': True})
        self.assertTrue(
            self.review_model
                .sudo(self.uk_user)
                .should_trigger_review()
        )
