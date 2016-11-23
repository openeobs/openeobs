from openerp.osv import orm
import openerp.modules as addons
import openerp.addons.nh_eobs_mobile.controllers.main as mobile_controller
from openerp.addons.nh_eobs_mobile.controllers.urls import URLS


class NHEobsMobileMain(orm.AbstractModel):

    _name = 'nh.eobs.mobile.mental'

    def process_patient_list(self, cr, uid, patient_list, context=None):
        spell_model = self.pool['nh.clinical.spell']
        ews_model = self.pool['nh.clinical.patient.observation.ews']
        patient_ids = [patient.get('id') for patient in patient_list]
        spell_ids = spell_model.search(cr, uid, [
            ['patient_id', 'in', patient_ids],
            ['state', 'not in', ['completed', 'cancelled']]
        ], context=context)
        spells = spell_model.read(cr, uid, spell_ids, [
            'obs_stop',
            'patient_id'
        ], context=context)
        obs_stop = {}
        for spell in spells:
            patient_id = spell.get('patient_id')
            if patient_id:
                obs_stop[patient_id[0]] = spell.get('obs_stop')
        for patient in patient_list:
            patient['url'] = '{0}{1}'.format(
                URLS['single_patient'], patient['id'])
            patient['color'] = self.calculate_ews_class(
                patient['clinical_risk'])
            patient['trend_icon'] = 'icon-{0}-arrow'.format(
                patient['ews_trend'])
            if obs_stop.get(patient.get('id')):
                patient['deadline_time'] = 'Observations Stopped'
            elif ews_model.is_patient_refusal_in_effect(
                    cr, uid, patient.get('id'), context=context):
                patient['deadline_time'] = \
                    'Refused - {0}'.format(patient.get('next_ews_time'))
            else:
                patient['deadline_time'] = patient['next_ews_time']
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
        return patient_list

    @staticmethod
    def calculate_ews_class(clinical_risk):
        return mobile_controller.MobileFrontend.calculate_ews_class(
            clinical_risk)

    def __init__(self, pool, cr):
        loaded = addons.module.loaded
        if 'nh_eobs_mental_health' in loaded:
            mobile_controller.MobileFrontend.process_patient_list = \
                self.process_patient_list
        super(NHEobsMobileMain, self).__init__(pool, cr)
