# CAME FROM observation_extension.py.

# class nh_clinical_patient_weight_monitoring(orm.Model):
#     _inherit = 'nh.clinical.patient.weight_monitoring'
#
#     @refresh_materialized_views('weight')
#     def complete(self, cr, uid, activity_id, context=None):
#         return super(
#             nh_clinical_patient_weight_monitoring, self).complete(
#             cr, uid, activity_id, context)

# CAME FROM wardboard.py overriden _columns attribute.

# 'weight_monitoring': fields.selection(
#            _boolean_selection, "Weight Monitoring"),

# 'weight_monitoring_ids': fields.function(
#         _get_data_ids_multi, multi='weight_monitoring_ids',
#         type='many2many', relation='nh.clinical.patient.weight_monitoring',
#         string='Weight Monitoring'),

# CAME FROM wardboard.py overriden write method.

# if 'weight_monitoring' in vals:
#                 wm_pool = self.pool['nh.clinical.patient.weight_monitoring']
#                 wm_id = wm_pool.create_activity(cr, SUPERUSER_ID, {
#                     'parent_id': wb.spell_activity_id.id,
#                 }, {
#                     'patient_id': wb.spell_activity_id.patient_id.id,
#                     'status': vals['weight_monitoring'] == 'yes'
#                 }, context=context)
#                 activity_pool.complete(cr, uid, wm_id, context=context)

# CAME FROM wardboard.py overridden init method's SQL statement.
# Weight may not need a materialised view.

# drop materialized view if exists weight cascade;
#
# create materialized view
# weight as(
#     select
#         activity.spell_id,
#         weight.status
#     from wb_activity_latest activity
#     left join nh_clinical_patient_weight_monitoring weight
#         on activity.ids && array[weight.activity_id]
#     where activity.state = 'completed'
# );

# CAME FROM the 'Monitoring' section of wardboard_view.xml

# <group string="Weight">
#     <field name="weight_monitoring" string="Active"/>
#     <field name="weight_monitoring_ids" colspan="2" readonly="True" nolabel="1">
#         <tree>
#             <field name="date_terminated" string="Date" widget="nhc_datetime"/>
#             <field name="value" string="Value"/>
#             <field name="terminate_uid"/>
#         </tree>
#     </field>
# </group>
