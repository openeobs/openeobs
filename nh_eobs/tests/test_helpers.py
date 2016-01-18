# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from openerp.tests.common import TransactionCase
from mock import MagicMock
from openerp.addons.nh_eobs.helpers import refresh_materialized_views


class TestRefreshMaterializedViews(TransactionCase):

    def test_RMV_decorator_calls_cr(self):
        cr, uid = self.cr, self.uid

        cr.execute = MagicMock(return_value=True)

        @refresh_materialized_views('view_1')
        def fake_complete(self, cr, uid, activity_id, context=None):
            return True

        result = fake_complete(self, cr, uid, 1)
        self.assertEqual(result, True)
        cr.execute.assert_called_with('refresh materialized view view_1;\n')
