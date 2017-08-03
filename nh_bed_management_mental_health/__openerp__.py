# -*- encoding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
{
    'name': 'LiveObs Bed Management Mental Health',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': 'Mental Health extension of Bed Management for LiveObs',
    'description': """Mental Health extension of Bed Management for LiveObs""",
    'author': 'BJSS',
    'website': 'http://bjss.com',
    'depends': [
        'nh_bed_management',
        'nh_eobs_mental_health'
    ],
    'data': [
        'views/bed_availability.xml'
    ],
    'qweb': [],
    'application': True,
    'installable': True,
    'active': False
}
