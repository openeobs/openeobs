# -*- encoding: utf-8 -*-
{
    'name': 'T4clinical Production Settings',
    'version': '2.0-alpha',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': 'T4clinical Common Production Settings',
    'description': """This module holds common production settings for t4Clinical

    """,
    'author': 'Tactix4',
    'website': 'http://www.tactix4.com/',
    'depends': ['t4clinical_base','t4clinical_activity_types'],
    'data': ['t4clinical_production_data.xml'
        ],
    'js': ['static/src/js/t4clinical_production.js'],
    'qweb': ['static/src/xml/t4clinical_production.xml'],
    'installable': True,
    'active': False,
}
