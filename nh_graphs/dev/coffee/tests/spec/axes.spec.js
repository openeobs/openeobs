
/*
  Created by Jon Wyatt on 13/10/15 (copied from Colin Wren 29/06/15).
 */
describe('Axes', function() {
  var context, focus, graph, graphlib, test_area;
  graphlib = null;
  graph = null;
  context = null;
  focus = null;
  test_area = null;
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
    if (graph === null) {
      graph = new NHGraph();
    }
    if (context === null) {
      context = new NHContext();
    }
    if (focus === null) {
      focus = new NHFocus();
    }
    graph.options.keys = ['respiration_rate'];
    graph.options.label = 'RR';
    graph.options.measurement = '/min';
    graph.axes.y.min = 0;
    graph.axes.y.max = 60;
    graph.options.normal.min = 12;
    graph.options.normal.max = 20;
    graph.style.dimensions.height = 250;
    graph.style.data_style = 'linear';
    graph.style.label_width = 60;
    focus.graphs.push(graph);
    graphlib.focus = focus;
    return graphlib.data.raw = ews_data.single_record;
  });
  afterEach(function() {
    if (graphlib !== null) {
      graphlib = null;
    }
    if (graph !== null) {
      graph = null;
    }
    if (context !== null) {
      context = null;
    }
    if (focus !== null) {
      focus = null;
    }
    if (test_area !== null) {
      return test_area.parentNode.removeChild(test_area);
    }
  });
  describe("NHGraphLib, NHContext, NHFocus, NHGraph axes properties", function() {
    it('NHGraphLib has properties for setting the axis label height', function() {
      return expect(graphlib.style.hasOwnProperty('axis_label_text_height')).toBe(true);
    });
    it('NHContext has axes property that holds information for X and Y axes', function() {
      expect(context.hasOwnProperty('axes')).toBe(true);
      expect(context.axes.hasOwnProperty('x')).toBe(true);
      expect(context.axes.hasOwnProperty('y')).toBe(true);
      expect(context.axes.x.hasOwnProperty('scale')).toBe(true);
      expect(context.axes.x.hasOwnProperty('axis')).toBe(true);
      expect(context.axes.x.hasOwnProperty('min')).toBe(true);
      expect(context.axes.x.hasOwnProperty('max')).toBe(true);
      expect(context.axes.y.hasOwnProperty('scale')).toBe(true);
      expect(context.axes.y.hasOwnProperty('axis')).toBe(true);
      expect(context.axes.y.hasOwnProperty('min')).toBe(true);
      return expect(context.axes.y.hasOwnProperty('max')).toBe(true);
    });
    it('NHFocus has axes property that holds information for X and Y axes', function() {
      expect(focus.hasOwnProperty('axes')).toBe(true);
      expect(focus.axes.hasOwnProperty('x')).toBe(true);
      expect(focus.axes.hasOwnProperty('y')).toBe(true);
      expect(focus.axes.x.hasOwnProperty('scale')).toBe(true);
      expect(focus.axes.x.hasOwnProperty('axis')).toBe(true);
      expect(focus.axes.x.hasOwnProperty('min')).toBe(true);
      expect(focus.axes.x.hasOwnProperty('max')).toBe(true);
      expect(focus.axes.y.hasOwnProperty('scale')).toBe(true);
      expect(focus.axes.y.hasOwnProperty('axis')).toBe(true);
      expect(focus.axes.y.hasOwnProperty('min')).toBe(true);
      return expect(focus.axes.y.hasOwnProperty('max')).toBe(true);
    });
    it('NHGraph has axes property that holds information for X and Y axes', function() {
      expect(graph.hasOwnProperty('axes')).toBe(true);
      expect(graph.axes.hasOwnProperty('x')).toBe(true);
      expect(graph.axes.hasOwnProperty('y')).toBe(true);
      expect(graph.axes.hasOwnProperty('obj')).toBe(true);
      expect(graph.axes.x.hasOwnProperty('scale')).toBe(true);
      expect(graph.axes.x.hasOwnProperty('axis')).toBe(true);
      expect(graph.axes.x.hasOwnProperty('min')).toBe(true);
      expect(graph.axes.x.hasOwnProperty('max')).toBe(true);
      expect(graph.axes.x.hasOwnProperty('obj')).toBe(true);
      expect(graph.axes.y.hasOwnProperty('scale')).toBe(true);
      expect(graph.axes.y.hasOwnProperty('axis')).toBe(true);
      expect(graph.axes.y.hasOwnProperty('min')).toBe(true);
      expect(graph.axes.y.hasOwnProperty('max')).toBe(true);
      expect(graph.axes.y.hasOwnProperty('obj')).toBe(true);
      return expect(graph.axes.y.hasOwnProperty('ranged_extent')).toBe(true);
    });
    return it('NHGraph has styling properties for X and Y axes', function() {
      expect(graph.style.hasOwnProperty('axis')).toBe(true);
      expect(graph.style.hasOwnProperty('axis_label_text_height')).toBe(true);
      expect(graph.style.hasOwnProperty('axis_label_text_padding')).toBe(true);
      expect(graph.style.axis.hasOwnProperty('x')).toBe(true);
      expect(graph.style.axis.hasOwnProperty('y')).toBe(true);
      expect(graph.style.axis.x.hasOwnProperty('hide')).toBe(true);
      expect(graph.style.axis.y.hasOwnProperty('hide')).toBe(true);
      expect(graph.style.axis.x.hasOwnProperty('size')).toBe(true);
      return expect(graph.style.axis.y.hasOwnProperty('size')).toBe(true);
    });
  });
  describe("Structure", function() {
    beforeEach(function() {
      graphlib.init();
      return graphlib.draw();
    });
    return it("Creates a DOM structure for the axis which is easy to understand", function() {
      var focus_el, focus_els, graph_el, graph_els, x_el, x_els, y_el, y_els;
      focus_els = document.getElementsByClassName('nhfocus');
      expect(focus_els.length).toBe(1);
      focus_el = focus_els[0];
      graph_els = focus_el.getElementsByClassName('nhgraph');
      expect(graph_els.length).toBe(1);
      graph_el = graph_els[0];
      x_els = graph_el.getElementsByClassName('x');
      expect(x_els.length).toBe(1);
      x_el = x_els[0];
      expect(x_el.getAttribute('class')).toBe('x axis');
      y_els = graph_el.getElementsByClassName('y');
      expect(y_els.length).toBe(1);
      y_el = y_els[0];
      return expect(y_el.getAttribute('class')).toBe('y axis');
    });
  });
  describe('X-Axis', function() {
    describe("Visibility", function() {
      it("is visible by default", function() {
        graphlib.init();
        return expect(document.querySelectorAll('.x').length).toBe(1);
      });
      return it("can be hidden", function() {
        graph.style.axis.x.hide = true;
        graphlib.init();
        return expect(document.querySelectorAll('.x').length).toBe(0);
      });
    });
    describe('Scale', function() {
      it('Adds time padding of 100 to the scale when plotting a single data point and no time padding defined', function() {
        var data_point, end, start;
        data_point = graphlib.date_from_string(graphlib.data.raw[0]['date_terminated']);
        graphlib.init();
        expect(graphlib.style.time_padding).toBe(100);
        start = new Date(data_point);
        end = new Date(data_point);
        start.setMinutes(start.getMinutes() - 100);
        end.setMinutes(end.getMinutes() + 100);
        expect(graphlib.date_to_string(graphlib.data.extent.start)).toBe(graphlib.date_to_string(start));
        return expect(graphlib.date_to_string(graphlib.data.extent.end)).toBe(graphlib.date_to_string(end));
      });
      it('Adds time padding of 3 to the scale when plotting a single data point and time padding of 3 is defined', function() {
        var data_point, end, start;
        data_point = graphlib.date_from_string(graphlib.data.raw[0]['date_terminated']);
        graphlib.style.time_padding = 3;
        graphlib.init();
        expect(graphlib.style.time_padding).toBe(3);
        start = new Date(data_point);
        end = new Date(data_point);
        start.setMinutes(start.getMinutes() - 3);
        end.setMinutes(end.getMinutes() + 3);
        expect(graphlib.date_to_string(graphlib.data.extent.start)).toBe(graphlib.date_to_string(start));
        return expect(graphlib.date_to_string(graphlib.data.extent.end)).toBe(graphlib.date_to_string(end));
      });
      it('Adds time padding of date difference divided by SVG width divided by 500 to the scale when plotting multiple data points and no time padding defined', function() {
        var end, original_extent, start;
        graphlib.data.raw = ews_data.multiple_records;
        original_extent = [graphlib.date_from_string(graphlib.data.raw[0]['date_terminated']), graphlib.date_from_string(graphlib.data.raw[1]['date_terminated'])];
        graphlib.init();
        expect(graphlib.style.time_padding).toBe(14.4);
        start = new Date(original_extent[0]);
        end = new Date(original_extent[1]);
        start.setMinutes(start.getMinutes() - 14.4);
        end.setMinutes(end.getMinutes() + 14.4);
        expect(graphlib.date_to_string(graphlib.data.extent.start)).toBe(graphlib.date_to_string(start));
        return expect(graphlib.date_to_string(graphlib.data.extent.end)).toBe(graphlib.date_to_string(end));
      });
      return it('Adds time padding of 3 to the scale when plotting multiple data points when time padding of 3 is defined', function() {
        var end, original_extent, start;
        graphlib.data.raw = ews_data.multiple_records;
        original_extent = [graphlib.date_from_string(graphlib.data.raw[0]['date_terminated']), graphlib.date_from_string(graphlib.data.raw[1]['date_terminated'])];
        graphlib.style.time_padding = 3;
        graphlib.init();
        expect(graphlib.style.time_padding).toBe(3);
        start = new Date(original_extent[0]);
        end = new Date(original_extent[1]);
        start.setMinutes(start.getMinutes() - 3);
        end.setMinutes(end.getMinutes() + 3);
        expect(graphlib.date_to_string(graphlib.data.extent.start)).toBe(graphlib.date_to_string(start));
        return expect(graphlib.date_to_string(graphlib.data.extent.end)).toBe(graphlib.date_to_string(end));
      });
    });
    return describe('Ticks', function() {
      it("has sensible amount", function() {
        var x_ticks;
        graphlib.init();
        graphlib.draw();
        x_ticks = document.querySelectorAll('.x .tick');
        expect(x_ticks.length).toBeLessThan(10);
        return expect(x_ticks.length).toBeGreaterThan(2);
      });
      it("are evenly spaced", function() {
        var i, j, k, lastGap, len, ref, results, tick, xPos, x_ticks;
        graphlib.init();
        graphlib.draw();
        x_ticks = document.querySelectorAll('.x .tick');
        xPos = [];
        for (j = 0, len = x_ticks.length; j < len; j++) {
          tick = x_ticks[j];
          xPos.push(+(tick.getAttribute('transform').substr(10, 5)));
        }
        lastGap = null;
        results = [];
        for (i = k = 1, ref = xPos.length - 1; 1 <= ref ? k <= ref : k >= ref; i = 1 <= ref ? ++k : --k) {
          if (lastGap !== null) {
            expect(Math.round(xPos[i] - xPos[i - 1])).toBe(lastGap);
          }
          results.push(lastGap = Math.round(xPos[i] - xPos[i - 1]));
        }
        return results;
      });
      return describe('Labels', function() {
        it("use default size if no size defined", function() {
          var j, len, results, tick, tspans, x_ticks;
          graphlib.init();
          graphlib.draw();
          x_ticks = document.querySelectorAll('.x .tick');
          results = [];
          for (j = 0, len = x_ticks.length; j < len; j++) {
            tick = x_ticks[j];
            tspans = tick.getElementsByTagName('tspan');
            expect(tspans.length).toBe(3);
            expect(tspans[0].getAttribute('x')).toBe(null);
            expect(tspans[0].getAttribute('dy')).toBe(null);
            expect(tspans[0].getAttribute('style')).toBe('font-size: 12px;');
            expect(tspans[1].getAttribute('x')).toBe('0');
            expect(tspans[1].getAttribute('dy')).toBe('14');
            expect(tspans[1].getAttribute('style')).toBe('font-size: 12px;');
            expect(tspans[2].getAttribute('x')).toBe('0');
            expect(tspans[2].getAttribute('dy')).toBe('14');
            results.push(expect(tspans[2].getAttribute('style')).toBe('font-size: 12px;'));
          }
          return results;
        });
        it("use defined size if provided", function() {
          var j, len, results, text_el, tick, tspans, x_ticks;
          graph.style.axis_label_font_size = 30;
          graph.style.axis_label_line_height = 2;
          graphlib.init();
          graphlib.draw();
          x_ticks = document.querySelectorAll('.x .tick');
          results = [];
          for (j = 0, len = x_ticks.length; j < len; j++) {
            tick = x_ticks[j];
            text_el = tick.getElementsByTagName('text');
            expect(text_el.length).toBe(1);
            expect(text_el[0].getAttribute('y')).toBe('-150');
            tspans = tick.getElementsByTagName('tspan');
            expect(tspans.length).toBe(3);
            expect(tspans[0].getAttribute('x')).toBe(null);
            expect(tspans[0].getAttribute('dy')).toBe(null);
            expect(tspans[0].getAttribute('style')).toBe('font-size: 30px;');
            expect(tspans[1].getAttribute('x')).toBe('0');
            expect(tspans[1].getAttribute('dy')).toBe('60');
            expect(tspans[1].getAttribute('style')).toBe('font-size: 30px;');
            expect(tspans[2].getAttribute('x')).toBe('0');
            expect(tspans[2].getAttribute('dy')).toBe('60');
            results.push(expect(tspans[2].getAttribute('style')).toBe('font-size: 30px;'));
          }
          return results;
        });
        return it("have sensible text values for day / date/ time", function() {
          var date_re, day_re, j, len, results, tick, time_re, tspans, x_ticks;
          graphlib.init();
          graphlib.draw();
          x_ticks = document.querySelectorAll('.x .tick');
          day_re = new RegExp('[MTWFS][a-z][a-z]');
          date_re = new RegExp('[0-9]?[0-9]/[0-9]?[0-9]/[0-9]?[0-9]');
          time_re = new RegExp('[0-2]?[0-9]:[0-5]?[0-9]');
          results = [];
          for (j = 0, len = x_ticks.length; j < len; j++) {
            tick = x_ticks[j];
            tspans = tick.getElementsByTagName('tspan');
            expect(tspans.length).toBe(3);
            expect(day_re.exec(tspans[0].textContent)).not.toBe(null);
            expect(date_re.exec(tspans[1].textContent)).not.toBe(null);
            results.push(expect(time_re.exec(tspans[2].textContent)).not.toBe(null));
          }
          return results;
        });
      });
    });
  });
  return describe('Y-Axis', function() {
    describe("Visibility", function() {
      it("is visible by default", function() {
        graphlib.init();
        return expect(document.querySelectorAll('.y').length).toBe(1);
      });
      return it("can be hidden", function() {
        graph.style.axis.y.hide = true;
        graphlib.init();
        return expect(document.querySelectorAll('.y').length).toBe(0);
      });
    });
    describe('Scale', function() {
      return it("Uses min/max values set in graph.axes.y object", function() {
        var y_ticks_text;
        graphlib.init();
        graphlib.draw();
        y_ticks_text = document.querySelectorAll('.y .tick text');
        expect(y_ticks_text.length).toBeGreaterThan(3);
        expect(+y_ticks_text[0].textContent).toBe(graph.axes.y.min);
        return expect(+y_ticks_text[y_ticks_text.length - 1].textContent).toBe(graph.axes.y.max);
      });
    });
    return xdescribe('Ticks', function() {
      return it("are evenly spaced", function() {
        var i, j, k, lastGap, len, ref, results, tick, yPos, y_ticks;
        graphlib.init();
        graphlib.draw();
        y_ticks = document.querySelectorAll('.y .tick');
        yPos = [];
        for (j = 0, len = x_ticks.length; j < len; j++) {
          tick = x_ticks[j];
          yPos.push(+(tick.getAttribute('transform').substr(10, 5)));
        }
        lastGap = null;
        results = [];
        for (i = k = 1, ref = xPos.length - 1; 1 <= ref ? k <= ref : k >= ref; i = 1 <= ref ? ++k : --k) {
          if (lastGap !== null) {
            expect(Math.round(xPos[i] - xPos[i - 1])).toBe(lastGap);
          }
          results.push(lastGap = Math.round(xPos[i] - xPos[i - 1]));
        }
        return results;
      });
    });
  });
});
