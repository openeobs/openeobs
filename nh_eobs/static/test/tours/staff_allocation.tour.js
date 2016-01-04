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
                //element:   ".oe_topbar_name:contains('Winifred')",
                content: _t("It's 8pm, I am the designated nurse in charge for ward C for the upcoming night shift. I need to assign staff to patients at the beginning of my shift."),
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Logged in as a ward manager"),
                content: _t("Only ward managers and senior managers are able to access the 'Nursing Shift Change' wizard"),
                element:   ".oe_topbar_name:contains('Winifred')",
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Click 'Nursing Shift Change'"),
                content: _t("This will open the nursing shift change wizard"),
                element:   "span.oe_menu_text:contains('Nursing Shift Change')",
                popover:   { fixed: false }
            },
            {
                title:     _t("Select Ward"),
                content: _t("Choose your ward from the drop down menu and click 'Start'"),
                element:   ".modal-dialog button:contains('Start')",
                popover:   { fixed: false },
                placement: 'right'
            },
            {
                title:     _t("Previous Shift"),
                element: "div:contains('Previous Shift')",
                content: _t("This shows a list of all beds in selected ward and the responsible staff members"),
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Click 'Deallocate Previous Shift'"),
                content: _t("This will deallocate all HCA's and nurses from previous shift"),
                element:   ".modal-dialog button:contains('Deallocate Previous Shift')",
                popover:   { fixed: true }
            },
            {
                title:     _t("Enter staff for next shift"),
                content: _t("Begin typing a name to get a list of matching staff members"),
                element: "textarea",
                sampleText:   "Nad"
            },
            {
                title:     _t("Select staff from dropdown"),
                content: _t("You can add multiple staff members to the list then click 'Select'"),
                element:   ".modal-dialog button:contains('Select')", // Add 7 x HCA's and 7 x nurses
                popover:   { fixed: false },
                placement: 'bottom'
            },
            {
                title:     _t("Click Allocate"),
                content: _t("To assign staff to bed"),
                element:   ".modal-dialog button:contains('Allocate')"
            },
            {
                title:     _t("Select Nurse"),
                content: _t("Choose from dropdown or begin typing to get suggested names"),
                element:   "Select"
            },
            {
                title:     _t("Click HCA"),
                content: _t("Choose from dropdown or begin typing to get suggested names"),
                element:   "Select"
            },
            {
                title:     _t("Click Next Arrow"),
                content: _t("To save changes and assign staff to next bed in list"),
                element:   "Next arrow"
            }, // Assign staff to all beds on ward
            {
                title:     _t("Click Save"),
                content: _t("When finished allocating staff to beds"),
                element:   "Save"
            },
            {
                title:     _t("Confirm Allocation"),
                content: _t("Check that your changes are correct and confirm by clicking here"),
                element:   "Confirm Allocation"
            },
            {
                title:     _t("Completed"),
                content: _t("Tutorial complete"),
                popover:   { end: _t("Exit") }
            }
        ]
    });
    //openerp.Tour.register({
    //    id: 'allocate_nursing_staff',
    //    name: _t("Adding / Removing nursing staff during shift tutorial (Winifred)"),
    //    path: '/web?debug=',
    //    mode: 'tour',
    //    steps: [
    //
    //    ]
    //});
}());