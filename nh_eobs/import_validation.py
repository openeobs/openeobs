from openerp.osv import orm
import logging
import psycopg2

_logger = logging.getLogger(__name__)


class ir_import_extension(orm.TransientModel):
    _name = 'base_import.import'
    _inherit = 'base_import.import'

    def format_patient_data(self, data, fields):
        for index, field in enumerate(fields):
            if field in ['other_identifier', 'patient_identifier']:
                for d in data:
                    d[index].replace(" ", "")

    def do(self, cr, uid, id, fields, options, dryrun=False, context=None):
        cr.execute('SAVEPOINT import')

        (record,) = self.browse(cr, uid, [id], context=context)
        try:
            data, import_fields = self._convert_import_data(
                record, fields, options, context=context)
        except ValueError, e:
            return [{
                'type': 'error',
                'message': unicode(e),
                'record': False,
            }]

        if record.res_model == 'nh.clinical.patient':
            self.format_patient_data(data, import_fields)
        _logger.info('importing %d rows...', len(data))
        import_result = self.pool[record.res_model].load(
            cr, uid, import_fields, data, context=context)
        _logger.info('done')

        try:
            if dryrun:
                cr.execute('ROLLBACK TO SAVEPOINT import')
            else:
                cr.execute('RELEASE SAVEPOINT import')
        except psycopg2.InternalError:
            pass

        return import_result['messages']
