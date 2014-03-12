from openerp.osv import osv, fields
import random
from faker import Faker

class patient_adt_wizard(osv.TransientModel):
    _name = 't4clinical.patient.events.wizard'
    _columns = {
        'other_identifier': fields.char('Other Identifier (HospId)', size=100, required=True),
        'patient_identifier': fields.char('Patient Identifier (NHS Number)', size=100),
        'given_name': fields.char('Given Name', size=200),
        'middle_names': fields.char('Middle Names', size=200),
        'family_name': fields.char('Family Name', size=200),
        'dob': fields.datetime('Date Of Birth'),
        'sex': fields.char('Sex', size=1),
        'gender': fields.char('Gender', size=1),
        #patient visit information
        'visit_ref': fields.char('Ward Ref', help='eg: GW001'),
        'visit_no': fields.char('Visit No'),
        'visit_start': fields.datetime('Start')
    }

    _defaults = {
        'visit_start': lambda *a: fields.datetime.now(),
        'given_name': 'Jane',
        'family_name': 'Test',
        'sex': 'F',
        'visit_ref': 'W8',
        'other_identifier': lambda *a: str(random.randint(1000, 99999)),
        'visit_no': lambda *a: str(random.randint(100000, 999999))
    }

    def call_patientNew(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0], context)
        if data.other_identifier:

            #todo: Note what is optional data in the api and what is required
            patient_data = {
                'other_identifier': data.other_identifier,
                'given_name': data.given_name or 'Dummy',
                'middle_names': data.middle_names or '',
                'family_name': data.family_name or '',
                'dob': data.dob or '03-09-1966 13:00:00'
            }

            #todo: separate the calls depending on identifier sent over.
            #if data.patient_identifier:
            #    req.update({'patient_identifier': data.patient_identifier})

            register_pool = self.pool.get('t4.clinical.adt.patient.register')
            register_pool.create_task(cr, uid, {}, patient_data)

        return {'type': 'ir.actions.act_window_close'}

    def call_patientVisit(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0], context)

        admission_pool = self.pool.get('t4.clinical.adt.patient.admit')
        admission_pool.create_task(cr, uid, {}, {'other_identifier': data.other_identifier,
                                                 'location': data.visit_ref,
                                                 'code': data.visit_no,
                                                 'start_date': data.visit_start})

        return {'type': 'ir.actions.act_window_close'}

    def call_both(self, cr, uid, ids, context=None):
        self.call_patientNew(cr, uid, ids, context=context)
        return self.call_patientVisit(cr, uid, ids, context=context)

