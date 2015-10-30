
/*
  Created by Jon Wyatt on 18/10/15
 */
describe('Rangify', function() {
  var bp_graph, click, focus, graphlib, pulse_graph, rangify, test_area;
  graphlib = null;
  pulse_graph = null;
  bp_graph = null;
  focus = null;
  test_area = null;
  rangify = null;
  click = function(el) {
    var ev;
    ev = document.createEvent('MouseEvent');
    ev.initMouseEvent('click', true, true, window, null, 0, 0, 0, 0, false, false, false, false, 0, null);
    el.dispatchEvent(ev);
  };

  beforeEach(function() {
    var body_el, keys;
    body_el = document.getElementsByTagName('body')[0];
    test_area = document.createElement('div');
    test_area.setAttribute('id', 'test_area');
    test_area.style.width = '500px';
    rangify = document.createElement('input');
    rangify.setAttribute('id', 'rangify');
    rangify.setAttribute('type', 'checkbox');
    test_area.appendChild(rangify);
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
    graphlib.options.controls.rangify = rangify;
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
    if (rangify !== null) {
      rangify = null;
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

  describe("Properties", function() {
    beforeEach(function() {
      graphlib.init();
    });
    it("nhgraphlib.graph has ranged_extent property", function() {
      expect(bp_graph.axes.y.ranged_extent).toBeDefined();
    });
    it("nhgraphlib.graph initialises range_extent with correct range", function() {
      expect(bp_graph.axes.y.ranged_extent[1]).toBe(120);
    });
    it("nhgraphlib.graph has rangify method", function() {
      expect(bp_graph.rangify_graph).toBeDefined();
    });
    it("nhgraphlib has link to rangify checkbox element", function() {
      expect(graphlib.options.controls.rangify).toBeDefined();
    });
  });

  describe("Events", function() {
    var graphs;
    graphs = null;

    beforeEach(function() {
      spyOn(bp_graph, 'redraw').and.callThrough();
      spyOn(bp_graph, 'rangify_graph').and.callThrough();
      spyOn(pulse_graph, 'redraw').and.callThrough();
      spyOn(pulse_graph, 'rangify_graph').and.callThrough();

      graphs = [bp_graph, pulse_graph];
      graphlib.init();
      graphlib.draw();
    });

    describe("Check", function() {
      it("calls rangify method on all graphs when checkbox clicked", function() {
        var count;
        click(rangify);
        count = bp_graph.rangify_graph.calls.count();
        count += pulse_graph.rangify_graph.calls.count();
        expect(count).toBe(2);
      });

      it("calls redraw method on all graphs", function() {
        var count;
        click(rangify);
        count = bp_graph.redraw.calls.count();
        count += pulse_graph.redraw.calls.count();
        expect(count).toBe(2);
      });

      it("switches axes to ranged min/max", function() {
        var expectedMax, expectedMin, graph, i, j, k, len, len1, len2, max, min, padding, tick, ticks, val;
        click(rangify);
        for (i = 0, len = graphs.length; i < len; i++) {
          graph = graphs[i];
          padding = graph.style.range_padding;
          expectedMin = graph.axes.y.ranged_extent[0] - padding;
          expectedMax = graph.axes.y.ranged_extent[1] + padding;
          ticks = graph.axes.obj[0][0].querySelectorAll('.tick text');
          expect(ticks.length).toBeGreaterThan(2);
          min = 300;
          for (j = 0, len1 = ticks.length; j < len1; j++) {
            tick = ticks[j];
            if (tick.textContent !== '') {
              val = +tick.textContent;
              if (val < min) {
                min = val;
              }
            }
          }
          expect(min).toBeGreaterThan(expectedMin - 2);
          max = 0;
          for (k = 0, len2 = ticks.length; k < len2; k++) {
            tick = ticks[k];
            if (tick.textContent !== '') {
              val = +tick.textContent;
              if (val > max) {
                max = val;
              }
            }
          }
          expect(max).toBeLessThan(expectedMax + 2);
        }
      });
    });

    describe("Uncheck", function() {

      beforeEach(function() {
        rangify.checked = true;
      });

      it("calls rangify method on all graphs when checkbox clicked", function() {
        var count;
        click(rangify);
        count = bp_graph.rangify_graph.calls.count();
        count += pulse_graph.rangify_graph.calls.count();
        expect(count).toBe(2);
      });

      it("calls redraw method on all graphs", function() {
        var count;
        click(rangify);
        count = bp_graph.redraw.calls.count();
        count += pulse_graph.redraw.calls.count();
        expect(count).toBe(2);
      });

      it("switches axes back to initial min/max on all graphs", function() {
        var expectedMax, expectedMin, i, j, len, len1, max, min, tick, ticks, val;
        click(rangify);
        expectedMin = pulse_graph.axes.y.min;
        expectedMax = pulse_graph.axes.y.max;
        ticks = pulse_graph.axes.obj[0][0].querySelectorAll('.tick text');

        expect(ticks.length).toBeGreaterThan(2);

        min = 300;
        for (i = 0, len = ticks.length; i < len; i++) {
          tick = ticks[i];
          if (tick.textContent !== '') {
            val = +tick.textContent;
            if (val < min) {
              min = val;
            }
          }
        }
        expect(min).toBe(expectedMin);

        max = 0;
        for (j = 0, len1 = ticks.length; j < len1; j++) {
          tick = ticks[j];
          if (tick.textContent !== '') {
            val = +tick.textContent;
            if (val > max) {
              max = val;
            }
          }
        }
        expect(max).toBe(expectedMax);
      });
    });
  });
});
