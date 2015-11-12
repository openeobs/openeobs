// Global beforeEach function
beforeEach(function() {
    // Custom matcher to check value matches one of a set of possible values
    jasmine.addMatchers({
        toBeEither: function (util, customEqualityTesters) {
            return {
                compare: function (actual, expected) {
                    var result = {};
                    result.pass = false;
                    for (i = 0; i < expected.length; i++) {
                        if (expected[i] === actual) result.pass = true
                    }
                    if (result.pass) {
                        result.message = actual + " matched one of " + expected
                    }
                    else {
                        result.message = "Expected " + actual + " to be one of " + expected.toString()
                    }
                    return result
                }
            }
        }
    })
});


// Event helper object
ev = {}

/*
 Function to create and dispatch mouse events using browser specific method
 Expects action as string e.g. 'mouseover','click' and the target element
*/
ev.mouse = function (action, el, x, y) {
    var ev;
    if (el.dispatchEvent) {
        try {
            // Chrome, Firefox, Safari
            ev = new MouseEvent(action, {bubbles: true, cancelable: true});
        }
        catch (e) {
            // PhantomJS
            ev = document.createEvent('MouseEvent');
            ev.initMouseEvent(action, true, true, window, null, 0, 0, 0, 0, false, false, false, false, 0, null);
        }
        if (x) {
            ev.pageX = x;
            ev.pageY = y
        }
        el.dispatchEvent(ev);
    }
    else {
        // IE
        ev = document.createEventObject('MouseEvent');
        if (x) {
            ev.pageX = x;
            ev.pageY = y
        }
        el.fireEvent(action, ev)
    }
};

/*
 Function to dispatch HTML Events e.g. resize
 If no element provided defaults to window
*/
ev.html = function (action, el) {
    var ev;
    if (el.dispatchEvent) {
        try {
            // Chrome, Firefox, Safari
            ev = CustomEvent(action);
        }
        catch (e) {
            // PhantomJS
            ev = document.createEvent('HTMLEvents');
            ev.initEvent(action, true, true);
        }
        el.dispatchEvent(ev);
    }
    else {
        // IE
        ev = document.createEventObject('HTMLEvent');
        el.fireEvent(action, ev)
    }
};

