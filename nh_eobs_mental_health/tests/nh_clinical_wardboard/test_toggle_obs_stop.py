from openerp.tests.common import TransactionCase


class TestToggleObsStop(TransactionCase):
    """
    Test the toggle Stop Observation button
    """
    def setUp(self):
        super(TestToggleObsStop, self).setUp()
        self.wardboard_model = self.registry('nh.clinical.wardboard')
        self.activity_model = self.registry('nh.activity')
        self.spell_model = self.registry('nh.clinical.spell')

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

        def patch_spell_search(*args, **kwargs):
            return [1]

        def patch_spell_read(*args, **kwargs):
            return {
                'obs_stop': False
            }

        self.activity_model._patch_method('search', patch_activity_search)
        self.wardboard_model._patch_method('read', patch_wardboard_read)
        self.spell_model._patch_method('search', patch_spell_search)
        self.spell_model._patch_method('read', patch_spell_read)

    def tearDown(self):
        self.activity_model._revert_method('search')
        self.wardboard_model._revert_method('read')
        self.spell_model._revert_method('read')
        self.spell_model._revert_method('search')
        super(TestToggleObsStop, self).tearDown()
