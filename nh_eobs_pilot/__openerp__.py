# Part of Open eObs. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'NH eObs Pilot',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """     """,
    'author': 'Neova Health',
    'website': 'http://www.neovahealth.co.uk/',
    'depends': ['nh_eobs'],
    'data': ['views/spell_management_views.xml',
             'views/menuitem.xml',
             'security/ir.model.access.csv'],
    'application': True,
    'installable': True,
    'active': False,
}