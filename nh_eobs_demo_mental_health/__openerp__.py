# -*- encoding: utf-8 -*-
{
    'name': 'LiveObs Demo Loader for Mental Health',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': 'Create a mental health demo installation of LiveObs.',
    'description': """
    Extends the data created by the 'LiveObs Demo Loader' module to create a \
    demo that includes mental health specific functionality.
    """,
    'author': 'Neova Health',
    'website': 'http://www.neovahealth.co.uk/',
    'depends': ['nh_eobs_demo', 'nh_eobs_mental_health'],
    'data': [
        'data/ward_a/obs_stop.xml',
        'data/ward_b/obs_stop.xml',
        'data/ward_c/obs_stop.xml',
        'data/ward_d/obs_stop.xml',
        'data/ward_e/obs_stop.xml',
        'data/ward_a/refused_obs.xml'
    ],
    'application': True,
    'installable': True,
    'active': False,
}
