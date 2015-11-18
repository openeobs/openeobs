import logging
from psycopg2 import ProgrammingError

_logger = logging.getLogger(__name__)


def migrate(cr, installed_version):
    if installed_version[-3:] == "0.1":
        tables = [
            ("nh_clinical_patient_mrsa", "mrsa"),
            ("nh_clinical_patient_diabetes", "diabetes"),
            ("nh_clinical_patient_weight_monitoring", "weight_monitoring")
        ]
        for t in tables:
            try:
                query = "ALTER TABLE %s RENAME COLUMN %s TO status" % (t[0], t[1])
                cr.execute(query)
            except ProgrammingError as e:
                cr.rollback()
                _logger.info("Migration already made: " + str(e))
                pass



