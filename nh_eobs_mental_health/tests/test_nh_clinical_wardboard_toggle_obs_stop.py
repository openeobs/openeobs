from openerp.tests.common import TransactionCase
from openerp.osv import osv


class TestNHClinicalWardBoardToggleObsStop(TransactionCase):
    """
    Test the toggle Stop Observation button
    """

    def setUp(self):
        super(TestNHClinicalWardBoardToggleObsStop, self).setUp()
        self.wardboard_model = self.registry('nh.clinical.wardboard')
        self.activity_model = self.registry('nh.activity')

        def patch_activity_search(*args, **kwargs):
            context = kwargs.get('context', {})
            test = context.get('test', '')
            output = {
                'has_activities': [1],
                'no_activities': []
            }
            return output.get(test, [])



        def patch_wardboard_read(*args, **kwargs):
            return {
                'spell_activity_id': (1, 'Spell/Visit'),
                'patient_id': (1, 'Test Patient')
            }

        self.activity_model._patch_method('search', patch_activity_search)
        self.wardboard_model._patch_method('read', patch_wardboard_read)

    def tearDown(self):
        self.activity_model._revert_method('search')
        self.wardboard_model._revert_method('read')
        super(TestNHClinicalWardBoardToggleObsStop, self).tearDown()

    def test_raises_on_open_escalation_tasks(self):
        """
        Test that toggle_obs_stop raises osv exception when spell has open
        escalation tasks
        """
        cr, uid = self.cr, self.uid
        with self.assertRaises(osv.except_osv):
            self.wardboard_model.toggle_obs_stop(
                cr, uid, 1, context={'test': 'has_activities'})
