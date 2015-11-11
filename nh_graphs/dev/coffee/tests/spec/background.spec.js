
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
        if (context !== null) {
            context = null;
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

    describe("Structure", function() {

        var countClass, validAbnormal;
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
            graphlib.draw();
        });

        it("has one background group", function() {
            expect(countClass('.background')).toBe(1);
        });

        it("containing one normal rect", function() {
            expect(countClass('.background .normal')).toBe(1);
        });

        it("and 3 range rects", function() {
            expect(countClass('.background .range')).toBe(3);
        });

        it("..one green rect", function() {
            expect(countClass('.background .green')).toBe(1);
        });

        it("..one amber rect", function() {
            expect(countClass('.background .amber')).toBe(1);
        });

        it("..one red rect", function() {
            expect(countClass('.background .red')).toBe(1);
        });

        it("has a label", function() {
            expect(countClass('.label')).toBe(1);
        });

        it("has a measurement", function() {
            expect(countClass('.measurement')).toBe(1);
        });

        it("has at least 3 vertical grid lines", function() {
            expect(countClass('.background .vertical')).toBeGreaterThan(2);
        });

        it("has at least 3 horizontal grid lines", function() {
            expect(countClass('.background .horizontal')).toBeGreaterThan(2);
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
                graphlib.draw();
            });

            it("NHGraphLib_Graph has properties for normal ranges", function() {
                expect(graph.options.normal.min).toBeDefined();
                expect(graph.options.normal.max).toBeDefined();
            });

            it("NHGraphLib_Graph has properties for score ranges", function() {
                expect(graph.drawables.background.obj).toBeDefined();
                expect(graph.drawables.background.data).toBeDefined();
            });
        });

        describe("Data", function() {

            describe("Normal range", function() {

                it("draws range height 0 if data out of expected range", function() {
                    var normals;
                    graph.options.normal.min = -3;
                    graph.options.normal.max = 100;
                    graphlib.init();
                    graphlib.draw();
                    normals = document.querySelectorAll('.normal');
                    expect(normals[0].getAttribute('height')).toBe('0');
                });

                it("draw range height 0 if data invalid", function() {
                    var normals;
                    graph.options.normal.min = 1;
                    graph.options.normal.max = 'hello';
                    graphlib.init();
                    graphlib.draw();
                    normals = document.querySelectorAll('.normal');
                    expect(normals[0].getAttribute('height')).toBe('0');
                });
            });

            describe("Score range", function() {

                // Invalid property names / NaN values
                var invalidRange = [
                    {'class': 'green', t: 20, e: 30},
                    {'class': 'amber', s: 30, e: 40},
                    {'class': 'red', s: 'abc', e: 60}
                ];

                // Overlapping ranges
                var overlapRange = [
                    {'class': 'green', s: 20, e: 30},
                    {'class': 'amber', s: 20, e: 40},
                    {'class': 'red', s: 40, e: 60}
                ];

                // Out of graph range
                var oobRange = [
                    {'class': 'green', s: 20, e: 30},
                    {'class': 'amber', s: 20, e: 40},
                    {'class': 'red', s: 40, e: 60}
                ];

                var validRange = [
                    {'class': 'green', s: 20, e: 30},
                    {'class': 'amber', s: 30, e: 40},
                    {'class': 'red', s: 40, e: 60}
                ];

                it("handles no background data being provided", function() {
                    graph.drawables.background.data = null;
                    graphlib.init();
                    graphlib.draw();
                    var ranges = document.querySelectorAll('.range');
                    expect(ranges.length).toBe(0)
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
                    graphHeight = graphs[0].getAttribute('height');
                });

                it("renders only one normal rect inside nhgraph", function() {
                    expect(graphs.length).toBe(1);
                    expect(normals.length).toBe(1);
                });

                it("spans full width of graph", function() {
                    expect(+normals[0].getAttribute('width')).toBe(+graphWidth);
                });

                it("is the expected height", function() {
                    var normalHeight;
                    normalHeight = normals[0].getAttribute('height');
                    expect(+normalHeight).toBeCloseTo((8 / 60) * graphHeight, 1);
                });

                it("is positioned correctly", function() {
                    var expected, normalY;
                    expect(normals[0].getAttribute('x')).toBe('0');
                    normalY = normals[0].getAttribute('y');
                    expected = graphHeight - ((20 / 60) * graphHeight);
                    expect(+normalY).toBeCloseTo(expected, 1);
                });
            });

            describe("No normal range", function() {

                beforeEach(function() {
                    graph.options.normal.min = null;
                    graph.options.normal.max = null;
                    graphlib.init();
                    graphlib.draw();
                });

                it("renders normal rect with height 0", function() {
                    var norm;
                    norm = document.querySelectorAll('.normal');
                    expect(norm[0].getAttribute('height')).toBe('0');
                });
            });
        });

        describe("Score Range", function() {

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
                    graphHeight = graphs[0].getAttribute('height');
                });

                it("renders only one green rect inside nhgraph", function() {
                    expect(graphs.length).toBe(1);
                    expect(greens.length).toBe(1);
                });

                it("spans full width of graph", function() {
                    expect(+greens[0].getAttribute('width')).toBe(+graphWidth);
                });

                it("is the expected height", function() {
                    var dif, expected, greenHeight;
                    greenHeight = greens[0].getAttribute('height');
                    dif = singleAbnormal[0].e - singleAbnormal[0].s;
                    expected = (dif / 60) * graphHeight;
                    expect(+greenHeight).toBeCloseTo(expected + 1, 1);
                });

                it("is positioned correctly", function() {
                    var expected, greenX, greenY;
                    greenY = greens[0].getAttribute('y');
                    greenX = greens[0].getAttribute('x');
                    expected = graphHeight - ((singleAbnormal[0].e / 60) * graphHeight);
                    expect(greenX).toBe('0');
                    expect(+greenY).toBeCloseTo(expected - 1, 1);
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
                expect(amberRects.length).toBe(0);
            });

            describe("Multiple score ranges", function() {
                var amberRects, greenRects, rects, redRects, validAbnormal;
                greenRects = null;
                amberRects = null;
                redRects = null;
                rects = null;
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
                    rects = [greenRects[0], amberRects[0], redRects[0]];
                });

                it("creates the right number of rects", function() {
                    expect(greenRects.length).toBe(1);
                    expect(amberRects.length).toBe(1);
                    expect(redRects.length).toBe(1);
                    expect(rects.length).toBe(3);
                });

                it("creates the right size rects", function() {
                    var dif, expected, i, j, rectHeight, rectWidth, ref;
                    for (var i = 0; i < rects.length; i++) {
                        rectHeight = rects[i].getAttribute('height');
                        rectWidth = rects[i].getAttribute('width');
                        expect(+rectWidth).toBe(+graphWidth);
                        dif = validAbnormal[i].e - validAbnormal[i].s;
                        expected = (dif / 60) * graphHeight;
                        expect(+rectHeight).toBeCloseTo(expected + 1, 1);
                    }
                });

                it("positions each rect correctly", function() {
                    var expected, i, j, rectX, rectY, ref;
                    for (var i = 0; i < rects.length; i++) {
                        rectX = rects[i].getAttribute('x');
                        rectY = rects[i].getAttribute('y');
                        expected = graphHeight - ((validAbnormal[i].e / 60) * graphHeight);
                        expect(rectX).toBe('0');
                        expect(+rectY).toBeCloseTo(expected - 1, 1);
                    }
                });

                describe("Redraw", function() {

                    beforeEach(function() {
                        graph.redraw();
                        greenRects = document.querySelectorAll('.green');
                        amberRects = document.querySelectorAll('.amber');
                        graphs = document.querySelectorAll('.nhgraph');
                        graphWidth = graphs[0].getAttribute('width');
                        graphHeight = graphs[0].getAttribute('height');
                        rects = [greenRects[0], amberRects[0], redRects[0]];
                    });

                    it("creates the right number of rects", function() {
                        expect(greenRects.length).toBe(1);
                        expect(amberRects.length).toBe(1);
                        expect(redRects.length).toBe(1);
                        expect(rects.length).toBe(3);
                    });

                    it("creates the right size rects", function() {
                        var dif, expected, i, j, rectHeight, rectWidth, ref;
                        for (var i = 0; i < rects.length; i++) {
                            rectHeight = rects[i].getAttribute('height');
                            rectWidth = rects[i].getAttribute('width');
                            expect(+rectWidth).toBe(+graphWidth);
                            dif = validAbnormal[i].e - validAbnormal[i].s;
                            expected = (dif / 60) * graphHeight;
                            expect(+rectHeight).toBeCloseTo(expected + 1, 1);
                        }
                    });

                    it("positions each rect correctly", function() {
                        var expected, i, j, rectX, rectY, ref;
                        for (var i = 0; i < rects.length; i++) {
                            rectX = rects[i].getAttribute('x');
                            rectY = rects[i].getAttribute('y');
                            expected = graphHeight - ((validAbnormal[i].e / 60) * graphHeight);
                            expect(rectX).toBe('0');
                            expect(+rectY).toBeCloseTo(expected - 1, 1);
                        }
                    });
                })
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
            expect(label[0].textContent).toBe('RR');
        });

        it("displays the correct units when provided", function() {
            var measure;
            graph.options.keys = ['respiration_rate'];
            graph.options.label = 'RR';
            graph.options.measurement = '/min';
            graphlib.init();
            graphlib.draw();
            measure = document.querySelectorAll('.background .measurement');
            expect(measure[0].textContent).toBe('18/min');
        });

        it("displays nothing when no label specified", function() {
            graph.options.label = null;
            graphlib.init();
            expect(document.querySelectorAll('.label').length).toBe(0);
        });

        it("displays multiple measurements when more than one key specified", function() {
            graph.options.keys = ['respiration_rate', 'pulse_rate'];
            graph.options.label = 'RR/HR';
            graph.options.measurement = '/min';
            graphlib.init();
            graphlib.draw();
            expect(document.querySelectorAll('.measurement').length).toBe(2);
        });
    });

    describe("Gridlines", function() {

        var horis, vertis;
        horis = null;
        vertis = null;

        beforeEach(function() {
            graphlib.init();
            graphlib.draw();
            vertis = document.querySelectorAll('.background .vertical');
            horis = document.querySelectorAll('.background .horizontal');
        });

        it("has at least one vertical grid line per tick", function() {
            var xTicks;
            xTicks = document.querySelectorAll('.x .tick');
            expect(horis.length).toBeGreaterThan(xTicks.length - 1);
        });

        it("has at least one horizontal grid line per tick", function() {
            var yTicks;
            yTicks = document.querySelectorAll('.y .tick');
            expect(vertis.length).toBeGreaterThan(yTicks.length - 1);
        });

        it("has evenly spaced horizontal grid lines", function() {
            var lastGap, yPos;
            yPos = [];
            for (var i = 0; i < horis.length; i++) {
                line = horis[i];
                yPos.push(+(line.getAttribute('y1')));
            }
            lastGap = null;
            for (var i = 1; i < horis.length; i++) {
                if (lastGap !== null) {
                    expect(yPos[i] - yPos[i - 1]).toBeCloseTo(lastGap, 1);
                }
                lastGap = yPos[i] - yPos[i - 1];
            }
        });

        it("has evenly spaced vertical grid lines", function() {
            var lastGap, xPos;
            xPos = [];

            for (var i = 0; i < vertis.length; i++) {
                line = vertis[i];
                xPos.push(+(line.getAttribute('x1')));
            }

            lastGap = null;
            for (var i = 1; i < vertis.length; i++) {
                if (lastGap !== null) {
                    expect(xPos[i] - xPos[i - 1]).toBeCloseTo(lastGap, 1);
                }
                lastGap = xPos[i] - xPos[i - 1];
            }
        });
    });
});
