from openerp.osv import orm, osv, fields
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class t4_clinical_apikey(orm.Model):
    _name = 't4.clinical.apikey'

    _columns = {
        'username': fields.char('Username', size=150, required=True),
        'database': fields.char('Database', size=150, required=True),

    }


class t4_clinical_api(orm.AbstractModel):
    _name = 't4.clinical.api'
    _inherit = 't4.clinical.api'

    def _check_activity_id(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.activity']
        domain = [('id', '=', activity_id)]
        activity_ids = activity_pool.search(cr, uid, domain, context=context)
        if not activity_ids:
            raise osv.except_osv(_('Error!'), 'Activity ID not found: %s' % activity_id)
        return True

    def _create_activity(self, cr, uid, data_model, vals_activity=None, vals_data=None, context=None):
        model_pool = self.pool[data_model]
        activity_id = model_pool.create_activity(cr, uid, vals_activity, vals_data, context=context)
        _logger.info("Activity created id=%s, data_model=%s\n vals_activity: %s\n vals_data: %s"
                     % (activity_id, data_model, vals_activity, vals_data))
        return activity_id

    def _check_hospital_number(self, cr, uid, hospital_number, context=None):
        patient_pool = self.pool['t4.clinical.patient']
        domain = [('other_identifier', '=', hospital_number)]
        return patient_pool.search(cr, uid, domain, context=context)

    # # # # # # # #
    #  ACTIVITIES #
    # # # # # # # #

    def getActivities(self, cr, uid, ids, context=None):
        """
        Return a list of activities in dictionary format (containing every field from the table)
        :param ids: ids of the activities we want. If empty returns all activities.
        """
        domain = [('id', 'in', ids)] if ids else []
        activity_pool = self.pool['t4.activity']
        activity_ids = activity_pool.search(cr, uid, domain, context=context)
        activity_values = activity_pool.read(cr, uid, activity_ids, [], context=context)
        return activity_values

    def cancel(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.activity']
        self._check_activity_id(cr, uid, activity_id, context=context)
        return activity_pool.cancel(cr, uid, activity_id, context=context)

    def submit(self, cr, uid, activity_id, data, context=None):
        activity_pool = self.pool['t4.activity']
        self._check_activity_id(cr, uid, activity_id, context=context)
        return activity_pool.submit(cr, uid, activity_id, data, context=context)

    def unassign(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.activity']
        self._check_activity_id(cr, uid, activity_id, context=context)
        return activity_pool.unassign(cr, uid, activity_id, context=context)

    def assign(self, cr, uid, activity_id, data, context=None):
        activity_pool = self.pool['t4.activity']
        user_pool = self.pool['res.users']
        user_id = uid
        self._check_activity_id(cr, uid, activity_id, context=context)
        if data.get('user_id'):
            user_id = data['user_id']
            domain = [('id', '=', user_id)]
            user_ids = user_pool.search(cr, uid, domain, context=context)
            if not user_ids:
                raise osv.except_osv(_('Error!'), 'User ID not found: %s' % user_id)
        return activity_pool.assign(cr, uid, activity_id, user_id, context=context)

    def complete(self, cr, uid, activity_id, data, context=None):
        activity_pool = self.pool['t4.activity']
        self._check_activity_id(cr, uid, activity_id, context=context)
        return activity_pool.complete(cr, uid, activity_id, data, context=context)

    # # # # # # #
    #  PATIENTS #
    # # # # # # #

    def getPatients(self, cr, uid, ids, context=None):
        """
        Return a list of patients in dictionary format (containing every field from the table)
        :param ids: ids of the patients we want. If empty returns all patients.
        """
        domain = [('id', 'in', ids)] if ids else []
        patient_pool = self.pool['t4.clinical.patient']
        patient_ids = patient_pool.search(cr, uid, domain, context=context)
        patient_values = patient_pool.read(cr, uid, patient_ids, [], context=context)
        return patient_values

    def update(self, cr, uid, patient_id, data, context=None):
        activity_pool = self.pool['t4.activity']
        if not self._check_hospital_number(cr, uid, patient_id, context=context):
            _logger.warn("Patient registered from an update call - data available:%s" % data)
            self.register(cr, uid, patient_id, data, context=context)
        data.update({'other_identifier': patient_id})
        update_activity = self._create_activity('t4.clinical.adt.patient.update', {}, {})
        activity_pool.submit(cr, uid, update_activity, data, context=context)
        activity_pool.complete(cr, uid, update_activity, context=context)
        _logger.info("Patient updated\n data: %s" % data)
        return True

    def register(self, cr, uid, patient_id, data, context=None):
        activity_pool = self.pool['t4.activity']
        register_activity = self._create_activity('t4.clinical.adt.patient.register', {}, {})
        data.update({'other_identifier': patient_id})
        activity_pool.submit(cr, uid, register_activity, data, context=context)
        activity_pool.complete(cr, uid, register_activity, context=context)
        _logger.info("Patient registered\n data: %s" % data)
        return True

    def admit(self, cr, uid, patient_id, data, context=None):
        activity_pool = self.pool['t4.activity']
        if not self._check_hospital_number(cr, uid, patient_id, context=context):
            _logger.warn("Patient registered from an admit call")
            self.register(cr, uid, patient_id, {}, context=context)
        data.update({'other_identifier': patient_id})
        admit_activity = self._create_activity('t4.clinical.adt.patient.admit', {}, {})
        activity_pool.submit(cr, uid, admit_activity, data, context=context)
        activity_pool.complete(cr, uid, admit_activity, context=context)
        _logger.info("Patient admitted\n data: %s" % data)
        return True

    def discharge(self, cr, uid, patient_id, context=None):
        if not self._check_hospital_number(cr, uid, patient_id, context=context):
            raise osv.except_osv(_('Error!'), 'Patient ID not found: %s' % patient_id)
        activity_pool = self.pool['t4.activity']
        discharge_activity = self._create_activity('t4.clinical.adt.patient.discharge', {}, {'other_identifier': patient_id})
        activity_pool.complete(cr, uid, discharge_activity, context=context)
        _logger.info("Patient discharged: %s" % patient_id)
        return True

    def getActivitiesForPatient(self, cr, uid, patient_id, activity_type, start_date=dt.now()+td(days=-30),
                                end_date=dt.now(), context=None):
        """
        Returns a list of activities in dictionary format (containing every field from the table)
        :param patient_id: Postgres ID of the patient to get the activities from.
        :param activity_type: Type of activity we want. Must be an observation.
        :param start_date: start date to filter. A month from now by default.
        :param end_date: end date to filter. Now by default.
        """
        model_pool = self.pool['t4.clinical.patient.observation.'+activity_type]
        ids = model_pool.search(cr, uid, [
            ('patient_id', '=', patient_id),
            ('state', '=', 'completed'),
            ('date_terminated', '>=', start_date.strftime(DTF)),
            ('date_terminated', '<=', end_date.strftime(DTF))], context=context)
        return model_pool.read(cr, uid, ids, [], context=context)