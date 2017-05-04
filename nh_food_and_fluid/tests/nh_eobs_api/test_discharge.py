# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestDischarge(TransactionCase):
    def setUp(self):
        super(TestDischarge, self).setUp()

    def test_calls_cancel_last_review_task(self):
        pass
