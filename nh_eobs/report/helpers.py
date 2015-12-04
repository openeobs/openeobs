# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from openerp.osv import fields
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

class DataObj(object):
    def __init__(self, spell_id=None, start_time=None, end_time=None,
                 ews_only=None):
        self.spell_id = spell_id
        self.start_time = start_time
        self.end_time = end_time
        self.ews_only = ews_only

def create_search_filter(spell_activity_id, model, start_date, end_date):
    if not spell_activity_id:
        raise ValueError('No spell activity id supplied')
    if not model:
        raise ValueError('No model supplied')
    filter = []
    if model in ['nh.clinical.patient.o2target',
                 'nh.clinical.patient.move']:
        filter = [['parent_id', '=', spell_activity_id],
                  ['data_model', '=', model]]
    else:
        filter = [['parent_id', '=', spell_activity_id],
                  ['data_model', '=', model], ['state', '=', 'completed']]
    if start_date:
        filter.append(['date_started', '>=', start_date.strftime(dtf)])
    if end_date:
        filter.append(['date_terminated', '<=', end_date.strftime(dtf)])
    return filter

def convert_db_date_to_context_date(cr, uid, date_string, format,
                                    context=None):
    if format:
        return fields.datetime.context_timestamp(
            cr, uid, date_string,context=context).strftime(format)
    else:
        return fields.datetime.context_timestamp(
            cr, uid, date_string, context=context)

def data_dict_to_obj(data_dict):
    spell_id = data_dict['spell_id'] if 'spell_id' in data_dict and data_dict['spell_id'] else None
    start = data_dict['start_time'] if 'start_time' in data_dict and data_dict['start_time'] else None
    end = data_dict['end_time'] if 'end_time' in data_dict and data_dict['end_time'] else None
    ews_only = data_dict['ews_only'] if 'ews_only' in data_dict and data_dict['ews_only'] else None
    return DataObj(spell_id, start, end, ews_only)