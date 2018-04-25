{
    'name': 'Therapeutic',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': 'Adds therapeutic observations to LiveObs.',
    'description': """
    Adds therapeutic observations to LiveObs. Therapeutic observations attempt 
    to assess the general well-being of the patient by making note of things 
    like their status and location.
    """,
    'author': 'BJSS',
    'website': 'http://www.liveobs.com/',
    'depends': ['nh_eobs_mental_health'],
    'data': [
        'security/ir.model.access.csv',
        'views/set_therapeutic_level.xml'
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
