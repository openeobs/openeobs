# -*- coding: utf-8 -*-
from datetime import datetime

from openerp.tests.common import TransactionCase


class TestPrintReport(TransactionCase):
    """
    Test the `print_report` method of the report wizard.
    """
    def setUp(self):
        """
        Patch the time so that the time cannot be the cause of any
        failures.
        """
        super(TestPrintReport, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()

        self.datetime_utils = self.env['datetime_utils']
        # Important that `pool` is used for testing V7 API.
        self.report_wizard_model = \
            self.registry('nh.clinical.observation_report_wizard')

        def patch_get_current_time(*args, **kwargs):
            return datetime(1988, 1, 12, 23, 0, 0)
        self.datetime_utils._patch_method(
            'get_current_time',
            patch_get_current_time
        )

        self.report_id = self.report_wizard_model.create(
            self.env.cr, self.env.uid,
            {
                'start_time': None,
                'end_time': None
            },
            self.env.context
        )

    def tearDown(self):
        self.datetime_utils._revert_method('get_current_time')
        super(TestPrintReport, self).tearDown()

    def test_does_not_fail_when_called_from_v7_api(self):
        """
        The base module that handles the calls from the front-end for printing
        reports calls our wizard model using the V7 API. There can therefore
        be failures  if our methods are not V7 or do not have an API decorator.

        This is a high-level method and so should fail if any of the lower
        level methods in the wizard fail.
        """
        context = {'active_id': self.test_utils.spell.id}
        self.report_wizard_model.print_report(
            self.env.cr, self.env.uid, [self.report_id], context=context)
