'use strict';

/*global
    openerp, $
 */

(function () {
    var _t = openerp._t;
    openerp.Tour.register({
        id: 'nursing_shift_change',
        name: _t("Nursing staff shift change tutorial (Winifred)"),
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
                content: _t("Choose your ward from the drop down menu and click 'Start'"),
                element:   ".modal-dialog input:eq(0)",
                placement: 'top'
            },
            {
                title:     _t("Previous Shift"),
                element: "li.oe_active span.label:contains('De-allocate')",
                content: _t("This shows a list of all beds in the selected ward and the currently responsible staff members"),
                popover:   { next: _t("Continue"), end: _t("Exit") },
                placement: 'bottom'
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
                element:   ".modal-dialog textarea",
                placement: 'top'
            },
            {
                title:     _t("Allocation Tab"),
                element: "li.oe_active span.label:contains('Allocation')",
                content: _t("This shows all the beds in the ward requiring staff allocation"),
                popover:   { next: _t("Continue"), end: _t("Exit") },
                placement: 'bottom'
            },
            {
                title:     _t("Click Allocate"),
                content: _t("To assign staff to this bed"),
                element:   ".modal-dialog button[title='Allocate']:eq(0)",
                placement: 'top'
            },
            {
                title:     _t("Select Nurse / HCA"),
                content: _t("Choose from dropdown or begin typing to get suggested names. Click 'Continue' when done."),
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
        name: _t("Re-allocating nursing staff during shift (Winifred)"),
        path: '/web',
        mode: 'tour',
        steps: [
            {
                title:     _t("Nursing Staff Re-Allocation Tutorial"),
                content: _t("This tour shows you how to change the staff available on shift and re-allocate beds. e.g. If a new nurse starts their shift and needs to be allocated beds"),
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Click here"),
                content: _t("This will open the nursing re-allocation wizard"),
                element:   "span.oe_menu_text:contains('Nursing Re-Allocation')"
            },
            {
                title:     _t("Add / Remove Staff"),
                content: _t("Remove staff by clicking the 'x' next to their name. Add staff by typing in their name or selecting from the dropdown."),
                element:   ".modal-dialog textarea",
                popover:   { next: _t("Continue"), end: _t("Exit") },
                placement: 'top'
            },
            {
                title:     _t("Confirm Changes"),
                content: _t("When happy with changes to staff on shift, click here"),
                element:   "button:contains('Re-Allocate')",
                placement: 'bottom'
            },
            {
                title:     _t("Allocation Tab"),
                element: "li.oe_active span.label:contains('Allocation')",
                content: _t("This shows all the beds in the ward and the staff currently assigned"),
                popover:   { next: _t("Continue"), end: _t("Exit") },
                placement: 'bottom'
            },
            {
                title:     _t("Click Here"),
                content: _t("To re-allocate the unassigned bed to the new member of staff"),
                element:   ".modal-dialog button[title='Allocate']:eq(0)",
                placement: 'top'
            },
            {
                title:     _t("Select Nurse"),
                content: _t("Choose from dropdown or begin typing to get suggested name"),
                element:   ".modal-dialog:eq(1) input:eq(0)",
                popover:   { next: _t("Continue"), end: _t("Exit") },
                placement: 'top'
            },
            {
                title:     _t("Click Here"),
                content: _t("To confirm changes and close popup"),
                element:   ".modal-dialog:eq(1) button.oe_form_button_save",
                placement: 'bottom'
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