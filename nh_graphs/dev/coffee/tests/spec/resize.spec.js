
/*
  Created by Jon Wyatt on 2/11/15
*/

describe('Resize', function() {

    var context, focus, graphlib, pulse_graph, score_graph, test_area, bp_graph;
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

    describe("Event listeners", function() {

        it("NHGraphLib.handle_resize() fires on 'resize' event",function() {

            spyOn(NHGraphLib.prototype, 'redraw_resize').and.callThrough();

            graphlib.init();
            graphlib.draw();

            var resize_event = document.createEvent('HTMLEvents');
            resize_event.initEvent('resize', true, true);
            window.dispatchEvent(resize_event);

            expect(NHGraphLib.prototype.redraw_resize).toHaveBeenCalled()
        });

        it("NHContext.handle_resize() fires on 'context_resize' event",function() {

            spyOn(context, 'handle_resize').and.callThrough();

            graphlib.init();
            graphlib.draw();

            var resize_event = document.createEvent('HTMLEvents');
            resize_event.initEvent('context_resize', true, true);
            window.dispatchEvent(resize_event);

            expect(context.handle_resize).toHaveBeenCalled()
        });

        it("NHFocus.handle_resize() fires on 'focus_resize' event",function() {
            spyOn(NHFocus.prototype, 'handle_resize').and.callThrough();

            graphlib.init();
            graphlib.draw();

            var focus_resize = document.createEvent('HTMLEvents');
            focus_resize.initEvent('focus_resize', true, true);
            window.dispatchEvent(focus_resize);

            expect(NHFocus.prototype.handle_resize).toHaveBeenCalled()
        });

        xit("NHGraph.resize_graph() fires on 'graph_resize' event",function() {
            spyOn(NHGraph.prototype, 'resize_graph').and.callThrough();

            graphlib.init();
            graphlib.draw();

            var resize_event = document.createEvent('HTMLEvents');
            resize_event.initEvent('graph_resize', true, true);
            window.dispatchEvent(resize_event);

            expect(NHGraph.prototype.resize_graph).toHaveBeenCalled()
        });
    });

    describe("NHGraphLib.redraw_resize()", function() {

        beforeEach(function() {

            spyOn(context, 'handle_resize').and.callThrough();

            graphlib.init();
            graphlib.draw();

            // Set new div width and trigger resize event
            test_area.style.width = '800px';

            var resize_event = document.createEvent('HTMLEvents');
            resize_event.initEvent('resize', true, true);
            //window.dispatchEvent(resize_event);
            graphlib.redraw_resize(graphlib,resize_event);

        });

        it("sets style.dimensions.width to element width - margins", function () {
            expect(graphlib.style.dimensions.width).toBe(800)
        });

        it("sets SVG object's width to style.dimensions.width", function () {
            expect(+graphlib.obj.attr('width')).toBe(graphlib.style.dimensions.width)
        });

        it("triggers NHContext.handle_resize() via 'context_resize' event", function () {
            expect(context.handle_resize).toHaveBeenCalled()
        });
    });

    describe("NHContext.handle_resize()", function() {

        beforeEach(function() {
            spyOn(NHFocus.prototype, 'handle_resize').and.callThrough();
            spyOn(context.graph, 'redraw').and.callThrough();

            graphlib.init();
            graphlib.draw();

            // Set new div width and trigger resize event
            test_area.style.width = '800px';

            var resize_event = document.createEvent('HTMLEvents');
            resize_event.initEvent('resize', true, true);
            context.handle_resize(context,context.parent_obj.obj,resize_event)
        });

        it("sets style.dimensions.width to element width - margins", function () {
            var expected = graphlib.style.dimensions.width -
            ((graphlib.style.padding.left +
            graphlib.style.padding.right) +
            (context.style.margin.left + context.style.margin.right));

            expect(context.style.dimensions.width).toBe(expected)
        });

        it("sets SVG object's width to style.dimensions.width", function () {
            expect(+context.obj.attr('width')).toBe(context.style.dimensions.width)
        });

        it("sets axes.x.scale.range (max) to new width", function () {
            var actual = context.axes.x.scale.range()[1];
            expect(actual).toBe(context.style.dimensions.width)
        });

        it("dispatches 'focus_resize' event and triggers focus.handle_resize()", function () {
            expect(NHFocus.prototype.handle_resize).toHaveBeenCalled()
        });

        it("sets the context graph x-axis range correctly", function() {
            expect(context.graph.axes.x.scale.range()[1]).toBe(context.style.dimensions.width-context.graph.style.label_width)
        });

        it("triggers context graph redraw", function() {
            // Works in chrome console but not here, tried all spy options
            expect(context.graph.redraw).toHaveBeenCalled()
        });
    });




    describe("NHFocus.handle_resize()", function() {

        beforeEach(function() {

            spyOn(focus, 'redraw').and.callThrough();

            graphlib.init();
            graphlib.draw();

            var focus_resize = document.createEvent('HTMLEvents');
            focus_resize.initEvent('focus_resize', true, true);
            focus.handle_resize(focus,focus_resize)
        });

        it("sets style.dimensions.width to parent object - padding + margin",function() {
            var width = focus.style.dimensions.width;
            var expected = focus.style.dimensions.width
                - focus.style.padding.left
                - focus.style.padding.right
                - focus.style.margin.left
                - focus.style.margin.right;
            expect(width).toBe(expected)
        });

        it("sets the object width to style.dimensions.width",function() {
           expect(+focus.obj.attr('width')).toBe(focus.style.dimensions.width)
        });

        it("sets the x axis range to the new width if scale exists", function() {
            if (focus.axes.x.scale) {
                expect(focus.axes.x.scale.range()[1]).toBe(focus.style.dimensions.width)
            }
            else expect(true).toBe(true)
        });

        it("calls redraw with correct extent",function(){
            // Not being called. Works in chrome console
            expect(focus.redraw).toHaveBeenCalledWith([focus.axes.x.min,focus.axes.x.max])
        });
    });

    describe("NHFocus.redraw()",function() {

        var newExtent, graphs;

        beforeEach(function() {

            spyOn(focus, 'redraw').and.callThrough();
            spyOn(pulse_graph, 'redraw').and.callThrough();
            spyOn(bp_graph, 'redraw').and.callThrough();

            graphlib.init();
            graphlib.draw();

            var max = new Date(focus.axes.x.max);
            var min = new Date(max);
            min.setDate(max.getDate() - 5);
            newExtent = [min,max];

            focus.redraw(newExtent);
        });


        it("sets graph x-axis scale domain to new extent",function() {
            expect(bp_graph.axes.x.scale.domain()[0].toString()).toBe(newExtent[0].toString());
            expect(bp_graph.axes.x.scale.domain()[1].toString()).toBe(newExtent[1].toString())
        });

        it("sets graph x-axis ticks to correct value",function() {
            expect(bp_graph.axes.x.axis.ticks()[0]).toBe(focus.style.dimensions.width/100)
        });

        it("sets graph x-axis range to new extent",function() {
            expect(bp_graph.axes.x.scale.range()[1]).toBe(focus.style.dimensions.width - pulse_graph.style.label_width)
        });

        it("calls redraw on all graphs in array",function() {
            expect(pulse_graph.redraw).toHaveBeenCalled();
            expect(bp_graph.redraw).toHaveBeenCalled()
        });

    });

    describe("NHGraph.resize_graph()", function() {

        beforeEach(function() {

            spyOn(pulse_graph, 'redraw').and.callThrough();
            spyOn(NHGraph.prototype, 'resize_graph').and.callThrough();

            graphlib.init();
            graphlib.draw();

            focus.style.dimensions.width = 500;

            var resize_event = document.createEvent('HTMLEvents');
            resize_event.initEvent('graph_resize', true, true);
            pulse_graph.resize_graph(pulse_graph,resize_event)
        });


        it("sets style.dimensions.width to parent object width - padding / margins",function() {
            var actual = pulse_graph.style.dimensions.width;
            var expected = 500
                            - focus.style.padding.left
                            - focus.style.padding.right
                            - pulse_graph.style.margin.left
                            - pulse_graph.style.margin.right
                            - pulse_graph.style.label_width;

            expect(actual).toBe(expected)
        });

        it("sets object width to dimensions.width",function() {
            expect(+pulse_graph.obj.attr('width')).toBe(pulse_graph.style.dimensions.width)
        });

        it("sets x-axis scale range if defined",function() {
            if (pulse_graph.axes.x.scale) {
                expect(pulse_graph.axes.x.scale.range()[1]).toBe(pulse_graph.style.dimensions.width)
            }
            else expect(true).toBe(true)
        });

        it("calls own redraw method",function() {
            // Not being called, works in chrome console. ?why
            expect(pulse_graph.redraw).toHaveBeenCalled()
        });
    });

    describe("Mobile (is_mob)",function() {

        beforeEach(function() {

            graphlib.options.mobile.is_mob = true;
            graphlib.init();
            graphlib.draw();
        });

        describe("is_landscape()", function() {

            it("returns true if screen orientation is landscape",function() {
                window.innerWidth = 800;
                window.innerHeight = 600;
                expect(graphlib.is_landscape()).toBe(1);
            });

            it("returns true if screen orientation is landscape",function() {
                window.innerWidth = 600;
                window.innerHeight = 800;
                expect(graphlib.is_landscape()).toBe(0);
            });

        });


        describe("NHContext.handle_resize()",function() {

            describe("Portrait",function() {

                beforeEach(function() {

                    spyOn(NHGraphLib.prototype, 'is_landscape').and.returnValue(0);

                    var resize_event = document.createEvent('HTMLEvents');
                    resize_event.initEvent('context_resize', true, true);
                    //window.dispatchEvent(resize_event);
                    context.handle_resize(context,context.parent_obj.obj,resize_event)
                });

                it("adjusts x-axis min to max minus 1 day", function() {
                    /*
                        As above - works in isolation (fit) but not with landscape
                        both work in chrome console, ?set-up/tear-down pollution
                     */
                    expect(NHGraphLib.prototype.is_landscape).toHaveBeenCalled();

                    var min = context.graph.axes.x.scale.domain()[0];

                    var expected = new Date(focus.axes.x.max);
                    expected.setDate(expected.getDate() - 1);
                    expect(min.toString()).toBe(expected.toString())
                })
            });

            describe("Landscape",function() {

                beforeEach(function() {

                    spyOn(NHGraphLib.prototype, 'is_landscape').and.returnValue(1);

                    var resize_event = document.createEvent('HTMLEvents');
                    resize_event.initEvent('context_resize', true, true);
                    context.handle_resize(context,context.parent_obj.obj,resize_event)
                });

                it("adjusts x-axis min to max minus 5 days", function() {
                    /*
                        Works in isolation (fit) but not with portrait test
                        both work in chrome console
                    */
                    expect(NHGraphLib.prototype.is_landscape).toHaveBeenCalled();
                    var min = context.graph.axes.x.scale.domain()[0];

                    var expected = new Date(focus.axes.x.max);
                    expected.setDate(expected.getDate() - 5);
                    expect(min.toString()).toBe(expected.toString())
                })
            })
        });

        describe("NHFocus.handle_resize()", function() {

            describe("Landscape",function() {

                beforeEach(function() {
                    spyOn(NHGraphLib.prototype, 'is_landscape').and.returnValue(1);
                    spyOn(focus, 'redraw').and.callThrough();

                    var resize_event = document.createEvent('HTMLEvents');
                    resize_event.initEvent('focus_resize', true, true);
                    focus.handle_resize(focus,focus.parent_obj.obj,resize_event)
                });

                it("sets focus graphs x-axis min to max minus 5 days", function() {

                    expect(NHGraphLib.prototype.is_landscape).toHaveBeenCalled();

                    var min = pulse_graph.axes.x.scale.domain()[0];
                    var expected = new Date(pulse_graph.axes.x.max);
                    expected.setDate(expected.getDate() - 5);

                    expect(min.toString()).toBe(expected.toString());
                });

                it("calls redraw with x-axis min to x-axis max minus 5 days", function() {

                    expect(NHGraphLib.prototype.is_landscape).toHaveBeenCalled();

                    var max = new Date(focus.axes.x.max);
                    var min = new Date(max);
                    min.setDate(max.getDate() - graphlib.options.mobile.date_range.landscape);

                    expect(focus.redraw).toHaveBeenCalledWith([min,max]);
                });
            });

            describe("Portrait",function() {

                beforeEach(function() {

                    spyOn(NHGraphLib.prototype, 'is_landscape').and.returnValue(0);

                    var resize_event = document.createEvent('HTMLEvents');
                    resize_event.initEvent('focus_resize', true, true);
                    focus.handle_resize(focus,focus.parent_obj.obj,resize_event)
                });

                it("calls redraw with x-axis min to max minus 1 day", function() {

                    expect(NHGraphLib.prototype.is_landscape).toHaveBeenCalled()

                    var min = pulse_graph.axes.x.scale.domain()[0];
                    var expected = new Date(pulse_graph.axes.x.max);
                    expected.setDate(expected.getDate() - 1);

                    expect(min.toString()).toBe(expected.toString());
                });
            });
        });
    });
});


