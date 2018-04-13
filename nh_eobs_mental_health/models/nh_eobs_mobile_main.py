import openerp.addons.nh_eobs_mobile.controllers.main as mobile_controller
import openerp.modules as addons
from openerp.addons.nh_eobs_mobile.controllers.urls import URLS
from openerp.osv import orm


class NHEobsMobileMain(orm.AbstractModel):

    _name = 'nh.eobs.mobile.mental'

    def process_task_list(self, cr, uid, task_list, context=None):
        """
        Process the task list from nh.eobs.api.get_activities

        :param cr: Odoo cursor
        :param uid: user id
        :param task_list: list of tasks from get_activities
        :param context: Odoo context
        :return: list of tasks with extra processing
        """
        patient_ids = [task.get('patient_id') for task in task_list]
        patient_pool = ['nh.clinical.patient']
        status_map = patient_pool.get_status_map_for_patient_ids(
            cr, uid, patient_ids)
        for task in task_list:
            task['rapid_tranq'] = status_map.get(
                task.get('patient_id'), {}).get('rapid_tranq', False)
            task['url'] = '{0}{1}'.format(URLS['single_task'], task['id'])
            task['color'] = self.calculate_ews_class(task['clinical_risk'])
        return task_list

    def process_patient_list(self, cr, uid, patient_list, context=None):
        """
        Process the patient list.

        :param cr:
        :param uid:
        :param patient_list:
        :param context:
        :return:
        """
        patient_ids = [patient.get('id') for patient in patient_list]
        for patient in patient_list:
            patient['url'] = '{0}{1}'.format(
                URLS['single_patient'], patient['id'])
            patient['color'] = self.calculate_ews_class(
                patient['clinical_risk'])
            patient['trend_icon'] = 'icon-{0}-arrow'.format(
                patient['ews_trend'])
            patient['summary'] = patient.get('summary', False)
            if patient.get('followers'):
                followers = patient['followers']
                follow_csv = ', '.join([f['name'] for f in followers])
                patient['followers'] = follow_csv
                patient['follower_ids'] = [f['id'] for f in followers]
            if patient.get('invited_users'):
                users = patient['invited_users']
                invite_csv = ', '.join([u['name'] for u in users])
                patient['invited_users'] = invite_csv
        return sorted(
            sorted(
                patient_list,
                key=lambda pat: pat.get('location')
            ),
            key=lambda rec: rec.get('rapid_tranq'),
            reverse=True
        )

    @staticmethod
    def calculate_ews_class(clinical_risk):
        return mobile_controller.MobileFrontend.calculate_ews_class(
            clinical_risk)

    def __init__(self, pool, cr):
        loaded = addons.module.loaded
        if 'nh_eobs_mental_health' in loaded:
            mobile_controller.MobileFrontend.process_patient_list = \
                self.process_patient_list
            mobile_controller.MobileFrontend.process_task_list = \
                self.process_task_list
        super(NHEobsMobileMain, self).__init__(pool, cr)
