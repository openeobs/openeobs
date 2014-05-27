# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
import logging        
_logger = logging.getLogger(__name__)

from openerp import SUPERUSER_ID

T4SUID = SUPERUSER_ID

class ir_model_access(orm.Model):
    _inherit = 'ir.model.access'
    _columns = {
        'perm_responsibility': fields.boolean('T4 Clinical Activity Responsibility'),
    }

class t4clinical_res_partner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'doctor': fields.boolean('Doctor', help="Check this box if this contact is a Doctor"),
        'code': fields.char('Code', size=256),
    }



class t4_clinical_device_type(orm.Model):
    _name = 't4.clinical.device.type'

    _columns = {
        'name': fields.text("Device Type"),
        'flow_direction': fields.selection([('none', 'None'), ('in', 'In'), ('out', 'Out'), ('both', 'Both')], 'Flow Direction')
    }


class t4_clinical_device(orm.Model):
    _name = 't4.clinical.device'
    _rec_name = 'type_id'
    _columns = {
        'type_id': fields.many2one('t4.clinical.device.type', "Device Type"),
        'name': fields.related('type_id', 'name', type='text'),
        'is_available': fields.boolean('Is Available?'),
        
    }
    
    _defaults = {
         'is_available': True
     }
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        for device in self.browse(cr, uid, ids, context):
            res.append((device.id, device.type_id.name))
        return res

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
        #'ews_init_frequency': fields.integer('EWS Initial Frequency in Minutes')
    }

    _defaults = {
        #'ews_init_frequency': 15
    }


class res_company(orm.Model):
    _name = 'res.company'
    _inherit = 'res.company'
    _columns = {
        'pos_ids': fields.one2many('t4.clinical.pos', 'company_id', 'Points of Service'),
    }
    

class res_users(orm.Model):
    _name = 'res.users'
    _inherit = 'res.users'
    _columns = {
        'pos_id': fields.many2one('t4.clinical.pos', 'POS'),
        'location_ids': fields.many2many('t4.clinical.location', 'user_location_rel', 'user_id', 'location_id', 'Parent Locations of Responsibility'),
    }
    def get_all_responsibility_location_ids(self, cr, uid, user_id, context=None):
        location_pool = self.pool['t4.clinical.location']
        location_ids =[]
        #import pdb; pdb.set_trace()
        for user_location_id in self.browse(cr, uid, user_id, context).location_ids: 
            location_ids.extend( location_pool.search(cr, uid, [['id', 'child_of', user_location_id.id]]) )
        return location_ids

 

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
        #import pdb; pdb.set_trace()
        for location in self.browse(cr, uid, ids, context):
            pos_location_id = self.search(cr, uid, [['parent_id','=',False],['child_ids','child_of',location.id]])
            pos_location_id = pos_location_id and pos_location_id[0] or False
            pos_id = pos_pool.search(cr, uid, [['location_id','=',pos_location_id]])
            res[location.id] = pos_id and pos_id[0] or False
            if not pos_id:
                _logger.warning("pos_id not found for location '%s', id=%s" % (location.code, location.id))
        return res
    
    def _pos2location_id(self, cr, uid, ids, context=None):
        res = []
        for pos in self.browse(cr, uid, ids, context):
            res.extend(self.pool['t4.clinical.location'].search(cr, uid, [['id','child_of',pos.location_id.id]]))
        return res          
 
    def _is_available(self, cr, uid, ids, field, args, context=None):
        res = {}
        available_location_ids = self.get_available_location_ids(cr, uid, context=context)
        for location in self.browse(cr, uid, ids, context):
            res[location.id] = location.id in available_location_ids
        return res
    
    def _placement2location_id(self, cr, uid, ids, context=None):
        sql = """
            select distinct m.location_id from t4_activity a
            inner join t4_clinical_patient_move m on a.data_model = 't4.clinical.patient.move' and m.activity_id = a.id
            where a.state = 'completed'     
        """
        cr.execute(sql)
        res = [rec['location_id'] for rec in cr.dictfetchall()]
        return res

    
    def _get_patient_ids (self, cr, uid, ids, field, args, context=None):
        pass   
         
         
    _columns = {
        'name': fields.char('Location', size=100, required=True, select=True),
        'code': fields.char('Code', size=256),
        'parent_id': fields.many2one('t4.clinical.location', 'Parent Location'),
        'child_ids': fields.one2many('t4.clinical.location', 'parent_id', 'Child Locations'),
        'type': fields.selection(_types, 'Location Type'),
        'usage': fields.selection(_usages, 'Location Usage'),
        'active': fields.boolean('Active'),
        'pos_id': fields.function(_location2pos_id, type='many2one', relation='t4.clinical.pos', string='POS', store={
                                  't4.clinical.location': (lambda s, cr, uid, ids, c: s.search(cr, uid, [['id','child_of',ids]]), ['parent_id'], 10),
                                  't4.clinical.pos': (_pos2location_id, ['location_id'], 5),
                                    }),
        'company_id': fields.related('pos_id', 'company_id', type='many2one', relation='res.company', string='Company'),
        'is_available': fields.function(_is_available, type='boolean', string='Is Available?', 
                                        store={
                                               't4.clinical.location': (lambda self, cr, uid, ids, c: ids, [], 10),
                                               't4.activity': (_placement2location_id, ['state'], 20)
                                        }),
        'patient_capacity': fields.integer('Patient Capacity'),
        'patient_ids': fields.function(_get_patient_ids, type='one2many',relation='t4.clinical.patient', string="Location Patients"),
        'user_ids': fields.many2many('res.users', 'user_location_rel', 'location_id', 'user_id', 'Responsible Users'),
      
    }

        
    _defaults = {
        'active': True,
        'patient_capacity': 1
    }

    def get_location_activity_ids(self, cr, uid, location_id, context=None):
        """
        """
        location_models = [model for model_name, model in self.pool.models.items() 
                           if 'location_id' in model._columns.keys()
                           and model._columns['location_id']._obj == 't4.clinical.location']
        activity_ids = []
        for m in location_models:
            data = m.browse_domain(cr, uid, [('location_id','=',location_id)], context=context)
            data = data and data[0]
            data and data.activity_id and activity_ids.append(data.activity_id.id)
        return activity_ids
    
    
    def get_available_location_ids(self, cr, uid, usages=[], location_id=None, context=None):
          api_pool = self.pool['t4.clinical.api']  
          location_map = api_pool.location_availability_map(cr, uid, 
                                                            ids=[], types=[], usages=[], codes=[],
                                                            occupied_range=[], capacity_range=[], available_range=[1,1])
          res = [k for k,v in location_map.items()]
          return res


    def activate_deactivate(self, cr, uid, location_id, context=None):
        location = self.browse(cr, uid, location_id[0], context=context)
        data = {'active': False} if location.active and location.is_available else {'active': True}
        if location.active and not location.is_available:
            raise osv.except_osv('Error!', "Can't deactivate a location that is being used.")
        return self.write(cr, uid, location.id, data, context=context)
    

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
        'current_location_id': fields.many2one('t4.clinical.location', 'Current Location'),    
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
