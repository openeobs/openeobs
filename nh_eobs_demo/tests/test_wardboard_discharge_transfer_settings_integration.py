from openerp.tests.common import TransactionCase
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestWardboardDischargeTransferSettingsIntegration(TransactionCase):

    def setUp(self):
        super(TestWardboardDischargeTransferSettingsIntegration, self).setUp()
        cr, uid = self.cr, self.uid
        self.api_pool = self.registry('nh.eobs.api')
        self.user_pool = self.registry('res.users')
        self.wardboard_pool = self.registry('nh.clinical.wardboard')
        self.patient_pool = self.registry('nh.clinical.patient')
        self.activity_pool = self.registry('nh.activity')
        self.settings_pool = self.registry('nh.clinical.settings')
        self.config_pool = self.registry('nh.clinical.config.settings')
        self.location_pool = self.registry('nh.clinical.location')

        # Need to find a patient to discharge and change their dates so can
        # check if in list
        wards = self.location_pool.search(cr, uid, [['usage', '=', 'ward']])
        if not wards:
            raise ValueError('Could not find ward for test')
        ward = wards[0]
        beds = self.location_pool.search(cr, uid, [
            ['usage', '=', 'bed'],
            ['parent_id', '=', ward]
        ])
        if not beds:
            raise ValueError('Could not find bed for test')

        patients = self.patient_pool.search(cr, uid, [
            ['current_location_id', 'in', beds]
        ])
        if not patients:
            raise ValueError('Could not find patients for test')
        self.patient = self.patient_pool.read(cr, uid, patients[0])
        self.patient_2 = self.patient_pool.read(cr, uid, patients[1])

        ward_managers = self.user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical Ward Manager Group'],
            ['location_ids', 'in', [ward]]
        ])
        if not ward_managers:
            raise ValueError('Could not find ward manager for test')
        self.ward_manager = ward_managers[0]

        adt_user = self.user_pool.search(cr, uid, [
            ['login', '=', 'adt']
        ])
        if not adt_user:
            raise ValueError('Could not find ADT user for test')
        self.adt_user = adt_user[0]

    def test_three_days_init(self):
        """
        Test that on the settings set to only show 3 days that the patient
        in for 5 days won't be shown
        """
        cr, uid = self.cr, self.uid
        self.api_pool.discharge(
            cr, self.adt_user, self.patient.get('other_identifier'),
            {'discharge_date': datetime.now().strftime(DTF)})
        self.api_pool.discharge(
            cr, self.adt_user, self.patient_2.get('other_identifier'),
            {
                'discharge_date':
                    (datetime.now() - timedelta(days=5)).strftime(DTF)
            })
        self.settings_pool.write(cr, uid, 1, {'discharge_transfer_period': 3})
        self.wardboard_pool.init(self.cr)
        wardboard = self.wardboard_pool.read(cr, self.ward_manager,
                                             self.patient.get('id'))
        wardboard_2 = self.wardboard_pool.read(cr, self.ward_manager,
                                               self.patient_2.get('id'))
        self.assertTrue(wardboard.get('recently_discharged'))
        self.assertFalse(wardboard_2.get('recently_discharged'))

    def test_three_days_config_refresh(self):
        """
        Test that on the settings set to only show 3 days that the refresh
        view will make sure that the 5 days aren't shown
        """
        cr, uid = self.cr, self.uid
        self.api_pool.discharge(
            cr, self.adt_user, self.patient.get('other_identifier'),
            {'discharge_date': datetime.now().strftime(DTF)})
        self.api_pool.discharge(
            cr, self.adt_user, self.patient_2.get('other_identifier'),
            {
                'discharge_date':
                    (datetime.now() - timedelta(days=5)).strftime(DTF)
            })
        wizard = self.config_pool.create(
            cr, uid, {
                'discharge_transfer_period': 3,
                'workload_bucket_period': [[6, 0, []]],
                'activity_period': 1
            })
        self.config_pool.set_discharge_transfer_period(cr, uid, wizard)
        wardboard = self.wardboard_pool.read(cr, self.ward_manager,
                                             self.patient.get('id'))
        wardboard_2 = self.wardboard_pool.read(cr, self.ward_manager,
                                               self.patient_2.get('id'))
        self.assertTrue(wardboard.get('recently_discharged'))
        self.assertFalse(wardboard_2.get('recently_discharged'))

    def test_ten_days_init(self):
        """
        Test that on the settings set to only show 10 days that the patient
        in for 15 days won't be shown
        """
        cr, uid = self.cr, self.uid
        self.api_pool.discharge(
            cr, self.adt_user, self.patient.get('other_identifier'),
            {
                'discharge_date':
                    (datetime.now() - timedelta(days=5)).strftime(DTF)
            })
        self.api_pool.discharge(
            cr, self.adt_user, self.patient_2.get('other_identifier'),
            {
                'discharge_date':
                    (datetime.now() - timedelta(days=15)).strftime(DTF)
            })
        self.settings_pool.write(cr, uid, 1, {'discharge_transfer_period': 10})
        self.wardboard_pool.init(self.cr)
        wardboard = self.wardboard_pool.read(cr, self.ward_manager,
                                             self.patient.get('id'))
        wardboard_2 = self.wardboard_pool.read(cr, self.ward_manager,
                                               self.patient_2.get('id'))
        self.assertTrue(wardboard.get('recently_discharged'))
        self.assertFalse(wardboard_2.get('recently_discharged'))

    def test_ten_days_config_refresh(self):
        """
        Test that on the settings set to only show 10 days that the refresh
        view will make sure that the 15 days aren't shown
        """
        cr, uid = self.cr, self.uid
        self.api_pool.discharge(
            cr, self.adt_user, self.patient.get('other_identifier'),
            {
                'discharge_date':
                    (datetime.now() - timedelta(days=5)).strftime(DTF)
            })
        self.api_pool.discharge(
            cr, self.adt_user, self.patient_2.get('other_identifier'),
            {
                'discharge_date':
                    (datetime.now() - timedelta(days=15)).strftime(DTF)
            })
        wizard = self.config_pool.create(
            cr, uid, {
                'discharge_transfer_period': 10,
                'workload_bucket_period': [[6, 0, []]],
                'activity_period': 1
            })
        self.config_pool.set_discharge_transfer_period(cr, uid, wizard)
        wardboard = self.wardboard_pool.read(cr, self.ward_manager,
                                             self.patient.get('id'))
        wardboard_2 = self.wardboard_pool.read(cr, self.ward_manager,
                                               self.patient_2.get('id'))
        self.assertTrue(wardboard.get('recently_discharged'))
        self.assertFalse(wardboard_2.get('recently_discharged'))
