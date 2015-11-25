from openerp.osv import orm,fields
import logging

_logger = logging.getLogger(__name__)


class nh_ui_location(orm.Model):

    _name = 'nh.clinical.location'
    _inherit = 'nh.clinical.location'

    def _get_patient_info(self, cr, uid, ids, field_names, arg, context=None):
        ewsfields = {
            'patient_score': 'score',
            'patient_risk': 'clinical_risk'
        }
        res = {id: {field_name: [] for field_name in field_names} for id in ids}
        activity_pool = self.pool['nh.activity']
        for location_id in ids:
            spell_id = activity_pool.search(cr, uid, [
                ['location_id', '=', location_id],
                ['data_model', '=', 'nh.clinical.spell'],
                ['state', '=', 'started']], context=context)
            ews = False
            if len(spell_id) == 1:
                ews_id = activity_pool.search(cr, uid, [
                    ['data_model', '=', 'nh.clinical.patient.observation.ews'],
                    ['state', '=', 'completed'],
                    ['parent_id', '=', spell_id[0]]
                ], order='date_terminated desc, sequence desc', context=context)
                if ews_id:
                    ews = activity_pool.browse(cr, uid, ews_id[0], context=context).data_ref
            for field_name in field_names:
                if not ews:
                    res[location_id][field_name] = False
                else:
                    res[location_id][field_name] = str(eval("ews.%s" % ewsfields[field_name]))
        return res

    _columns = {
        'patient_score': fields.function(_get_patient_info, type='char', multi='score_string', string='Score'),
        'patient_risk': fields.function(_get_patient_info, type='char', multi='clinical_risk', string='Risk')
    }

    def search(self, cr, uid, domain, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('nh_open_form'):
            group_pool = self.pool.get('res.groups')
            group_ids = group_pool.search(cr, uid, [('users', 'in', [uid])], context=context)
            groups = group_pool.read(cr, uid, group_ids, ['name'], context=context)
            group_names = [g.get('name') for g in groups]
            if 'NH Clinical Ward Manager Group' in group_names:
                for filter in domain:
                    if filter[0] == 'parent_id' and filter[1] == 'in':
                        types = self.read(cr, uid, filter[2], ['type'])
                        if types[0].get('type') == 'pos':
                            user_pool = self.pool.get('res.users')
                            user = user_pool.browse(cr, uid, uid, context=context)
                            location_ids = [l.id for l in user.location_ids]
                            domain += [('id', 'in', location_ids)]
        return super(nh_ui_location, self).search(cr, uid, domain, offset=offset, limit=limit, order=order, context=context, count=count)

    def create(self, cr, uid, vals, context=None):
        res = super(nh_ui_location, self).create(cr, uid, vals, context=context)
        sql = """
                refresh materialized view ward_locations;
        """
        cr.execute(sql)
        return res