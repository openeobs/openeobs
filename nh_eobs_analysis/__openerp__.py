# Part of Open eObs. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'NH eObs Analysis',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """    """,
    'author': 'Neova Health',
    'website': 'http://www.neovahealth.co.uk/',
    'depends': ['nh_eobs', 'board', 'web_graph'],
    'data': [
        'views/news.xml',
        'views/dashboard.xml',
        'views/menuitem.xml',
        'views/static_resources.xml',
        'security/ir.model.access.csv'],
    'qweb': [],
    'application': True,
    'installable': True,
    'active': False,
}
