
/*
  Created by Jon Wyatt on 14/10/15
 */
describe('Background', function() {
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
  describe("Structure", function() {
    var ambers, countClass, greens, normals, ranges, reds, validAbnormal;
    ranges = null;
    normals = null;
    greens = null;
    ambers = null;
    reds = null;
    validAbnormal = null;
    countClass = function(className) {
      return document.querySelectorAll(className).length;
    };
    beforeEach(function() {
      graph.options.normal.min = 12;
      graph.options.normal.max = 20;
      validAbnormal = [
        {
          'class': 'green',
          s: 20,
          e: 30
        }, {
          'class': 'amber',
          s: 30,
          e: 40
        }, {
          'class': 'red',
          s: 40,
          e: 60
        }
      ];
      graph.drawables.background.data = validAbnormal;
      graphlib.init();
      return graphlib.draw();
    });
    it("has one background group", function() {
      return expect(countClass('.background')).toBe(1);
    });
    it("containing one normal rect", function() {
      return expect(countClass('.background .normal')).toBe(1);
    });
    it("and 3 range rects", function() {
      return expect(countClass('.background .range')).toBe(3);
    });
    it("..one green rect", function() {
      return expect(countClass('.background .green')).toBe(1);
    });
    it("..one amber rect", function() {
      return expect(countClass('.background .amber')).toBe(1);
    });
    it("..one red rect", function() {
      return expect(countClass('.background .red')).toBe(1);
    });
    it("has a label", function() {
      return expect(countClass('.label')).toBe(1);
    });
    it("has a measurement", function() {
      return expect(countClass('.measurement')).toBe(1);
    });
    it("has at least 3 vertical grid lines", function() {
      return expect(countClass('.background .vertical')).toBeGreaterThan(2);
    });
    return it("has at least 3 horizontal grid lines", function() {
      return expect(countClass('.background .horizontal')).toBeGreaterThan(2);
    });
  });
  describe("Ranges", function() {
    var graphHeight, graphWidth, graphs;
    graphs = null;
    graphWidth = null;
    graphHeight = null;
    describe("Object properties", function() {
      beforeEach(function() {
        graphlib.init();
        return graphlib.draw();
      });
      it("NHGraphLib_Graph has properties for normal ranges", function() {
        expect(graph.options.normal.min).toBeDefined();
        return expect(graph.options.normal.max).toBeDefined();
      });
      return it("NHGraphLib_Graph has properties for score ranges", function() {
        expect(graph.drawables.background.obj).toBeDefined();
        return expect(graph.drawables.background.data).toBeDefined();
      });
    });
    describe("Data", function() {
      describe("Normal range", function() {
        it("throws error if normal range outside of axis range", function() {
          graph.options.normal.min = -3;
          graph.options.normal.max = 100;
          graphlib.init();
          return expect(function() {
            return graphlib.draw();
          }).toThrow(new Error('Invalid normal range'));
        });
        return it("throws error if normal range data invalid", function() {
          graph.options.normal.min = "yay";
          graph.options.normal.max = NaN;
          graphlib.init();
          return expect(function() {
            return graphlib.draw();
          }).toThrow(new Error('Invalid normal range'));
        });
      });
      return describe("Score range", function() {
        var invalidAbnormal;
        invalidAbnormal = [
          {
            'class': 'green',
            t: 'abc',
            e: 30
          }, {
            'class': 'amber',
            s: 30,
            e: 40
          }, {
            'class': 'red',
            s: 40,
            e: 60
          }
        ];
        it("throws error if array not in expected format", function() {
          graph.drawables.background.data = invalidAbnormal;
          graphlib.init();
          return expect(function() {
            return graphlib.draw();
          }).toThrow(new Error('Invalid background range data'));
        });
        return it("throws error if range larger than axis range", function() {
          invalidAbnormal = [
            {
              'class': 'green',
              s: 20,
              e: 30
            }, {
              'class': 'amber',
              s: 30,
              e: 40
            }, {
              'class': 'red',
              s: 40,
              e: 200
            }
          ];
          graph.drawables.background.data = invalidAbnormal;
          graphlib.init();
          return expect(function() {
            return graphlib.draw();
          }).toThrow(new Error('Invalid background range data'));
        });
      });
    });
    describe("Normal Range", function() {
      var normals;
      normals = [];
      describe("Single normal range", function() {
        beforeEach(function() {
          graph.options.normal.min = 12;
          graph.options.normal.max = 20;
          graphlib.init();
          graphlib.draw();
          normals = document.querySelectorAll('.normal');
          graphs = document.querySelectorAll('.nhgraph');
          graphWidth = graphs[0].getAttribute('width');
          return graphHeight = graphs[0].getAttribute('height');
        });
        it("renders only one normal rect inside nhgraph", function() {
          expect(graphs.length).toBe(1);
          return expect(normals.length).toBe(1);
        });
        it("spans full width of graph", function() {
          return expect(+normals[0].getAttribute('width')).toBe(+graphWidth);
        });
        it("is the expected height", function() {
          var normalHeight;
          normalHeight = normals[0].getAttribute('height');
          return expect(+normalHeight).toBeCloseTo((8 / 60) * graphHeight, 1);
        });
        return it("is positioned correctly", function() {
          var normalY;
          expect(normals[0].getAttribute('x')).toBe('0');
          normalY = normals[0].getAttribute('y');
          return expect(+normalY).toBeCloseTo(graphHeight - ((20 / 60) * graphHeight), 1);
        });
      });
      return describe("No normal range", function() {
        beforeEach(function() {
          graph.options.normal.min = null;
          graph.options.normal.max = null;
          graphlib.init();
          return graphlib.draw();
        });
        return it("renders normal rect with height 0", function() {
          var norm;
          norm = document.querySelectorAll('.normal');
          return expect(norm[0].getAttribute('height')).toBe('0');
        });
      });
    });
    return describe("Score Range", function() {
      var rects;
      rects = null;
      describe("One range", function() {
        var greens, singleAbnormal;
        greens = null;
        singleAbnormal = null;
        beforeEach(function() {
          singleAbnormal = [
            {
              'class': 'green',
              s: 20,
              e: 30
            }
          ];
          graph.drawables.background.data = singleAbnormal;
          graphlib.init();
          graphlib.draw();
          greens = document.querySelectorAll('.green');
          graphs = document.querySelectorAll('.nhgraph');
          graphWidth = graphs[0].getAttribute('width');
          return graphHeight = graphs[0].getAttribute('height');
        });
        it("renders only one green rect inside nhgraph", function() {
          expect(graphs.length).toBe(1);
          return expect(greens.length).toBe(1);
        });
        it("spans full width of graph", function() {
          return expect(+greens[0].getAttribute('width')).toBe(+graphWidth);
        });
        it("is the expected height", function() {
          var dif, expected, greenHeight;
          greenHeight = greens[0].getAttribute('height');
          dif = singleAbnormal[0].e - singleAbnormal[0].s;
          expected = (dif / 60) * graphHeight;
          return expect(+greenHeight).toBeCloseTo(expected + 1, 1);
        });
        return it("is positioned correctly", function() {
          var expected, greenX, greenY;
          greenY = greens[0].getAttribute('y');
          greenX = greens[0].getAttribute('x');
          expected = graphHeight - ((singleAbnormal[0].e / 60) * graphHeight);
          expect(greenX).toBe('0');
          return expect(+greenY).toBeCloseTo(expected - 1, 1);
        });
      });
      it("handles no abnormal ranges", function() {
        var amberRects, greenRects, normalRects;
        graph.drawables.background.data = null;
        graphlib.init();
        graphlib.draw();
        normalRects = document.querySelectorAll('.normal');
        greenRects = document.querySelectorAll('.green');
        amberRects = document.querySelectorAll('.amber');
        graphs = document.querySelectorAll('.nhgraph');
        expect(graphs.length).toBe(1);
        expect(normalRects.length).toBe(1);
        expect(greenRects.length).toBe(0);
        return expect(amberRects.length).toBe(0);
      });
      return describe("Multiple score ranges", function() {
        var amberRects, greenRects, redRects, validAbnormal;
        greenRects = null;
        amberRects = null;
        redRects = null;
        validAbnormal = null;
        beforeEach(function() {
          validAbnormal = [
            {
              'class': 'green',
              s: 20,
              e: 30
            }, {
              'class': 'amber',
              s: 30,
              e: 40
            }, {
              'class': 'red',
              s: 40,
              e: 60
            }
          ];
          graph.drawables.background.data = validAbnormal;
          graphlib.init();
          graphlib.draw();
          greenRects = document.querySelectorAll('.green');
          amberRects = document.querySelectorAll('.amber');
          redRects = document.querySelectorAll('.red');
          graphs = document.querySelectorAll('.nhgraph');
          graphWidth = graphs[0].getAttribute('width');
          graphHeight = graphs[0].getAttribute('height');
          return rects = [greenRects[0], amberRects[0], redRects[0]];
        });
        it("creates the right number of rects", function() {
          expect(greenRects.length).toBe(1);
          expect(amberRects.length).toBe(1);
          expect(redRects.length).toBe(1);
          return expect(rects.length).toBe(3);
        });
        it("creates the right size rects", function() {
          var dif, expected, i, j, rectHeight, rectWidth, ref, results;
          results = [];
          for (i = j = 0, ref = rects.length - 1; 0 <= ref ? j <= ref : j >= ref; i = 0 <= ref ? ++j : --j) {
            rectHeight = rects[i].getAttribute('height');
            rectWidth = rects[i].getAttribute('width');
            expect(+rectWidth).toBe(+graphWidth);
            dif = validAbnormal[i].e - validAbnormal[i].s;
            expected = (dif / 60) * graphHeight;
            results.push(expect(+rectHeight).toBeCloseTo(expected + 1, 1));
          }
          return results;
        });
        return it("positions each rect correctly", function() {
          var expected, i, j, rectX, rectY, ref, results;
          results = [];
          for (i = j = 0, ref = rects.length - 1; 0 <= ref ? j <= ref : j >= ref; i = 0 <= ref ? ++j : --j) {
            rectX = rects[i].getAttribute('x');
            rectY = rects[i].getAttribute('y');
            expected = graphHeight - ((validAbnormal[i].e / 60) * graphHeight);
            expect(rectX).toBe('0');
            results.push(expect(+rectY).toBeCloseTo(expected - 1, 1));
          }
          return results;
        });
      });
    });
  });
  describe("Labels", function() {
    it("displays the correct label when provided", function() {
      var label;
      graph.options.label = 'RR';
      graphlib.init();
      label = document.querySelectorAll('.background .label');
      expect(label.length).toBe(1);
      return expect(label[0].textContent).toBe('RR');
    });
    it("displays the correct units when provided", function() {
      var measure;
      graph.options.keys = ['respiration_rate'];
      graph.options.label = 'RR';
      graph.options.measurement = '/min';
      graphlib.init();
      graphlib.draw();
      measure = document.querySelectorAll('.background .measurement');
      return expect(measure[0].textContent).toBe('18/min');
    });
    it("displays nothing when no label specified", function() {
      graph.options.label = null;
      graphlib.init();
      return expect(document.querySelectorAll('.label').length).toBe(0);
    });
    return it("displays multiple measurements when more than one key specified", function() {
      graph.options.keys = ['respiration_rate', 'pulse_rate'];
      graph.options.label = 'RR/HR';
      graph.options.measurement = '/min';
      graphlib.init();
      graphlib.draw();
      return expect(document.querySelectorAll('.measurement').length).toBe(2);
    });
  });
  return describe("Gridlines", function() {
    var horis, vertis;
    horis = null;
    vertis = null;
    beforeEach(function() {
      graphlib.init();
      graphlib.draw();
      vertis = document.querySelectorAll('.background .vertical');
      return horis = document.querySelectorAll('.background .horizontal');
    });
    it("has at least one vertical grid line per tick", function() {
      var xTicks;
      xTicks = document.querySelectorAll('.x .tick');
      return expect(horis.length).toBeGreaterThan(xTicks.length - 1);
    });
    it("has at least one horizontal grid line per tick", function() {
      var yTicks;
      yTicks = document.querySelectorAll('.y .tick');
      return expect(vertis.length).toBeGreaterThan(yTicks.length - 1);
    });
    it("has evenly spaced horizontal grid lines", function() {
      var i, j, k, lastGap, len, line, ref, results, yPos;
      yPos = [];
      for (j = 0, len = horis.length; j < len; j++) {
        line = horis[j];
        yPos.push(+(line.getAttribute('y1')));
      }
      lastGap = null;
      results = [];
      for (i = k = 1, ref = yPos.length - 1; 1 <= ref ? k <= ref : k >= ref; i = 1 <= ref ? ++k : --k) {
        if (lastGap !== null) {
          expect(yPos[i] - yPos[i - 1]).toBeCloseTo(lastGap, 1);
        }
        results.push(lastGap = yPos[i] - yPos[i - 1]);
      }
      return results;
    });
    return it("has evenly spaced vertical grid lines", function() {
      var i, j, k, lastGap, len, line, ref, results, xPos;
      xPos = [];
      for (j = 0, len = vertis.length; j < len; j++) {
        line = vertis[j];
        xPos.push(+(line.getAttribute('x1')));
      }
      lastGap = null;
      results = [];
      for (i = k = 1, ref = xPos.length - 1; 1 <= ref ? k <= ref : k >= ref; i = 1 <= ref ? ++k : --k) {
        if (lastGap !== null) {
          expect(xPos[i] - xPos[i - 1]).toBeCloseTo(lastGap, 1);
        }
        results.push(lastGap = xPos[i] - xPos[i - 1]);
      }
      return results;
    });
  });
});
