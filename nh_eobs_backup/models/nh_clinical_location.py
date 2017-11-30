from openerp.osv import orm, fields


class NHClinicalObservationBackupLocation(orm.Model):
    """
    Add backup_observations field to nh.clinical.location model
    """
    _inherit = 'nh.clinical.location'
    _name = 'nh.clinical.location'
    _columns = {
        'backup_observations': fields.boolean(
            'Backup observations for this location'
        )
    }

    _defaults = {
        'backup_observations': False
    }
