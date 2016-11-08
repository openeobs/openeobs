# Part of Open eObs. See LICENSE file for full copyright and licensing details.
"""
Defines the `policy` for :mod:`operations<operations>` and
:mod:`ADT<adt>`.

See :meth:`trigger_policy()<activity.nh_activity_data.trigger_policy>`
for how policies are executed.
"""
from openerp.osv import orm


class nh_clinical_patient_placement(orm.Model):
    """
    Extends :class:`placement<operations.nh_clinical_patient_placement>`
    to update ``_POLICY``.

    When a :class:`patient<base.nh_clinical_patient>` is placed in a bed
    :class:`location<base.nh_clinical_location>` then a recurring
    :class:`EWS<ews.nh_clinical_patient_observation_ews>` will be
    `scheduled`. All existing EWS will be cancelled.
    """

    _name = 'nh.clinical.patient.placement'
    _inherit = 'nh.clinical.patient.placement'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.observation.ews',
                               'type': 'recurring',
                               'cancel_others': True,
                               'context': 'eobs'}]}


class nh_clinical_patient_admission(orm.Model):
    """
    Extends :class:`admission<operations.nh_clinical_patient_admission>`
    to update ``_POLICY``.

    When a :class:`patient<base.nh_clinical_patient>` is admitted into
    hospital then a
    :class:`placement<operations.nh_clinical_patient_placement>` is
    `scheduled`. All other placements will be `cancelled`.
    """

    _name = 'nh.clinical.patient.admission'
    _inherit = 'nh.clinical.patient.admission'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement',
                               'type': 'schedule',
                               'cancel_others': True,
                               'context': 'eobs',
                               'create_data': {
                                   'suggested_location_id':
                                       'activity.data_ref.location_id.id'
                               }}]}


class nh_clinical_patient_transfer(orm.Model):
    """
    Extends :class:`transfer<operations.nh_clinical_patient_transfer>`
    to update ``_POLICY``.

    When a :class:`patient<base.nh_clinical_patient>` is transferred
    into the hospital then a
    :class:`placement<operations.nh_clinical_patient_placement>` is
    `scheduled`. All other placements will be `cancelled`.
    """

    _name = 'nh.clinical.patient.transfer'
    _inherit = 'nh.clinical.patient.transfer'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement',
                               'type': 'schedule',
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id':
                                       'activity.data_ref.location_id.id'
                               },
                               'case': 1
                               },
                              {'model': 'nh.clinical.patient.placement',
                               'type': 'schedule',
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id':
                                       "location_pool.get_closest_parent_id("
                                       "cr, uid, "
                                       "activity.data_ref.origin_loc_id.id, "
                                       "'ward', "
                                       "context=context) if "
                                       "activity.data_ref.origin_loc_id."
                                       "usage != 'ward' else "
                                       "activity.data_ref.origin_loc_id.id"
                               }, 'case': 2}
                              ]
               }


class nh_clinical_adt_spell_update(orm.Model):
    """
    Extends
    :class:`spell update<adt.nh_clinical_adt_spell_update>` to
    update ``_POLICY``.

    When `completed` a
    :class:`placement<operations.nh_clinical_patient_placement>` is
    `scheduled`. All other placements will be `cancelled`.
    """

    _name = 'nh.clinical.adt.spell.update'
    _inherit = 'nh.clinical.adt.spell.update'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement',
                               'type': 'schedule',
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id':
                                       'activity.data_ref.location_id.id'
                               }
                               }]}


class nh_clinical_patient_discharge(orm.Model):
    """
    Extends
    :class:`discharge<operations.nh_clinical_patient_discharge>` to
    update ``_POLICY``.

    When `cancelled` a new
    :class:`placement<operations.nh_clinical_patient_placement>` is
    `scheduled`. All other placements will be `cancelled`.
    """

    _name = 'nh.clinical.patient.discharge'
    _inherit = 'nh.clinical.patient.discharge'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement',
                               'type': 'schedule',
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id':
                                       "location_pool.get_closest_parent_id("
                                       "cr, uid, "
                                       "activity.data_ref.location_id.id, "
                                       "'ward', context=context) if "
                                       "activity.data_ref.location_id.usage "
                                       "!= 'ward' else "
                                       "activity.data_ref.location_id.id"
                               }
                               }]}
