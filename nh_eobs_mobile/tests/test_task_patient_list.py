__author__ = 'colin'
from common import NHMobileCommonTest
import helpers

class TaskPatientListTest(NHMobileCommonTest):

    def setUp(self):
        super(TaskPatientListTest, self).setUp()

        # demo data
        demo_data = self.create_test_data(self.cr, self.uid)[0]
        self.nurse = demo_data['users']['nurse']

    def test_patient_list(self):
        cr, uid = self.cr, self.uid

        # get patients
        patients = self.api.get_patients(cr, self.nurse['id'], [], context=self.context)
        for patient in patients:
            patient['url'] = '{0}{1}'.format(helpers.URLS['single_patient'], patient['id'])
            patient['color'] = 'level-one'
            patient['trend_icon'] = 'icon-{0}-arrow'.format(patient['ews_trend'])
            patient['deadline_time'] = patient['next_ews_time']
            patient['summary'] = patient['summary'] if patient.get('summary') else False

        get_patients_html = self.render_template(cr, uid, 'nh_eobs_mobile.patient_task_list', {'items': patients,
                                                                                               'section': 'patient',
                                                                                               'username': self.nurse['display_name'],
                                                                                               'urls': helpers.URLS})

        # Create BS instances
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
        example_html = helpers.BASE_HTML.format(content='<ul class="tasklist">{0}</ul>'.format(patient_list_string), patient_selected=' class="selected"', task_selected='', user=self.nurse['display_name'])

        # test
        self.assertTrue(self.compare_doms(get_patients_html, example_html),
                        'DOM from Controller ain\'t the same as DOM from example')

    def test_task_list(self):
        cr, uid = self.cr, self.uid

        # Call controller
        tasks = self.api.get_activities(cr, self.nurse['id'], [], context=self.context)
        for task in tasks:
            task['url'] = '{0}{1}'.format(helpers.URLS['single_task'], task['id'])
            task['color'] = 'level-one'
            task['trend_icon'] = 'icon-{0}-arrow'.format(task['ews_trend'])
            task['summary'] = task['summary'] if task.get('summary') else False
            task['notification_string'] = '<i class="icon-alert"></i>' if task['notification']==True else ''

        generated_html = self.render_template(cr, uid, 'nh_eobs_mobile.patient_task_list',
                                              {'items': tasks,
                                               'section': 'task',
                                               'username': self.nurse['display_name'],
                                               'urls': helpers.URLS})

        # Create BS instances
        task_list_string = ""
        for task in tasks:
            task_list_string += helpers.LIST_ITEM.format(url=task['url'],
                                                         deadline=task['deadline_time'],
                                                         notification=task['notification_string'],
                                                         full_name=task['full_name'],
                                                         ews_score=task['ews_score'],
                                                         trend_icon=task['trend_icon'],
                                                         location=task['location'],
                                                         parent_location=task['parent_location'],
                                                         summary=task['summary'])
        example_html = helpers.BASE_HTML.format(content='<ul class="tasklist">{0}</ul>'.format(task_list_string), task_selected=' class="selected"', patient_selected='', user=self.nurse['display_name'])

        # Assert that shit
        self.assertTrue(self.compare_doms(generated_html, example_html),
                        'DOM from Controller ain\'t the same as DOM from example')
