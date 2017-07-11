from openerp.tests.common import SingleTransactionCase
import __builtin__


class PatchedReadSuper(object):

    def read(*args, **kwargs):
        context = kwargs.get('context', {})
        test = context.get('test', '')
        res = {
            'patient_id': 1,
            'next_diff': 'soon',
            'frequency': '15 Minutes',
            'acuity_index': 'Low'
        }
        if test == 'refused':
            res['acuity_index'] = 'Refused'
        return res


class TestReadRefusedAcuityIndex(SingleTransactionCase):
    """
    Test that next_diff and frequency are set to 'refused - value' on wardboard
    when acuity_index is set to 'Refused'
    """

    @classmethod
    def setUpClass(cls):
        super(TestReadRefusedAcuityIndex, cls).setUpClass()
        cls.wardboard_model = cls.registry('nh.clinical.wardboard')
        cls.spell_model = cls.registry('nh.clinical.spell')

        def patch_wardboard_read_super(*args, **kwargs):
            return PatchedReadSuper()

        cls.patch_wardboard_read_super = patch_wardboard_read_super

        def patch_spell_search(*args, **kwargs):
            return [1]

        def patch_spell_read(*args, **kwargs):
            context = kwargs.get('context', {})
            test = context.get('test', '')
            res = {
                'id': 1,
            }
            if test == 'refused':
                res['refusing_obs'] = True
            return res

        cls.spell_model._patch_method('search', patch_spell_search)
        cls.spell_model._patch_method('read', patch_spell_read)
        cls.original_super = super

    def setUp(self):
        super(TestReadRefusedAcuityIndex, self).setUp()
        __builtin__.super = self.patch_wardboard_read_super

    def tearDown(self):
        __builtin__.super = self.original_super
        super(TestReadRefusedAcuityIndex, self).tearDown()

    @classmethod
    def tearDownClass(cls):
        __builtin__.super = cls.original_super
        cls.spell_model._revert_method('search')
        cls.spell_model._revert_method('read')
        super(TestReadRefusedAcuityIndex, cls).tearDownClass()

    def test_next_diff_frequency_with_refused(self):
        """
        Test that next_diff is prepended to 'Refused - value' when acuity_index
        on wardboard is 'Refused'
        """
        cr, uid = self.cr, self.uid
        read = self.wardboard_model.read(
            cr, uid, 1, fields=['next_diff', 'patient_id'],
            context={'test': 'refused'})
        self.assertEqual(read.get('next_diff'), 'Refused - soon')
        self.assertEqual(read.get('frequency'), 'Refused - 15 Minutes')

    def test_next_diff_frequency_without_refused(self):
        """
        Test that next_diff is set untouched when acuity_index
        on wardboard isn't 'Refused'
        """
        cr, uid = self.cr, self.uid
        read = self.wardboard_model.read(cr, uid, 1,
                                         fields=['next_diff', 'patient_id'],
                                         context={'test': 'not_refused'})
        self.assertEqual(read.get('next_diff'), 'soon')
        self.assertEqual(read.get('frequency'), '15 Minutes')
