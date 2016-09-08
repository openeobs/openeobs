from . import test_eobs_settings
from . import test_eobs_settings_manually_set
from . import test_spell_obs_stop_property
from . import test_nh_clinical_wardboard_escalation_tasks
from . import test_nh_clinical_wardboard_toggle_obs_stop
from . import test_nh_clinical_wardboard_toggle_obs_stop_flag
from . import test_nh_eobs_api_get_active_observations
from . import test_nh_eobs_api_transfer
from . import test_nh_clinical_wardboard_prompt_user_for_obs_stop_reason
# These unit tests were never working because of some strange behaviour with
# the wizard class. It has a many2one field to reasons even though the
# relationship is actually a many2one. The aim was to get a drop down menu of
# all reason records and previous examples were copied that used many2one
# despite that relationship being semantically incorrect.
#
# When creating a new wizard class the reasons field is False and cannot be set
# to multiple reasons using `reasons = [(6, 0, [list_of_ids])]`.
# from . import test_nh_clinical_patient_monitoring_exception_select_reason
