var _ = {
    debounce: function (x) { return x }
};
/*
  Created by Jon Wyatt on 1/2/16
*/

describe('Events', function() {

    var context, focus, graphlib, pulse_graph, score_graph, test_area, bp_graph, rangify;
    graphlib = null;
    pulse_graph = null;
    score_graph = null;
    context = null;
    focus = null;
    test_area = null;
    bp_graph = null;

    beforeEach(function () {
        var body_el;

        body_el = document.getElementsByTagName('body')[0];
        test_area = document.createElement('div');
        test_area.setAttribute('id', 'test_area');
        test_area.style.width = '500px';
        body_el.appendChild(test_area);
        rangify = document.createElement('input');
        rangify.setAttribute('id', 'rangify');
        rangify.setAttribute('type', 'checkbox');
        test_area.appendChild(rangify);

        if (graphlib === null) {
            graphlib = new NHGraphLib('#test_area');
        }
        if (pulse_graph === null) {
            pulse_graph = new NHGraph();
        }
        if (bp_graph === null) {
            bp_graph = new NHGraph();
        }
        if (score_graph === null) {
            score_graph = new NHGraph();
        }
        if (context === null) {
            context = new NHContext();
        }
        if (focus === null) {
            focus = new NHFocus();
        }

        pulse_graph.options.keys = ['pulse_rate'];
        pulse_graph.options.label = 'HR';
        pulse_graph.options.measurement = '/min';
        pulse_graph.axes.y.min = 30;
        pulse_graph.axes.y.max = 200;
        pulse_graph.options.normal.min = 50;
        pulse_graph.options.normal.max = 100;
        pulse_graph.style.dimensions.height = 70;
        pulse_graph.style.axis.x.hide = true;
        pulse_graph.style.data_style = 'linear';
        pulse_graph.style.label_width = 60;

        bp_graph.options.keys = ['blood_pressure_systolic', 'blood_pressure_diastolic'];
        bp_graph.options.label = 'BP';
        bp_graph.options.measurement = 'mmHg';
        bp_graph.axes.y.min = 30;
        bp_graph.axes.y.max = 260;
        bp_graph.options.normal.min = 150;
        bp_graph.options.normal.max = 151;
        bp_graph.style.dimensions.height = 90;
        bp_graph.style.axis.x.hide = true;
        bp_graph.style.data_style = 'range';
        bp_graph.style.label_width = 60;

        score_graph.options.keys = ['score'];
        score_graph.style.dimensions.height = 132.5;
        score_graph.style.data_style = 'stepped';
        score_graph.axes.y.min = 0;
        score_graph.axes.y.max = 22;
        score_graph.drawables.background.data = [
          {
            "class": "green",
            s: 1,
            e: 4
          }, {
            "class": "amber",
            s: 4,
            e: 6
          }, {
            "class": "red",
            s: 6,
            e: 22
          }
        ];
        score_graph.style.label_width = 60;

        focus.graphs.push(pulse_graph);
        focus.graphs.push(bp_graph);
        focus.title = 'Individual values';
        focus.style.padding.right = 0;
        focus.style.margin.top = 0;
        focus.style.padding.top = 0;

        context.graph = score_graph;
        context.title = 'NEWS Score';

        graphlib.focus = focus;
        graphlib.context = context;
        graphlib.data.raw = ews_data.multi_partial;
        graphlib.options.controls.rangify = rangify;
        graphlib.options.controls.rangify.checked = true;
        graphlib.options.ranged = true;
    });

    afterEach(function () {

        if (graphlib !== null) {
            graphlib = null;
        }
        if (pulse_graph !== null) {
            pulse_graph = null;
        }
        if (bp_graph !== null) {
            bp_graph = null;
        }
        if (score_graph !== null) {
            score_graph = null;
        }
        if (context !== null) {
            context = null;
        }
        if (focus !== null) {
            focus = null;
        }
        if (rangify !== null) {
            rangify = null;
        }
        if (test_area !== null) {
            test_area.parentNode.removeChild(test_area);
            test_area = null;
        }
        var pops = document.querySelectorAll('#chart_popup');
        if (pops.length > 0) {
            for (var i = 0, len = pops.length; i < len; i++) {
                var pop = pops[i];
                pop.parentNode.removeChild(pop);
            }
        }

        var tests = document.querySelectorAll('#test_area');
        if (tests.length > 0) {
            for (var j = 0, len1 = tests.length; j < len1; j++) {
                var test = tests[j];
                test.parentNode.removeChild(test);
            }
        }
    });

    describe("Dependencies", function () {

        it("Function has bind method available", function () {
            expect(typeof Function.prototype.bind).toBe('function')
        });
    });

    describe("add_listeners", function() {

        beforeEach(function () {
            spyOn(NHGraphLib.prototype, 'add_listeners').and.callThrough();
        });

        it("is called by NHGraphLib.init()", function () {
            graphlib.init();
            expect(NHGraphLib.prototype.add_listeners).toHaveBeenCalled()
        });

        it("stores handler functions in options.handler object", function () {
            graphlib.init();
            expect(typeof graphlib.options.handler.resize).toBe('function');
            expect(typeof graphlib.options.handler.rangify).toBe('function')
        });

        it("wraps handle_resize in debounce when underscore available", function () {
            spyOn(_, 'debounce').and.callThrough();
            graphlib.init();
            expect(_.debounce).toHaveBeenCalled()
        });

        it("doesn't break if _ not available", function () {
            _ = null;
            graphlib.init();
            expect(typeof graphlib.options.handler.resize).toBe('function')
        });

        //it("adds window resize event listeners", function () {
        //    spyOn(window, 'addEventListener').and.callThrough();
        //    graphlib.init();
        //    expect(window.addEventListener).toHaveBeenCalled()
        //}); Skipping as test fails in Phantom and listeners tested by resize suite anyway

        it("adds rangify event listeners", function () {
            spyOn(rangify, 'addEventListener').and.callThrough();
            graphlib.init();
            expect(rangify.addEventListener).toHaveBeenCalled();
        });
    });

    describe("NHGraphLib.redraw_resize", function() {

        var resize;

        beforeEach(function () {

        });

        it("is called on resize event", function () {
            spyOn(NHGraphLib.prototype, 'redraw_resize').and.callThrough();
            graphlib.init();
            graphlib.draw();
            ev.html('resize', window);
            expect(NHGraphLib.prototype.redraw_resize).toHaveBeenCalled()
        });

        it("checks whether element exists using is_alive method", function () {
            spyOn(NHGraphLib.prototype, 'is_alive').and.callThrough()
            graphlib.init();
            graphlib.draw();
            ev.html('resize', window);
            expect(NHGraphLib.prototype.is_alive).toHaveBeenCalled()
        });

        it("calls NHContext.handle_resize if is_alive", function () {
            skipIfCantResize();
            spyOn(context, 'handle_resize').and.callThrough();
            graphlib.init();
            graphlib.draw();
            ev.html('resize', window);
            expect(context.handle_resize).toHaveBeenCalled();
            context.handle_resize.calls.reset()
        });

        it("doesn't call NHContext.handle_resize if not alive", function () {
            spyOn(context, 'handle_resize').and.callThrough();
            spyOn(NHGraphLib.prototype, 'is_alive').and.returnValue(false);
            graphlib.init();
            graphlib.draw();
            ev.html('resize', window);
            expect(context.handle_resize).not.toHaveBeenCalled();
            context.handle_resize.calls.reset()
        });
    });

    describe("rangify_graphs()", function() {

        beforeEach(function () {
            spyOn(NHGraphLib.prototype, 'rangify_graphs').and.callThrough();
            spyOn(bp_graph, 'rangify_graph').and.callThrough();
            spyOn(pulse_graph, 'rangify_graph').and.callThrough();
            spyOn(score_graph, 'rangify_graph').and.callThrough();
            graphlib.init();
            graphlib.draw();
            ev.mouse('click',rangify)
        });

        it("is called when rangify checkbox is clicked", function () {
            expect(NHGraphLib.prototype.rangify_graphs).toHaveBeenCalled()
        });

        it("is toggles options.ranged true / false in sync with box", function () {
            expect(graphlib.options.ranged).toBe(false);
            expect(rangify.checked).toBe(false);
            ev.mouse('click',rangify);
            expect(graphlib.options.ranged).toBe(true);
            expect(rangify.checked).toBe(true);
        });

        it("is toggles options.ranged true / false in sync with box", function () {
            expect(graphlib.options.ranged).toBe(false);
            expect(rangify.checked).toBe(false);
            ev.mouse('click',rangify);
            expect(graphlib.options.ranged).toBe(true);
            expect(rangify.checked).toBe(true);
        });

        it("calls graph.rangify_graph on all graphs if is_alive()", function () {
            expect(bp_graph.rangify_graph).toHaveBeenCalled();
            expect(score_graph.rangify_graph).toHaveBeenCalled();
            expect(pulse_graph.rangify_graph).toHaveBeenCalled()
        });

        it("doesn't call rangify_graph if not is_alive()", function () {
            bp_graph.rangify_graph.calls.reset();
            score_graph.rangify_graph.calls.reset();
            pulse_graph.rangify_graph.calls.reset();

            spyOn(NHGraphLib.prototype, 'is_alive').and.returnValue(false);
            ev.mouse('click',rangify);

            expect(bp_graph.rangify_graph).not.toHaveBeenCalled();
            expect(score_graph.rangify_graph).not.toHaveBeenCalled();
            expect(pulse_graph.rangify_graph).not.toHaveBeenCalled()
        });

    });

    describe("remove_listeners()", function() {

        beforeEach(function () {
            spyOn(NHGraphLib.prototype, 'remove_listeners').and.callThrough();
            spyOn(window, 'removeEventListener').and.callThrough();
            spyOn(rangify, 'removeEventListener').and.callThrough();

            graphlib.init();
            graphlib.draw();
            var ob = [[
                {baseURI: ''}
            ]];
            graphlib.obj = ob;
            graphlib.is_alive();
        });

        it("is called by is_alive() when object not in DOM", function () {
            expect(NHGraphLib.prototype.remove_listeners).toHaveBeenCalled()
        });

        //it("removes resize event listener", function () {
        //    expect(window.removeEventListener).toHaveBeenCalled()
        //}); Skipping as test fails in Phantom and listeners tested by resize suite anyway

        it("removes rangify event listener", function () {
            expect(rangify.removeEventListener).toHaveBeenCalled()
        });
    });

    describe("is_alive()", function() {

        beforeEach(function () {
            spyOn(NHGraphLib.prototype, 'remove_listeners').and.callThrough();
            graphlib.init();
            graphlib.draw();
        });

        it("returns true if baseURI is set", function () {
            expect(graphlib.is_alive()).toBe(true)
        });

        it("returns false if baseURI is not set", function () {
            var ob = [[
                {baseURI: ''}
            ]];
            graphlib.obj = ob;
            expect(graphlib.is_alive()).toBe(false)
        });

        it("calls remove_listeners if object is not alive", function () {
            var ob = [[
                {baseURI: ''}
            ]];
            graphlib.obj = ob;
            graphlib.is_alive();
            expect(NHGraphLib.prototype.remove_listeners).toHaveBeenCalled()
        });

    });
});


