__author__ = 'colin'
from common import NHMobileCommonTest
import helpers


class TaskPatientListTest(NHMobileCommonTest):
    def setUp(self):
        super(TaskPatientListTest, self).setUp()

        self.demo_data = self.create_test_data(self.cr, self.uid)
        self.nurse = self.demo_data[0]['users']['nurse']
        self.nurse2 = self.demo_data[1]['users']['nurse']

    def test_tasklist_when_patient(self):
        cr, uid = self.cr, self.uid

        patients = self.api.get_patients(cr, self.nurse['id'], [],
                                         context=self.context)
        for patient in patients:
            patient['url'] = '{0}{1}'.format(helpers.URLS['single_patient'],
                                             patient['id'])
            patient['color'] = 'level-one'
            patient['trend_icon'] = 'icon-{0}-arrow'.format(patient['ews_trend'])
            patient['deadline_time'] = patient['next_ews_time']
            patient['summary'] = "This is a summary for %s" % patient['id']
            patient['follower_ids'] = [self.nurse['id'], self.nurse2['id']]
            patient['notification'] = True

        get_patients_html = self.render_template(
            cr, uid, 'nh_eobs_mobile.patient_task_list',
            {'items': patients, 'section': 'patient',
             'username': self.nurse['display_name'],
             'urls': helpers.URLS, 'user_id': self.nurse['id']})

        # when "section=='patient'"
        self.assertIn(helpers.URLS['task_list'], get_patients_html)
        self.assertIn(helpers.URLS['patient_list'], get_patients_html)

        for patient in patients:
            self.assertIn(patient['url'], get_patients_html)
            self.assertIn(patient['deadline_time'], get_patients_html)
            self.assertIn(patient['full_name'], get_patients_html)
            self.assertIn(patient['ews_score'], get_patients_html)
            self.assertIn(patient['trend_icon'], get_patients_html)
            self.assertIn(patient['location'], get_patients_html)
            self.assertIn(patient['parent_location'], get_patients_html)
            self.assertIn(patient['summary'], get_patients_html)

        # test 'follower_ids'
        self.assertIn('Claim', get_patients_html)
        # test 'notification'
        self.assertIn('<i class="icon-alert"></i>', get_patients_html)
        # test javascript element
        self.assertIn("var patient_list", get_patients_html)

    def test_tasklist_when_patient_and_no_followers_summaries_notifications(self):
        cr, uid = self.cr, self.uid

        patients = self.api.get_patients(cr, self.nurse['id'], [],
                                         context=self.context)
        for patient in patients:
            patient['url'] = '{0}{1}'.format(helpers.URLS['single_patient'],
                                             patient['id'])
            patient['color'] = 'level-one'
            patient['trend_icon'] = 'icon-{0}-arrow'.format(patient['ews_trend'])
            patient['deadline_time'] = patient['next_ews_time']
            patient['summary'] = False
            patient['notification'] = False
            patient['follower_ids'] = [self.nurse2['id']]

        get_patients_html = self.render_template(
            cr, uid, 'nh_eobs_mobile.patient_task_list',
            {'items': patients, 'section': 'patient',
             'username': self.nurse['display_name'],
             'urls': helpers.URLS, 'user_id': self.nurse['id']})

        # test 'follower_ids'
        self.assertNotIn('<p class="aside">Claim</p>', get_patients_html)
        # test no 'notification' icon is displayed
        self.assertNotIn('<i class="icon-alert"></i>', get_patients_html)
        # test for that no 'summary' is displayed
        self.assertIn('<p class="taskInfo"><br/></p>', get_patients_html)

    def test_tasklist_when_task(self):
        cr, uid = self.cr, self.uid

        tasks = self.api.get_activities(cr, self.nurse['id'], [],
                                        context=self.context)
        for task in tasks:
            task['url'] = '{0}{1}'.format(helpers.URLS['single_task'],
                                          task['id'])
            task['color'] = 'level-one'
            task['trend_icon'] = 'icon-{0}-arrow'.format(task['ews_trend'])
            task['summary'] = "This is a summary for %s" % task['id']
            task['notification'] = True
            task['follower_ids'] = [self.nurse['id'], self.nurse2['id']]

        get_task_html = self.render_template(
            cr, uid, 'nh_eobs_mobile.patient_task_list',
            {'items': tasks, 'section': 'task',
             'username': self.nurse['display_name'],
             'urls': helpers.URLS, 'user_id': self.nurse['id']})

        # when "section==task"
        self.assertIn(helpers.URLS['task_list'], get_task_html)
        self.assertIn(helpers.URLS['patient_list'], get_task_html)

        for task in tasks:
            self.assertIn(task['url'], get_task_html)
            self.assertIn(task['color'], get_task_html)
            self.assertIn(task['trend_icon'], get_task_html)
            self.assertIn(task['location'], get_task_html)
            self.assertIn(task['parent_location'], get_task_html)
            self.assertIn(task['summary'], get_task_html)

        # test 'follower_ids'
        self.assertIn('Claim', get_task_html)
        # test 'notification'
        self.assertIn('<i class="icon-alert"></i>', get_task_html)
        # test javascript element
        self.assertIn("var patient_list", get_task_html)

    def test_tasklist_when_task_and_no_followers_summaries_notifications(self):
        cr, uid = self.cr, self.uid

        tasks = self.api.get_activities(cr, self.nurse['id'], [],
                                        context=self.context)
        for task in tasks:
            task['url'] = '{0}{1}'.format(helpers.URLS['single_task'],
                                          task['id'])
            task['color'] = 'level-one'
            task['trend_icon'] = 'icon-{0}-arrow'.format(task['ews_trend'])
            task['summary'] = False
            task['notification'] = False
            task['follower_ids'] = [self.nurse2['id']]

        get_task_html = self.render_template(
            cr, uid, 'nh_eobs_mobile.patient_task_list',
            {'items': tasks, 'section': 'task',
             'username': self.nurse['display_name'],
             'urls': helpers.URLS, 'user_id': self.nurse['id']})

        # test 'follower_ids'
        self.assertNotIn('<p class="aside">Claim</p>', get_task_html)
        # test no 'notification' icon is displayed
        self.assertNotIn('<i class="icon-alert"></i>', get_task_html)
        # test for that no 'summary' is displayed
        self.assertIn('<p class="taskInfo"><br/></p>', get_task_html)

    def test_followed_patients(self):
        cr, uid = self.cr, self.uid

        patients_to_follow = self.api.get_patients(cr, self.nurse2['id'], [],
                                                   context=self.context)
        patient_ids = [patient['id'] for patient in patients_to_follow]
        follow_activity_id = self.api.follow_invite(cr, self.nurse2['id'],
                                                    patient_ids,
                                                    self.nurse['id'],
                                                    context=self.context)
        self.api.complete(cr, self.nurse['id'], follow_activity_id, {},
                          context=self.context)

        patients = self.api.get_patients(cr, self.nurse['id'], [],
                                         context=self.context)
        for patient in patients:
            patient['url'] = '{0}{1}'.format(helpers.URLS['single_patient'],
                                             patient['id'])
            patient['color'] = 'level-one'
            patient['trend_icon'] = 'icon-{0}-arrow'.format(patient['ews_trend'])
            patient['deadline_time'] = patient['next_ews_time']
            patient['summary'] = patient['summary'] if patient.get('summary') else False

        followed_patients = self.api.get_followed_patients(
            cr, self.nurse['id'], context=self.context)
        for patient in followed_patients:
            patient['url'] = '{0}{1}'.format(helpers.URLS['single_patient'],
                                             patient['id'])
            patient['color'] = 'level-one'
            patient['trend_icon'] = 'icon-{0}-arrow'.format(patient['ews_trend'])
            patient['deadline_time'] = patient['next_ews_time']
            patient['summary'] = patient['summary'] if patient.get('summary') else False

        get_patients_html = self.render_template(
            cr, uid, 'nh_eobs_mobile.patient_task_list',
            {'items': patients, 'followed_items': followed_patients,
             'section': 'patient', 'username': self.nurse['display_name'],
             'urls': helpers.URLS})

        for patient in followed_patients:
            self.assertIn(patient['url'], get_patients_html)
            self.assertIn(patient['deadline_time'], get_patients_html)
            self.assertIn(patient['location'], get_patients_html)
            self.assertIn(patient['parent_location'], get_patients_html)
            self.assertIn(patient['color'], get_patients_html)

