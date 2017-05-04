import openerp.addons.nh_eobs_mobile.controllers.main as mobile_controller
import openerp.modules as addons
from openerp.addons.nh_eobs_mobile.controllers.urls import URLS
from openerp.osv import orm


class NHEobsMobileMain(orm.AbstractModel):

    _name = 'nh.eobs.mobile.mental'

    def get_status_map_for_patient_ids(
            self, cr, uid, patient_ids, context=None):
        """
        Take a list of patient IDs and return the spells

        :param cr: Odoo cursor
        :param uid: user
        :param patient_ids: list of patient IDs
        :param context: Odoo context
        :return: dict containing patient ID to status flag mapping
        """
        spell_model = self.pool['nh.clinical.spell']
        spell_ids = spell_model.search(cr, uid, [
            ['patient_id', 'in', patient_ids],
            ['state', 'not in', ['completed', 'cancelled']]
        ], context=context)
        spells = spell_model.read(cr, uid, spell_ids, [
            'obs_stop',
            'rapid_tranq',
            'patient_id'
        ], context=context)
        status_mapping = {}
        for spell in spells:
            patient_id = spell.get('patient_id')
            if patient_id:
                patient_status = status_mapping[patient_id[0]] = {}
                patient_status['obs_stop'] = spell.get('obs_stop')
                patient_status['rapid_tranq'] = spell.get('rapid_tranq')
        return status_mapping

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
        status_map = self.get_status_map_for_patient_ids(cr, uid, patient_ids)
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
        status_map = self.get_status_map_for_patient_ids(cr, uid, patient_ids)
        for patient in patient_list:
            patient['url'] = '{0}{1}'.format(
                URLS['single_patient'], patient['id'])
            patient['color'] = self.calculate_ews_class(
                patient['clinical_risk'])
            patient['trend_icon'] = 'icon-{0}-arrow'.format(
                patient['ews_trend'])
            if status_map.get(patient.get('id'), {}).get('obs_stop'):
                patient['deadline_time'] = 'Observations Stopped'
            else:
                patient['deadline_time'] = patient['next_ews_time']
            patient['rapid_tranq'] = status_map.get(
                patient.get('id'), {}).get('rapid_tranq', False)
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
