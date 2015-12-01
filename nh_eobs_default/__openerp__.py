# Part of Open eObs. See LICENSE file for full copyright and licensing details.
# -*- encoding: utf-8 -*-
{
    'name': 'Open e-Obs Default Configuration',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """    """,
    'author': 'Neova Health',
    'website': 'http://www.neovahealth.co.uk/',
    'depends': ['nh_eobs_mobile'],
    'data': ['trust.xml', 'params.xml'],
    'qweb': ['static/src/xml/nh_eobs_default.xml'],
    'css': ['static/src/css/nh_eobs_default.css'],
    'application': True,
    'installable': True,
    'active': False,
}