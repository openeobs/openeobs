# -*- encoding: utf-8 -*-
{
    'name': 'NH Clinical Default Configuration',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """    """,
    'author': 'Neova Health',
    'website': 'http://www.neovahealth.co.uk/',
    'depends': ['nh_clinical_ui', 'mobile_frontend'],
    
    
    'data': ['trust.xml',
             'greenford_pos.xml', 'greenford_locations.xml', 'greenford_users.xml','greenford_devices.xml','greenford_params.xml'],
             
             
    'qweb': ['static/src/xml/nh_clinical_default.xml'],
    'css': ['static/src/css/nh_clinical_default.css'],
    
    
    'application': True,
    'installable': True,
    'active': False,
}