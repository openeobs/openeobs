# -*- coding: utf-8 -*-
from openerp import models, fields, api


class NhClinicalBedAvailability(models.Model):

    _name = 'nh.clinical.bed_availability'
    _inherit = 'nh.activity.data'

    location = fields.Many2one(
        comodel_name='nh.clinical.location'
    )
    name = fields.Char(related='location.name')
    hospital_name = fields.Char(
        string='Hospital Name',
        compute='_get_hospital_name',
        store=True
    )
    ward_name = fields.Char(
        string='Ward Name',
        compute='_get_ward_name',
        store=True
    )
    bed_name = fields.Char(
        string='Bed Name',
        compute='_get_bed_name',
        store=True
    )
    bed_status_selection = [
        ('available', 'Available'),
        ('occupied', 'Occupied')
    ]
    bed_status = fields.Selection(
        selection=bed_status_selection,
        string='Bed Status',
        compute='_get_bed_status'
    )

    def init(self, cr):
        self.delete_and_recreate_all_records(cr, 1)

    @api.model
    def delete_and_recreate_all_records(self):
        self.search([]).unlink()

        location_model = self.env['nh.clinical.location']
        # Read all hospitals, wards, and beds.
        locations = location_model.search_read(
            domain=[('usage', '=', 'bed')],
            fields=['parent_id', 'name', 'patient_ids', 'usage'],
        )

        bed_availability_records = []
        for location in locations:
            bed_availability_record = self.create({
                'location': location['id']
            })
            bed_availability_records.append(bed_availability_record)
        return bed_availability_records

    @api.depends('location')
    def _get_hospital_name(self):
        for record in self:
            record.hospital_name = \
                record._get_location_name(record.location, 'hospital')

    @api.depends('location')
    def _get_ward_name(self):
        for record in self:
            record.ward_name = record._get_location_name(
                record.location, 'ward')

    @api.depends('location')
    def _get_bed_name(self):
        for record in self:
            record.bed_name = record._get_location_name(record.location, 'bed')

    @staticmethod
    def _get_location_name(location, location_type):
        while True:
            if location.usage == location_type:
                return location.name
            if location.parent_id:
                location = location.parent_id
                continue
            return None

    @api.depends('location')
    def _get_bed_status(self):
        for record in self:
            bed_status = None
            if record.location.usage == 'bed':
                # Originally tried just using `record.location.patient_ids` but
                # for some reason this destroyed performance, taking
                # ~10 minutes to create all the bed availability records.
                # Not sure why this is but read did not have the same problem.
                patient_ids = record.location.read(
                    fields=['patient_ids'])[0]['patient_ids']
                if patient_ids:
                    bed_status = 'occupied'
                else:
                    bed_status = 'available'
            record.bed_status = bed_status
