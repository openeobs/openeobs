# Part of Open eObs. See LICENSE file for full copyright and licensing details.

# Misc Tests
from . import test_helpers
from . import test_workload

# Test Observation Reports
from openeobs.nh_eobs.tests.observation_report import \
    test_get_allowed_activity_states_for_model
from openeobs.nh_eobs.tests.observation_report import \
    test_create_search_filter
from openeobs.nh_eobs.tests.observation_report import test_data_dict_to_obj
from openeobs.nh_eobs.tests.observation_report import \
    test_report_get_triggered_actions
from openeobs.nh_eobs.tests.observation_report import \
    test_report_start_and_end_date
from openeobs.nh_eobs.tests.observation_report import test_report_structure
from openeobs.nh_eobs.tests.observation_report import test_report_without_dob
from openeobs.nh_eobs.tests.observation_report import test_table_structure
from openeobs.nh_eobs.tests.observation_report import \
    test_get_patient_monitoring_exception_report_data
from openeobs.nh_eobs.tests.observation_report import test_get_ews_observations

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
