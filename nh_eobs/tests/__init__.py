# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from . import test_api_get_activities_settings
from . import test_eobs_settings
from . import test_helpers
from . import test_sql_statements
from . import test_workload
from .nh_clinical_frequencies_ews import *
from .nh_clinical_observation_report_wizard import *
from .nh_clinical_patient_monitoring_exception import *
from .nh_clinical_patient_observation_ews import *
from .nh_clinical_wardboard import *
from .nh_eobs_api import *
from .nh_eobs_ward_dashboard import *
from .report_nh_clinical_observation_report import *
from .nh_clinical_patient_placement import *
from .ir_ui_menu import *
from .nh_clinical_adt_spell_update import *
from .nh_clinical_patient_admission import *
from .nh_clinical_patient_discharge import *
from .nh_clinical_patient_transfer import *

# Disabled tests
from . import test_api_demo
# from openeobs.nh_eobs.tests.wardboard import test_wardboard
from . import test_palliative_status_tour
from . import test_staff_allocation_tours
from . import test_stand_in_api

# uncommented tests above, added the following ones
from . import test_get_last_full_obs_activity, \
    test_patient_refusal_after_transfer, test_workload_bucket_settings

