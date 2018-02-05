import datetime

import babel.dates
import dateutil.relativedelta
import pytz
from openerp.models import BaseModel


def read_group_process_groupby_override(self, gb, query, context):
    """
    Override of `openerp.BaseModel_read_group_process_groupby_override`.
    """
    split = gb.split(':')
    field_type = self._fields[split[0]].type
    gb_function = split[1] if len(split) == 2 else None
    temporal = field_type in ('date', 'datetime')
    tz_convert = field_type == 'datetime' and \
        context.get('tz') in pytz.all_timezones
    alias = self._table
    qualified_field = self._inherits_join_calc(alias, split[0], query)
    if temporal:
        display_formats = {
            # Careful with week/year formats:
            #  - yyyy (lower) must always be used,
            #         *except* for week+year formats
            #  - YYYY (upper) must always be used for week+year format
            #         e.g. 2006-01-01 is W52 2005 in some locales (de_DE),
            #                         and W1 2006 for others
            #
            # Mixing both formats, e.g. 'MMM YYYY' would yield wrong results,
            # such as 2006-01-01 being formatted as "January 2005"
            # in some locales.
            # Cfr: http://babel.pocoo.org/docs/dates/#date-fields
            'hour': 'HH:00 dd MMM yyyy',
            'day': 'dd MMM yyyy',  # yyyy = normal year
            'week': "'W'w YYYY",  # w YYYY = ISO week-year
            'month': 'MMMM yyyy',
            'quarter': 'QQQ yyyy',
            'year': 'yyyy',
        }
        time_intervals = {
            'hour': dateutil.relativedelta.relativedelta(hours=1),
            'day': dateutil.relativedelta.relativedelta(days=1),
            'week': datetime.timedelta(days=7),
            'month': dateutil.relativedelta.relativedelta(months=1),
            'quarter': dateutil.relativedelta.relativedelta(months=3),
            'year': dateutil.relativedelta.relativedelta(years=1)
        }
        if tz_convert:
            qualified_field = "timezone('%s', timezone('UTC',%s))" % \
                              (context.get('tz', 'UTC'), qualified_field)
        qualified_field = "date_trunc('%s', %s)" % (gb_function or 'month',
                                                    qualified_field)
    if field_type == 'boolean':
        qualified_field = "coalesce(%s,false)" % qualified_field
    return {
        'field': split[0],
        'groupby': gb,
        'type': field_type,
        'display_format': display_formats[gb_function or 'month'] if temporal
        else None,
        'interval': time_intervals[gb_function or 'month'] if temporal
        else None,
        'tz_convert': tz_convert,
        'qualified_field': qualified_field
    }


def read_group_format_result_override(self, data, annotated_groupbys, groupby,
                                      groupby_dict, domain, context):
    """
        Helper method to format the data contained in the dictionary data by
        adding the domain corresponding to its values, the groupbys in the
        context and by properly formatting the date/datetime values.
    """
    domain_group = [dom for gb in annotated_groupbys
                    for dom in self._read_group_get_domain(gb,
                                                           data[gb['groupby']])
                    ]
    for k, v in data.iteritems():
        gb = groupby_dict.get(k)
        if gb and gb['type'] in ('date', 'datetime') and v:
            data[k] = babel.dates.format_datetime(
                v, format=gb['display_format'],
                locale=context.get('lang', 'en_US'))

    data['__domain'] = domain_group + domain
    if len(groupby) - len(annotated_groupbys) >= 1:
        data['__context'] = {'group_by': groupby[len(annotated_groupbys):]}
    del data['id']
    return data


BaseModel._read_group_process_groupby = read_group_process_groupby_override
BaseModel._read_group_format_result = read_group_format_result_override
