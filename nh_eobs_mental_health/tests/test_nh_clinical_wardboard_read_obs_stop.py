from openerp.tests.common import SingleTransactionCase
import __builtin__


class PatchedReadSuper(object):

    def read(*args, **kwargs):
        return {
            'patient_id': 1,
            'next_diff': 'soon',
            'frequency': '15 Minutes'
        }


class TestNHClinicalWardboardReadObsStop(SingleTransactionCase):
    """
    Test that next_diff on wardboard is set to 'Observations Stopped' when
    obs_stop flag is set to True
    """

    @classmethod
    def setUpClass(cls):
        super(TestNHClinicalWardboardReadObsStop, cls).setUpClass()
        cls.wardboard_model = cls.registry('nh.clinical.wardboard')
        cls.spell_model = cls.registry('nh.clinical.spell')
        cls.pme_model = \
            cls.registry('nh.clinical.patient_monitoring_exception')

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
                'obs_stop': False
            }
            if test in ['obs_stopped', 'no_reason']:
                res['obs_stop'] = True
            return res

        def patch_pme_search(*args, **kwargs):
            context = kwargs.get('context', {})
            test = context.get('test', '')
            if test == 'no_reason':
                return []
            return [1]

        def patch_pme_read(*args, **kwargs):
            return {
                'reason': (1, 'Acute hospital ED')
            }

        cls.spell_model._patch_method('search', patch_spell_search)
        cls.spell_model._patch_method('read', patch_spell_read)
        cls.pme_model._patch_method('search', patch_pme_search)
        cls.pme_model._patch_method('read', patch_pme_read)

        cls.original_super = super

    def setUp(self):
        super(TestNHClinicalWardboardReadObsStop, self).setUp()
        __builtin__.super = self.patch_wardboard_read_super

    def tearDown(self):
        __builtin__.super = self.original_super
        super(TestNHClinicalWardboardReadObsStop, self).tearDown()

    @classmethod
    def tearDownClass(cls):
        __builtin__.super = cls.original_super
        cls.spell_model._revert_method('search')
        cls.spell_model._revert_method('read')
        cls.pme_model._revert_method('search')
        cls.pme_model._revert_method('read')
        super(TestNHClinicalWardboardReadObsStop, cls).tearDownClass()

    def test_next_diff_with_obs_stop(self):
        """
        Test that next_diff is set to 'Observation Stopped' when obs_stop flag
        on spell is True
        """
        cr, uid = self.cr, self.uid
        read = self.wardboard_model.read(
            cr, uid, 1, fields=['next_diff', 'patient_id'],
            context={'test': 'obs_stopped'})
        self.assertEqual(read.get('next_diff'), 'Observations Stopped')
        self.assertEqual(read.get('frequency'), 'Acute hospital ED')

    def test_next_diff_without_obs_stop(self):
        """
        Test that next_diff is set to the next EWS deadline when obs_stop flag
        on spell is False
        """
        cr, uid = self.cr, self.uid
        read = self.wardboard_model.read(cr, uid, 1,
                                         fields=['next_diff', 'patient_id'],
                                         context={'test': 'obs_not_stopped'})
        self.assertEqual(read.get('next_diff'), 'soon')
        self.assertEqual(read.get('frequency'), '15 Minutes')

    def test_next_diff_without_obs_stop_reason(self):
        """
        Test that next_diff is set to the next EWS deadline when obs_stop flag
        on spell is True but no reason
        """
        cr, uid = self.cr, self.uid
        read = self.wardboard_model.read(cr, uid, 1,
                                         fields=['next_diff', 'patient_id'],
                                         context={'test': 'no_reason'})
        self.assertEqual(read.get('next_diff'), 'Observations Stopped')
        self.assertEqual(read.get('frequency'), '15 Minutes')
