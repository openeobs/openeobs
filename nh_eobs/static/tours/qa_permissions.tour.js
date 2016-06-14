/**
 * User Permissions
 * Automated QA tours
 * Created by Jon on 12/01/16.
 */
'use strict';

/*global
    openerp, $
 */

(function () {
    var _t = openerp._t,
        admin = openerp.Tour.users.admin,
        hca = openerp.Tour.users.hca,
        nurse = openerp.Tour.users.nurse,
        doctor = openerp.Tour.users.doctor,
        wm = openerp.Tour.users.wm,
        capitalise = openerp.Tour.helpers.capitalise;
    openerp.Tour.register({
        id: 'admin_permissions',
        name: "Describe permissions when logged in as admin (" + admin + ")",
        path: '/web?debug=',
        user: admin,
        mode: 'test',
        steps: [
            {
                title:     "User logged in",
                waitFor:   ".oe_topbar_name:contains('" + capitalise(admin) + "')"
            },
            {
                title: "They can't can see the acuity board",
                waitNot: "span.oe_menu_text:contains('Acuity Board')"
            },
            {
                title: "They can't see the patient records",
                waitNot: "div.oe_kanban_card"
            },
            {
                title: "They can't manage devices",
                waitNot: "a.ui-tabs-anchor:contains('Devices')"
            },
            {
                title: "They can't manage patient movements",
                waitNot: "button.oe_form_button:contains('Move Patient')"
            },
            {
                title: "They can't see the patient waiting list",
                waitNot: "span.oe_menu_text:contains('Patients without bed')"
            },
            {
                title: "They can't see the last discharged patient list",
                waitNot: "span.oe_menu_text:contains('Recently Discharged')"
            },
            {
                title: "They can't see the last transferred patient list",
                waitNot: "span.oe_menu_text:contains('Recently Discharged')"
            },
            {
                title: "They can manage user accounts",
                element: "span.oe_menu_text:contains('Open eObs Users')"
            },
            {
                title: "They can manage Ward Manager accounts",
                waitFor: "tr:contains('Ward Manager')"
            },
            {
                title: "They can manage Doctor accounts",
                waitFor: "tr:contains('Doctor')"
            },
            {
                title: "They can manage Nurse accounts",
                waitFor: "tr:contains('Nurse')"
            },
            {
                title: "They can manage HCA accounts",
                waitFor: "tr:contains('HCA')"
            },
            {
                title: "They can select user accounts",
                element: "tr[data-id] input[type='checkbox']:eq(0)"
            },
            {
                title: "They can perform actions on accounts",
                element: "button.oe_dropdown_toggle:contains('More')"
            },
            {
                title: "They can export user accounts",
                waitFor: "ul.oe_dropdown_menu.oe_opened:contains('Export')"
            },
            {
                title: "They can change account passwords",
                waitFor: "ul.oe_dropdown_menu.oe_opened:contains('Change Password')"
            },
            {
                title: "They can't delete user accounts",
                waitNot: "ul.oe_dropdown_menu.oe_opened:contains('Delete')"
            },
            {
                title: "They can create new user accounts",
                waitFor: "button.oe_list_add:contains('Create')"
            },
            {
                title: "They can see the ward dashboard",
                element: "span.oe_menu_text:contains('Ward Dashboard')"
            },
            //{
            //    title: "They can see all ward record cards",
            //    waitFor: "div.oe_kanban_card:contains('Ward A')"
            //},
            //{
            //    title: "They can see all ward records cards",
            //    waitFor: "div.oe_kanban_card:contains('Ward B')"
            //},
            //{
            //    title: "They can see all ward records cards",
            //    element: "div.oe_kanban_card:contains('Ward C')"
            //},
            //{
            //    title: "They can view the ward record beds tab",
            //    element: "a.ui-tabs-anchor:contains('Beds')"
            //},
            //{
            //    title: "They can view the ward record Patients Waiting tab",
            //    element: "a.ui-tabs-anchor:contains('Patients Waiting')"
            //},
            {
                title: "They can't manage the nursing and doctor shifts",
                waitNot: "div.oe_secondary_menu_section:contains('Shift Management')"
            },
            {
                title: "They can manage location data",
                waitFor: "span.oe_menu_text:contains('Locations')"
            }
        ]
    });

    openerp.Tour.register({
        id: 'hca_permissions',
        name: "Describe permissions when logged in as HCA (" + hca + ")",
        path: '/web?debug=',
        user: hca,
        mode: 'test',
        steps: [
            {
                title:     _t("User logged in"),
                element:   ".oe_topbar_name:contains('" + capitalise(hca) + "')"
            },
            {
                title: _t("They can see the acuity board"),
                waitFor: "span.oe_menu_text:contains('Acuity Board')"
            },
            {
                title: _t("They can see the patients they are responsible for"),
                waitFor: "div.oe_kanban_card:eq(0)"
            },
            //{
            //    title: _t("They can't see patients they aren't responsible for"),
            //    waitNot: "div.oe_kanban_card:contains('Doe, James Xen')"
            //},
            //{
            //    title: _t("They can see the patients they are responsible for"),
            //    element: "div.oe_kanban_card:contains('Doe, Jenni April')"
            //},
            {
                title: _t("They can manage devices"),
                element: "a.ui-tabs-anchor:contains('Devices')"
            },
            {
                title: _t("They can start device sessions"),
                waitFor: "button:contains('Start Device Session')"
            },
            {
                title: _t("They can stop device sessions"),
                waitFor: "td[title='Complete Device Session']"
            },
            {
                title: _t("They can't edit the patient information"),
                waitNot: "button.oe_form_button_edit"
            },
            {
                title: _t("They can't manage patient movements"),
                waitFor: "button.oe_form_button.oe_form_invisible:contains('Move Patient')"
            },
            {
                title: _t("They can't see the patient waiting list"),
                waitNot: "span.oe_menu_text:contains('Patients without bed')"
            },
            {
                title: _t("They can't see the last discharged patient list"),
                waitNot: "span.oe_menu_text:contains('Recently Discharged')"
            },
            {
                title: _t("They can't see the last transferred patient list"),
                waitNot: "span.oe_menu_text:contains('Recently Transferred')"
            },
            {
                title: _t("They can't manage user accounts"),
                waitNot: "span.oe_menu_text:contains('Account Administration')"
            },
            {
                title: _t("They can't see the ward dashboard"),
                waitNot: "span.oe_menu_text:contains('Ward Dashboard')"
            },
            {
                title: _t("They can't manage the nursing and doctor shifts"),
                waitNot: "div.oe_secondary_menu_section:contains('Shift Management')"
            },
            {
                title: _t("They can't manage location data"),
                waitNot: "span.oe_menu_text:contains('NH Clinical')"
            }
        ]
    });

    openerp.Tour.register({
        id: 'nurse_permissions',
        name: "Describe permissions when logged in as a nurse (" + nurse +")",
        path: '/web?debug=',
        mode: 'test',
        steps: [
            {
                title:     _t("User logged in"),
                element:   ".oe_topbar_name:contains('" + capitalise(nurse) + "')"
            },
            {
                title: _t("They can see the acuity board"),
                waitFor: "span.oe_menu_text:contains('Acuity Board')"
            },
            //{
            //    title: _t("They can see the patients they are responsible for"),
            //    waitFor: "div.oe_kanban_card:contains('Doe, John Robert')"
            //},
            //{
            //    title: _t("They can't see patients they aren't responsible for"),
            //    waitNot: "div.oe_kanban_card:contains('Doe, James Xen')"
            //},
            {
                title: _t("They can see view patient records"),
                element: "div.oe_kanban_card:eq(0)"
            },
            {
                title: _t("They can manage devices"),
                element: "a.ui-tabs-anchor:contains('Devices')"
            },
            {
                title: _t("They can start device sessions"),
                waitFor: "button:contains('Start Device Session')"
            },
            {
                title: _t("They can stop device sessions"),
                waitFor: "td[title='Complete Device Session']"
            },
            {
                title: _t("They can edit some patient information"),
                element: "button.oe_form_button_edit"
            },
            {
                title: _t("They can edit 'Other Obs' info"),
                // Needed to ensure edit mode has been enabled
                waitFor: "select[name='mrsa']",
                element: "a.ui-tabs-anchor:contains('Other Obs')"
            },
            {
                title: _t("They can change MRSA status"),
                waitFor: "select[name='mrsa']"
            },
            {
                title: _t("They can change Diabetes status"),
                waitFor: "select[name='diabetes']"
            },
            {
                title: _t("They can edit 'Monitoring' information"),
                element: "a.ui-tabs-anchor:contains('Monitoring')"
            },
            {
                title: _t("They can change the Palliative Care status"),
                waitFor: "select[name='palliative_care']"
            },
            {
                title: _t("They can't manage patient movements"),
                waitFor: "button.oe_form_button.oe_form_invisible:contains('Move Patient')"
            },
            {
                title: _t("They can't see the patient waiting list"),
                waitNot: "span.oe_menu_text:contains('Patients without bed')"
            },
            {
                title: _t("They can't see the last discharged patient list"),
                waitNot: "span.oe_menu_text:contains('Recently Discharged')"
            },
            {
                title: _t("They can't see the last transferred patient list"),
                waitNot: "span.oe_menu_text:contains('Recently Transferred')"
            },
            {
                title: _t("They can't manage user accounts"),
                waitNot: "span.oe_menu_text:contains('Account Administration')"
            },
            {
                title: _t("They can't see the ward dashboard"),
                waitNot: "span.oe_menu_text:contains('Ward Dashboard')"
            },
            {
                title: _t("They can't manage the nursing and doctor shifts"),
                waitNot: "div.oe_secondary_menu_section:contains('Shift Management')"
            },
            {
                title: _t("They can't manage location data"),
                waitNot: "span.oe_menu_text:contains('NH Clinical')"
            }
        ]
    });

    openerp.Tour.register({
        id: 'doctor_permissions',
        name: "Describe permissions when logged in as a doctor (" + doctor + ")",
        path: '/web?debug=',
        user: doctor,
        mode: 'test',
        steps: [
            {
                title:     _t("User logged in"),
                element:   ".oe_topbar_name:contains('" + capitalise(doctor) + "')"
            },
            {
                title: _t("They can see the acuity board"),
                waitFor: "span.oe_menu_text:contains('Acuity Board')"
            },
            {
                title: _t("They can see the 'Doctor Tasks' list"),
                waitFor: "span.oe_menu_text:contains('Doctor Tasks')"
            },
            {
                title: _t("They can see the 'Overdue Tasks'"),
                waitFor: "span.oe_menu_text:contains('Overdue Tasks')"
            },
            //{
            //    title: _t("They can see the patients they are responsible for"),
            //    waitFor: "div.oe_kanban_card:contains('Doe, John Robert')"
            //},
            //{
            //    title: _t("They can't see patients they aren't responsible for"),
            //    waitNot: "div.oe_kanban_card:contains('Doe, James Xen')"
            //},
            {
                title: _t("They can see view patient records"),
                element: "div.oe_kanban_card:eq(0)"
            },
            {
                title: _t("They can manage devices"),
                element: "a.ui-tabs-anchor:contains('Devices')"
            },
            {
                title: _t("They can start device sessions"),
                waitFor: "button:contains('Start Device Session')"
            },
            {
                title: _t("They can stop device sessions"),
                waitFor: "td[title='Complete Device Session']"
            },
            {
                title: _t("They can edit some patient information"),
                element: "button.oe_form_button_edit"
            },
            {
                title: _t("They can edit 'Other Obs' info"),
                waitFor: "select[name='mrsa']",
                element: "a.ui-tabs-anchor:contains('Other Obs')"
            },
            {
                title: _t("They can change MRSA status"),
                waitFor: "select[name='mrsa']"
            },
            {
                title: _t("They can change Diabetes status"),
                waitFor: "select[name='diabetes']"
            },
            {
                title: _t("They can edit 'Monitoring' information"),
                element: "a.ui-tabs-anchor:contains('Monitoring')"
            },
            {
                title: _t("They can change the Palliative Care status"),
                waitFor: "select[name='palliative_care']"
            },
            {
                title: _t("They can change the Postural Blood Pressure monitoring status"),
                waitFor: "select[name='pbp_monitoring']"
            },
            {
                title: _t("They can change the Weight monitoring status"),
                waitFor: "select[name='weight_monitoring']"
            },
            {
                title: _t("They can change the O2 Sats Target"),
                waitFor: "select[name='o2target']"
            },
            {
                title: _t("They can't manage patient movements"),
                waitFor: "button.oe_form_button.oe_form_invisible:contains('Move Patient')"
            },
            {
                title: _t("They can't see the patient waiting list"),
                waitNot: "span.oe_menu_text:contains('Patients without bed')"
            },
            {
                title: _t("They can't see the last discharged patient list"),
                waitNot: "span.oe_menu_text:contains('Recently Discharged')"
            },
            {
                title: _t("They can't see the last transferred patient list"),
                waitNot: "span.oe_menu_text:contains('Recently Transferred')"
            },
            {
                title: _t("They can't manage user accounts"),
                waitNot: "span.oe_menu_text:contains('Account Administration')"
            },
            {
                title: _t("They can't see the ward dashboard"),
                waitNot: "span.oe_menu_text:contains('Ward Dashboard')"
            },
            {
                title: _t("They can't manage the nursing and doctor shifts"),
                waitNot: "div.oe_secondary_menu_section:contains('Shift Management')"
            },
            {
                title: _t("They can't manage location data"),
                waitNot: "span.oe_menu_text:contains('NH Clinical')"
            }
        ]
    });

    openerp.Tour.register({
        id: 'wardmanager_permissions',
        name: "Describe permissions when logged in as a ward manager (" + wm + ")",
        path: '/web?debug=',
        user: wm,
        mode: 'test',
        steps: [
            {
                title:     _t("User logged in"),
                element:   ".oe_topbar_name:contains('" + capitalise(wm) + "')"
            },
            {
                title: _t("They can see the acuity board"),
                waitFor: "span.oe_menu_text:contains('Acuity Board')"
            },
            //{
            //    title: _t("They can see the patients they are responsible for"),
            //    waitFor: "div.oe_kanban_card:contains('Doe, John Robert')"
            //},
            //{
            //    title: _t("They can't see patients they aren't responsible for"),
            //    waitNot: "div.oe_kanban_card:contains('Doe, James Xen')"
            //},
            {
                title: _t("They can view patient records"),
                element: "div.oe_kanban_card:eq(0)"
            },
            {
                title: _t("They can manage devices"),
                element: "a.ui-tabs-anchor:contains('Devices')"
            },
            {
                title: _t("They can start device sessions"),
                waitFor: "button:contains('Start Device Session')"
            },
            {
                title: _t("They can stop device sessions"),
                waitFor: "td[title='Complete Device Session']"
            },
            {
                title: _t("They can edit the patient information"),
                waitFor: "button.oe_form_button_edit"
            },
            {
                title: _t("They can manage patient movements"),
                waitFor: "button.oe_form_button:contains('Move Patient')"
            },
            {
                title: _t("They can see the patient waiting list"),
                waitFor: "span.oe_menu_text:contains('Patients without bed')"
            },
            {
                title: _t("They can see the last discharged patient list"),
                waitFor: "span.oe_menu_text:contains('Recently Discharged')"
            },
            {
                title: _t("They can see the last transferred patient list"),
                waitFor: "span.oe_menu_text:contains('Recently Transferred')"
            },
            {
                title: _t("They can see the ward dashboard"),
                element: "span.oe_menu_text:contains('Ward Dashboard')"
            },
            {
                title: _t("They can view the ward records"),
                waitFor: "h3:contains('Ward A')"
            },
            {
                title: _t("They can manage the nursing and doctor shifts"),
                waitFor: "div.oe_secondary_menu_section:contains('Shift Management')"
            },
            {
                title: _t("They can't manage location data"),
                waitNot: "span.oe_menu_text:contains('Locations')"
            },
            {
                title: _t("They can manage user accounts"),
                waitFor: "span.oe_menu_text:contains('Account Administration')"
            }
        ]
    });
}());