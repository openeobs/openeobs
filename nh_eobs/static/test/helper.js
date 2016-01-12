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