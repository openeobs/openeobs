# coding=utf-8

# Misc Tests
from . import test_api
from . import test_wardboard_print_report_permissions

# Test Staff Allocation / Reallocation
from . import test_staff_allocation_integration
from . import test_staff_allocation_multi_ward
from . import test_staff_reallocation_integration
from . import test_staff_reallocation_multi_ward

# Test Settings
from . import test_api_get_activities_settings_integration
from . import test_wardboard_discharge_transfer_settings_integration
from . import test_workload_bucket_settings_integration

# Test Patient Name - EOBS-195
from . import test_workload_patient_name_get
from . import test_placement_patient_name_get

# Disabled tests
# from . import test_demo
