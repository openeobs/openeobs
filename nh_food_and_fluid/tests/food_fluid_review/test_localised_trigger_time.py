from openerp.tests.common import TransactionCase
import uuid
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
        self.gmt_user = users_model.create({
            'login': uuid.uuid4(),
            'password': 'pass',
            'name': 'GMT user',
            'tz': 'Etc/GMT'
        })
        self.bst_user = users_model.create({
            'login': uuid.uuid4(),
            'password': 'pass',
            'name': 'BST user',
            'tz': 'Etc/GMT-1'
        })
        self.utc_plus_12_user = users_model.create({
            'login': uuid.uuid4(),
            'password': 'pass',
            'name': 'UTC+12 user',
            'tz': 'Etc/GMT+12'
        })

        def patch_get_current_time(*args, **kwargs):
            obj = args[0]
            hours = obj._context.get('hours', 6)
            return datetime(1988, 1, 12, hours, 0, 0, 0)

        self.dateutils_model._patch_method(
            'get_current_time', patch_get_current_time)

    def tearDown(self):
        self.dateutils_model._revert_method('get_current_time')
        super(TestLocalisedTriggerTime, self).tearDown()

    def test_gmt_timezone(self):
        """
        Test that GMT timezone will trigger task at 15:00 +0000 and 06:00 +0000
        """
        self.assertTrue(
            self.review_model.sudo(self.gmt_user).should_trigger_review()
        )

    def test_bst_timezone(self):
        """
        Test that BST timezone will trigger task at 15:00 +0100 and 06:00 +0100
        """
        ctx = self.env.context.copy()
        ctx.update({'hours': 5})
        self.assertTrue(
            self.review_model
            .sudo(self.bst_user)
            .with_context(ctx)
            .should_trigger_review()
        )
        self.assertFalse(
            self.review_model
            .sudo(self.bst_user)
            .should_trigger_review()
        )

    def test_utc_plus_12_timezone(self):
        """
        Test that UTC + 12 timezone will trigger task at 15:00 +1200 and
        06:00 +1200
        """
        ctx = self.env.context.copy()
        ctx.update({'hours': 18})
        self.assertTrue(
            self.review_model
            .sudo(self.utc_plus_12_user)
            .with_context(ctx)
            .should_trigger_review()
        )
        self.assertFalse(
            self.review_model
            .sudo(self.utc_plus_12_user)
            .should_trigger_review()
        )
