/**
 * Created by Colin.Wren on 14/12/2016.
 */
describe('Refused observation visualisation', function () {

    var context, focus, graphlib, pulse_graph, score_graph, test_area, bp_graph, rangify, resp_graph, empty_bp_graph;
    graphlib = null;
    pulse_graph = null;
    score_graph = null;
    context = null;
    focus = null;
    test_area = null;
    bp_graph = null;
    resp_graph = null;
    empty_bp_graph = null;

    beforeEach(function () {
        // Plot score, respiration_rate, pulse_rate, blood_pressure_*, empty_blood_pressure_*
        var body_el;

        body_el = document.getElementsByTagName('body')[0];
        test_area = document.createElement('div');
        test_area.setAttribute('id', 'test_area');
        test_area.style.width = '500px';
        body_el.appendChild(test_area);
        rangify = document.createElement('input');
        rangify.setAttribute('id', 'rangify');
        rangify.setAttribute('type', 'checkbox');
        rangify.setAttribute('checked', true);
        test_area.appendChild(rangify);

        if (graphlib === null) {
            graphlib = new NHGraphLib('#test_area');
        }
        if (pulse_graph === null) {
            pulse_graph = new NHGraph();
        }
        if (resp_graph === null) {
            resp_graph = new NHGraph();
        }
        if (bp_graph === null) {
            bp_graph = new NHGraph();
        }
        if (empty_bp_graph === null) {
            empty_bp_graph = new NHGraph();
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
        
        resp_graph.options.keys = ['respiration_rate'];
        resp_graph.options.label = 'RR';
        resp_graph.options.measurement = '/min';
        resp_graph.axes.y.min = 30;
        resp_graph.axes.y.max = 200;
        resp_graph.options.normal.min = 50;
        resp_graph.options.normal.max = 100;
        resp_graph.style.dimensions.height = 70;
        resp_graph.style.axis.x.hide = true;
        resp_graph.style.data_style = 'linear';
        resp_graph.style.label_width = 60;

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
        
        empty_bp_graph.options.keys = ['empty_blood_pressure_systolic', 'empty_blood_pressure_diastolic'];
        empty_bp_graph.options.label = 'BP';
        empty_bp_graph.options.measurement = 'mmHg';
        empty_bp_graph.axes.y.min = 30;
        empty_bp_graph.axes.y.max = 260;
        empty_bp_graph.options.normal.min = 150;
        empty_bp_graph.options.normal.max = 151;
        empty_bp_graph.style.dimensions.height = 90;
        empty_bp_graph.style.axis.x.hide = true;
        empty_bp_graph.style.data_style = 'range';
        empty_bp_graph.style.label_width = 60;

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
        focus.graphs.push(resp_graph)
        focus.graphs.push(bp_graph);
        focus.graphs.push(empty_bp_graph);
        focus.title = 'Individual values';
        focus.style.padding.right = 0;
        focus.style.margin.top = 0;
        focus.style.padding.top = 0;

        context.graph = score_graph;
        context.title = 'NEWS Score';

        graphlib.focus = focus;
        graphlib.context = context;
        graphlib.data.raw = ews_data.refused_observation;
        graphlib.options.controls.rangify = rangify;
        graphlib.options.controls.rangify.checked = false;
        graphlib.options.ranged = false;
        graphlib.options.refused = true;
        graphlib.init();
        graphlib.draw();
    });
    afterEach(function () {
        if (graphlib !== null) {
            graphlib = null;
        }
        if (pulse_graph !== null) {
            pulse_graph = null;
        }
        if (resp_graph !== null) {
            resp_graph = null;
        }
        if (bp_graph !== null) {
            bp_graph = null;
        }
        if (empty_bp_graph !== null) {
            empty_bp_graph = null;
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
    describe('Data Point Styling', function () {
        describe('Context refused observation data points', function () {
            it('Draws the data point with a \'R\' symbol', function () {
                var score_point = score_graph.drawables.data.select('text')[0][0];
                expect(score_point.textContent).toBe('R');
            });
        });
        describe('Focus refused observation with value data points', function () {
            it('Draws the data point with a white circle with black border', function () {
                var valued_point = pulse_graph.drawables.data.select('circle')[0][0];
                expect(valued_point.getAttribute('class')).toBe('empty_point');
            });
        });
        describe('Focus refused observation without value data points', function () {
            it('Draws the data point with a \'R\' symbol', function () {
                var refused_point = resp_graph.drawables.data.select('text')[0][0];
                expect(refused_point.textContent).toBe('R');
            });
        });
        describe('Ranged Focus refused observation with value data points', function() {
            it('Draws the ranged caps and extent with white fills and black borders', function() {
                var valued_extent = bp_graph.drawables.data.select('.extent')[0][0];
                var valued_top_cap = bp_graph.drawables.data.select('.top')[0][0];
                var valued_bottom_cap = bp_graph.drawables.data.select('.bottom')[0][0];
                expect(valued_extent.getAttribute('class')).toBe('range extent empty_point');
                expect(valued_top_cap.getAttribute('class')).toBe('range top empty_point');
                expect(valued_bottom_cap.getAttribute('class')).toBe('range bottom empty_point');
            });
        });
        describe('Ranged Focus refused observation without value data points', function(){
           it('Draws the data poit with a \'R\' symbol', function(){
              var refused_point = empty_bp_graph.drawables.data.select('text')[0][0];
                expect(refused_point.textContent).toBe('R');
           });
        });
    });
    describe('Ranged Y-Axis positioning', function () {
        beforeEach(function(){
           if(rangify.checked){
                ev.mouse('click', rangify)
           }
        });
        describe('Context refused observation data points', function () {
            it('Puts the data point in the middle of the Y-Axis', function () {
                var score_point = score_graph.drawables.data.select('text')[0][0];
                var score_y = parseInt(score_point.getAttribute('y'));
                expect(score_y > 38 && score_y < 42).toBeTruthy();
            });
        });
        describe('Focus refused observation with value data points', function () {
            it('Puts the data point at the value\'s position on the Y-Axis', function () {
                var valued_point = pulse_graph.drawables.data.select('circle')[0][0];
                var valued_y = parseInt(valued_point.getAttribute('cy'));
                expect(valued_y > 47 && valued_y < 51).toBeTruthy();
            });
        });
        describe('Focus refused observation without value data points', function () {
            it('Puts the data point in the middle of the Y-Axis', function () {
                var refused_point = resp_graph.drawables.data.select('text')[0][0];
                var refused_y = parseInt(refused_point.getAttribute('y'));
                expect(refused_y > 129 && refused_y < 133).toBeTruthy();
            });
        });
        describe('Ranged Focus refused observation with value data points', function() {
            it('Draws the ranged caps and extent at the value\'s position on the Y-Axis', function() {
               var valued_extent = bp_graph.drawables.data.select('.extent')[0][0];
                var valued_top_cap = bp_graph.drawables.data.select('.top')[0][0];
                var valued_bottom_cap = bp_graph.drawables.data.select('.bottom')[0][0];
                var extent_y = parseInt(valued_extent.getAttribute('y'));
                var top_y = parseInt(valued_top_cap.getAttribute('y'));
                var bottom_y = parseInt(valued_bottom_cap.getAttribute('y'));
                expect(extent_y > 232 && extent_y < 236).toBeTruthy();
                expect(top_y > 232 && top_y < 236).toBeTruthy();
                expect(bottom_y > 248 && bottom_y < 252).toBeTruthy();
            });
        });
        describe('Ranged Focus refused observation without value data points', function(){
           it('Puts the data point in the middle of the Y-Axis', function(){
              var refused_point = empty_bp_graph.drawables.data.select('text')[0][0];
            var refused_y = parseInt(refused_point.getAttribute('y'));
            expect(refused_y > 338 && refused_y < 342).toBeTruthy();
           });
        });
    });
    describe('Unranged Y-Axis positioning', function () {
        beforeEach(function(){
           if(!rangify.checked){
                ev.mouse('click', rangify)
           }
        });
        describe('Context refused observation data points', function () {
            it('Puts the data point in the middle of the Y-Axis', function () {
                var score_point = score_graph.drawables.data.select('text')[0][0];
                var score_y = parseInt(score_point.getAttribute('y'));
                expect(score_y > 38 && score_y < 42).toBeTruthy();
            });
        });
        describe('Focus refused observation with value data points', function () {
            it('Puts the data point at the value\'s position on the Y-Axis', function () {
                var valued_point = pulse_graph.drawables.data.select('circle')[0][0];
                var valued_y = parseInt(valued_point.getAttribute('cy'));
                expect(valued_y > 33 && valued_y < 37).toBeTruthy();
            });
        });
        describe('Focus refused observation without value data points', function () {
            it('Puts the data point in the middle of the Y-Axis', function () {
                var refused_point = resp_graph.drawables.data.select('text')[0][0];
                var refused_y = parseInt(refused_point.getAttribute('y'));
                expect(refused_y > 129 && refused_y < 133).toBeTruthy();
            });
        });
        describe('Ranged Focus refused observation with value data points', function() {
            it('Draws the ranged caps and extent at the value\'s position on the Y-Axis', function() {
               var valued_extent = bp_graph.drawables.data.select('.extent')[0][0];
                var valued_top_cap = bp_graph.drawables.data.select('.top')[0][0];
                var valued_bottom_cap = bp_graph.drawables.data.select('.bottom')[0][0];
                var extent_y = parseInt(valued_extent.getAttribute('y'));
                var top_y = parseInt(valued_top_cap.getAttribute('y'));
                var bottom_y = parseInt(valued_bottom_cap.getAttribute('y'));
                expect(extent_y > 180 && extent_y < 184).toBeTruthy();
                expect(top_y > 180 && top_y < 184).toBeTruthy();
                expect(bottom_y > 265 && bottom_y < 269).toBeTruthy();
            });
        });
        describe('Ranged Focus refused observation without value data points', function(){
           it('Puts the data point in the middle of the Y-Axis', function(){
              var refused_point = empty_bp_graph.drawables.data.select('text')[0][0];
            var refused_y = parseInt(refused_point.getAttribute('y'));
            expect(refused_y > 338 && refused_y < 342).toBeTruthy();
           });
        });
    });
});