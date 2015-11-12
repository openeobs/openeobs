
/*
  Created by Jon Wyatt on 18/10/15
 */

describe('Pop-Ups', function() {

  var bp_graph, focus, graphlib, mouseout, mouseover, pulse_graph, test_area;
  graphlib = null;
  pulse_graph = null;
  bp_graph = null;
  focus = null;
  test_area = null;

  mouseover = function(el) {
    var ev;

    if (el.dispatchEvent) {
      try {
        // Chrome, Firefox, Safari
        ev = new MouseEvent('mouseover', {bubbles: true, cancelable: true});
      }
      catch (e) {
        // PhantomJS
        ev = document.createEvent('MouseEvent');
        ev.initMouseEvent('mouseover', true, true, window, null, 0, 0, 0, 0, false, false, false, false, 0, null);
      }
      el.dispatchEvent(ev);
    }
    else {
      // IE
      ev = document.createEventObject('MouseEvent')
      el.fireEvent('mouseover', ev)
    }
  };

  mouseout = function(el) {
    var ev;

    if (el.dispatchEvent) {
      try {
        // Chrome, Firefox, Safari
        ev = new MouseEvent('mouseout', {bubbles: true, cancelable: true});
      }
      catch (e) {
        // PhantomJS
        ev = document.createEvent('MouseEvent');
        ev.initMouseEvent('mouseout', true, true, window, null, 0, 0, 0, 0, false, false, false, false, 0, null);
      }
      el.dispatchEvent(ev);
    }
    else {
      // IE
      ev = document.createEventObject('MouseEvent')
      el.fireEvent('mouseout', ev)
    }
  };


  beforeEach(function() {

    var body_el, keys;
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

    keys = ['blood_pressure_systolic', 'blood_pressure_diastolic'];
    bp_graph.options.keys = keys;
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

    focus.graphs.push(pulse_graph);
    focus.graphs.push(bp_graph);
    focus.title = 'Individual values';
    focus.style.padding.right = 0;
    focus.style.margin.top = 0;
    focus.style.padding.top = 0;

    graphlib.focus = focus;
    graphlib.data.raw = ews_data.multi_partial;
  });

  afterEach(function() {
    var i, j, len, len1, pop, pops, test, tests;

    if (graphlib !== null) {
      graphlib = null;
    }
    if (pulse_graph !== null) {
      pulse_graph = null;
    }
    if (bp_graph !== null) {
      bp_graph = null;
    }
    if (focus !== null) {
      focus = null;
    }

    if (test_area !== null) {
      test_area.parentNode.removeChild(test_area);
      test_area = null;
    }
    pops = document.querySelectorAll('#chart_popup');
    if (pops.length > 0) {
      for (i = 0, len = pops.length; i < len; i++) {
        pop = pops[i];
        pop.parentNode.removeChild(pop);
      }
    }
    tests = document.querySelectorAll('#test_area');
    if (tests.length > 0) {
      for (j = 0, len1 = tests.length; j < len1; j++) {
        test = tests[j];
        test.parentNode.removeChild(test);
      }
    }
  });

  describe("Methods", function() {

    beforeEach(function() {
      graphlib.init();
      graphlib.draw();
    });

    it("nh-graphlib_graph has pop-up methods", function() {
      expect(typeof bp_graph.show_popup).toBe('function');
      expect(typeof bp_graph.hide_popup).toBe('function');
    });

    it("show popup works as expected", function() {
      var pop, popLeft, popText, popTop;
      pulse_graph.show_popup('Hello', 42, 69);
      pop = document.getElementById('chart_popup');
      popLeft = pop.style.left;
      popTop = pop.style.top;
      popText = pop.innerHTML;
      expect(popLeft).toBe('42px');
      expect(popTop).toBe('69px');
      expect(popText).toBe('Hello');
    });

    it("hide popup works as expected", function() {
      var pop, popClass;
      pulse_graph.hide_popup();
      pop = document.getElementById('chart_popup');
      popClass = pop.classList;
      expect(popClass[0]).toBe('hidden');
    });
  });

  describe("Event listeners", function() {

    var points, ranges;
    points = null;
    ranges = null;

    beforeEach(function() {

      spyOn(NHGraph.prototype, 'show_popup').and.callThrough();
      spyOn(NHGraph.prototype, 'hide_popup').and.callThrough();

      graphlib.init();
      graphlib.draw();
    });

    describe("Linear / Stepped Points", function() {

      beforeEach(function() {
        points = document.querySelectorAll('.point');
      });

      it("mouse over event calls show_popup method on all points", function() {
        var c, i, len, point;
        expect(points.length).toBeGreaterThan(0);
        for (i = 0, len = points.length; i < len; i++) {
          point = points[i];
          mouseover(point);
        }
        c = NHGraph.prototype.show_popup.calls.count();
        expect(c).toBe(points.length);
      });

      it("mouse out event calls hide_popup method on all points", function() {
        var c, i, len, point;
        expect(points.length).toBeGreaterThan(0);
        for (i = 0, len = points.length; i < len; i++) {
          point = points[i];
          mouseout(point);
        }
        c = NHGraph.prototype.hide_popup.calls.count();
        expect(c).toBe(points.length);
      });
    });

    describe("Linear / Stepped Empty Points", function() {

      beforeEach(function() {
        points = document.querySelectorAll('.empty_point');
      });

      it("mouse over event calls show_popup method on all empty points", function() {
        var c, i, len, point;
        expect(points.length).toBeGreaterThan(1);
        for (i = 0, len = points.length; i < len; i++) {
          point = points[i];
          mouseover(point);
        }
        c = NHGraph.prototype.show_popup.calls.count();
        expect(c).toBe(points.length);
      });

      it("mouse out event calls hide_popup method on all empty points", function() {
        var c, i, len, point;
        expect(points.length).toBeGreaterThan(1);
        for (i = 0, len = points.length; i < len; i++) {
          point = points[i];
          mouseout(point);
        }
        c = NHGraph.prototype.hide_popup.calls.count();
        expect(c).toBe(points.length);
      });
    });

    describe("Range Bars", function() {

      beforeEach(function() {
        ranges = document.querySelectorAll('.data .range');
      });

      it("mouseover event calls show_popup method on all range elements", function() {
        var c, i, len, range;
        expect(ranges.length).toBeGreaterThan(1);
        for (i = 0, len = ranges.length; i < len; i++) {
          range = ranges[i];
          mouseover(range);
        }
        c = NHGraph.prototype.show_popup.calls.count();
        expect(c).toBe(ranges.length);
      });

      it("mouseout event calls hide_popup method on all range elements", function() {
        var c, i, len, range;
        expect(ranges.length).toBeGreaterThan(1);
        for (i = 0, len = ranges.length; i < len; i++) {
          range = ranges[i];
          mouseout(range);
        }
        c = NHGraph.prototype.hide_popup.calls.count();
        expect(c).toBe(ranges.length);
      });

    });
  });
});
