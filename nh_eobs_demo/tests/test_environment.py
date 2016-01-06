# coding=utf-8
import logging

from openerp.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestApiDemo(TransactionCase):

    def setUp(self):
        super(TestApiDemo, self).setUp()
        cr, uid = self.cr, self.uid
        demo_loader = self.registry('nh.clinical.demo.loader')

    def test_1(self):
        pass
