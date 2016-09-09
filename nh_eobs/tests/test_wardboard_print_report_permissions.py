from openerp.tests.common import SingleTransactionCase
from lxml import etree


class TestWardboardPrintReportPermissions(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWardboardPrintReportPermissions, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        ir_model_pool = cls.registry('ir.model.data')
        cls.ui_view_pool = cls.registry('ir.ui.view')
        cls.qweb = cls.registry('ir.qweb')
        user_pool = cls.registry('res.users')
        location_pool = cls.registry('nh.clinical.location')

        wards = location_pool.search(cr, uid, [['usage', '=', 'ward']])
        if not wards:
            raise ValueError('Wards not found')

        beds = location_pool.search(cr, uid, [
            ['usage', '=', 'bed'],
            ['parent_id', '=', wards[0]]
        ])
        if not beds:
            raise ValueError('Beds not found')

        hcas = user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical HCA Group'],
            ['location_ids', 'in', beds]
        ])
        if not hcas:
            raise ValueError('HCA not found')
        cls.hca = hcas[0]

        nurses = user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical Nurse Group'],
            ['location_ids', 'in', beds]
        ])
        if not nurses:
            raise ValueError('Nurses not found')
        cls.nurse = nurses[0]

        shift_coordinators = user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical Shift Coordinator Group'],
            ['location_ids', 'in', wards]
        ])
        if not shift_coordinators:
            raise ValueError('Shift Coordinator not found')
        cls.shift_coordinator = shift_coordinators[0]

        senior_managers = user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical Senior Manager Group'],
            ['location_ids', 'in', wards]
        ])
        if not senior_managers:
            raise ValueError('Shift Coordinator not found')
        cls.senior_manager = senior_managers[0]

        view_id = ir_model_pool.get_object_reference(cr, uid, 'nh_eobs',
                                                     'view_wardboard_form')[1]
        view_rec = cls.ui_view_pool.read_template(cr, uid, view_id, context={})
        view = etree.fromstring(view_rec)
        button = view.findall(".//header/button[@string='Print Report']")
        cls.button_groups = button[0].get('groups')

    def test_hca_cant_see_print_report_button(self):
        self.assertFalse(
            self.registry('ir.ui.view').user_has_groups(
                self.cr, self.hca, groups=self.button_groups, context={}))

    def test_nurse_cant_see_print_report_button(self):
        self.assertFalse(
            self.registry('ir.ui.view').user_has_groups(
                self.cr, self.nurse, groups=self.button_groups, context={}))

    def test_shift_coordinator_can_see_print_report_button(self):
        self.assertTrue(
            self.registry('ir.ui.view').user_has_groups(
                self.cr, self.shift_coordinator, groups=self.button_groups,
                context={}))

    def test_senior_manager_can_see_print_report_button(self):
        self.assertTrue(
            self.registry('ir.ui.view').user_has_groups(
                self.cr, self.senior_manager, groups=self.button_groups,
                context={}))

    # def test_openeobs_admin_can_see_print_report_button(self):
    #     self.assertTrue(
    #         self.registry('ir.ui.view').user_has_groups(
    #             self.cr, self.shift_coordinator, groups=self.button_groups,
    #             context={}))

    def test_default_admin_can_see_print_report_button(self):
        self.assertTrue(
            self.registry('ir.ui.view').user_has_groups(
                self.cr, self.uid, groups=self.button_groups,
                context={}))
