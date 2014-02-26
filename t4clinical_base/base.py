# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv

class res_company(orm.Model):
    _name = 'res.company'
    _inherit = 'res.company'
    # default company has xmlid == 'main_company'
    _columns = {
        'pos_ids': fields.many2many('t4.clinical.location', 'company_pos_rel', 'company_id', 'pos_id', 'POS Locations'),
        'lot_admission_id': fields.many2one('t4.clinical.location', 'Admission Location'),
        'lot_discharge_id': fields.many2one('t4.clinical.location', 'Discharge Location'),
        
        
    }


class t4_clinical_location(orm.Model):
    """ Clinical point of service LOCATION """

    _name = 't4.clinical.location'
    #_parent_name = 'location_id'
    _rec_name = 'code'
    _types = [('poc', 'Point of Care'), ('structural', 'Structural'), ('virtual', 'Virtual'), ('pos', 'POS')]
    _usages = [('bed', 'Bed'), ('ward', 'Ward'), ('department', 'Department'), ('hospital', 'Hospital')]
    
    def _location2pos_id(self, cr, uid, ids, field, args, context=None):
        res = {}
        for location in self.browse(cr, uid, ids, context):
            domain = [('type','=','pos'),('parent_id.parent_left', '>=', location.parent_left),('parent_id.parent_right', '<=', location.parent_right)]
            pos_id = self.search(cr, uid, domain, context=context)
            res[location.id] = pos_id and pos_id[0] or False
        return res
    
    def _location2company_id(self, cr, uid, ids, field, args, context=None):
        res = {}
        company_pool = self.pool['res.company']
        for location in self.browse(cr, uid, ids, context):
            domain = [('pos_ids','in',location.pos_id)]
            company_id = company_pool.search(cr, uid, domain, context=context)
            res[location.id] = company_id and company_id[0] or False
        return res    
    
    _columns = {
        'name': fields.char('Point of Care', size=100, required=True, select=True),
        'code': fields.char('Code', size=256),
        'parent_id': fields.many2one('t4.clinical.location', 'Parent Location'),
        'type': fields.selection(_types, 'Location Type'),
        'usage': fields.selection(_usages, 'Location Usage'),
        'is_available': fields.boolean('Is Available', help="Will"),
        'active': fields.boolean('Active'),
        'pos_id': fields.function(_location2pos_id, type='many2one', relation='t4.clinical.location', string='POS'),
        'company_id': fields.function(_location2company_id, type='many2one', relation='res.company', string='Company') 
    }
    

        
    _defaults = {
        'active': True
    }

class hr_employee(orm.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    
    _columns = {
        'location_ids': fields.many2many('t4.clinical.location', 'employee_location_rel', 'employee_id', 'location_id', 'Locations of Responsibility'),
        
    }
    
    
    
    

class t4_clinical_patient(osv.Model):
    """T4Clinical Patient object, to store all the parameters of the Patient
    """
    _name = 't4.clinical.patient'
    _description = "A Patient"

    _inherits = {'res.partner': 'partner_id'}

    def _get_fullname(self, vals):

        #TODO: Make this better and support comma dependency / format etc
        return ''.join([vals.get('family_name', '') or '', ', ',
                        vals.get('given_name', '') or '', ' ',
                        vals.get('middle_names', '') or ''])

    def _get_name(self, cr, uid, ids, fn, args, context=None):
        result = dict.fromkeys(ids, False)
        for r in self.read(cr, uid, ids, ['family_name', 'given_name', 'middle_name'], context=context):
            #TODO This needs to be manipulable depending on locale
            result[r['id']] = self._get_fullname(r)
        return result

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True, ondelete='restrict'),
        'dob': fields.datetime('Date Of Birth'),  # Partner birthdate is NOT a date.
        'sex': fields.char('Sex', size=1),
        'gender': fields.char('Gender', size=1),
        'ethnicity': fields.char('Ethnicity', size=20),
        'patient_identifier': fields.char('Patient Identifier', size=100, select=True, help="NHS Number"),
        'other_identifier': fields.char('Other Identifier', size=100, required=True, select=True,
                                        help="Hospital Number"),

        'given_name': fields.char('Given Name', size=200),
        'middle_names': fields.char('Middle Name(s)', size=200),
        'family_name': fields.char('Family Name', size=200, select=True),
        }

    _defaults = {
        'active': True,
        'name': 'unknown'
    }
    
    def create(self, cr, uid, vals, context=None):
        if not vals.get('name'):
            vals.update({'name': self._get_fullname(vals)})
        rec_id = super(t4_clinical_patient, self).create(cr, uid, vals, context)
        return rec_id    
    
    
