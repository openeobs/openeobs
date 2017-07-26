# -*- coding: utf-8 -*-
from openerp import models, fields, api


class NhClinicalBedAvailability(models.AbstractModel):

    _name = 'nh.clinical.bed_availability'
    _order = 'bed_status desc'

    hospital_name = fields.Char()
    ward_name = fields.Char()
    bed_name = fields.Char()
    bed_status = fields.Char()
    patient_status = fields.Char()

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None,
                    order=None, context=None):
        location_model = self.env['nh.clinical.location']
        # Read all hospitals, wards, and beds.
        locations = location_model.search_read(
            domain=[('usage', 'in', ['hospital', 'ward', 'bed'])],
            fields=['parent_id', 'name', 'patient_ids', 'usage'],
            offset=offset,
            limit=limit
        )

        bed_availability_records = []
        for location in locations:
            hospital_name, ward_name, bed_name = self._get_location_names(
                location)
            bed_status = self._get_bed_status(location)
            patient_status = 'Unknown'

            bed_availability_record = {
                'id': location['id'],
                'hospital_name': hospital_name,
                'ward_name': ward_name,
                'bed_name': bed_name,
                'bed_status': bed_status,
                'patient_status': patient_status,
            }
            bed_availability_records.append(bed_availability_record)

        if order:
            order_field, order_type = order.split(' ')
            bed_availability_records = sorted(
                bed_availability_records,
                cmp=None,
                key=lambda i: i[order_field],
                reverse=order_type.lower() == 'desc'
            )
        return bed_availability_records

    def _get_location_names(self, location):
        location_names = [None] * 3
        usage = location['usage']

        if isinstance(location['parent_id'], tuple):
            # Is actually a 'reference' tuple, not an ID.
            parent_id = location['parent_id'][0]

        if usage == 'hospital':
            location_names[0] = location['name']

        elif usage == 'ward':
            location_model = self.env['nh.clinical.location']
            location_names[0] = location_model.browse(parent_id).name
            location_names[1] = location['name']

        elif usage == 'bed':
            location_model = self.env['nh.clinical.location']
            ward = location_model.browse(parent_id)
            hospital = ward.parent_id

            location_names[0] = hospital.name
            location_names[1] = ward.name
            location_names[2] = location['name']

        return location_names

    @staticmethod
    def _get_bed_status(location):
        if location['usage'] == 'bed':
            if len(location['patient_ids']):
                return 'Occupied'
            else:
                return 'Available'
