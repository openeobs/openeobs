from openerp.models import AbstractModel


class NhClinicalTestUtils(AbstractModel):

    _inherit = 'nh.clinical.test_utils'

    def setup_ward(self):
        super(NhClinicalTestUtils, self).setup_ward()
        self.create_shifts()

    def create_shifts(self):
        shift_model = self.env['nh.clinical.shift']
        shift_model.create({
            'ward': self.ward.id,
            'nurses': [(6, 0, [self.nurse.id])],
            'hcas': [(6, 0, [self.hca.id])]
        })
