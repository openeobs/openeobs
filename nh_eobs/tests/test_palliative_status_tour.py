from openerp.tests.common import HttpCase
from openerp.modules.module import get_module_path


class TestPalliativeStatusTour(HttpCase):
    """
    Test that the palliative status tour passes as a test
    """

    module_path = get_module_path('nh_eobs')

    inject = [
        (
            "openerp.Tour.palliative_status_tour",
            "{0}/static/tours/palliative_status.tour.js".format(
                module_path
            )
        )
    ]

    def test_palliative_status_tour(self):
        """
        Run the palliative status change tour as a test
        """
        self.phantom_js(
            "/web",
            "openerp.Tour.run('palliative_care_flag','test')",
            "openerp.Tour.tours.palliative_care_flag",
            login="winifred",
            inject=self.inject
        )
