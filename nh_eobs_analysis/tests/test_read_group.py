# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestReadGroup(TransactionCase):

    def setUp(self):
        super(TestReadGroup, self).setUp()
        self.news_report_model = self.env['nh.eobs.news.report']

    # EOBS-2342
    def test_no_exception_raised(self):
        """
        This test is regression for a feature branch bug introduced by
        'EOBS-2269 Move onto a more recent tag of Odoo v8' which caused an
        error dialog to be shown when clicking on the 'NEWS Analysis' view.

        Clicking on the view causes a JSON-RPC request which results in the
        method call below (discovered this by inspecting the JSON-RPC request).
        Calling the method directly seemed sensible for regression as it cuts
        out the HTTP stack and some of Odoo's view framework so it's fairly
        quick to run but also not so low-level that it might miss other
        similar bugs.
        """
        self.news_report_model.read_group(
            groupby='ward_id',
            fields=['ward_id', 'on_time'],
            # Removed domain as it had a demo data ID in it and do not want
            # regression to depend on the demo data being installed.
            # Still reproduces the error without it.
            domain=[],
            lazy=False,
            limit=False,
            offset=0,
            orderby=False
        )
