from openerp.osv import osv, fields


class NHClinicalObservationBackupSettings(osv.TransientModel):
    """
    Add settings for the list of wards to backup
    """

    _inherit = 'base.config.settings'
    _name = 'base.config.settings'

    _columns = {
        'locations_to_print': fields.many2many(
            'nh.clinical.location',
            domain=[['usage', '=', 'ward']],
            string='Locations to print backup observation reports for'
        )
    }

    def set_locations(self, cr, uid, id, context=None):
        """
        Set the locations to backup. This is a 'magical' method name used by
        Odoo for setting the value of fields exposed on the GUI

        :param cr: Odoo Cursor
        :param uid: User ID
        :param ids: IDs of the setting wizard
        :param context: Odoo context
        :return: Result of writing field
        """
        loc_pool = self.pool.get('nh.clinical.location')
        record = self.browse(cr, uid, id, context=context)
        loc_ids = [l.id for l in record.locations_to_print]
        locs = loc_pool.search(
            cr,
            uid,
            [
                ['usage', '=', 'ward'],
                ['backup_observations', '=', True],
                ['id', 'not in', loc_ids]
            ]
        )
        loc_pool.write(cr, uid, locs, {'backup_observations': False})
        return loc_pool.write(cr, uid, loc_ids, {'backup_observations': True})

    def get_default_all(self, cr, uid, ids, context=None):
        """
        Get the value when the field is loaded in the GUI. This is a 'magical'
        method name used by Odoo.

        :param cr: Odoo cursor
        :param uid: User Id
        :param ids: ID of wizard
        :param context: Odoo context
        :return: Dictionary of location objects
        """
        loc_pool = self.pool.get('nh.clinical.location')
        locs = loc_pool.search(
            cr, uid,
            [
                ['usage', '=', 'ward'],
                ['backup_observations', '=', True]
            ]
        )
        return dict(locations_to_print=locs)
