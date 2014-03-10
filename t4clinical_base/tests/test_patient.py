from openerp.tests import common
from datetime import datetime


class TestPatients(common.TransactionCase):
    def setUp(self):
        """***setup patient tests***"""
        super(TestPatients, self).setUp()
        cr, uid, = self.cr, self.uid
        self.patient_pool = self.registry('t4.clinical.patient')
        self.location_pool = self.registry('t4.clinical.location')
        
        
        self.new_patient_id = self.patient_pool.create(cr, uid, {

            'given_name': 'Fred',
            'middle_names': 'John',
            'family_name': 'Flintstone',
            'dob': datetime.now(),
            'sex': 'M',
            'gender': 'M',
            'patient_identifier': 'NHS2223',
            'other_identifier': 'HOSPNO778',
            })

    def xml2db_id(self, xmlid):
        imd_pool = self.registry('ir.model.data')
        imd_id = imd_pool.search(self.cr, self.uid, [('name','=', xmlid)])
        imd = imd_pool.browse(self.cr, self.uid, imd_id)
        return imd.res_id
     
    def test_patient_name_returns_concatenated(self):
        cr, uid = self.cr, self.uid
        patient = self.patient_pool.browse(cr, uid, self.new_patient_id, context=None)
        self.assertEqual('Flintstone, Fred John', patient.name,
                         msg="Patient has the wrong name: %s" % patient.name)
        self.assertTrue(isinstance(patient.color, int))

#     def test_admit_patient(self):
#         pos_id = self.xml2db_id('demo_location_pos_uhg')
#         self.spell_pool.admit_patient(self.cr, self.uid, self.new_patient_id, pos_id)
        
        