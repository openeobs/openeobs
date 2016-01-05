from openerp.tests.common import HttpCase
from openerp.modules.module import get_module_path


class TestStaffAllocationTours(HttpCase):
    """
    Test that the nursing allocation tours pass as tests
    """

    module_path = get_module_path('nh_eobs')

    inject = [
        (
            "openerp.Tour.staff_allocation",
            "{0}/static/tour/staff_allocation.tour.js".format(
                module_path
            )
        )
    ]

    def test_nursing_shift_change_tour(self):
        """
        Run the nursing shift change tour as a test
        """
        self.phantom_js(
            "/web",
            "openerp.Tour.run('nursing_shift_change','test')",
            "openerp.Tour.tours.nursing_shift_change",
            login="winifred",
            inject=self.inject
        )

    def test_nursing_reallocation_tour(self):
        """
        Run the nursing staff reallocation tour as a test
        """
        self.phantom_js(
            "/web",
            "openerp.Tour.run('nursing_reallocation','test')",
            "openerp.Tour.tours.nursing_reallocation",
            login="winifred",
            inject=self.inject
        )