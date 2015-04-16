from openerp.osv import orm, fields, osv
from datetime import datetime as dt
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
import logging

_logger = logging.getLogger(__name__)


class nh_clinical_spellboard(orm.Model):
    _name = "nh.clinical.spellboard"
    _inherits = {'nh.activity': 'activity_id'}
    _description = "Spell Management View"
    _auto = False
    _table = "nh_clinical_spellboard"
    _rec_name = 'patient_id'
    _states = [('new', 'New'), ('scheduled', 'Scheduled'),
               ('started', 'Started'), ('completed', 'Completed'), ('cancelled', 'Cancelled')]

    def _get_ward_id(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        location_pool = self.pool['nh.clinical.location']
        for spell in self.browse(cr, uid, ids, context=context):
            res[spell.id] = spell.location_id.id if spell.location_id.usage == 'ward' \
                else location_pool.get_closest_parent_id(cr, uid, spell.location_id.id, context=context)
        return res

    _columns = {
        'activity_id': fields.many2one('nh.activity', 'Activity', required=1, ondelete='restrict'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'location_id': fields.many2one('nh.clinical.location', 'Current Location', required=True),
        'ward_id': fields.function(_get_ward_id, type='many2one', relation='nh.clinical.location', string='Ward'),
        'pos_id': fields.many2one('nh.clinical.pos', 'Point of Service'),
        'code': fields.char("Code", size=20),
        'start_date': fields.datetime("Admission Date"),
        'move_date': fields.datetime("Last Movement Date"),
        'ref_doctor_ids': fields.many2many('nh.clinical.doctor', 'ref_doctor_spell_rel', 'spell_id', 'doctor_id', "Referring Doctors"),
        'con_doctor_ids': fields.many2many('nh.clinical.doctor', 'con_doctor_spell_rel', 'spell_id', 'doctor_id', "Consulting Doctors"),
    }

    def init(self, cr):

        cr.execute("""
                drop view if exists %s;
                create or replace view %s as (
                    select
                        spell_activity.id as id,
                        spell_activity.id as activity_id,
                        spell.patient_id as patient_id,
                        spell.location_id as location_id,
                        spell.pos_id as pos_id,
                        spell.code as code,
                        spell.start_date as start_date,
                        spell.move_date as move_date
                    from nh_activity spell_activity
                    inner join nh_clinical_spell spell on spell.activity_id = spell_activity.id
                    where spell_activity.data_model = 'nh.clinical.spell'
                )
        """ % (self._table, self._table))

    def create(self, cr, uid, vals, context=None):
        api = self.pool['nh.eobs.api']
        patient_pool = self.pool['nh.clinical.patient']
        location_pool = self.pool['nh.clinical.location']
        activity_pool = self.pool['nh.activity']
        patient = patient_pool.read(cr, uid, vals.get('patient_id'), ['other_identifier', 'patient_identifier'], context=context)
        location = location_pool.read(cr, uid, vals.get('location_id'), ['code'], context=context)
        api.admit(cr, uid, patient['other_identifier'], {
            'code': vals.get('code'),
            'patient_identifier': patient['patient_identifier'],
            'location': location['code'],
            'start_date': vals.get('start_date'),
            'ref_doctor_ids': vals.get('ref_doctor_ids'),
            'con_doctor_ids': vals.get('con_doctor_ids')
        }, context=context)
        spell_activity_id = activity_pool.search(cr, uid, [['patient_id', '=', vals.get('patient_id')], ['state', 'not in', ['completed', 'cancelled']], ['data_model', '=', 'nh.clinical.spell']], context=context)
        if not spell_activity_id:
            osv.except_osv('Error!', 'Spell does not exist after admission!')
        return spell_activity_id

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        res = super(nh_clinical_spellboard, self).read(cr, uid, ids, fields=fields, context=context, load=load)
        if not fields or 'ref_doctor_ids' in fields or 'con_doctor_ids' in fields:
            activity_pool = self.pool['nh.activity']
            for r in res:
                spell_activity = activity_pool.browse(cr, uid, r['id'], context=context)
                r['con_doctor_ids'] = [cd.id for cd in spell_activity.data_ref.con_doctor_ids]
                r['ref_doctor_ids'] = [rd.id for rd in spell_activity.data_ref.ref_doctor_ids]
        return res

    def write(self, cr, uid, ids, vals, context=None):
        api = self.pool['nh.eobs.api']
        location_pool = self.pool['nh.clinical.location']
        if vals.get('patient_id'):
            osv.except_osv('Error!', 'Cannot change patient from an existing spell, edit patient information instead!')
        res = {}
        for spell in self.browse(cr, uid, ids, context=context):
            if vals.get('location_id'):
                location = location_pool.read(cr, uid, vals.get('location_id'), ['code'], context=context)
                res[spell.id] = api.transfer(cr, uid, spell.patient_id.other_identifier, {'location': location['code']}, context=context)
            else:
                res[spell.id] = api.admit_update(cr, uid, spell.patient_id.other_identifier, {
                    'location': spell.location_id.code,
                    'code': vals.get('code'),
                    'ref_doctor_ids': vals.get('ref_doctor_ids'),
                    'con_doctor_ids': vals.get('con_doctor_ids')
                }, context=context)
        return all([res[r] for r in res.keys()])

    def cancel(self, cr, uid, ids, context=None):
        api = self.pool['nh.eobs.api']
        res = {}
        for spell in self.browse(cr, uid, ids, context=context):
            res[spell.id] = api.cancel_admit(cr, uid, spell.patient_id.other_identifier, context=context)
        return all([res[r] for r in res.keys()])

    def discharge(self, cr, uid, ids, context=None):
        api = self.pool['nh.eobs.api']
        res = {}
        for spell in self.browse(cr, uid, ids, context=context):
            res[spell.id] = api.discharge(cr, uid, spell.patient_id.other_identifier, {'discharge_date': dt.now().strftime(dtf)}, context=context)
        return all([res[r] for r in res.keys()])

    def cancel_discharge(self, cr, uid, ids, context=None):
        api = self.pool['nh.eobs.api']
        res = {}
        for spell in self.browse(cr, uid, ids, context=context):
            res[spell.id] = api.cancel_discharge(cr, uid, spell.patient_id.other_identifier, context=context)
        return all([res[r] for r in res.keys()])