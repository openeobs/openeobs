# -*- coding: utf-8 -*-
{
    'name': 'Neurological Observations',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': "Allows users to record neurological observations.",
    'author': 'BJSS',
    'website': 'http://www.liveobs.com/',
    'depends': ['nh_gcs',
                'nh_eobs',
                'nh_eobs_mobile'],
    'data': [
        'security/ir.model.access.csv',
        'views/template.xml',
        'views/observation_report_template.xml',
        'views/acuity_board_buttons.xml'
    ],
    'qweb': [],
    'application': True,
    'installable': True,
    'active': False,
}
