from openerp.osv import orm, fields


class NHClinicalBackupSpellFlag(orm.Model):
    """
    Add the report_printed column to the nh.clinical.spell model
    """

    _name = 'nh.clinical.spell'
    _inherit = 'nh.clinical.spell'

    _columns = {
        'report_printed': fields.boolean('Has the report been printed?')
    }

    _defaults = {
        'report_printed': False
    }
