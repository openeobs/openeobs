/**
 * Created by colinwren on 29/06/15.
 */
describe('Axis', function () {
    var graphlib, graph, context , focus, test_area;
    beforeEach(function () {
        var body_el = document.getElementsByTagName('body')[0];
        test_area = document.createElement('div');
        test_area.setAttribute('id', 'test_area');
        test_area.style.width = '500px';
        body_el.appendChild(test_area);
        if (graphlib == null) {
            graphlib = new NHGraphLib('#test_area');
        }
        if (graph == null) {
            graph = new NHGraph();
        }
        if (context == null) {
            context = new NHContext();
        }
        if (focus == null) {
            focus = new NHFocus();
        }

        // set up a demo graph
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
        graphlib.data.raw = ews_data.single;
    });

    afterEach(function () {
        if (graphlib != null) {
            graphlib = null;
        }
        if (graph != null) {
            graph = null;
        }
        if (context != null) {
            context = null;
        }
        if (focus != null) {
            focus = null;
        }
        if(test_area != null){
            test_area.parentNode.removeChild(test_area);
        }
    });

    it('NHGraphLib has properties for setting the axis label height', function () {
        expect(graphlib.style.hasOwnProperty('axis_label_text_height')).toBe(true);
    });

    it('NHContext has axes property that holds information for X and Y axes', function(){
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
        expect(context.axes.y.hasOwnProperty('max')).toBe(true);
    });
    
    it('NHFocus has axes property that holds information for X and Y axes', function(){
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
        expect(focus.axes.y.hasOwnProperty('max')).toBe(true);
    });

    it('NHGraph has axes property that holds information for X and Y axes', function(){
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
        expect(graph.axes.y.hasOwnProperty('ranged_extent')).toBe(true);
    });

    it('NHGraph has styling properties for X and Y axes', function(){
        expect(graph.style.hasOwnProperty('axis')).toBe(true);
        expect(graph.style.hasOwnProperty('axis_label_text_height')).toBe(true);
        expect(graph.style.hasOwnProperty('axis_label_text_padding')).toBe(true);
        expect(graph.style.axis.hasOwnProperty('x')).toBe(true);
        expect(graph.style.axis.hasOwnProperty('y')).toBe(true);
        expect(graph.style.axis.x.hasOwnProperty('hide')).toBe(true);
        expect(graph.style.axis.y.hasOwnProperty('hide')).toBe(true);
        expect(graph.style.axis.x.hasOwnProperty('size')).toBe(true);
        expect(graph.style.axis.y.hasOwnProperty('size')).toBe(true);
    });

    describe('Scale', function () {

        it('Adds time padding of 100 to the scale when plotting a single data point and no time padding defined', function () {

            // Set up the original extent so can check
            var data_point = graphlib.date_from_string(graphlib.data.raw[0]['date_terminated']);

            // initalise the graph
            graphlib.init();

            // As we're dealing with a single data point the initialisation should pad the extent by 100 minutes
            expect(graphlib.style.time_padding).toBe(100);
            var start = new Date(data_point);
            var end = new Date(data_point);

            start.setMinutes(start.getMinutes()-100);
            end.setMinutes(end.getMinutes()+100);

            // Need to do string conversion as can't compare date to date
            expect(graphlib.date_to_string(graphlib.data.extent.start)).toBe(graphlib.date_to_string(start));
            expect(graphlib.date_to_string(graphlib.data.extent.end)).toBe(graphlib.date_to_string(end));
        });

        it('Adds time padding of 3 to the scale when plotting a single data point and time padding of 3 is defined', function () {

            // Set up the original extent so can check
            var data_point = graphlib.date_from_string(graphlib.data.raw[0]['date_terminated']);

            // set time padding to 3
            graphlib.style.time_padding = 3;

            // initalise the graph
            graphlib.init();

            // As we're dealing with a single data point the initialisation should pad the extent by 100 minutes
            expect(graphlib.style.time_padding).toBe(3);
            var start = new Date(data_point);
            var end = new Date(data_point);

            start.setMinutes(start.getMinutes()-3);
            end.setMinutes(end.getMinutes()+3);

            // Need to do string conversion as can't compare date to date
            expect(graphlib.date_to_string(graphlib.data.extent.start)).toBe(graphlib.date_to_string(start));
            expect(graphlib.date_to_string(graphlib.data.extent.end)).toBe(graphlib.date_to_string(end));
        });

        it('Adds time padding of date difference divided by SVG width divided by 500 to the scale when plotting multiple data points and no time padding defined', function () {
            graphlib.data.raw = ews_data.multiple;
            var original_extent = [graphlib.date_from_string(graphlib.data.raw[0]['date_terminated']), graphlib.date_from_string(graphlib.data.raw[1]['date_terminated'])];

            graphlib.init();

            // dates are 1 hour apart (3600000), svg is 500px (500px - 0 margins) and 3600000 / 500 / 500 = 14.4
            expect(graphlib.style.time_padding).toBe(14.4);
            var start = new Date(original_extent[0]);
            var end = new Date(original_extent[1]);

            start.setMinutes(start.getMinutes()-14.4);
            end.setMinutes(end.getMinutes()+14.4);

            // Need to do string conversion as can't compare date to date
            expect(graphlib.date_to_string(graphlib.data.extent.start)).toBe(graphlib.date_to_string(start));
            expect(graphlib.date_to_string(graphlib.data.extent.end)).toBe(graphlib.date_to_string(end));
        });

         it('Adds time padding of 3 to the scale when plotting multiple data points when time padding of 3 is defined', function () {
            graphlib.data.raw = ews_data.multiple;
            var original_extent = [graphlib.date_from_string(graphlib.data.raw[0]['date_terminated']), graphlib.date_from_string(graphlib.data.raw[1]['date_terminated'])];

             // set time padding to 3
            graphlib.style.time_padding = 3;
            graphlib.init();

            // As we're dealing with a single data point the initialisation should pad the extent by 100 minutes
            expect(graphlib.style.time_padding).toBe(3);
            var start = new Date(original_extent[0]);
            var end = new Date(original_extent[1]);

            start.setMinutes(start.getMinutes()-3);
            end.setMinutes(end.getMinutes()+3);

            // Need to do string conversion as can't compare date to date
            expect(graphlib.date_to_string(graphlib.data.extent.start)).toBe(graphlib.date_to_string(start));
            expect(graphlib.date_to_string(graphlib.data.extent.end)).toBe(graphlib.date_to_string(end));
        });

    });

    describe('Labels', function () {

        beforeEach(function(){
            graphlib.init();
            graphlib.draw();
        });

        it('Draws the labels as defined in the object', function () {
            expect(false).toBe(true);
        });

        it('Creates the labels in the correct date format', function () {
            expect(false).toBe(true);
        });

        it('Adds line breaks to the X axis so ticks are easier to read', function () {
            // Get focus
            var focus_els = test_area.getElementsByClassName('nhfocus');
            expect(focus_els.length).toBe(1);
            var focus_el = focus_els[0];

            // Get graph
            var graph_els = focus_el.getElementsByClassName('nhgraph');
            expect(graph_els.length).toBe(1);
            var graph_el = graph_els[0];

            // Get X Axis
            var x_els = graph_el.getElementsByClassName('x');
            expect(x_els.length).toBe(1);
            var x_el = x_els[0];
            expect(x_el.getAttribute('class')).toBe('x axis');

            // Set up regex for ticks
            var day_re = new RegExp('[MTWFS][a-z][a-z]');
            var date_re = new RegExp('[0-9]?[0-9]/[0-9]?[0-9]/[0-9]?[0-9]');
            var time_re = new RegExp('[0-2]?[0-9]:[0-5]?[0-9]');

            // Get X Axis ticks
            var tick_els = x_el.getElementsByClassName('tick');
            for(var i = 0; i < tick_els.length; i++){
                // do for each tick
                var tick_el = tick_els[i];

                // get text el
                var text_els = tick_el.getElementsByTagName('text');
                expect(text_els.length).toBe(1);
                var text_el = text_els[0];

                // get tspans (should be three, one for day, one for date, one for time
                var tspan_els = text_el.getElementsByTagName('tspan');
                expect(tspan_els.length).toBe(3);
                var tspan_day = tspan_els[0].textContent;
                var tspan_date = tspan_els[1].textContent;
                var tspan_time = tspan_els[2].textContent;
                expect(day_re.exec(tspan_day)).not.toBe(null);
                expect(date_re.exec(tspan_date)).not.toBe(null);
                expect(time_re.exec(tspan_time)).not.toBe(null);
            }
        });

    });

    describe('Ticks', function () {

        beforeEach(function(){
            graphlib.init();
            graphlib.draw();
        });

        it('Draws ticks in the right size', function () {
            expect(false).toBe(true);
        });

        it('Creates ticks in the right incremenets', function () {
            expect(false).toBe(true);
        });

    });

    describe('Styling', function () {

        beforeEach(function(){
            graphlib.init();
            graphlib.draw();
        });

        it('Draws the axis with other elements styling needs taken into consideration', function () {
            expect(false).toBe(true);
        });
    });

    describe('Structure', function () {

        beforeEach(function(){
            graphlib.init();
            graphlib.draw();
        });

        it('Creates a DOM structure for the axis which is easy to understand', function () {
            // Get focus
            var focus_els = test_area.getElementsByClassName('nhfocus');
            expect(focus_els.length).toBe(1);
            var focus_el = focus_els[0];

            // Get graph
            var graph_els = focus_el.getElementsByClassName('nhgraph');
            expect(graph_els.length).toBe(1);
            var graph_el = graph_els[0];

            // Get X Axis
            var x_els = graph_el.getElementsByClassName('x');
            expect(x_els.length).toBe(1);
            var x_el = x_els[0];
            expect(x_el.getAttribute('class')).toBe('x axis');

            // Get Y Axis
            var y_els = graph_el.getElementsByClassName('y');
            expect(y_els.length).toBe(1);
            var y_el = y_els[0];
            expect(y_el.getAttribute('class')).toBe('y axis');
        });
    });
});