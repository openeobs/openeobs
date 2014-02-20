# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import SUPERUSER_ID


class t4_clinical_pos(orm.Model):
    """ Clinical point of service.
    Place of service Managed care The 'where' a medical service is provided–eg, 
    clinic, hospital inpatient, hospital outpatient, nursing facility, home, clinic, etc
     
    Trust-level. In most cases will probably have 1"""
     
    _name = 't4.clinical.pos'
    _columns = {
        'name': fields.char('Name', size=256),  
        'company_id': fields.many2one('res.company', 'Trust'),
        'lot_input_id': fields.many2one('t4.clinical.location', 'Input Lot'),
        'lot_pos_id': fields.many2one('t4.clinical.location', 'POS Lot'),
        'lot_output_id': fields.many2one('t4.clinical.location', 'Output Lot'),     
    }
    
    # we may put all the api here
     
class t4_clinical_location(orm.Model):
    """ Clinical point of service LOCATION """
     
    _name = 't4.clinical.location'
    _parent_name = 'location_id'
    _rec_name = 'code'
    # poc == bed, surgery table, shelf in morgue. Place where patient may be allocated to receive service. It may make sense to split into specific types
    # structural == storey, ward, corridor
    _types = [('poc','Point of Care'), ('structural', 'Structural'), ('virtual', 'Virtual')]
    _usages = [('bed','Bed'), ('ward','Ward'), ('department', 'Department'), ('pos', 'POS')]
    _columns = {
        'code': fields.char('Code', size=256),
        'location_id': fields.many2one('t4.clinical.location', 'Parent Location'),
        'type': fields.selection(_types, 'Location Type'),
        'usage': fields.selection(_usages, 'Location Usage'),
        'capacity': fields.integer('Capacity'),
        'is_available': fields.boolean('Is Available', help="Will")
    }     

class res_partner(orm.Model):
    """
    """
    _inherit = 'res.partner'
    _columns = {
        'is_patient': fields.boolean('Is Patient?'),
    }

 
# class t4_clinical_device(orm.Model):
#     _name = 't4.clinical.device'
#     _inherit = ['t4.clinical.equipment', 't4.clinical.agent']
#     
#     def connect_patient(self, cr, uid, device_id, patient_id, context=None):
#         pass
#     def disconnect_patient(self, cr, uid, device_id, patient_id, context=None):
#         pass  


# class t4_clinical_agent(orm.Model):
#     """ Clinical Agent
#     openEHR concept of HCA - health care agent, to who a task may be assigned  
#     this is base class for employee and device
#     """
#     
#     _name = 't4.clinical.agent'
#     _columns = {
#         'cinical_agent_id': fields.many2one('t4.clinical.agent', 'Clinical Agent'),
#     }
#     
# class t4_clinical_patient_agent(orm.Model):
#     """ 
#     """
#     
#     _name = 't4.clinical.patient.agent'
#     _columns = {
#         'patient_agent_id': fields.many2one('t4.clinical.patient.agent', 'Patient Agent'),
#     }   
