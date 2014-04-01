from openerp.osv import fields, osv


class t4_clinical_patient_extension(osv.Model):

    _name = 't4.clinical.patient'
    _inherit = 't4.clinical.patient'

    _columns = {
        'spell_ids': fields.one2many('t4.clinical.spell', 'patient_id', 'Spells')
    }