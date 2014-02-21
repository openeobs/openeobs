# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv


class t4_clinical_location(orm.Model):
    """ Clinical point of service LOCATION """

    _name = 't4.clinical.location'
    _parent_name = 'location_id'
    _rec_name = 'code'
    _types = [('poc', 'Point of Care'), ('structural', 'Structural'), ('virtual', 'Virtual'), ('pos', 'POS')]
    _usages = [('bed', 'Bed'), ('ward', 'Ward'), ('department', 'Department'), ('hospital', 'Hospital')]
    _columns = {
        'name': fields.char('Point of Care', size=100, required=True, select=True),
        'code': fields.char('Code', size=256),
        'location_id': fields.many2one('t4.clinical.location', 'Parent Location'),
        'type': fields.selection(_types, 'Location Type'),
        'usage': fields.selection(_usages, 'Location Usage'),
        'is_available': fields.boolean('Is Available', help="Will"),
        'active': fields.boolean('Active')
    }
    _defaults = {
        'active': True
    }


class t4_clinical_patient(osv.Model):
    """T4Clinical Patient object, to store all the parameters of the Patient
    """
    _name = "t4.clinical.patient"
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
    }
