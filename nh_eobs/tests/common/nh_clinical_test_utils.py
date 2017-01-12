# -*- coding: utf-8 -*-

from openerp.models import AbstractModel
from lxml import etree
from openerp.addons.nh_eobs.report.helpers import DataObj


class NhClinicalTestUtils(AbstractModel):

    _name = 'nh.clinical.test_utils'
    _inherit = 'nh.clinical.test_utils'

    # Setup methods
    def admit_and_place_patient(self):
        self.admit_patient()
        self.place_patient()

    def admit_patient(self):
        self.spell_model = self.env['nh.clinical.spell']
        self.api_model = self.env['nh.eobs.api']

        self.search_for_hospital_and_pos()
        self.create_locations()
        self.nurse = self.create_nurse()
        self.hca = self.create_hca()
        self.create_and_register_patient()

        self.api_model.admit(
            self.hospital_number, {'location': 'WA'}
        )

        self.spell = self.spell_model.search(
            [('patient_id', '=', self.patient_id)]
        )[0]
        self.spell_activity_id = self.spell.activity_id.id
        self.spell_activity = self.spell_model.browse(self.spell_activity_id)

    def create_and_register_patient(self):
        self.api_model = self.env['nh.eobs.api']
        self.patient_model = self.env['nh.clinical.patient']

        self.hospital_number = 'TESTHN001'
        self.patient_id = self.api_model.sudo().register(
            self.hospital_number,
            {
                'family_name': 'Testersen',
                'given_name': 'Test'
            }
        )
        self.patient = self.patient_model.browse(self.patient_id)

    def place_patient(self, location_id=None):
        if not location_id:
            location_id = self.bed.id
        self.activity_model = self.env['nh.activity']
        self.activity_pool = self.pool['nh.activity']

        self.placement = self.activity_model.search(
            [
                ('patient_id', '=', self.patient_id),
                ('data_model', '=', 'nh.clinical.patient.placement'),
                ('state', '=', 'scheduled')
            ]
        )[0]
        self.activity_pool.submit(
            self.env.cr, self.env.uid,
            self.placement.id, {'location_id': location_id}
        )
        self.activity_pool.complete(
            self.env.cr, self.env.uid, self.placement.id
        )

    def transfer_patient(self, location_code, hospital_number=None):
        if not hospital_number:
            hospital_number = self.hospital_number
        api_model = self.env['nh.eobs.api']
        api_model.transfer(hospital_number, {
            'location': location_code
        })

    def nursing_shift_change(self):
        ward = self.ward
        other_hca = self.create_hca(ward.id)
        other_nurse = self.create_nurse(ward.id)
        self.allocating_pool = self.env['nh.clinical.allocating']
        self.allocation_pool = self.env['nh.clinical.staff.allocation']
        wizard = self.allocation_pool.create({'ward_id': ward.id})
        wizard.submit_ward()
        wizard.deallocate()
        wizard.write({'user_ids': [[6, 0, [other_hca.id, other_nurse.id]]]})
        wizard.submit_users()
        allocating_ids = wizard.allocating_ids
        allocating_ids.write({
            'nurse_id': other_nurse.id,
            'hca_ids': [[6, 0, [other_hca.id]]],
            'location_id': self.bed.id
        })
        wizard.complete()
        return {
            'nurse': other_nurse,
            'hca': other_hca
        }

    def complete_open_activity(self, data_model, user_id=None):
        """
        Find and complete open activity in specified model

        :param data_model: Model to complete
        :param user_id: user to complete as
        """
        if not user_id:
            user_id = self.nurse.id
        api_pool = self.pool['nh.eobs.api']
        activity_model = self.env['nh.activity']
        task = activity_model.search([
            ['state', 'not in', ['completed', 'cancelled']],
            ['user_ids', 'in', [user_id]],
            ['data_model', '=', data_model]
        ])
        api_pool.complete(
            self.env.cr,
            user_id,
            task.id,
            {}
        )

    def cancel_open_activity(self, data_model, user_id=None):
        """
        Find and cancel open activity in specified model

        :param data_model: Model to cancel
        :param user_id: user to cancel as
        """
        if not user_id:
            user_id = self.nurse.id
        api_pool = self.pool['nh.eobs.api']
        activity_model = self.env['nh.activity']
        task = activity_model.search([
            ['state', 'not in', ['completed', 'cancelled']],
            ['user_ids', 'in', [user_id]],
            ['data_model', '=', data_model]
        ])
        api_pool.cancel(
            self.env.cr,
            user_id,
            task.id,
            {}
        )

    def get_report_triggered_action_status(self, activity_summary):
        """
        Generate report and find triggered action with summary

        :param activity_summary: String of triggered action summary
        :return: text content of status node in report
        """
        report_model = self.env['report.nh.clinical.observation_report']
        report = report_model.browse(self.spell.id)
        data = DataObj(spell_id=self.spell.id)
        report_data = report.get_report_data(data)
        report_html = self.env['report'].render(
            'nh_eobs.observation_report', report_data)
        root = etree.fromstring(report_html)
        return ''.join(
            root.xpath(
                "//h4[@class='triggered_action_task_header']"
                "[text()[contains(.,'{}')]]"
                "/parent::td/parent::tr/parent::table/tr[last()]/td[last()]"
                .format(activity_summary))[0].itertext()).strip()


