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
                content: _t("This tutorial demonstrates how changing a patients palliative care status will remove their scheduled observations tasks."),
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
                content: _t("Select the status from the dropdown below. Click continue when done."),
                element:   "select[name='palliative_care']",
                placement: 'top',
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Confirm Change"),
                content: _t("Click here to save changes"),
                element:   "button.oe_button:contains('Save')",
                placement: 'bottom'
            },
            {
                title:     _t("Change Logged"),
                content: _t("The change is logged with the date, time and clinician. Click 'Continue' to proceed."),
                element:   "tr[data-id='1']:eq(1)",
                placement: 'bottom',
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
                title:     _t("Completed"),
                content: _t("All observation tasks for palliative patient have been removed. This completes the tutorial."),
                popover:   { next: _t("Exit")}
            }


        ]
    });
}());