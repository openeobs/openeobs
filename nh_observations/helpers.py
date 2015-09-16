__author__ = 'Will'
import logging
from functools import wraps

_logger = logging.getLogger(__name__)


def refresh_materialized_views(*views):
    """
    Decorator method to refresh materialized views passed
    as arguments.
    :param views: name(s) of materialized view(s) to refresh
    :return: True if activity is completed
    """
    def _refresh_materialized_views(f):
        @wraps(f)
        def _complete(*args, **kwargs):
            self, cr, uid = args[:3]
            result = f(*args, **kwargs)
            sql = ''
            for view in views:
                sql += 'refresh materialized view ' + view + ';\n'
            cr.execute(sql)
            _logger.debug('Materialized view(s) refreshed')
            return result
        return _complete
    return _refresh_materialized_views