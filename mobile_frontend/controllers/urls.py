__author__ = 'colin'
URL_PREFIX = '/mobile/'

routes = [
    {
        'name': 'patient_list',
        'endpoint': 'patients/',
        'methods': ['GET'],
        'args': []
    },
    {
        'name': 'single_list',
        'endpoint': 'patient/',
        'methods': ['GET'],
        'args': ['patient_id']
    },
    {
        'name': 'task_list',
        'endpoint': 'tasks/',
        'methods': ['GET'],
        'args': []
    },
    {
        'name': 'single_task',
        'endpoint': 'task/',
        'methods': ['GET'],
        'args': ['task_id']
    },
    {
        'name': 'stylesheet',
        'endpoint': 'src/css/main.css',
        'methods': ['GET'],
        'args': []
    },
    {
        'name': 'jquery',
        'endpoint': 'src/js/jquery.js',
        'methods': ['GET'],
        'args': []
    },
    {
        'name': 'js_routes',
        'endpoint': 'src/js/routes.js',
        'methods': ['GET'],
        'args': []
    },
    {
        'name': 'logo',
        'endpoint': 'src/img/logo.png',
        'methods': ['GET'],
        'args': []
    },
    {
        'name': 'login',
        'endpoint': 'login/',
        'methods': ['GET','POST'],
        'args': []
    },
    {
        'name': 'logout',
        'endpoint': 'logout/',
        'methods': ['GET'],
        'args': []
    },
    {
        'name': 'task_form_action',
        'endpoint': 'task/submit/',
        'methods': ['POST'],
        'args': ['task_id']
    },
    {
        'name': 'patient_form_action',
        'endpoint': 'patient/submit/',
        'methods': ['POST'],
        'args': ['patient_id']
    },
    {
        'name': 'ews_score',
        'endpoint': 'ews/score/',
        'methods': ['POST'],
        'args': []
    }
]


def get_urls():
    r = {}
    for route in routes:
        r[route['name']] = URL_PREFIX+route['endpoint']
    return r



URLS = get_urls()