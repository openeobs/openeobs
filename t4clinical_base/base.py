# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv

class t4_clinical_pos(orm.Model):
    """ Clinical point of service """
    _name = 't4.clinical.pos'
    _columns = {
        'name': fields.char('Point of Service', size=100, required=True, select=True),
        'code': fields.char('Code', size=256),
        'location_id': fields.many2one('t4.clinical.location', 'POS Location', required=True), 
        'company_id': fields.many2one('res.company', 'Company'),
        'lot_admission_id': fields.many2one('t4.clinical.location', 'Admission Location'),
        'lot_discharge_id': fields.many2one('t4.clinical.location', 'Discharge Location'),          
    }

class res_company(orm.Model):
    _name = 'res.company'
    _inherit = 'res.company'
    # default company has xmlid == 'main_company'
    _columns = {
        'pos_ids': fields.one2many('t4.clinical.pos', 'company_id', 'POSs'),
    }

class t4_clinical_location(orm.Model):
    """ Clinical LOCATION """

    _name = 't4.clinical.location'
    #_parent_name = 'location_id'
    _rec_name = 'code'
    _types = [('poc', 'Point of Care'), ('structural', 'Structural'), ('virtual', 'Virtual'), ('pos', 'POS')]
    _usages = [('bed', 'Bed'), ('ward', 'Ward'), ('room', 'Room'),('department', 'Department'), ('hospital', 'Hospital')]
    
    def _location2pos_id(self, cr, uid, ids, field, args, context=None):
        res = {}
        pos_pool = self.pool['t4.clinical.pos']
        #pos_ids = pos_pool.search(cr, uid, [])
        #import pdb; pdb.set_trace()
        for pos in pos_pool.browse_domain(cr, uid, []):
            for location in self.browse(cr, uid, ids, context):
                domain = ['|',('id', 'child_of', pos.location_id.id),('id','=',pos.location_id.id)]
                location_id = self.search(cr, uid, domain, context=context)
                res[location.id] = location_id and pos.id
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
        'name': fields.char('Location', size=100, required=True, select=True),
        'code': fields.char('Code', size=256),
        'parent_id': fields.many2one('t4.clinical.location', 'Parent Location'),
        'type': fields.selection(_types, 'Location Type'),
        'usage': fields.selection(_usages, 'Location Usage'),
        'active': fields.boolean('Active'),
        'pos_id': fields.function(_location2pos_id, type='many2one', relation='t4.clinical.pos', string='POS'),
        'company_id': fields.function(_location2company_id, type='many2one', relation='res.company', string='Company'),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),        
    }

        
    _defaults = {
        'active': True
    }

    def get_location_tasks(self, cr, uid, location_id, context=None):
        """
        """
        data_type_pool = self.pool['t4.clinical.task.data.type']
        all_models = [self.pool[data_type.data_model] for data_type in data_type_pool.browse_domain(cr, uid, [], context=context)]
        location_models = [m for m in all_models if 'location_id' in m._columns.keys()]
        task_ids = []
        for m in location_models:
            data = m.browse_domain(cr, uid, [('location_id','=',location_id)], context=context)
            data = data and data[0]
            data and data.task_id and task_ids.append(data.task_id.id)
        return task_ids

class hr_employee(orm.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    
    _columns = {
        'location_ids': fields.many2many('t4.clinical.location', 'employee_location_rel', 'employee_id', 'location_id', 'Locations of Responsibility'),
        
    }
    
    def get_employee_tasks(self, cr, uid, employee_id, context=None):
        """
        """
        location_pool = self.pool['location_pool']
        task_ids = []
        for employee in self.browse(cr, uid, employee_id, context):
            task_ids.extend(location_pool.get_location_tasks(cr, uid, location_id, context))
        return task_ids  
    
    
    

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
    
    
