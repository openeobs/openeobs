# Part of Open eObs. See LICENSE file for full copyright and licensing details.
import os
from . import test_helpers
from . import test_observation_report_data_dict
from . import test_workload
if not os.environ.get('TRAVIS'):
    # Due to the inability to install nh_eobs_demo before Travis tests this
    # test can only be run locally - TODO: Fix this!
    from . import test_staff_allocation_integration
    from . import test_staff_allocation_multi_ward
# from . import test_api
# from . import test_api_demo
# from . import test_observation_report
# from . import test_observation_report_create_filter
# from . import test_observation_report_structure
# from . import test_observation_table_structure
# from . import test_wardboard
# from . import test_ward_dashboard
# from . import test_palliative_status_tour
# from . import test_staff_allocation_tours
# from . import test_stand_in_api
