# -*- encoding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
{
    'name': 'NH Food and Fluid Observation',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """    """,
    'author': 'BJSS',
    'website': 'http://www.bjss.com/',
    'depends': ['nh_observations'],
    'data': [
        'security/ir.model.access.csv',
        'data/recorded_concerns.xml',
        'data/dietary_needs.xml'
    ],
    'demo': [],
    'css': [],
    'js': [],
    'qweb': [],
    'images': [],
    'application': True,
    'installable': True,
    'active': False,
}
