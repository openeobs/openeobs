from openerp import models, fields, api


class NhClinicalWardboard(models.Model):

    _inherit = 'nh.clinical.wardboard'

    transfer_in_datetime = fields.Datetime(
        string='Transfer In Date & Time',
        compute='_get_transfer_in_datetime'
    )

    @api.depends('patient_id')
    def _get_transfer_in_datetime(self):
        """
        :return: The datetime when the patient was transferred to the current
        ward.
        :rtype: str
        """
        for record in self:
            ward_moves = self.move_ids.filtered(
                lambda move: move.location_id.usage == 'ward'
            )
            # If two items have the same sort key then their original order is
            # maintained.
            # This means that we can use `move_datetime` as the primary sort
            # key and `id` as the secondary sort key simply by doing the id
            # sort first.
            moves_sorted_by_id = sorted(
                ward_moves, key=lambda move: move.id
            )
            moves_sorted_by_move_datetime_then_id = sorted(
                moves_sorted_by_id, key=lambda move: move.move_datetime
            )
            last_move = moves_sorted_by_move_datetime_then_id[-1]
            record.transfer_in_datetime = last_move.move_datetime
