from . import test_nh_clinical_patient_monitoring_exception
from . import test_patient_refusal_after_patient_monitoring_exception

# These unit tests were never working because of some strange behaviour with
# the wizard class. It has a many2one field to reasons even though the
# relationship is actually a many2one. The aim was to get a drop down menu of
# all reason records and previous examples were copied that used many2one
# despite that relationship being semantically incorrect.
#
# When creating a new wizard class the reasons field is False and cannot be set
# to multiple reasons using `reasons = [(6, 0, [list_of_ids])]`.
# from . import test_select_reason
