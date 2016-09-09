'use strict';

/*global
    openerp, $
 */

(function () {
    var _t = openerp._t;
    openerp.Tour.register({
        id: 'nursing_shift_change',
        name: _t("Nursing Staff Shift Change"),
        description: "Describes the steps the nurse in charge should take at the beginning of their shift in order to de-allocate the previous shift's nursing staff and allocate the next.",
        users: ['Shift Coordinator', 'Admin'],
        duration: "3 - 4 mins",
        path: '/web',
        mode: 'tour',
        steps: [
            {
                title:     _t("Nursing Staff Shift Change Tutorial"),
                content: _t("This tour shows the steps needed to change the staff available at the beginning of a shift and then allocate them to beds."),
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Start Here"),
                content: _t("Click here to open the nursing shift change wizard"),
                element:   "span.oe_menu_text:contains('Nursing Shift Change')"
            },
            {
                title:     _t("Select Ward"),
                content: _t("Choose your ward from the drop down menu, then click <strong>Start</strong>"),
                element:   ".modal-dialog input:eq(0)",
                placement: 'top',
                next: "button:contains('Start')",
                onload: function () {
                    var state = openerp.Tour.getState();
                    if (state.mode !== 'tutorial') {
                        // Hack as just setting input with .val() failed because Odoo.
                        // Have to click dropdown and select option as user would..
                        $(state.step.element).parent().find('span.oe_m2o_drop_down_button').click();
                        setTimeout(function () {
                            $("a:contains('Ward C')").click();
                        }, 300);
                        setTimeout(function () {
                            $(state.step.next).click();
                        }, 300);
                    }
                }
            },
            {
                title:     _t("Previous Shift List"),
                waitFor: "li.oe_active span.label:contains('De-allocate')",
                content: _t("This shows a list of all beds in the selected ward and the currently responsible staff members"),
                popover:   { next: _t("Continue"), end: _t("Exit") },
                placement: 'bottom'
            },
            {
                title:     _t("Click Here"),
                content: _t("To deallocate all HCA's and nurses from the previous shift"),
                element:   "button:contains('Deallocate Previous Shift')",
                placement: 'bottom'
            },
            {
                title:     _t("Enter New Staff"),
                content: _t("You can add multiple staff members. Begin typing a name to find matches or press down key to view list. <br/>Click <strong>Select</strong> when done"),
                element:   ".modal-dialog textarea",
                placement: 'top',
                next: "button:contains('Select')",
                onload: function () {
                    var state = openerp.Tour.getState();
                    if (state.mode !== 'tutorial') {
                        $(state.step.next).click();
                    }
                }
            },
            {
                title:     _t("Allocation List"),
                waitFor: "li.oe_active span.label:contains('Allocation')",
                content: _t("This shows all the beds in the ward requiring staff allocation"),
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
                content: _t("Choose from dropdown or begin typing to get suggested names.  <br/>Click <strong>Continue</strong> when done"),
                element:   ".modal-dialog:eq(1) input:eq(0)",
                popover:   { next: _t("Continue"), end: _t("Exit") },
                placement: 'top'
            },
            {
                title:     _t("Navigation"),
                content: _t("You can use the arrows to scroll through the beds in the ward. Any changes will be saved automatically."),
                element:   ".modal-dialog:eq(1) a[data-pager-action='next']:eq(0)",
                placement: 'bottom',
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Save Changes"),
                content: _t("When you've finished allocating, click here to save changes and close the popup"),
                element:   ".modal-dialog:eq(1) button.oe_form_button_save",
                placement: 'bottom'
            },
            {
                waitNot: ".modal-dialog:eq(1)",
                title:     _t("Confirm Changes"),
                content: _t("Review your changes then click here to confirm and return to the main page"),
                element:   ".modal-dialog span:contains('Confirm Allocation')",
                placement: 'bottom'
            },
            {
                waitNot: ".modal-dialog",
                title:     _t("Tutorial Completed"),
                content: _t("That's it. You're staff have now been allocated"),
                popover:   { next: _t("Exit")}
            }
        ]
    });
    openerp.Tour.register({
        id: 'nursing_reallocation',
        name: _t("Nursing Staff Re-Allocation"),
        description: "Shows how to make adjustments to nursing staff during a shift, e.g. if one HCA finishes their shift and their beds need to be allocated to a new member of staff.",
        users: ['Shift Coordinator', 'Admin'],
        duration: "2 - 3 mins",
        path: '/web',
        mode: 'tour',
        steps: [
            {
                title:     _t("Nursing Staff Re-Allocation Tutorial"),
                content: _t("This tour shows you how to change the staff available on shift and re-allocate beds. e.g. If a nurse finishes their shift and their allocated beds need to be assigned to a different member of staff"),
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Click here"),
                content: _t("This will open the nursing re-allocation wizard"),
                element:   "span.oe_menu_text:contains('Nursing Re-Allocation')"
            },
            {
                title:     _t("Add / Remove Staff"),
                content: _t("Remove staff by clicking the 'x' next to their name. Add staff by typing in their name or selecting from the dropdown. Click <strong>Re-Allocate</strong> to confirm."),
                element:   ".modal-dialog textarea",
                placement: 'top',
                next: "button:contains('Re-Allocate')",
                onload: function () {
                    var state = openerp.Tour.getState();
                    if (state.mode !== 'tutorial') {
                        $(state.step.next).click();
                    }
                }
            },
            {
                title:     _t("Allocation List"),
                waitFor: "li.oe_active span.label:contains('Allocation')",
                content: _t("This shows all the beds in the ward and the staff currently assigned"),
                popover:   { next: _t("Continue"), end: _t("Exit") },
            },
            {
                title:     _t("Click Here"),
                content: _t("To allocate a bed to a different member of staff"),
                element:   ".modal-dialog button[title='Allocate']:eq(0)",
                placement: 'top'
            },
            {
                title:     _t("Select Nurse"),
                content: _t("Choose from dropdown or begin typing to get suggested name. Click <strong>Save</strong> when done."),
                element:   ".modal-dialog:eq(1) input:eq(0)",
                //popover:   { next: _t("Continue"), end: _t("Exit") },
                placement: 'top',
                next: ".modal-dialog:eq(1) button:contains('Save')",
                onload: function () {
                    var state = openerp.Tour.getState();
                    if (state.mode !== 'tutorial') {
                        $(state.step.next).click();
                    }
                }
            },
            {
                waitNot: ".modal-dialog:eq(1)",
                title:     _t("Review and Confirm"),
                content: _t("Review your changes then click here to confirm and return to the main page"),
                element:   ".modal-dialog span:contains('Confirm Allocation')",
                placement: 'bottom'
            },
            {
                waitNot: ".modal-dialog",
                title:     _t("Tutorial Completed"),
                content: _t("That's it. You're staff have been successfully allocated."),
                popover:   { next: _t("Exit")}
            }
        ]
    });
}());