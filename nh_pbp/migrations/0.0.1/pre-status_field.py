import logging

_logger = logging.getLogger(__name__)


def migrate(cr, installed_version):
    if installed_version[-3:] == '0.1':
        cr.execute(
            'ALTER TABLE nh_clinical_patient_pbp_monitoring RENAME COLUMN pbp_monitoring TO status'
        )
        _logger.debug("Version upgraded to 0.1.1 (from 0.1)")