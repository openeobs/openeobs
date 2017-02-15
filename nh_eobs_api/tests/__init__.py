# Part of Open eObs. See LICENSE file for full copyright and licensing details.
import os
from . import test_get_next_action
if not os.environ.get('TRAVIS'):
    from . import test_routing
    from . import test_controller_api
