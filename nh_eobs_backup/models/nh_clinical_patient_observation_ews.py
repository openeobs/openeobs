from openerp.osv import orm


class NHClinicalObservationCompleteOverride(orm.AbstractModel):
    """
    Override the complete method of nh.clinical.patient.observation.ews so
    that it changes the report_printed flag on the nh.clinical.spell model
    """
    _inherit = 'nh.clinical.patient.observation.ews'

    def complete(self, cr, uid, activity_id, context=None):
        """
        Change the report_printed flag on the nh.clinical.spell model on
        complete() being called

        :param cr: Odoo Cursor
        :param uid: User Id
        :param activity_id: ID of the activity being completed
        :param context: Odoo context
        :return: Result of complete() from super class
        """
        res = super(NHClinicalObservationCompleteOverride, self)\
            .complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        patient_id = activity.data_ref.patient_id.id
        spell_pool = self.pool['nh.clinical.spell']
        spell_id = spell_pool.get_by_patient_id(
            cr, uid, patient_id, context=context)
        spell_pool.write(cr, uid, spell_id, {'report_printed': False})
        return res
