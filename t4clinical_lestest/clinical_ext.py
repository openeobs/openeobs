from openerp.osv import orm, fields, osv
import logging
_logger = logging.getLogger(__name__)
from openerp import tools

class t4_clinical_o2_saturation_level(osv.Model):
    _name = "t4.clinical.o2saturation.level"

    def _get_name(self, cr, uid, ids, fn, args, context=None):
        result = dict.fromkeys(ids, False)
        for r in self.read(cr, uid, ids, ['max_value', 'min_value'], context=context):
            result[r['id']] = str(r['min_value']) + '-' + str(r['max_value'])
        return result

    _columns = {
        'name': fields.function(_get_name, 'Range', type='char', size=50),
        'max_value': fields.integer('Max Value', required=True),
        'min_value': fields.integer('Min Value', required=True),
        'active': fields.boolean('Active', help="If the active field is set to false, it will allow you to hide the"
                                                " O2 target without removing it."),
        }

    _defaults = {
        'active': True
    }

    def unlink(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'active': False}, context=context)