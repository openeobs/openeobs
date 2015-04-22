import logging

from openerp.tests.common import SingleTransactionCase

_logger = logging.getLogger(__name__)


class TestApiDemo(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestApiDemo, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        cls.api_demo = cls.registry('nh.clinical.api.demo')

    def test_generate_patients(self):
        cr, uid = self.cr, self.uid

        self.assertEquals(10, len(self.api_demo.generate_patients(cr, uid, 10)))
        self.assertEquals(0, len(self.api_demo.generate_patients(cr, uid)))
        self.assertEquals(0, len(self.api_demo.generate_patients(cr, uid, -1)))
        self.assertRaises(TypeError, self.api_demo.generate_patients, cr, uid, "test")
