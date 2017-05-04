# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestTransfer(TransactionCase):
    def setUp(self):
        super(TestTransfer, self).setUp()

    def test_calls_cancel_last_review_task(self):
        pass
