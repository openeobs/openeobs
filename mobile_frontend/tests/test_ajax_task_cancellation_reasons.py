__author__ = 'colin'

import openerp.tests
import helpers

class TestAjaxTaskCancellationReasons(openerp.tests.HttpCase):

    # test score calculation ajax
    def test_ajax_task_cancellation_reasons(self):
        self.phantom_js('/ajax_test/', helpers.TASK_CANCELLATION_REASONS_AJAX, 'document', login='norah')