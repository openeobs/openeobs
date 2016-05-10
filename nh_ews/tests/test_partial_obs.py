from openerp.tests.common import SingleTransactionCase
from itertools import product


class TestPartialObservation(SingleTransactionCase):
    """
    Test that partial observations are detected and don't trigger any
    additional actions
    """

    standard_values = {
        'respiration_rate': [18, None],
        'indirect_oxymetry_spo2': [100, None],
        'oxygen_administration_flag': [False, None],
        'body_temperature': [38.0, None],
        'blood_pressure_systolic': [120, None],
        'blood_pressure_diastolic': [80, None],
        'pulse_rate': [50, None],
        'avpu_text': ['A', None]
    }
    standard_combinations = list(product(*standard_values.values()))

    ews_keys = ['respiration_rate', 'indirect_oxymetry_spo2',
            'oxygen_administration_flag', 'body_temperature',
            'blood_pressure_systolic', 'blood_pressure_diastolic',
            'pulse_rate', 'avpu_text']

    @classmethod
    def setUpClass(cls):
        super(TestPartialObservation, cls).setUpClass()
        cls.ews_pool = cls.registry('nh.clinical.patient.observation.ews')

    # This is a gross method and should be changed to use the dynamic test
    # pattern
    def test_partial_obs(self):
        for combo in self.standard_combinations:
            def mock_ews_read(*args, **kwargs):
                none_values = '[' + ', '.join(["'" + self.ews_keys[i] + "'" for i, j in enumerate(combo) if not j]) + ']'
                return [
                    {
                        'id': '1',
                        'none_values': none_values,
                        'oxygen_administration_flag': combo[2],
                        'device_id': None,
                        'flow_rate': None,
                        'cpap_peep': None,
                        'niv_epap': None,
                        'niv_backup': None,
                        'niv_ipap': None,
                        'concentration': None
                    }
                ]
            self.ews_pool._patch_method('read', mock_ews_read)
            partial = self.ews_pool._is_partial(self.cr, self.uid, 1, None, None)['1']
            self.ews_pool._revert_method('read')
            if [self.ews_keys[i] for i, j in enumerate(combo) if not j]:
                self.assertTrue(partial)
            else:
                self.assertFalse(partial)

    def test_partial_flag_no_device(self):
        def mock_ews_read(*args, **kwargs):
            return [
                {
                    'id': '1',
                    'none_values': '[]',
                    'oxygen_administration_flag': True,
                    'device_id': None,
                    'flow_rate': None,
                    'cpap_peep': None,
                    'niv_epap': None,
                    'niv_backup': None,
                    'niv_ipap': None,
                    'concentration': None
                }
            ]

        self.ews_pool._patch_method('read', mock_ews_read)
        partial = self.ews_pool._is_partial(self.cr, self.uid, 1, None, None)[
            '1']
        self.ews_pool._revert_method('read')
        self.assertTrue(partial)

    def test_partial_flag_no_flow_or_concentration(self):
        def mock_ews_read(*args, **kwargs):
            return [
                {
                    'id': '1',
                    'none_values': '[]',
                    'oxygen_administration_flag': True,
                    'device_id': (34, 'Nasal Cannula'),
                    'flow_rate': None,
                    'cpap_peep': None,
                    'niv_epap': None,
                    'niv_backup': None,
                    'niv_ipap': None,
                    'concentration': None
                }
            ]

        self.ews_pool._patch_method('read', mock_ews_read)
        partial = self.ews_pool._is_partial(self.cr, self.uid, 1, None, None)[
            '1']
        self.ews_pool._revert_method('read')
        self.assertTrue(partial)

    def test_partial_flag_no_flow_but_concentration(self):
        def mock_ews_read(*args, **kwargs):
            return [
                {
                    'id': '1',
                    'none_values': '[]',
                    'oxygen_administration_flag': True,
                    'device_id': (34, 'Nasal Cannula'),
                    'flow_rate': None,
                    'cpap_peep': None,
                    'niv_epap': None,
                    'niv_backup': None,
                    'niv_ipap': None,
                    'concentration': 18
                }
            ]

        self.ews_pool._patch_method('read', mock_ews_read)
        partial = self.ews_pool._is_partial(self.cr, self.uid, 1, None, None)[
            '1']
        self.ews_pool._revert_method('read')
        self.assertFalse(partial)

    def test_partial_flag_flow_no_concentration(self):
        def mock_ews_read(*args, **kwargs):
            return [
                {
                    'id': '1',
                    'none_values': '[]',
                    'oxygen_administration_flag': True,
                    'device_id': (34, 'Nasal Cannula'),
                    'flow_rate': 18,
                    'cpap_peep': None,
                    'niv_epap': None,
                    'niv_backup': None,
                    'niv_ipap': None,
                    'concentration': None
                }
            ]

        self.ews_pool._patch_method('read', mock_ews_read)
        partial = self.ews_pool._is_partial(self.cr, self.uid, 1, None, None)[
            '1']
        self.ews_pool._revert_method('read')
        self.assertFalse(partial)

    def test_partial_flag_no_cpap(self):
        def mock_ews_read(*args, **kwargs):
            return [
                {
                    'id': '1',
                    'none_values': '[]',
                    'oxygen_administration_flag': True,
                    'device_id': (34, 'CPAP'),
                    'flow_rate': None,
                    'cpap_peep': None,
                    'niv_epap': None,
                    'niv_backup': None,
                    'niv_ipap': None,
                    'concentration': 18
                }
            ]

        self.ews_pool._patch_method('read', mock_ews_read)
        partial = self.ews_pool._is_partial(self.cr, self.uid, 1, None, None)[
            '1']
        self.ews_pool._revert_method('read')
        self.assertTrue(partial)

    def test_partial_flag_cpap(self):
        def mock_ews_read(*args, **kwargs):
            return [
                {
                    'id': '1',
                    'none_values': '[]',
                    'oxygen_administration_flag': True,
                    'device_id': (34, 'CPAP'),
                    'flow_rate': None,
                    'cpap_peep': 18,
                    'niv_epap': None,
                    'niv_backup': None,
                    'niv_ipap': None,
                    'concentration': 18
                }
            ]

        self.ews_pool._patch_method('read', mock_ews_read)
        partial = self.ews_pool._is_partial(self.cr, self.uid, 1, None, None)[
            '1']
        self.ews_pool._revert_method('read')
        self.assertFalse(partial)

    def test_partial_flag_no_niv(self):
        def mock_ews_read(*args, **kwargs):
            return [
                {
                    'id': '1',
                    'none_values': '[]',
                    'oxygen_administration_flag': True,
                    'device_id': (34, 'NIV BiPAP'),
                    'flow_rate': None,
                    'cpap_peep': None,
                    'niv_epap': None,
                    'niv_backup': None,
                    'niv_ipap': None,
                    'concentration': 18
                }
            ]

        self.ews_pool._patch_method('read', mock_ews_read)
        partial = self.ews_pool._is_partial(self.cr, self.uid, 1, None, None)[
            '1']
        self.ews_pool._revert_method('read')
        self.assertTrue(partial)

    def test_partial_flag_niv_backup(self):
        def mock_ews_read(*args, **kwargs):
            return [
                {
                    'id': '1',
                    'none_values': '[]',
                    'oxygen_administration_flag': True,
                    'device_id': (34, 'NIV BiPAP'),
                    'flow_rate': None,
                    'cpap_peep': None,
                    'niv_epap': None,
                    'niv_backup': 18,
                    'niv_ipap': None,
                    'concentration': 18
                }
            ]

        self.ews_pool._patch_method('read', mock_ews_read)
        partial = self.ews_pool._is_partial(self.cr, self.uid, 1, None, None)[
            '1']
        self.ews_pool._revert_method('read')
        self.assertTrue(partial)

    def test_partial_flag_niv_ipap(self):
        def mock_ews_read(*args, **kwargs):
            return [
                {
                    'id': '1',
                    'none_values': '[]',
                    'oxygen_administration_flag': True,
                    'device_id': (34, 'NIV BiPAP'),
                    'flow_rate': None,
                    'cpap_peep': None,
                    'niv_epap': None,
                    'niv_backup': None,
                    'niv_ipap': 18,
                    'concentration': 18
                }
            ]

        self.ews_pool._patch_method('read', mock_ews_read)
        partial = self.ews_pool._is_partial(self.cr, self.uid, 1, None, None)[
            '1']
        self.ews_pool._revert_method('read')
        self.assertTrue(partial)

    def test_partial_flag_niv_epap(self):
        def mock_ews_read(*args, **kwargs):
            return [
                {
                    'id': '1',
                    'none_values': '[]',
                    'oxygen_administration_flag': True,
                    'device_id': (34, 'NIV BiPAP'),
                    'flow_rate': None,
                    'cpap_peep': None,
                    'niv_epap': 18,
                    'niv_backup': None,
                    'niv_ipap': None,
                    'concentration': 18
                }
            ]

        self.ews_pool._patch_method('read', mock_ews_read)
        partial = self.ews_pool._is_partial(self.cr, self.uid, 1, None, None)[
            '1']
        self.ews_pool._revert_method('read')
        self.assertTrue(partial)

    def test_partial_flag_niv_backup_ipap(self):
        def mock_ews_read(*args, **kwargs):
            return [
                {
                    'id': '1',
                    'none_values': '[]',
                    'oxygen_administration_flag': True,
                    'device_id': (34, 'NIV BiPAP'),
                    'flow_rate': None,
                    'cpap_peep': None,
                    'niv_epap': None,
                    'niv_backup': 18,
                    'niv_ipap': 18,
                    'concentration': 18
                }
            ]

        self.ews_pool._patch_method('read', mock_ews_read)
        partial = self.ews_pool._is_partial(self.cr, self.uid, 1, None, None)[
            '1']
        self.ews_pool._revert_method('read')
        self.assertTrue(partial)

    def test_partial_flag_niv_backup_epap(self):
        def mock_ews_read(*args, **kwargs):
            return [
                {
                    'id': '1',
                    'none_values': '[]',
                    'oxygen_administration_flag': True,
                    'device_id': (34, 'NIV BiPAP'),
                    'flow_rate': None,
                    'cpap_peep': None,
                    'niv_epap': 18,
                    'niv_backup': 18,
                    'niv_ipap': None,
                    'concentration': 18
                }
            ]

        self.ews_pool._patch_method('read', mock_ews_read)
        partial = self.ews_pool._is_partial(self.cr, self.uid, 1, None, None)[
            '1']
        self.ews_pool._revert_method('read')
        self.assertTrue(partial)

    def test_partial_flag_niv_ipap_epap(self):
        def mock_ews_read(*args, **kwargs):
            return [
                {
                    'id': '1',
                    'none_values': '[]',
                    'oxygen_administration_flag': True,
                    'device_id': (34, 'NIV BiPAP'),
                    'flow_rate': None,
                    'cpap_peep': None,
                    'niv_epap': 18,
                    'niv_backup': None,
                    'niv_ipap': 18,
                    'concentration': 18
                }
            ]

        self.ews_pool._patch_method('read', mock_ews_read)
        partial = self.ews_pool._is_partial(self.cr, self.uid, 1, None, None)[
            '1']
        self.ews_pool._revert_method('read')
        self.assertTrue(partial)

    def test_partial_flag_niv_all(self):
        def mock_ews_read(*args, **kwargs):
            return [
                {
                    'id': '1',
                    'none_values': '[]',
                    'oxygen_administration_flag': True,
                    'device_id': (34, 'NIV BiPAP'),
                    'flow_rate': None,
                    'cpap_peep': None,
                    'niv_epap': 18,
                    'niv_backup': 18,
                    'niv_ipap': 16,
                    'concentration': 18
                }
            ]

        self.ews_pool._patch_method('read', mock_ews_read)
        partial = self.ews_pool._is_partial(self.cr, self.uid, 1, None, None)[
            '1']
        self.ews_pool._revert_method('read')
        self.assertFalse(partial)