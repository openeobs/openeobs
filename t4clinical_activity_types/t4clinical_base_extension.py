from openerp.osv import orm, fields, osv
from openerp import SUPERUSER_ID
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class t4_clinical_patient_extension(osv.Model):

    _name = 't4.clinical.patient'
    _inherit = 't4.clinical.patient'

    _columns = {
#         'active_spell_ids': fields.one2many('t4.clinical.spell', 'patient_id', 'Spells', domain=[['state','=','started']]),
#         'active_spell_code': fields.related('active_spell_ids', 'code', type='text', string='Spell Code'),
        'spell_ids': fields.one2many('t4.clinical.spell', 'patient_id', 'Spells'),
        'move_ids': fields.one2many('t4.clinical.patient.move', 'patient_id', 'Moves'),
        'o2target_ids': fields.one2many('t4.clinical.patient.o2target', 'patient_id', 'O2 Targets'),
        'weight_ids': fields.one2many('t4.clinical.patient.observation.weight', 'patient_id', 'Weights'),
        'blood_sugar_ids': fields.one2many('t4.clinical.patient.observation.blood_sugar', 'patient_id', 'Blood Sugar'),
        'mrsa_ids': fields.one2many('t4.clinical.patient.mrsa', 'patient_id', 'MRSA'),
        'diabetes_ids': fields.one2many('t4.clinical.patient.diabetes', 'patient_id', 'Diabetes'),
        'terminated_device_session_ids': fields.one2many('t4.clinical.device.session', 'patient_id', 'Device Session History', domain=[('state','=','completed')]),
        'started_device_session_ids': fields.one2many('t4.clinical.device.session', 'patient_id', 'Active Device Sessions', domain=[('state','=','started')]),
        'ews_ids': fields.one2many('t4.clinical.patient.observation.ews', 'patient_id', 'EWS'),
        'ews_list_ids': fields.one2many('t4.clinical.patient.observation.ews', 'patient_id', 'EWS List', domain=[('state','=','completed')])
    }


class t4_clinical_api_extension(orm.AbstractModel):
    _name = 't4.clinical.api'
    _inherit = 't4.clinical.api'

    def change_activity_frequency(self, cr, uid, patient_id, activity_type, frequency, context=None):
        activity_pool = self.pool['t4.activity']
        change_freq_pool = self.pool['t4.clinical.notification.frequency']
        domain = [
            ('patient_id', '=', patient_id),
            ('state', '=', 'completed'),
            ('data_model', '=', activity_type)
        ]
        activity_ids = activity_pool.search(cr, uid, domain, order='create_date desc, id desc', context=context)
        spell_activity_id = self.get_patient_spell_activity_id(cr, uid, patient_id, context=context)
        if not activity_ids:
            creator_id = False
        else:
            creator_id = activity_ids[0]
        frequency_activity_id = change_freq_pool.create_activity(cr, SUPERUSER_ID, {
            'creator_id': creator_id, 'parent_id': spell_activity_id
        }, {
            'patient_id': patient_id,
            'observation': activity_type,
            'frequency': frequency
        })
        return activity_pool.complete(cr, uid, frequency_activity_id, context=context)

    def trigger_notifications(self, cr, uid, values, context=None):
        #import pdb; pdb.set_trace()
        for n in values['notifications']:
            # notifications: [{'summary','model','groups'}]
            if values.get('group') in n['groups']:
                pool = self.pool['t4.clinical.notification.'+n['model']]
                a_values = {
                    'parent_id': values.get('parent_id'),
                    'date_deadline': (dt.now()+td(minutes=5)).strftime(DTF),
                    'creator_id': values.get('creator_id'),
                }
                if n.get('summary'):
                    a_values.update({'summary': n['summary']})
                d_values = {
                    'patient_id': values.get('patient_id')
                }
                if n['model'] == 'frequency':
                    activity_pool = self.pool['t4.activity']
                    domain = [
                        ('patient_id', '=', values.get('patient_id')),
                        ('state', 'not in', ['completed', 'cancelled']),
                        ('data_model', '=', 't4.clinical.notification.frequency')]
                    frequency_activity_ids = activity_pool.search(cr, uid, domain, context=context)
                    for f in activity_pool.browse(cr, uid, frequency_activity_ids, context=context):
                        if f.data_ref.observation == values.get('model'):
                            activity_pool.cancel(cr, uid, f.id, context=context)
                    d_values.update({'observation': values.get('model')})
                pool.create_activity(cr, SUPERUSER_ID, a_values, d_values, context=context)

    # def trigger_notifications2(self, cr, uid, notifications, parent_id, creator_id, patient_id, model, context=None):
    #     nurse_pool = self.pool['t4.clinical.notification.nurse']
    #     for n in notifications['nurse']:
    #         nurse_pool.create_activity(cr, SUPERUSER_ID, {'summary': n,
    #                                                       'parent_id': parent_id,
    #                                                       'date_deadline': (dt.now()+td(minutes=5)).strftime(DTF),
    #                                                       'creator_id': creator_id}, {'patient_id': patient_id})
    #     if notifications['assessment']:
    #         assessment_pool = self.pool['t4.clinical.notification.assessment']
    #         assessment_pool.create_activity(cr, SUPERUSER_ID, {'parent_id': parent_id,
    #                                                            'date_deadline': (dt.now()+td(minutes=5)).strftime(DTF),
    #                                                            'creator_id': creator_id}, {'patient_id': patient_id})
    #     if notifications['frequency']:
    #         activity_pool = self.pool['t4.activity']
    #         domain = [
    #             ('patient_id', '=', patient_id),
    #             ('state', 'not in', ['completed', 'cancelled']),
    #             ('data_model', '=', 't4.clinical.notification.frequency')]
    #         frequency_activity_ids = activity_pool.search(cr, uid, domain, context=context)
    #         for f in activity_pool.browse(cr, uid, frequency_activity_ids, context=context):
    #             if f.data_ref.observation == model:
    #                 activity_pool.cancel(cr, uid, f.id, context=context)
    #         frequency_pool = self.pool['t4.clinical.notification.frequency']
    #         frequency_pool.create_activity(cr, SUPERUSER_ID, {'parent_id': parent_id,
    #                                                           'creator_id': creator_id,
    #                                                           'date_deadline': (dt.now()+td(minutes=5)).strftime(DTF)},
    #                                        {'patient_id': patient_id, 'observation': model})

    def cancel_open_activities(self, cr, uid, parent_id, model, context=None):
        activity_pool = self.pool['t4.activity']
        domain = [('parent_id', '=', parent_id),
                  ('data_model', '=', model),
                  ('state', 'not in', ['completed', 'cancelled'])]
        open_activity_ids = activity_pool.search(cr, uid, domain, context=context)
        return all([activity_pool.cancel(cr, uid, a, context=context) for a in open_activity_ids])