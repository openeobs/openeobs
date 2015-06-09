__author__ = 'colin'
from common import NHMobileCommonTest
import helpers


class TaskPatientListTest(NHMobileCommonTest):
    def setUp(self):
        super(TaskPatientListTest, self).setUp()

        # demo data
        self.demo_data = self.create_test_data(self.cr, self.uid)
        self.nurse = self.demo_data[0]['users']['nurse']
        self.nurse2 = self.demo_data[1]['users']['nurse']

    def test_nh_eobs_mobile_base(self):
        # test head contains correct URLs
        # self.assertIn(helpers.URLS['manifest'], get_patients_html)
        pass

    def test_tasklist_when_patient(self):
        cr, uid = self.cr, self.uid

        patients = self.api.get_patients(cr, self.nurse['id'], [], context=self.context)
        for patient in patients:
            patient['url'] = '{0}{1}'.format(helpers.URLS['single_patient'], patient['id'])
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
        # test user is included in footer block
        user = '<p class="user">{0}</p>'.format(self.nurse['login'])
        self.assertIn(user, get_patients_html)

    def test_tasklist_when_patient_and_no_followers_summaries_notifications(self):
        cr, uid = self.cr, self.uid

        patients = self.api.get_patients(cr, self.nurse['id'], [], context=self.context)
        for patient in patients:
            patient['url'] = '{0}{1}'.format(helpers.URLS['single_patient'], patient['id'])
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

    def test_task_list(self):
        cr, uid = self.cr, self.uid

        # Call controller
        tasks = self.api.get_activities(cr, self.nurse['id'], [], context=self.context)
        for task in tasks:
            task['url'] = '{0}{1}'.format(helpers.URLS['single_task'], task['id'])
            task['color'] = 'level-one'
            task['trend_icon'] = 'icon-{0}-arrow'.format(task['ews_trend'])
            task['summary'] = task['summary'] if task.get('summary') else False
            task['notification_string'] = '<i class="icon-alert"></i>' if task['notification'] == True else ''

        get_task_html = self.render_template(cr, uid, 'nh_eobs_mobile.patient_task_list',
                                              {'items': tasks,
                                               'section': 'task',
                                               'username': self.nurse['display_name'],
                                               'urls': helpers.URLS})


    def test_followed_patients(self):
        cr, uid = self.cr, self.uid

        # find patients to follow
        ptf = self.api.get_patients(cr, self.nurse2['id'], [], context=self.context)
        patient_ids = [p['id'] for p in ptf]
        # assign patients to this user
        follow_activity_id = self.api.follow_invite(cr, self.nurse2['id'], patient_ids, self.nurse['id'],
                                                    context=self.context)
        self.api.complete(cr, self.nurse['id'], follow_activity_id, {}, context=self.context)
        # get patient list
        patients = self.api.get_patients(cr, self.nurse['id'], [], context=self.context)
        for patient in patients:
            patient['url'] = '{0}{1}'.format(helpers.URLS['single_patient'], patient['id'])
            patient['color'] = 'level-one'
            patient['trend_icon'] = 'icon-{0}-arrow'.format(patient['ews_trend'])
            patient['deadline_time'] = patient['next_ews_time']
            patient['summary'] = patient['summary'] if patient.get('summary') else False
        # get followed patient list
        followed_patients = self.api.get_followed_patients(cr, self.nurse['id'], context=self.context)
        for patient in followed_patients:
            patient['url'] = '{0}{1}'.format(helpers.URLS['single_patient'], patient['id'])
            patient['color'] = 'level-one'
            patient['trend_icon'] = 'icon-{0}-arrow'.format(patient['ews_trend'])
            patient['deadline_time'] = patient['next_ews_time']
            patient['summary'] = patient['summary'] if patient.get('summary') else False
        # call controller
        get_patients_html = self.render_template(cr, uid, 'nh_eobs_mobile.patient_task_list', {'items': patients,
                                                                                               'followed_items': followed_patients,
                                                                                               'section': 'patient',
                                                                                               'username': self.nurse[
                                                                                                   'display_name'],
                                                                                               'urls': helpers.URLS})
        # create test DOm
        patient_list_string = ""
        for patient in patients:
            patient_list_string += helpers.LIST_ITEM.format(url=patient['url'],
                                                            deadline=patient['deadline_time'],
                                                            full_name=patient['full_name'],
                                                            ews_score=patient['ews_score'],
                                                            trend_icon=patient['trend_icon'],
                                                            location=patient['location'],
                                                            parent_location=patient['parent_location'],
                                                            notification='',
                                                            summary='')
        patient_list_string += "<li><hr/></li>"
        for patient in followed_patients:
            patient_list_string += helpers.LIST_ITEM.format(url=patient['url'],
                                                            deadline=patient['deadline_time'],
                                                            full_name=patient['full_name'],
                                                            ews_score=patient['ews_score'],
                                                            trend_icon=patient['trend_icon'],
                                                            location=patient['location'],
                                                            parent_location=patient['parent_location'],
                                                            notification='',
                                                            summary='')
        example_html = helpers.BASE_HTML.format(content='<ul class="tasklist">{0}</ul>'.format(patient_list_string),
                                                patient_selected=' class="selected"', task_selected='',
                                                user=self.nurse['display_name'])
        # assert
        self.assertTrue(self.compare_doms(get_patients_html, example_html),
                        'DOM from Controller ain\'t the same as DOM from example')
        # profit
