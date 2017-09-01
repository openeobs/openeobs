# -*- coding: utf-8 -*-
# from openerp import models


# class WardboardSql(models.AbstractModel):

# _inherit = 'nh.clinical.sql'
# _name = 'nh.clinical.sql'

# Add this to the SELECT of the wardboard_skeleton
# """
# CASE WHEN weight.status THEN 'yes' ELSE 'no' END AS weight_monitoring
# """
# Add this to the LEFT JOINs of the wardboard skeleton
# """
# LEFT JOIN weight ON weight.spell_id = spell.id
# """
