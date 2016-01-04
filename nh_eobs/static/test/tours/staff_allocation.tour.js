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
                title:     _t("Nursing Staff Shift Change"),
                content: _t("It's 8pm, I am the designated nurse in charge for ward C for the upcoming night shift. I need to assign staff to patients at the beginning of my shift."),
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Log in as a ward manager"),
                content: _t("Only ward manager and senior manager are able to access the 'Nursing Shift Change' wizard"),
                element: "Winifred",
                popover:   { next: _t("Continue"), end: _t("Exit") }
            }
        ]
    });
    openerp.Tour.register({
        id: 'allocate_nursing_staff',
        name: _t("Adding / Removing nursing staff during shift tutorial (Winifred)"),
        path: '/web?debug=',
        mode: 'tour',
        steps: [

        ]
    });
}());