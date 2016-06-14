from openerp.tests.common import SingleTransactionCase
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestApiGetActivitiesSettingsIntegration(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestApiGetActivitiesSettingsIntegration, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        cls.api_pool = cls.registry('nh.eobs.api')
        cls.user_pool = cls.registry('res.users')
        cls.activity_pool = cls.registry('nh.activity')
        cls.settings_pool = cls.registry('nh.clinical.settings')
        cls.location_pool = cls.registry('nh.clinical.location')

        # Need to create a set of activities to be carried out before and after
        # the time defined
        wards = cls.location_pool.search(cr, uid, [['usage', '=', 'ward']])
        if not wards:
            raise ValueError('Could not find ward for test')
        beds = cls.location_pool.search(cr, uid, [
            ['usage', '=', 'bed'],
            ['parent_id', 'in', wards]
        ])
        if not beds:
            raise ValueError('Could not find bed for test')
        nurses = cls.user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical Nurse Group'],
            ['location_ids', 'in', beds]
        ])
        if not nurses:
            raise ValueError('Could not find nurse for test')
        cls.nurse = nurses[0]

        domain = [
            ('state', 'not in', ['completed', 'cancelled']),
            ('user_ids', 'in', [cls.nurse]),
            ('data_model', 'not in', ['nh.clinical.spell']),
            '|', ('user_id', '=', False), ('user_id', '=', cls.nurse)
        ]
        nurse_activities = cls.activity_pool.search(cr, uid, domain)
        if not len(nurse_activities) >= 2:
            raise ValueError('Not enough activities for user')
        cls.one_hour_act = nurse_activities[0]
        cls.twelve_hour_act = nurse_activities[1]
        one_hour = datetime.now() + timedelta(minutes=59)
        twelve_hours = datetime.now() + timedelta(minutes=719)
        cls.activity_pool.write(cr, uid, cls.one_hour_act, {
            'date_scheduled': one_hour.strftime(DTF),
            'date_deadline': one_hour.strftime(DTF),
        })
        cls.activity_pool.write(cr, uid, cls.twelve_hour_act, {
            'date_scheduled': twelve_hours.strftime(DTF),
            'date_deadline': twelve_hours.strftime(DTF),
        })

    def test_one_hour_setting(self):
        """
        Test that on the settings set to only show 60 minutes in the future
        that the one hour task should be present and the twelve hour is not
        """
        cr, uid = self.cr, self.uid
        self.settings_pool.write(cr, uid, 1, {'activity_period': 60})
        activities = self.api_pool.get_activities(self.cr, self.nurse, [])
        activity_ids = [act.get('id') for act in activities]
        self.assertIn(self.one_hour_act, activity_ids)
        self.assertNotIn(self.twelve_hour_act, activity_ids)

    def test_twelve_hour_setting(self):
        """
        Test that on the settings set to only show 720 minutes in the future
        that the one hour task and the twelve hour are present
        """
        cr, uid = self.cr, self.uid
        self.settings_pool.write(cr, uid, 1, {'activity_period': 720})
        activities = self.api_pool.get_activities(self.cr, self.nurse, [])
        activity_ids = [act.get('id') for act in activities]
        self.assertIn(self.one_hour_act, activity_ids)
        self.assertIn(self.twelve_hour_act, activity_ids)
