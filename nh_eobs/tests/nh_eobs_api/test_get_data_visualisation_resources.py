from openerp.tests.common import TransactionCase


class TestGetDataVisualisationResources(TransactionCase):
    """
    Test that the get_data_visualisation_resources method iterates through
    the installed observation modules and returns a list of dictionaries
    containing:
    - Display name
    - data model
    - URL of JS file that draws the chart
    """

    def setUp(self):
        super(TestGetDataVisualisationResources, self).setUp()
        self.api_model = self.env['nh.eobs.api']
        self.mod_list = [
            mod for mod in self.env.registry.models
            if 'nh.clinical.patient.observation.' in mod
            ]

        def patch_get_data_visualisation_resource(*args, **kwargs):
            return None

        for mod in self.mod_list:
            self.env[mod]._patch_method(
                'get_data_visualisation_resource',
                patch_get_data_visualisation_resource
            )

    def tearDown(self):
        super(TestGetDataVisualisationResources, self).tearDown()
        for mod in self.mod_list:
            self.env[mod]._revert_method('get_data_visualisation_resource')

    def test_no_data_vis_resources(self):
        """
        Test that when no modules have resources for data visualisation it
        returns an empty list
        """
        data_vis = self.api_model.get_data_visualisation_resources()
        self.assertEqual(data_vis, [])

    def test_module_defines_data_vis_resource(self):
        """
        Test that when a module has a data visualisation resource defined
        that it returns that resource in a dictionary
        """
        # revert first module so can repatch it
        mod = self.mod_list[0]
        model = self.env[mod]
        test_resource = '/nh_fake/static/src/js/chart.js'

        def new_patch_method(*args, **kwargs):
            return test_resource

        model._revert_method('get_data_visualisation_resource')
        model._patch_method(
            'get_data_visualisation_resource',
            new_patch_method)
        data_vis = self.api_model.get_data_visualisation_resources()
        obs_prefix = 'nh.clinical.patient.observation.'
        self.assertEqual(
            data_vis,
            [
                {
                    'data_model': mod.replace(obs_prefix, ''),
                    'resource': test_resource,
                    'model_name': model._description
                }
            ]
        )
