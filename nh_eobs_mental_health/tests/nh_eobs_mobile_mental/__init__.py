import os

from . import test_patient_list_obs_stop
from . import test_patient_list_rapid_tranq

if not os.environ.get('TRAVIS'):
    from . import test_rapid_tranq_route
from . import test_task_list_rapid_tranq
