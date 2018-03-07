# -*- encoding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
{
    'name': 'Bed Management',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': 'Bed Management for LiveObs.',
    'description': """Bed Management for LiveObs.""",
    'author': 'BJSS',
    'website': 'http://www.liveobs.com/',
    'depends': [
        'nh_clinical'
    ],
    'data': [
        'data/bed_manager_user.xml',
        'views/bed_availability.xml',
        'security/ir.model.access.csv'
    ],
    'qweb': [],
    'application': True,
    'installable': True,
    'active': False
}
