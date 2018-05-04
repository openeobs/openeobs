from openerp import models, fields, api


class NhClinicalWardboard(models.Model):

    _inherit = 'nh.clinical.wardboard'

    last_movement_datetime = fields.Datetime(
        string='Last Movement Date & Time',
        compute='_get_last_movement_datetime'
    )

    @api.depends('move_ids')
    def _get_last_movement_datetime(self):
        """
        :return: The last patient movement datetime.
        :rtype: str
        """
        for record in self:
            # If two items have the same sort key then their original order is
            # maintained.
            # This means that we can use `move_datetime` as the primary sort
            # key and `id` as the secondary sort key simply by doing the id
            # sort first.
            moves_sorted_by_id = sorted(
                record.move_ids, key=lambda move: move.id
            )
            moves_sorted_by_move_datetime_then_id = sorted(
                moves_sorted_by_id, key=lambda move: move.move_datetime
            )
            last_move = moves_sorted_by_move_datetime_then_id[-1]
            last_movement_datetime = last_move.move_datetime
            record.last_movement_datetime = last_movement_datetime
