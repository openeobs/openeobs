# -*- coding: utf-8 -*-
from lxml import etree
from openerp.addons.nh_eobs.report.helpers import DataObj
from openerp.models import AbstractModel


class NhClinicalTestUtils(AbstractModel):

    _name = 'nh.clinical.test_utils'
    _inherit = 'nh.clinical.test_utils'

    def nursing_shift_change(self):
        ward = self.ward
        other_hca = self.create_hca(ward.id)
        other_nurse = self.create_nurse(ward.id)
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

    def complete_open_activity(self, data_model, user_id=None, vals=None):
        """
        Find and complete open activity in specified model

        :param data_model: Model to complete
        :param user_id: user to complete as
        """
        if not vals:
            vals = {}
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
            vals
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
        return task

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

    def create_locations(self):
        """
        Add eobs context to beds created by create_locations in nh_clinical
        """
        super(NhClinicalTestUtils, self).create_locations()
        self.context_pool = self.env['nh.clinical.context']
        self.eobs_context = self.context_pool.search(
            [['name', '=', 'eobs']]
        )[0]
        self.bed.write({'context_ids': [[4, self.eobs_context.id]]})
        self.other_bed.write({'context_ids': [[4, self.eobs_context.id]]})

    def discharge_patient(self, hospital_number=None):
        """ Overriding discharge patient to use nh.eobs.api so can take
        advantage of overrides there

        :param hospital_number: hospital number of patient
        """
        if not hospital_number:
            hospital_number = self.hospital_number
        api_model = self.env['nh.eobs.api']
        api_model.discharge(hospital_number, {
            'location': 'DISL'
        })

    def transfer_patient(self, location_code, hospital_number=None):
        """
        Overriding transfer patient to use nh.eobs.api so can take advantage of
        overrides there

        :param location_code: Code to transfer patient to
        :param hospital_number: Hospital number of patient
        """
        if not hospital_number:
            hospital_number = self.hospital_number
        api_model = self.env['nh.clinical.api']
        api_model.transfer(hospital_number, {
            'location': location_code
        })
