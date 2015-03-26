from openerp.tools import config
SERVER_PROTOCOL = "http"
SERVER_ADDRESS = "localhost"
SERVER_PORT = "{0}".format(config['xmlrpc_port'])
URL_PREFIX = '/mobile/'
BASE_URL = SERVER_PROTOCOL+'://'+SERVER_ADDRESS+':'+SERVER_PORT+URL_PREFIX

routes = [
    {
        'name': 'patient_list',
        'endpoint': 'patients/',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'single_patient',
        'endpoint': 'patient/',
        'method': 'GET',
        'args': ['patient_id']
    },
    {
        'name': 'json_patient_info',
        'endpoint': 'patient/info/',
        'method': 'GET',
        'args': ['patient_id']
    },
    {
        'name': 'task_list',
        'endpoint': 'tasks/',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'single_task',
        'endpoint': 'task/',
        'method': 'GET',
        'args': ['task_id']
    },
    {
        'name': 'stylesheet',
        'endpoint': 'src/css/main.css',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'manifest',
        'endpoint': 'src/manifest.json',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'small_icon',
        'endpoint': 'src/icon/hd_small.png',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'big_icon',
        'endpoint': 'src/icon/hd_hi.png',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'jquery',
        'endpoint': 'src/js/jquery.js',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'js_routes',
        'endpoint': 'src/js/routes.js',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'observation_form_js',
        'endpoint': 'src/js/observation.js',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'observation_form_validation',
        'endpoint': 'src/js/validation.js',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'data_driven_documents',
        'endpoint': 'src/js/d3.js',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'patient_graph',
        'endpoint': 'src/js/draw_ews_graph.js',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'graph_lib',
        'endpoint': 'src/js/graph_lib.js',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'logo',
        'endpoint': 'src/img/logo.png',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'login',
        'endpoint': 'login/',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'logout',
        'endpoint': 'logout/',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'task_form_action',
        'endpoint': 'task/submit/',
        'method': 'POST',
        'args': ['task_id']
    },
    {
        'name': 'json_task_form_action',
        'endpoint': 'task/submit_ajax/',
        'method': 'POST',
        'args': ['observation', 'task_id']
    },
    {
        'name': 'patient_form_action',
        'endpoint': 'patient/submit/',
        'method': 'POST',
        'args': ['patient_id']
    },
    {
        'name': 'json_patient_form_action',
        'endpoint': 'patient/submit_ajax/',
        'method': 'POST',
        'args': ['observation', 'patient_id']
    },
    {
        'name': 'calculate_obs_score',
        'endpoint': 'observation/score/',
        'method': 'POST',
        'args': ['observation']
    },
    {
        'name': 'json_take_task',
        'endpoint': 'tasks/take_ajax/',
        'method': 'POST',
        'args': ['task_id']
    },
    {
        'name': 'json_cancel_take_task',
        'endpoint': 'tasks/cancel_take_ajax/',
        'method': 'POST',
        'args': ['task_id']
    },
    {
        'name': 'json_partial_reasons',
        'endpoint': 'ews/partial_reasons/',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'confirm_clinical_notification',
        'endpoint': 'tasks/confirm_clinical/',
        'method': 'POST',
        'args': ['task_id']
    },
    {
        'name': 'cancel_clinical_notification',
        'endpoint': 'tasks/cancel_clinical/',
        'method': 'POST',
        'args': ['task_id']
    },
    {
        'name': 'json_colleagues_list',
        'endpoint': 'staff/colleagues/',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'share_patients',
        'endpoint': 'staff/assign/',
        'method': 'POST',
        'args': False
    },
    {
        'name': 'share_patient_list',
        'endpoint': 'patients/share/',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'ajax_task_cancellation_options',
        'endpoint': 'tasks/cancel_reasons/',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'confirm_review_frequency',
        'endpoint': 'tasks/confirm_review_frequency/',
        'method': 'POST',
        'args': ['task_id']
    },
    {
        'name': 'confirm_bed_placement',
        'endpoint': 'tasks/confirm_bed_placement/',
        'method': 'POST',
        'args': ['task_id']
    },
    {
        'name': 'ajax_get_patient_obs',
        'endpoint': 'patient/ajax_obs/',
        'method': 'GET',
        'args': ['patient_id']
    },
    {
        'name': 'patient_ob',
        'endpoint': 'patient/observation/',
        'method': 'GET',
        'args': ['observation', 'patient_id']
    },
    {
        'name': 'bristol_stools_chart',
        'endpoint': 'src/img/bristol_stools_chart.png',
        'method': 'GET',
        'args': False
    },
    {
        'name': 'json_patient_barcode',
        'endpoint': 'patient/barcode/',
        'method': 'GET',
        'args': ['hospital_number']
    }
]


def get_urls():
    r = {}
    for route in routes:
        r[route['name']] = URL_PREFIX+route['endpoint']
    return r



URLS = get_urls()