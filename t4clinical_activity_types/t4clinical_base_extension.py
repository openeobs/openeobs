from openerp.osv import fields, osv


class t4_clinical_patient_extension(osv.Model):

    _name = 't4.clinical.patient'
    _inherit = 't4.clinical.patient'

    _columns = {
#         'active_spell_ids': fields.one2many('t4.clinical.spell', 'patient_id', 'Spells', domain=[['state','=','started']]),
#         'active_spell_code': fields.related('active_spell_ids', 'code', type='text', string='Spell Code'),
        'spell_ids': fields.one2many('t4.clinical.spell', 'patient_id', 'Spells'),
        'move_ids': fields.one2many('t4.clinical.patient.move', 'patient_id', 'Moves'),
        'o2target_ids': fields.one2many('t4.clinical.patient.o2target', 'patient_id', 'O2 Targets'),
        'weight_ids': fields.one2many('t4.clinical.patient.observation.weight', 'patient_id', 'Weights'),
        'blood_sugar_ids': fields.one2many('t4.clinical.patient.observation.blood_sugar', 'patient_id', 'Blood Sugar'),
        'mrsa_ids': fields.one2many('t4.clinical.patient.mrsa', 'patient_id', 'MRSA'),
        'diabetes_ids': fields.one2many('t4.clinical.patient.diabetes', 'patient_id', 'Diabetes'),
        'terminated_device_session_ids': fields.one2many('t4.clinical.device.session', 'patient_id', 'Device Session History', domain=[('state','=','completed')]),
        'started_device_session_ids': fields.one2many('t4.clinical.device.session', 'patient_id', 'Active Device Sessions', domain=[('state','=','started')]),
        'ews_ids': fields.one2many('t4.clinical.patient.observation.ews', 'patient_id', 'EWS'),
    }