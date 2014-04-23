from openerp.tests import common
import requests

ACTIVITIES_URLS = [
    {
        'path': '/api/activities/',
        'method': 'GET',
        'result': {
            'params': [None, None],
            'method': 'GET'
        }
    },
    {
        'path': '/api/activities/1/',
        'method': 'GET',
        'result': {
            'params': ['1', None],
            'method': 'GET'
        }
    },
    {
        'path': '/api/activities/1/assign/',
        'method': 'POST',
        'result': {
            'params': ['1', 'assign'],
            'method': 'POST'
        }
    },
    {
        'path': '/api/activities/1/assign/',
        'method': 'DELETE',
        'result': {
            'params': ['1', 'assign'],
            'method': 'DELETE'
        }
    },
    {
        'path': '/api/activities/1/complete/',
        'method': 'POST',
        'result': {
            'params': ['1', 'complete'],
            'method': 'POST'
        }
    },
    {
        'path': '/api/activities/1/',
        'method': 'DELETE',
        'result': {
            'params': ['1', None],
            'method': 'DELETE'
        }
    },
    {
        'path': '/api/activities/1/',
        'method': 'POST',
        'result': {
            'params': ['1', None],
            'method': 'POST'
        }
    },
]

PATIENTS_URLS = [
    {
        'path': '/api/patients/',
        'method': 'GET',
        'result': {
            'params': [None, None, None, None],
            'method': 'GET'
        }
    },
    {
        'path': '/api/patients/1/',
        'method': 'GET',
        'result': {
            'params': ['1', None, None, None],
            'method': 'GET'
        }
    },
    {
        'path': '/api/patients/',
        'method': 'POST',
        'result': {
            'params': [None, None, None, None],
            'method': 'POST'
        }
    },
    {
        'path': '/api/patients/1/',
        'method': 'PUT',
        'result': {
            'params': ['1', None, None, None],
            'method': 'PUT'
        }
    },
    {
        'path': '/api/patients/1/admit/',
        'method': 'POST',
        'result': {
            'params': ['1', 'admit', None, None],
            'method': 'POST'
        }
    },
    {
        'path': '/api/patients/1/admit/',
        'method': 'DELETE',
        'result': {
            'params': ['1', 'admit', None, None],
            'method': 'DELETE'
        }
    },
    {
        'path': '/api/patients/1/merge/2/',
        'method': 'PUT',
        'result': {
            'params': ['1', 'merge', '2', None],
            'method': 'PUT'
        }
    },
    {
        'path': '/api/patients/1/transfer/1/',
        'method': 'PUT',
        'result': {
            'params': ['1', 'transfer', '1', None],
            'method': 'PUT'
        }
    },
    {
        'path': '/api/patients/1/activities/',
        'method': 'GET',
        'result': {
            'params': ['1', 'activities', None, None],
            'method': 'GET'
        }
    },
    {
        'path': '/api/patients/1/activities/ews',
        'method': 'GET',
        'result': {
            'params': ['1', 'activities', 'ews', None],
            'method': 'GET'
        }
    },
    {
        'path': '/api/patients/1/activities/ews',
        'method': 'POST',
        'result': {
            'params': ['1', 'activities', 'ews', None],
            'method': 'POST'
        }
    },
    {
        'path': '/api/patients/1/activities/ews/view',
        'method': 'GET',
        'result': {
            'params': ['1', 'activities', 'ews', 'view'],
            'method': 'GET'
        }
    },
    {
        'path': '/api/patients/1/activities/ews/frequency',
        'method': 'GET',
        'result': {
            'params': ['1', 'activities', 'ews', 'frequency'],
            'method': 'GET'
        }
    },
    {
        'path': '/api/patients/1/activities/ews/frequency',
        'method': 'POST',
        'result': {
            'params': ['1', 'activities', 'ews', 'frequency'],
            'method': 'POST'
        }
    },
]


class TestUrls(common.SingleTransactionCase):

    def setUp(self):
        global host
        host = 'http://localhost:8069'
        super(TestUrls, self).setUp()

    def test_activities_urls(self):
        global host
        for u in ACTIVITIES_URLS:
            if u['method'] == 'GET':
                r = requests.get(host+u['path'])
            elif u['method'] == 'POST':
                r = requests.post(host+u['path'])
            elif u['method'] == 'PUT':
                r = requests.put(host+u['path'])
            elif u['method'] == 'DELETE':
                r = requests.delete(host+u['path'])
            print 'TEST - testing activities urls'
            print r.json()
            print u['result']
            self.assertTrue(r.json() == u['result'], msg='your url does not work')

    def test_patients_urls(self):
        global host
        for u in PATIENTS_URLS:
            if u['method'] == 'GET':
                r = requests.get(host+u['path'])
            elif u['method'] == 'POST':
                r = requests.post(host+u['path'])
            elif u['method'] == 'PUT':
                r = requests.put(host+u['path'])
            elif u['method'] == 'DELETE':
                r = requests.delete(host+u['path'])
            print 'TEST - testing patients urls'
            print r.json()
            print u['result']
            self.assertTrue(r.json() == u['result'], msg='your url does not work')