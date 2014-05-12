from openerp.osv import orm, fields, osv
from openerp.addons.t4clinical_base.activity import except_if
import logging
_logger = logging.getLogger(__name__)


class activityAPI(orm.AbstractModel):
    _name = 'newsdemo.api'

    def set_patient_to_placement(self, cr, uid, rollback=True):
        admit_pool = self.pool['t4.clinical.adt.patient.admit']
        activity_pool = self.pool['t4.activity']
        placement_pool = self.pool['t4.clinical.patient.placement']

        except_if(rollback, msg="Rollback")
        return True

    def getPatients(self, cr, uid, rollback=True):
        admit_pool = self.pool['t4.clinical.adt.patient.admit']
        activity_pool = self.pool['t4.activity']
        placement_pool = self.pool['t4.clinical.patient.placement']

        except_if(rollback, msg="Rollback")
        return True
