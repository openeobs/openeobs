'use strict';

openerp.Tour.helpers = {};

openerp.Tour.helpers.assert = function (assertion, message) {
    if (!assertion) {
        console.log('Assert Failed: ' + message || ' ');
        return openerp.Tour.endTour();
    }
    console.log('Assert Passed: ' + message || ' ');
    return true;
};

openerp.Tour.helpers.capitalise = function (name) {
    return name.charAt(0).toUpperCase() + name.substring(1).toLowerCase();
};

openerp.Tour.templates = {
    combo: '<div class="popover tour fade top in"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div><nav class="popover-navigation"><button class="btn btn-sm btn-default" data-role="next">Continue</button> <small> <span class="text-muted"> or </span><button class="btn-link" data-role="end" style="float: none; padding: 0">Exit</button></small></nav></div>'
};

openerp.Tour.users = {
    admin: 'olga',
    hca: 'harold',
    nurse: 'norah',
    doctor: 'dave',
    wm: 'winifred',
    sm: 'sabastian'
};

openerp.Tour.error = function (step, message) {
        var state = openerp.Tour.getState();
        message += '\n tour: ' + state.id
            + (step ? '\n step: ' + step.id + ": '" + (step._title || step.title) + "'" : '' )
            + '\n href: ' + window.location.href
            + '\n referrer: ' + document.referrer
            + (step ? '\n element: ' + Boolean(!step.element || ($(step.element).size() && $(step.element).is(":visible") && !$(step.element).is(":hidden"))) : '' )
            + (step ? '\n waitNot: ' + Boolean(!step.waitNot || !$(step.waitNot).size()) : '' )
            + (step ? '\n waitFor: ' + Boolean(!step.waitFor || $(step.waitFor).size()) : '' )
            + "\n localStorage: " + JSON.stringify(localStorage);
        openerp.Tour.log(message, true);
        openerp.Tour.endTour();
    };