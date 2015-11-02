
/*
  Created by Jon Wyatt on 30/10/15
 */

describe('Resize', function() {

    var context, focus, graphlib, pulse_graph, score_graph, test_area;
    graphlib = null;
    pulse_graph = null;
    score_graph = null;
    context = null;
    focus = null;
    test_area = null;

    beforeEach(function () {
        var body_el;

        body_el = document.getElementsByTagName('body')[0];
        test_area = document.createElement('div');
        test_area.setAttribute('id', 'test_area');
        test_area.style.width = '500px';
        body_el.appendChild(test_area);

        if (graphlib === null) {
            graphlib = new NHGraphLib('#test_area');
        }
        if (pulse_graph === null) {
            pulse_graph = new NHGraph();
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
        focus.title = 'Individual values';
        focus.style.padding.right = 0;
        focus.style.margin.top = 0;
        focus.style.padding.top = 0;

        context.graph = score_graph;
        context.title = 'NEWS Score';

        graphlib.focus = focus;
        graphlib.context = context;
        graphlib.data.raw = ews_data.multi_partial;
    });

    afterEach(function () {

        if (graphlib !== null) {
            graphlib = null;
        }
        if (pulse_graph !== null) {
            pulse_graph = null;
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

    describe("Methods", function() {

        it("NHGraphLib has redraw_resize method", function () {
            expect(typeof graphlib.redraw_resize).toBe('function')
        });

        it("NHContext has handle_resize method", function () {
            expect(typeof context.handle_resize).toBe('function')
        });

        it("NHFocus has handle_resize method", function () {
            expect(typeof focus.handle_resize).toBe('function')
        });

        it("NHGraph has resize_graph method", function () {
            expect(typeof pulse_graph.resize_graph).toBe('function')
        });

    });

    describe("Window 'resize' Event", function() {

        beforeEach(function() {

            spyOn(NHGraphLib.prototype, 'redraw_resize').and.callThrough();
            spyOn(context, 'handle_resize').and.callThrough();

            spyOn(NHFocus.prototype, 'handle_resize').and.callThrough();
            spyOn(focus, 'redraw').and.callThrough();

            spyOn(pulse_graph, 'redraw').and.callThrough();
            spyOn(pulse_graph, 'resize_graph').and.callThrough();

            graphlib.init();
            graphlib.draw();

            // Set a new client width and trigger resize event
            var resize_event = document.createEvent('HTMLEvents');
            resize_event.initEvent('resize', true, true);
            window.dispatchEvent(resize_event);

        });

        it("NHGraphLib.redraw_resize() is called", function () {
            expect(NHGraphLib.prototype.redraw_resize).toHaveBeenCalled()
        });

        it("NHContext.handle_resize() is called", function () {
            expect(context.handle_resize).toHaveBeenCalled()
        });

        it("NHFocus.handle_resize() is called", function () {
            expect(NHFocus.prototype.handle_resize).toHaveBeenCalled()
        });

        it("NHFocus.redraw() is called", function () {
            expect(focus.redraw).toHaveBeenCalled()
        });

        it("NHGraph.redraw() is called", function () {
            expect(focus.redraw).toHaveBeenCalled()
        });

    })
})


