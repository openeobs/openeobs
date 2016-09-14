from openerp.tests.common import TransactionCase


class TestNHClinicalWardBoardEscalationTasks(TransactionCase):
    """
    Test that when a patient has escalation tasks that the method
    spell_has_open_escalation_tasks returns True and then they are none it
    returns False
    """

    def setUp(self):
        super(TestNHClinicalWardBoardEscalationTasks, self).setUp()
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

        self.activity_model._patch_method('search', patch_activity_search)

    def tearDown(self):
        self.activity_model._revert_method('search')
        super(TestNHClinicalWardBoardEscalationTasks, self).tearDown()

    def test_has_open_tasks(self):
        self.assertTrue(self.wardboard_model.spell_has_open_escalation_tasks(
            self.cr, self.uid, 1337, context={'test': 'has_activities'}))

    def test_no_open_tasks(self):
        self.assertFalse(self.wardboard_model.spell_has_open_escalation_tasks(
            self.cr, self.uid, 1337, context={'test': 'no_activities'}))
