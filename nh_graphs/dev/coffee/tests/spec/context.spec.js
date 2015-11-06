
/*
  Created by Jon Wyatt on 25/10/15

  'Context' suite covers nhgraphlib_context and nhgraphlib_focus
  and includes mobile date / time input changes in nhgraphlib
 */

describe('Context', function() {
  var context, focus, graphlib, mousedown, pulse_graph, score_graph, test_area, touchstart;
  graphlib = null;
  pulse_graph = null;
  score_graph = null;
  context = null;
  focus = null;
  test_area = null;

  mousedown = function(el) {
    var ev;
    ev = document.createEvent('MouseEvent');
    ev.initMouseEvent('mousedown', true, true, window, null, 0, 0, 0, 0, false, false, false, false, 0, null);
    el.dispatchEvent(ev);
  };

  touchstart = function(el) {
    var ev;
    ev = document.createEvent('MouseEvent');
    ev.initMouseEvent('touchstart', true, true, window, null, 50, 0, 50, 0, false, false, false, false, 0, null);
    el.dispatchEvent(ev);
  };

  beforeEach(function() {
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
                pop = pops[i];
                pop.parentNode.removeChild(pop);
            }
        }

        var tests = document.querySelectorAll('#test_area');
        if (tests.length > 0) {
            for (var j = 0, len1 = tests.length; j < len1; j++) {
                test = tests[j];
                test.parentNode.removeChild(test);
            }
        }
    });

  describe("Properties", function() {
    it("nhgraphlib has properties for data range covered", function() {
      expect(graphlib.data.extent.start).toBeDefined();
      expect(graphlib.data.extent.end).toBeDefined();
    });
    it("nhgraphlib has pointer to context object", function() {
      expect(graphlib.context).toBeDefined();
    });
    it("nhgraphlib has pointer to focus object", function() {
      expect(graphlib.focus).toBeDefined();
    });
    it("NHContext has graph object property", function() {
      expect(context.graph).toBeDefined();
    });
    it("NHContext has pointer to parent nhgraphlib object", function() {
      expect(context.parent_obj).toBeDefined();
    });
    it("NHContext has brush object property", function() {
      expect(context.brush).toBeDefined();
    });
  });
  describe("Methods", function() {
    beforeEach(function() {
      spyOn(context, 'init').and.callThrough();
      spyOn(context.graph, 'init').and.callThrough();
      spyOn(context.graph, 'draw').and.callThrough();
    });

    describe("nhcontext.init()", function() {
      it("errors if called before parent object", function() {
        var err;
        err = new Error('Context init being called before SVG initialised');
        expect(function() {
          context.init();
        }).toThrow(err);
      });
      it("is defined", function() {
        expect(context.init).toBeDefined();
      });
      it("is called when parent object init() is called", function() {
        graphlib.init();
        expect(context.init).toHaveBeenCalled();
      });
      it("adds title if defined", function() {
        var titles;
        context.title = "Hello";
        graphlib.init();
        titles = document.querySelectorAll('#test_area svg .title');
        expect(titles.length).toBe(2);
        expect(titles[0].textContent).toBe('Hello');
      });
      it("doesn't add title if not defined", function() {
        var titles;
        context.title = null;
        graphlib.init();
        titles = document.querySelectorAll('#test_area svg .title');
        expect(titles.length).toBe(1);
      });
      it("adds single context group element with class of nhcontext", function() {
        var contexts;
        graphlib.init();
        contexts = document.querySelectorAll('.nhcontext');
        expect(contexts.length).toBe(1);
      });
      it("uses offsets of parent object and title height to position g correctly", function() {
        var contexts, trans;
        graphlib.init();
        contexts = document.querySelectorAll('.nhcontext');
        trans = contexts[0].getAttribute('transform');
        expect(trans).toBe('translate(40,140)');
      });
      it("uses offsets of parent object to position g correctly", function() {
        var contexts, trans;
        context.title = null;
        graphlib.init();
        contexts = document.querySelectorAll('.nhcontext');
        trans = contexts[0].getAttribute('transform');
        expect(trans).toBe('translate(40,60)');
      });
      it("calculates dimensions for nhcontext and applies to g", function() {
        var contexts, width;
        width = context.style.dimensions.width;
        expect(width).toBe(0);
        graphlib.init();
        width = context.style.dimensions.width;
        expect(width).toBeGreaterThan(0);
        contexts = document.querySelectorAll('.nhcontext');
        expect(+contexts[0].getAttribute('width')).toBe(width);
      });
      it("sets up x axis based on parent (nhgraphlib) extent", function() {
        var parentEnd, parentStart;
        graphlib.init();
        parentStart = context.parent_obj.data.extent.start;
        parentEnd = context.parent_obj.data.extent.end;
        expect(context.axes.x.min).toBe(parentStart);
        expect(context.axes.x.max).toBe(parentEnd);
      });
      it("initialises context graph", function() {
        graphlib.init();
        expect(context.graph.init).toHaveBeenCalled();
      });
      it("adds brush-container element to graph", function() {
        var brushes;
        brushes = document.querySelectorAll('.nhcontext .brush-container');
        expect(brushes.length).toBe(0);
        graphlib.init();
        brushes = document.querySelectorAll('.nhcontext .brush-container');
        expect(brushes.length).toBe(1);
      });
      it("adds x brush element within brush container", function() {
        var xbrushes;
        xbrushes = document.querySelectorAll('.nhcontext .x.brush');
        expect(xbrushes.length).toBe(0);
        graphlib.init();
        xbrushes = document.querySelectorAll('.nhcontext .x.brush');
        expect(xbrushes.length).toBe(1);
      });
    });
    describe("draw()", function() {
      it("draws the context graph assigned to object", function() {
        graphlib.init();
        context.draw();
        expect(context.graph.draw).toHaveBeenCalled();
      });
    });
    describe("handle_brush()", function() {
      beforeEach(function() {
        spyOn(context, 'handle_brush').and.callThrough();
        spyOn(focus, 'redraw').and.callThrough();
      });
      it("has a handle_brush method to update focus and controls", function() {
        expect(context.handle_brush).toBeDefined();
      });
      it("is called when brush clicked", function() {
        var xbrushes;
        graphlib.init();
        xbrushes = document.querySelectorAll('.nhcontext .x.brush');
        mousedown(xbrushes[0]);
        expect(context.handle_brush).toHaveBeenCalled();
      });
      it("is called on 'tochstart'", function() {
        var xbrushes;
        graphlib.init();
        xbrushes = document.querySelectorAll('.nhcontext .x.brush');
        mousedown(xbrushes[0]);
        expect(context.handle_brush).toHaveBeenCalled();
      });
      it("calls focus.redraw with context min/max when brush extent is zero", function() {
        var conMax, conMin, extents, xbrushes;
        graphlib.init();
        graphlib.draw();
        xbrushes = document.querySelectorAll('.nhcontext .x.brush');
        extents = document.querySelectorAll('.nhcontext .x.brush .extent');
        extents[0].setAttribute('width', '0');
        touchstart(xbrushes[0]);
        expect(context.handle_brush).toHaveBeenCalled();
        conMin = context.axes.x.min;
        conMax = context.axes.x.max;
        expect(focus.redraw).toHaveBeenCalledWith([conMin, conMax]);
      });
      describe("Mobile", function() {
        beforeEach(function() {
          var inp;
          inp = document.createElement('input');
          inp.setAttribute('type', 'date');
          test_area.appendChild(inp);
          graphlib.options.controls.date.start = inp;
          inp = document.createElement('input');
          inp.setAttribute('type', 'time');
          test_area.appendChild(inp);
          graphlib.options.controls.time.start = inp;
          inp = document.createElement('input');
          inp.setAttribute('type', 'date');
          test_area.appendChild(inp);
          graphlib.options.controls.date.end = inp;
          inp = document.createElement('input');
          inp.setAttribute('type', 'time');
          test_area.appendChild(inp);
          graphlib.options.controls.time.end = inp;
        });
        describe("Inputs", function() {
          beforeEach(function() {
            var extents, xbrushes;
            graphlib.init();
            graphlib.draw();
            xbrushes = document.querySelectorAll('.nhcontext .x.brush');
            extents = document.querySelectorAll('.nhcontext .x.brush .extent');
            extents[0].setAttribute('width', '0');
            touchstart(xbrushes[0]);
          });
          it("updates start date input with new date", function() {
            var actual, expected;
            actual = new Date(graphlib.options.controls.date.start.value);
            expected = new Date(context.axes.x.min);
            actual = actual.toString().substr(0, 16);
            expected = expected.toString().substr(0, 16);
            expect(actual).toBe(expected);
          });
          it("updates start time input with new time", function() {
            var actual, conMin, expected;
            actual = graphlib.options.controls.time.start.value;
            conMin = new Date(context.axes.x.min);
            expected = conMin.getHours();
            expected += ':';
            expected += conMin.getMinutes();
            expect(actual).toBe(expected);
          });
          it("updates end date input with new date", function() {
            var actual, expected;
            actual = new Date(graphlib.options.controls.date.end.value);
            expected = new Date(context.axes.x.max);
            actual = actual.toString().substr(0, 16);
            expected = expected.toString().substr(0, 16);
            expect(actual).toBe(expected);
          });
          it("updates end time input with new time", function() {
            var actual, conMin, expected;
            actual = graphlib.options.controls.time.end.value;
            conMin = new Date(context.axes.x.max);
            expected = conMin.getHours();
            expected += ':';
            expected += conMin.getMinutes();
            expect(actual).toBe(expected);
          });
        });
      });
    });
  });
  describe("Mobile Inputs", function() {
    var changeEvent;
    changeEvent = null;

    beforeEach(function() {
      var inp;
      spyOn(graphlib, 'mobile_date_start_change').and.callThrough();
      spyOn(graphlib, 'mobile_date_end_change').and.callThrough();
      spyOn(graphlib, 'mobile_time_start_change').and.callThrough();
      spyOn(graphlib, 'mobile_time_end_change').and.callThrough();

      inp = document.createElement('input');
      inp.setAttribute('type', 'date');
      test_area.appendChild(inp);
      graphlib.options.controls.date.start = inp;
      inp = document.createElement('input');
      inp.setAttribute('type', 'time');
      test_area.appendChild(inp);
      graphlib.options.controls.time.start = inp;
      inp = document.createElement('input');
      inp.setAttribute('type', 'date');
      test_area.appendChild(inp);
      graphlib.options.controls.date.end = inp;
      inp = document.createElement('input');
      inp.setAttribute('type', 'time');
      test_area.appendChild(inp);
      graphlib.options.controls.time.end = inp;

      graphlib.init();
      graphlib.draw();
      graphlib.options.mobile.is_mob = true;
      changeEvent = document.createEvent('Event');
      changeEvent.initEvent('change', true, true);
    });

    it("nhgraphlib.init() adds event listeners to inputs if present", function() {
      graphlib.options.controls.date.start.dispatchEvent(changeEvent);
      graphlib.options.controls.date.end.dispatchEvent(changeEvent);
      graphlib.options.controls.time.start.dispatchEvent(changeEvent);
      graphlib.options.controls.time.end.dispatchEvent(changeEvent);
      expect(graphlib.mobile_date_start_change).toHaveBeenCalled();
      expect(graphlib.mobile_time_start_change).toHaveBeenCalled();
      expect(graphlib.mobile_date_end_change).toHaveBeenCalled();
      expect(graphlib.mobile_time_end_change).toHaveBeenCalled();
    });
  });
});
