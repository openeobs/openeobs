# Part of Open eObs. See LICENSE file for full copyright and licensing details.

from . import test_helpers
from . import test_workload
from .observation_report import *
from .nh_clinical_observation_report_wizard import *

# Test Settings
from . import test_api_get_activities_settings
from . import test_eobs_settings
from openeobs.nh_eobs.tests.wardboard import \
    test_wardboard_discharge_transfer_settings
from . import test_workload_bucket_settings

# Test SQL statements
from . import test_sql_statements

# Disabled tests
# from . import test_api
# from . import test_api_demo
# from openeobs.nh_eobs.tests.wardboard import test_wardboard
# from . import test_ward_dashboard
# from . import test_palliative_status_tour
# from . import test_staff_allocation_tours
# from . import test_stand_in_api
