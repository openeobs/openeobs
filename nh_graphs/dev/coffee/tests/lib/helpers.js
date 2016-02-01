// Global beforeEach function
beforeEach(function() {
    // Custom matcher to check value matches one of a set of possible values
    jasmine.addMatchers({
        toBeEither: function () {
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
ev = {};

/*
 Function to create and dispatch mouse events using browser specific method
 Expects action as string e.g. 'mouseover','click', target element and optional x/y co-ords
*/
ev.mouse = function (action, el, x, y) {
    var ev;
    if (!x) x = 0;
    if (!y) y = 0;
    if (el.dispatchEvent) {
        try {
            // Chrome, Firefox, Safari
            ev = new MouseEvent(action, {
                bubbles: true,
                cancelable: true,
                pageX: x,
                pageY: y,
                clientX: x,
                clientY: y});
        }
        catch (e) {
            // PhantomJS
            ev = document.createEvent('MouseEvent');
            ev.initMouseEvent(
                action,
                true,
                true,
                window,
                null,
                x,
                y,
                x,
                y,
                false,
                false,
                false,
                false,
                0,
                null);
        }
        el.dispatchEvent(ev);
    }
    else {
        // IE
        ev = document.createEventObject('MouseEvent');
        if (x) {
            ev.pageX = x;
            ev.pageY = y;
            ev.clientX = x;
            ev.clientY = y;
            ev.screenX = x;
            ev.screenY = y
        }
        el.fireEvent(action, ev)
    }
};

/*
 Function to dispatch HTML Events e.g. resize
 If no element provided returns event instead of dispatching
*/
ev.html = function (action, el) {
    var ev;
    if (window.dispatchEvent) {
        try {
            // Chrome, Firefox, Safari
            ev = new CustomEvent(action);
        }
        catch (e) {
            // PhantomJS, IE
            ev = document.createEvent('HTMLEvents');
            ev.initEvent(action, true, true);
        }
        if (el) el.dispatchEvent(ev);
        else return ev
    }
    else return "Fail, no event method found"
};

