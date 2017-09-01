# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


set_rapid_tranq_value_arg = None


class TestStartRapidTranq(TransactionCase):

    def setUp(self):
        super(TestStartRapidTranq, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)
        self.activity_model = self.env['nh.activity']
        self.rapid_tranq_model = self.env['nh.clinical.pme.rapid_tranq']

        self.activity_rapid_tranq = \
            self.test_utils.create_activity_rapid_tranq()
        self.rapid_tranq = self.activity_rapid_tranq.data_ref

    def test_calls_set_rapid_tranq_flag(self):
        def mock_set_rapid_tranq_flag(*args, **kwargs):
            global set_rapid_tranq_value_arg
            set_rapid_tranq_value_arg = args[1]
            return mock_set_rapid_tranq_flag.origin(*args, **kwargs)

        self.rapid_tranq_model._patch_method('set_rapid_tranq',
                                             mock_set_rapid_tranq_flag)

        try:
            self.rapid_tranq.start(self.activity_rapid_tranq.id)
            self.assertIs(set_rapid_tranq_value_arg, True)
        finally:
            self.rapid_tranq_model._revert_method('set_rapid_tranq')
