'use strict';

/*global
    openerp, $
 */

(function () {
    var _t = openerp._t;
    openerp.Tour.register({
        id: 'nursing_shift_change',
        name: _t("Nursing staff shift change tutorial (Winifred)"),
        path: '/web?debug=',
        mode: 'tour',
        steps: [
            {
                title:     _t("Nursing Staff Shift Change Tutorial"),
                content: _t("It's 8pm, I am the designated nurse in charge for ward C for the upcoming night shift. I need to assign staff to patients at the beginning of my shift."),
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Logged in as a ward manager"),
                content: _t("Only ward managers and senior managers are able to access the 'Nursing Shift Change' wizard"),
                element:   ".oe_topbar_name:contains('Winifred')",
                popover:   { next: _t("Continue"), end: _t("Exit") },
                placement: 'bottom'
            },
            {
                title:     _t("Click 'Nursing Shift Change'"),
                content: _t("This will open the nursing shift change wizard"),
                element:   "span.oe_menu_text:contains('Nursing Shift Change')"
            },
            {
                title:     _t("Select Ward"),
                content: _t("Choose your ward from the drop down menu and click 'Start'"),
                element:   "button:contains('Start')",
                placement: 'top'
            },
            {
                title:     _t("Previous Shift"),
                element: "div:contains('Previous Shift')",
                content: _t("This shows a list of all beds in the selected ward and the responsible staff members"),
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Click 'Deallocate Previous Shift'"),
                content: _t("This will deallocate all HCA's and nurses from previous shift"),
                element:   "button:contains('Deallocate Previous Shift')",
                placement: 'bottom'
            },
            {
                title:     _t("Enter staff for next shift"),
                content: _t("You can add multiple staff members. Begin typing a name to find matches or press down key to view list. Click 'Select' when done"),
                element:   ".modal-dialog button:contains('Select')", // Add 7 x HCA's and 7 x nurses
                //element:   ".modal-dialog input", // Add 7 x HCA's and 7 x nurses
                placement: 'top'
            },
            {
                title:     _t("Allocation Tab"),
                element: "div:contains('Previous Shift')",
                content: _t("This shows a list of all beds requiring staff allocation in this ward"),
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Click Allocate"),
                content: _t("To assign staff to this bed"),
                element:   ".modal-dialog button[title='Allocate']:eq(0)",
                placement: 'top'
            },
            {
                title:     _t("Select Nurse / HCA"),
                content: _t("Choose from dropdown or begin typing to get suggested names"),
                element:   ".modal-dialog:eq(1) input:eq(0)",
                popover:   { next: _t("Continue"), end: _t("Exit") },
                placement: 'top'
            },
            {
                title:     _t("Navigation"),
                content: _t("You can use the arrows to scroll through the beds in ward. Click here to view the next bed in list."),
                element:   ".modal-dialog:eq(1) a[data-pager-action='next']:eq(0)",
                placement: 'bottom'
            },
            {
                waitFor: ".modal-dialog:eq(1) span:contains('Bed 02')",
                title:     _t("Save Changes"),
                content: _t("When finished allocating you can click here to save changes and close popup"),
                element:   ".modal-dialog:eq(1) button.oe_form_button_save"
            },
            {
                waitNot: ".modal-dialog:eq(1)",
                title:     _t("Confirm Changes"),
                content: _t("Review your changes here and click to confirm and return to the main page"),
                element:   ".modal-dialog span:contains('Confirm Allocation')",
                placement: 'bottom'
            },
            {
                waitNot: ".modal-dialog",
                title:     _t("Tutorial Completed"),
                content: _t("That's it. You're staff have now been allocated"),
                popover:   { end: _t("Exit") }
            }
        ]
    });
    //openerp.Tour.register({
    //    id: 'nursing_reallocation',
    //    name: _t("Re-allocating nursing staff during shift (Winifred)"),
    //    path: '/web?debug=',
    //    mode: 'tour',
    //    steps: [
    //        {
    //            title:     _t("Nursing Staff Re-Allocation Tutorial"),
    //            content: _t("It's 8pm, I am the designated nurse in charge for ward C for the upcoming night shift. I need to assign staff to patients at the beginning of my shift."),
    //            popover:   { next: _t("Continue"), end: _t("Exit") }
    //        },
    //        {
    //            title:     _t("Logged in as a ward manager"),
    //            content: _t("Only ward managers and senior managers are able to access the 'Nursing Shift Change' wizard"),
    //            element:   ".oe_topbar_name:contains('Winifred')",
    //            popover:   { next: _t("Continue"), end: _t("Exit") },
    //            placement: 'bottom'
    //        },
    //        {
    //            title:     _t("Click 'Nursing Shift Change'"),
    //            content: _t("This will open the nursing shift change wizard"),
    //            element:   "span.oe_menu_text:contains('Nursing Shift Change')"
    //        },
    //    ]
    //});
}());