
/*
  Created by Jon Wyatt on 18/10/15
 */
describe('Data', function() {
  var focus, graph, graphlib, test_area;
  graphlib = null;
  graph = null;
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
    graphlib.data.raw = ews_data.single_record;
  });
  afterEach(function() {
    var j, k, len, len1, pop, pops, test, tests;
    if (graphlib !== null) {
      graphlib = null;
    }
    if (graph !== null) {
      graph = null;
    }
    if (focus !== null) {
      focus = null;
    }
    if (test_area !== null) {
      test_area.parentNode.removeChild(test_area);
    }
    pops = document.querySelectorAll('#chart_popup');
    if (pops.length > 0) {
      for (j = 0, len = pops.length; j < len; j++) {
        pop = pops[j];
        pop.parentNode.removeChild(pop);
      }
    }
    tests = document.querySelectorAll('#test_area');
    if (tests.length > 0) {
      for (k = 0, len1 = tests.length; k < len1; k++) {
        test = tests[k];
        test.parentNode.removeChild(test);
      }
    }
  });
  describe("Properties", function() {
    beforeEach(function() {
      graphlib.init();
    });
    it("NHGraphLib_Graph has properties for data", function() {
      expect(graph.drawables.data).toBeDefined();
      expect(graph.drawables.area).toBeDefined();
      expect(graph.options.keys).toBeDefined();
      expect(graph.options.plot_partial).toBeDefined();
    });
    return it("NHGraphLib_Graph has properties for data styles", function() {
      expect(graph.style.data_style).toBeDefined();
      expect(graph.style.range.cap.height).toBeDefined();
      expect(graph.style.range.cap.width).toBeDefined();
      expect(graph.style.range.width).toBeDefined();
      expect(graph.style.range_padding).toBeDefined();
    });
  });
  /*
  describe("Data", function() {
    describe("Invalid Data", function() {
      it("handles no observation data (e.g. no properties for given key)", function() {
        var err;
        graph.options.keys = ['fake_key'];
        expect(graphlib.data.raw[0].fake_key).not.toBeDefined();
        err = new Error("No data for 'fake_key'");
        expect(function() {
          return graphlib.init();
        }).toThrow(err);
      });
      it("handles invalid observation values (e.g. non-numeric values)", function() {
        var err;
        graphlib.data.raw[0].fake_key = 'Hello you';
        graph.options.keys = ['fake_key'];
        err = new Error("Invalid data for 'fake_key'");
        expect(function() {
          return graphlib.init();
        }).toThrow(err);
      });
      it("catches erroneous obs values (values outside of min/max range)", function() {
        var err;
        graphlib.data.raw[0].respiration_rate = 200;
        err = new Error("Out of bounds data for 'respiration_rate'");
        expect(function() {
          return graphlib.init();
        }).toThrow(err);
      });
    });
  });
  */
  describe("Styles", function() {
    var circles, graphHeight, graphWidth, paths;
    graph = null;
    graphHeight = null;
    graphWidth = null;
    circles = null;
    paths = null;

    it("throws error if no style defined", function() {
      graph.style.data_style = null;
      graphlib.init();
      expect(function() {
        graphlib.draw();
      }).toThrow(new Error("no graph style defined"));
    });

    describe("Linear", function() {
      var clipURL;
      clipURL = 'url(#respiration_rate-clip)';
      describe("Single observation", function() {
        beforeEach(function() {
          graphlib.init();
          graphlib.draw();
          graph = document.querySelectorAll('.nhgraph');
          graphHeight = +graph[0].getAttribute('height');
          graphWidth = +graph[0].getAttribute('width');
          circles = document.querySelectorAll('.nhgraph .data circle');
          paths = document.querySelectorAll('.nhgraph .data path');
        });
        it("creates a single circle element", function() {
          expect(paths.length).toBe(0);
          expect(circles.length).toBe(1);
        });
        it("..that has class of 'point'", function() {
          expect(circles[0].getAttribute('class')).toBe('point');
        });
        it("..which is the right size", function() {
          expect(circles[0].getAttribute('r')).toBe('3');
        });
        it("..and close to the expected position", function() {
          var expected, value;
          value = graphlib.data.raw[0].respiration_rate;
          expected = graphHeight - ((value / 60) * graphHeight);
          expect(circles[0].getAttribute('cy')).toBeCloseTo(expected, 1);
        });
      });

      describe("Multiple observations", function() {
        beforeEach(function() {
          graphlib.data.raw = ews_data.multiple_records;
          graphlib.init();
          graphlib.draw();
          graph = document.querySelectorAll('.nhgraph');
          graphHeight = +graph[0].getAttribute('height');
          graphWidth = +graph[0].getAttribute('width');
          circles = document.querySelectorAll('.nhgraph .data circle');
          paths = document.querySelectorAll('.nhgraph .data path');
        });

        describe("Circles", function() {
          it("creates a circle for each data point", function() {
            expect(circles.length).toBe(graphlib.data.raw.length);
          });
          it("..which is the right size", function() {
            var circle, j, len;
            for (j = 0, len = circles.length; j < len; j++) {
              circle = circles[j];
              expect(circle.getAttribute('r')).toBe('3');
            }
          });
          it("..and close to it's expected positions", function() {
            var expected, i, j, ref, value;
            for (i = j = 0, ref = circles.length - 1; 0 <= ref ? j <= ref : j >= ref; i = 0 <= ref ? ++j : --j) {
              value = graphlib.data.raw[i].respiration_rate;
              expected = graphHeight - ((value / 60) * graphHeight);
              expect(circles[i].getAttribute('cy')).toBeCloseTo(expected, 1);
            }
          });
        });
        describe("Path/s", function() {
          it("creates expected number of path elements", function() {
            expect(paths.length).toBe(graphlib.data.raw.length - 1);
          });
          it("has a class of 'path'", function() {
            var j, len, path;
            for (j = 0, len = paths.length; j < len; j++) {
              path = paths[j];
              expect(path.getAttribute('class')).toBe('path');
            }
          });
          it("has a clip path to prevent overflow", function() {
            var j, len, path;
            for (j = 0, len = paths.length; j < len; j++) {
              path = paths[j];
              expect(path.getAttribute('clip-path')).toBe(clipURL);
            }
          });
          it("starts and finishes at data points", function() {
            var dString, endX, expectedEndX, expectedStartX, i, j, ref, startX;
            for (i = j = 0, ref = paths.length - 1; 0 <= ref ? j <= ref : j >= ref; i = 0 <= ref ? ++j : --j) {
              expectedStartX = +circles[i].getAttribute('cx');
              expectedEndX = +circles[i + 1].getAttribute('cx');
              dString = paths[i].getAttribute('d');
              startX = +dString.substr(1, 4);
              endX = +dString.match(/L(.*)/)[1].substr(0, 6);
              expect(startX).toBeCloseTo(expectedStartX, 0);
              expect(endX).toBeCloseTo(expectedEndX, 0);
            }
          });
        });
      });
      describe("Incomplete observations", function() {
        beforeEach(function() {
          graphlib.data.raw = ews_data.multi_partial;
          graph.options.plot_partial = true;
          graphlib.init();
          graphlib.draw();
          graph = document.querySelectorAll('.nhgraph');
          graphHeight = +graph[0].getAttribute('height');
          graphWidth = +graph[0].getAttribute('width');
          circles = document.querySelectorAll('.nhgraph .data circle');
          paths = document.querySelectorAll('.nhgraph .data path');
        });
        it("doesn't create empty data points", function() {
          expect(circles.length).toBe(3);
          expect(paths.length).toBe(1);
        });
      });
    });
    describe("Stepped", function() {
      var clipURL;
      clipURL = 'url(#respiration_rate-clip)';
      beforeEach(function() {
        graph.style.data_style = 'stepped';
      });
      describe("Single observation", function() {
        beforeEach(function() {
          graphlib.init();
          graphlib.draw();
          graph = document.querySelectorAll('.nhgraph');
          graphHeight = +graph[0].getAttribute('height');
          graphWidth = +graph[0].getAttribute('width');
          circles = document.querySelectorAll('.nhgraph .data circle');
          paths = document.querySelectorAll('.nhgraph .data path');
        });
        it("creates a single circle element", function() {
          expect(paths.length).toBe(0);
          expect(circles.length).toBe(1);
        });
        it("..that has class of 'point'", function() {
          expect(circles[0].getAttribute('class')).toBe('point');
        });
        it("..which is the right size", function() {
          expect(circles[0].getAttribute('r')).toBe('3');
        });
        it("..and close to the expected position", function() {
          var expected, value;
          value = graphlib.data.raw[0].respiration_rate;
          expected = graphHeight - ((value / 60) * graphHeight);
          expect(circles[0].getAttribute('cy')).toBeCloseTo(expected, 1);
        });
      });
      describe("Multiple observations", function() {
        beforeEach(function() {
          graphlib.data.raw = ews_data.multiple_records;
          graphlib.init();
          graphlib.draw();
          graph = document.querySelectorAll('.nhgraph');
          graphHeight = +graph[0].getAttribute('height');
          graphWidth = +graph[0].getAttribute('width');
          circles = document.querySelectorAll('.nhgraph .data circle');
          paths = document.querySelectorAll('.nhgraph .data path');
        });
        describe("Circles", function() {
          it("creates a circle for each data point", function() {
            expect(circles.length).toBe(graphlib.data.raw.length);
          });
          it("..which is the right size", function() {
            var circle, j, len;
            for (j = 0, len = circles.length; j < len; j++) {
              circle = circles[j];
              expect(circle.getAttribute('r')).toBe('3');
            }
          });
          it("..and close to it's expected positions", function() {
            var expected, i, j, ref, value;
            for (i = j = 0, ref = circles.length - 1; 0 <= ref ? j <= ref : j >= ref; i = 0 <= ref ? ++j : --j) {
              value = graphlib.data.raw[i].respiration_rate;
              expected = graphHeight - ((value / 60) * graphHeight);
              expect(circles[i].getAttribute('cy')).toBeCloseTo(expected, 1);
            }
          });
        });
        describe("Path/s", function() {
          it("creates single path element", function() {
            expect(paths.length).toBe(1);
          });
          it("has a class of 'path'", function() {
            var j, len, path;
            for (j = 0, len = paths.length; j < len; j++) {
              path = paths[j];
              expect(path.getAttribute('class')).toBe('path');
            }
          });
          it("has a clip path to prevent overflow", function() {
            var j, len, path;
            for (j = 0, len = paths.length; j < len; j++) {
              path = paths[j];
              expect(path.getAttribute('clip-path')).toBe(clipURL);
            }
          });
        });
      });
      describe("Incomplete observations", function() {
        var partials;
        partials = null;
        beforeEach(function() {
          graphlib.data.raw = ews_data.multi_partial;
          graph.options.plot_partial = true;
          graphlib.init();
          graphlib.draw();
          graph = document.querySelectorAll('.nhgraph');
          graphHeight = +graph[0].getAttribute('height');
          graphWidth = +graph[0].getAttribute('width');
          circles = document.querySelectorAll('.nhgraph .data circle');
          paths = document.querySelectorAll('.nhgraph .data path');
          partials = document.querySelectorAll('.nhgraph .data .empty_point');
        });
        it("plots empty data points", function() {
          expect(circles.length).toBe(3);
          expect(paths.length).toBe(1);
          expect(partials.length).toBe(1);
        });
      });
    });
    describe("Range", function() {
      var bar, bottoms, capHeight, capWidth, clipURL, extents, rangeWidth, tops;
      tops = null;
      extents = null;
      bottoms = null;
      bar = null;
      capWidth = null;
      capHeight = null;
      rangeWidth = null;
      clipURL = 'url(#blood_pressure_systolic-blood_pressure_diastolic-clip)';
      beforeEach(function() {
        var keys;
        graph.style.data_style = 'range';
        keys = ['blood_pressure_systolic', 'blood_pressure_diastolic'];
        graph.options.keys = keys;
        graph.options.label = 'BP';
        graph.options.measurement = 'mmHg';
        graph.axes.y.min = 0;
        graph.axes.y.max = 250;
        graph.options.normal.min = 100;
        graph.options.normal.max = 140;
        capWidth = graph.style.range.cap.width;
        capHeight = graph.style.range.cap.height;
        rangeWidth = graph.style.range.width;
      });
      it("throws error if 2 keys are not defined", function() {
        var keys, msg;
        keys = ['blood_pressure_systolic'];
        graph.options.keys = keys;
        msg = 'Cannot plot ranged graph with ';
        msg += graph.options.keys.length;
        msg += ' data point(s)';
        graphlib.init();
        expect(function() {
          return graphlib.draw()();
        }).toThrow(new Error(msg));
      });
      describe("Single Record", function() {
        beforeEach(function() {
          graphlib.data.raw = ews_data.single_record;
          graphlib.init();
          graphlib.draw();
          tops = document.querySelectorAll('.range.top');
          bottoms = document.querySelectorAll('.range.bottom');
          extents = document.querySelectorAll('.range.extent');
          bar = [tops[0], extents[0], bottoms[0]];
        });
        it("has a single range bar made of 3 rects", function() {
          expect(tops.length).toBe(1);
          expect(bottoms.length).toBe(1);
          expect(extents.length).toBe(1);
        });
        it("has bar caps that are the defined size", function() {
          expect(+tops[0].getAttribute('width')).toBe(capWidth);
          expect(+tops[0].getAttribute('height')).toBe(capHeight);
          expect(+bottoms[0].getAttribute('width')).toBe(capWidth);
          expect(+bottoms[0].getAttribute('height')).toBe(capHeight);
        });
        it("has an extent that is the correct size", function() {
          var dia, dif, expected, sys;
          expect(+extents[0].getAttribute('width')).toBe(rangeWidth);
          sys = graphlib.data.raw[0].blood_pressure_systolic;
          dia = graphlib.data.raw[0].blood_pressure_diastolic;
          dif = sys - dia;
          expected = (dif / graph.axes.y.max) * graphHeight;
          expect(+extents[0].getAttribute('height')).toBeCloseTo(expected, 0);
        });
        it("is positioned correctly", function() {
          var expected, systolic;
          systolic = graphlib.data.raw[0].blood_pressure_systolic;
          expected = graphHeight - ((systolic / 250) * graphHeight);
          expect(+extents[0].getAttribute('y')).toBeCloseTo(expected, 0);
        });
        it("has the correct clip-path attribute", function() {
          var el, j, len;
          for (j = 0, len = bar.length; j < len; j++) {
            el = bar[j];
            expect(el.getAttribute('clip-path')).toBe(clipURL);
          }
        });
      });
      describe("Multiple Records", function() {
        beforeEach(function() {
          graphlib.data.raw = ews_data.multiple_records;
          graphlib.init();
          graphlib.draw();
          tops = document.querySelectorAll('.range.top');
          bottoms = document.querySelectorAll('.range.bottom');
          extents = document.querySelectorAll('.range.extent');
        });
        it("has the correct number of range bars", function() {
          expect(tops.length).toBe(graphlib.data.raw.length);
          expect(bottoms.length).toBe(graphlib.data.raw.length);
          expect(extents.length).toBe(graphlib.data.raw.length);
        });
        it("has correct sized bar caps", function() {
          var bottom, j, k, len, len1, top;
          for (j = 0, len = tops.length; j < len; j++) {
            top = tops[j];
            expect(+top.getAttribute('width')).toBe(capWidth);
            expect(+top.getAttribute('height')).toBe(capHeight);
          }
          for (k = 0, len1 = bottoms.length; k < len1; k++) {
            bottom = bottoms[k];
            expect(+bottom.getAttribute('width')).toBe(capWidth);
            expect(+bottom.getAttribute('height')).toBe(capHeight);
          }
        });
        it("has an extent that is the correct size", function() {
          var dia, dif, expected, i, j, ref, sys;
          for (i = j = 0, ref = extents.length - 1; 0 <= ref ? j <= ref : j >= ref; i = 0 <= ref ? ++j : --j) {
            expect(+extents[i].getAttribute('width')).toBe(rangeWidth);
            sys = graphlib.data.raw[i].blood_pressure_systolic;
            dia = graphlib.data.raw[i].blood_pressure_diastolic;
            dif = sys - dia;
            expected = (dif / graph.axes.y.max) * graphHeight;
            expect(+extents[i].getAttribute('height')).toBeCloseTo(expected, 0);
          }
        });
        it("is positioned correctly", function() {
          var expected, i, j, ref, sys;
          for (i = j = 0, ref = extents.length - 1; 0 <= ref ? j <= ref : j >= ref; i = 0 <= ref ? ++j : --j) {
            sys = graphlib.data.raw[i].blood_pressure_systolic;
            expected = graphHeight - ((sys / 250) * graphHeight);
            expect(+extents[i].getAttribute('y')).toBeCloseTo(expected, 0);
          }
        });
        it("has the correct clip-path attribute", function() {
          var el, j, len;
          for (j = 0, len = bar.length; j < len; j++) {
            el = bar[j];
            expect(el.getAttribute('clip-path')).toBe(clipURL);
          }
        });
      });
      describe("Incomplete Record", function() {
        beforeEach(function() {
          var none;
          graphlib.data.raw = ews_data.multi_partial;
          none = "['blood_pressure_systolic','blood_pressure_diastolic']";
          graphlib.data.raw[0].none_values = none;
          graphlib.data.raw[1].blood_pressure_diastolic = false;
          graphlib.data.raw[1].blood_pressure_systolic = false;
          graphlib.init();
          graphlib.draw();
          tops = document.querySelectorAll('.range.top');
          bottoms = document.querySelectorAll('.range.bottom');
          extents = document.querySelectorAll('.range.extent');
        });
        it("doesn't create empty data points", function() {
          expect(tops.length).toBe(2);
          expect(bottoms.length).toBe(2);
          expect(extents.length).toBe(2);
        });
      });
    });
  });
});
