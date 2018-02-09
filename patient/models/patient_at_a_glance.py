# -*- coding: utf-8 -*-
from openerp import models, fields


class NhClinicalPatientAtAtGlance(models.Model):

    _name = 'patient.at_a_glance'

    patient = fields.Many2one(comodel_name='patient',
                              required=True)

    location = fields.Char()

    clinical_risk = fields.Selection(selection=[
        ('low (score 0)', 'Low (Score 0)'),
        ('low', 'Low'),
        ('low-medium', 'Low-Medium'),
        ('medium', 'Medium'),
        ('high', 'High')
    ])
    news_score = fields.Integer()
    news_score_trend = fields.Selection(selection=[
        ('improving', 'Improving'),
        ('unchanged', 'Unchanged'),
        ('deteriorating', 'Deteriorating')
    ])

    time_to_next_observation = fields.Char()
