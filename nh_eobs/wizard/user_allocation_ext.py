from openerp.osv import osv, fields


class allocating_user(osv.TransientModel):
    _name = 'nh.clinical.allocating'
    _inherit = 'nh.clinical.allocating'

    _risk = ['None', 'Low', 'Medium', 'High']

    def _get_clinical_risk(self, cr, uid, ids, field, args, context=None):
        res = {}
        ews_pool = self.pool['nh.clinical.patient.observation.ews']
        for allocating in self.browse(cr, uid, ids, context=context):
            if allocating.patient_ids:
                case = ews_pool.get_last_case(cr, uid, allocating.patient_ids[0].id, context=context)
                case = case if case else 0
                res[allocating.id] = self._risk[case]
            else:
                res[allocating.id] = 'None'
        return res

    _columns = {
        'clinical_risk': fields.function(_get_clinical_risk, type='char', size=100, string='Clinical Risk')
    }