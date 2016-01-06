'use strict';

/*global
    openerp, $
 */

(function () {
    var _t = openerp._t;
    openerp.Tour.register({
        id: 'palliative_care_flag',
        name: _t("Palliative care status change will cancel NEWS observation scheduling and remove obs tasks for that patient"),
        path: '/web',
        mode: 'tour',
        steps: [
            {
                title:     _t("Palliative Care Status Change Tutorial"),
                content: _t("This tutorial demonstrates how changing a patients palliative care status will remove any scheduled observations tasks for that patient"),
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Open Patient Record"),
                content: _t("Click the card for the patient whose palliative care status you want to change"),
                element:   "div.oe_kanban_card:eq(0)",
                placement: 'bottom'
            },
            {
                title:     _t("Open Patient Record"),
                content: _t("Click the card for the patient whose palliative care status you want to change"),
                element:   "a.ui-tabs-anchor:contains('Monitoring')",
                placement: 'top'
            },
            {
                title:     _t("Open Monitoring Tab"),
                content: _t("Click here to view monitoring status for patient"),
                element:   "a.ui-tabs-anchor:contains('Monitoring')",
                placement: 'top'
            },
            {
                waitFor: "li.ui-tabs-active:contains('Monitoring')",
                title:     _t("Switch to 'Edit'"),
                content: _t("Click here to switch to edit mode"),
                element:   "button.oe_form_button_edit",
                placement: 'top'
            },
            {
                title:     _t("Change Status"),
                content: _t("Select the status from the dropdown below. <br/>Click <strong>Save</strong> when done."),
                element:   "select[name='palliative_care']",
                placement: 'top'
            },
            {
                title:     _t("Change Logged"),
                content: _t("The change has been logged with the date, time and clinician."),
                waitNot:   "select[name='palliative_care']",
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Click Here"),
                content: _t("To view overdue tasks list"),
                element:   "span.oe_menu_text:contains('Overdue Tasks')",
                placement: 'bottom'
            },
            {
                waitFor: "h2.oe_view_title:contains('Overdue Tasks')",
                title: _t("Completed"),
                content: _t("All observation tasks for the palliative patient have been removed. This completes the tutorial."),
                popover: {next: _t("Exit")}
            }
        ]
    });
}());