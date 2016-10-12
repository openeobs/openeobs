# -*- encoding: utf-8 -*-
{
    'name': 'Open e-Obs Mental Health Demo Loader',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """    """,
    'author': 'Neova Health',
    'website': 'http://www.neovahealth.co.uk/',
    'depends': ['nh_eobs_demo', 'nh_eobs_mental_health'],
    'data': [
        'data/ward_a/obs_stop.xml',
        'data/ward_b/obs_stop.xml',
        'data/ward_c/obs_stop.xml',
        'data/ward_d/obs_stop.xml',
        'data/ward_e/obs_stop.xml'
    ],
    'application': True,
    'installable': True,
    'active': False,
}
