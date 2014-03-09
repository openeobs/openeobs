
from datetime import datetime
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _


class assign_bed_and_obs_frequency_wizard_view(osv.TransientModel):

    def _get_location_ids(self, employee):
        return True

    def _get_assign_bed_tasks(self, cr, uid, context=None):
        task_pool = self.pool.get('t4.clinical.task')
        placement_pool = self.pool.get('t4.clinical.patient.placement')
        wizard_pool = self.pool.get('t4skr.assign.bed.and.obs.frequency.wizard')
        employee_pool = self.pool.get('hr.employee')

        employee_id = employee_pool.search(cr, uid, [('user_id', '=', uid)], context=context)
        employee_list = employee_pool.browse(cr, uid, employee_id, context=context)
        if len(employee_list) != 1:
            raise osv.except_osv(_('Error'), 'More than one Employee with user_id:%s' % uid)
        employee = employee_list[0]

        placement_task_ids = task_pool.search(cr, uid, [('data_model', '=', placement_pool._name)], context=context)
        wizard_ids = []

        for task_id in placement_task_ids:
            task = task_pool.browse(cr, uid, task_id, context=context)



            if task.visit_id.pos_location in employee.pos_location_ids:
                vals = {
                        'task_id': task.id,
                        'visit_id': task.visit_id.id,
                        'patient_name': task.visit_id.patient_id.name,
                        'hospital_number': task.visit_id.patient_id.other_identifier,
                        'ward_id': task.visit_id.pos_location.id,
                }
                wizard_ids.append(wizard_ob.create(cr, uid, vals, context=context))
        return wizard_ids

    def _get_last_finished(self, cr, uid, context=None):
        # pos_location_ob = self.pool.get('t4clinical.pos.delivery')
        # task_ob = self.pool.get('t4clinical.task.base')
        # task_type_ob = self.pool.get('t4clinical.task.type')
        # wizard_ob = self.pool.get('t4skr.assign.bed.and.obs.frequency.wizard')
        # employee_ob = self.pool.get('hr.employee')
        #
        # employee_id = employee_ob.search(cr, uid, [('user_id', '=', uid)], context=context)
        # employee_list = employee_ob.browse(cr, uid, employee_id, context=context)
        # if len(employee_list) != 1:
        #     raise osv.except_osv(_('Error'), 'More than one Employee with user_id:%s' % uid)
        # employee = employee_list[0]
        #
        # assign_bed_id = task_type_ob.search(cr, uid, [('name', '=', 'AssignBed')], context=context)
        # task_ids = task_ob.search(cr, uid, [('task_type_id', '=', assign_bed_id[0]),
        #                                     ('state', '=', 'done')], order='date_end', context=context)
        # wizard_ids = []
        #
        # for task_id in reversed(task_ids[-3:]):
        #     task = task_ob.browse(cr, uid, task_id, context=context)
        #     plids = [e.id for e in employee.pos_location_ids]
        #     if plids:
        #         location_ids = pos_location_ob.search(cr, uid, [('id', 'child_of', plids)])
        #     else:
        #         location_ids = []
        #     if task.visit_id.pos_location.id in location_ids:
        #         vals = {
        #                 'task_id': task.id,
        #                 'visit_id': task.visit_id.id,
        #                 'patient_name': task.visit_id.patient_id.name,
        #                 'hospital_number': task.visit_id.patient_id.other_identifier,
        #                 'ward_id': task.visit_id.pos_location.parent_id.id,
        #                 'bed_id': task.visit_id.pos_location.id,
        #                 'date': task.date_end,
        #         }
        #         wizard_ids.append(wizard_ob.create(cr, uid, vals, context=context))
        #
        wizard_ids = {}
        return wizard_ids

    def _get_name(self, cr, uid, ids, fn, args, context=None):
        result = dict.fromkeys(ids, False)
        for wv in self.browse(cr, uid, ids, context=context):
            result[wv.id] = 'Admit Patients'
        return result

    _name = "t4skr.assign.bed.and.obs.frequency.wizard.view"
    _columns = {
        'name': fields.function(_get_name, 'Name'),
        'wizards': fields.one2many('t4skr.assign.bed.and.obs.frequency.wizard', 'wizard_view_id', 'Patients Without Bed'),
        'last': fields.one2many('t4skr.assign.bed.and.obs.frequency.wizard', 'last_view_id', 'Last Assigned Patients')
    }
    _defaults = {
        'wizards': lambda s, cr, uid, c: s._get_assign_bed_tasks(cr, uid, context=c),
        'last': lambda s, cr, uid, c: s._get_last_finished(cr, uid, context=c),
    }

    def applyChanges(self, cr, uid, ids, context=None):

        view = {
            'type': 'ir.actions.act_window',
            'res_model': 't4skr.assign.bed.and.obs.frequency.wizard.view',
            'view_mode': 'form',
            'view_type': 'tree,form',
            'target': 'inline',
            'context': context,
            'res_id': ids[0]
        }
        return view

    def create(self, cr, user, vals, context=None):
        vals.update({
            'last': False
        })
        wiz_view_id = super(assign_bed_and_obs_frequency_wizard_view, self).create(cr, user, vals, context=context)
        context.update({
            'create_call': True
        })
        self.write(cr, user, wiz_view_id, vals, context=context)
        return wiz_view_id

    def write(self, cr, user, ids, vals, context=None):
        if context.get('create_call'):
            vals = {
                'last': [(6, False, self._get_last_finished(cr, user, context=context))]
            }
        else:
            vals.update({
                'last': [(6, False, self._get_last_finished(cr, user, context=context))]
            })
        return super(assign_bed_and_obs_frequency_wizard_view, self).write(cr, user, ids, vals, context=context)


class assign_bed_and_obs_frequency_wizard(osv.TransientModel):
    _name = "t4skr.assign.bed.and.obs.frequency.wizard"
    _columns = {
        'wizard_view_id': fields.many2one('t4skr.assign.bed.and.obs.frequency.wizard.view', 'Wizard View'),
        'last_view_id': fields.many2one('t4skr.assign.bed.and.obs.frequency.wizard.view', 'Last View'),
        'task_id': fields.many2one('t4.clinical.task', 'Source Task'),
        'spell_id': fields.many2one('t4.clinical.spell', 'Patient Visit'),
        'patient_name': fields.char('Patient Name', size=100),
        'hospital_number': fields.char('Patient Hospital Number', size=100),
        'ward_id': fields.many2one('t4.clinical.location', 'Ward', domain=[('usage', '=', 'ward')]),
        'bed_id': fields.many2one('t4.clinical.location', 'Bed', domain=[('usage', '=', 'bed'),
                                                                            ('occupants', '=', None)]),
        'news_frequency': fields.selection([('default', 'Default'),
                                           ('fifteen', '15 mins'),
                                           ('thirty', '30 mins'),
                                           ('hourly', '1 hourly'),
                                           ('fourhour', '4 hourly'),
                                           ('sixhour', '6 hourly'),
                                           ('twelvehour', '12 hourly')], 'NEWS Frequency'),
        'gcs_frequency': fields.selection([('default', 'Default'),
                                           ('fifteen', '15 mins'),
                                           ('thirty', '30 mins'),
                                           ('hourly', '1 hourly'),
                                           ('fourhour', '4 hourly'),
                                           ('sixhour', '6 hourly'),
                                           ('twelvehour', '12 hourly')], 'GCS Frequency'),
        'target_o2': fields.many2one('t4.clinical.o2saturation.level', 'Target O2 Saturation'),
        'date': fields.datetime('Assigned')
    }
    _defaults = {
        'news_frequency': 'default',
        'gcs_frequency': 'default',
        'target_o2': False
    }

    def write(self, cr, uid, ids, vals, context=None):

        if vals.get('bed_id'):

            data = self.read(cr, uid, ids[0], [], context=context)

            optional = {}
            if vals.get('news_frequency'):
                optional['news_frequency'] = vals.get('news_frequency')
            if vals.get('gcs_frequency'):
                optional['gcs_frequency'] = vals.get('gcs_frequency')
            if vals.get('target_o2'):
                optional['target_o2'] = vals.get('target_o2')

            self.pool.get('t4clinical.task.base').assignLocationFromTask(cr, uid, data.get('task_id')[0],
                                                                         vals.get('bed_id'), optional, context=context)
            return super(assign_bed_and_obs_frequency_wizard, self).unlink(cr, uid, ids, context=context)
        return super(assign_bed_and_obs_frequency_wizard, self).write(cr, uid, ids, vals, context=context)

