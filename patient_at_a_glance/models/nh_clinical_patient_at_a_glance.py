# -*- coding: utf-8 -*-
from openerp import models, fields


class NhClinicalPatientAtAtGlance(models.Model):

    _name = 'nh.clinical.patient.at_a_glance'

    given_name = fields.Char()
    middle_name = fields.Char()
    family_name = fields.Char()
    sex = fields.Selection(selection=[
        ('male', 'Male'),
        ('female', 'Female')
    ])
    gender = fields.Selection(selection=[
        ('cisgender', 'Cisgender'),
        ('non-binary', 'Non-binary'),
        ('gender fluid', 'Gender Fluid')
    ])

    hospital_number = fields.Char()
    nhs_number = fields.Char()

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

    patient_in_detail = fields.Many2one(
        comodel_name='nh.clinical.patient.in_detail')
