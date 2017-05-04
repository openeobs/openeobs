# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestManageReviewTasksForActivePeriods(TransactionCase):
    def setUp(self):
        super(TestManageReviewTasksForActivePeriods, self).setUp()

    def test_calls_cancel_review_tasks(self):
        pass