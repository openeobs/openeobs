from openerp.osv import orm


class NHeObsAPI(orm.AbstractModel):
    """
        Defines attributes and methods used by `Open eObs` in the making of
        patient observations.

        ``_active_observations`` are the observation types supported by
        eObs.
        """

    _name = 'nh.eobs.api'
    _inherit = 'nh.eobs.api'

    def get_active_observations(self, cr, uid, patient_id, context=None):
        """
        Returns all active observation types supported by eObs, if the
        :class:`patient<base.nh_clinical_patient>` has an active
        :class:`spell<spell.nh_clinical_spell>`.

        :param patient_id: id of patient
        :type patient_id: int
        :returns: list of all observation types
        :rtype: list
        """
        spell_model = self.pool['nh.clinical.spell']
        spell_id = spell_model.search(cr, uid, [
            ['patient_id', '=', patient_id],
            ['state', 'not in', ['completed', 'cancelled']]
        ], context=context)
        if spell_id:
            spell_id = spell_id[0]
            obs_stopped = spell_model.read(
                cr, uid, spell_id, ['obs_stop'], context=context)\
                .get('obs_stop')
            if obs_stopped:
                return []
        return super(NHeObsAPI, self)\
            .get_active_observations(cr, uid, patient_id, context=context)
