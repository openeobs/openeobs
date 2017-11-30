from openerp.tests.common import TransactionCase


class TestSettingsView(TransactionCase):
    """
    Test the overrides of the settings view
    """

    def setUp(self):
        """
        Set up the tests
        """
        super(TestSettingsView, self).setUp()
        self.view_model = self.env['ir.ui.view']

    def test_override_in_heirarchy(self):
        """
        Test that the override to the setting screen is in the view heirarchy
        """
        parent_view = self.view_model.search(
            [
                ['model', '=', 'base.config.settings'],
                ['mode', '=', 'primary']
            ]
        )[0]
        child_view_ids = parent_view.inherit_children_ids.ids
        our_view = self.view_model.search(
            [
                ['name', '=', 'base.config.settings.nhclinical']
            ]
        )[0]
        self.assertTrue(our_view.id in child_view_ids)
