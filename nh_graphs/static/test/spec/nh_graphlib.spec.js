describe('NHGraphlib - Date functions', function() {
    var graphlib;
    beforeEach(function () {
        if(graphlib == null){
            graphlib = new NHGraphLib();
        }
    });

    afterEach(function () {
        if (graphlib != null) {
           graphlib = null;
        }
    });

    it('creates a NHGraphLib object with version number', function () {
        expect(graphlib.version).toEqual('0.0.1')
    });

    it('converts date string to date object', function(){
        var date_string = '1988-01-12 06:00:00';
        var date_for_string = graphlib.date_from_string(date_string);
        expect(typeof(date_for_string)).toBe('object');
        expect(date_for_string.constructor.name).toBe('Date');
        expect(date_for_string.toString()).toBe('Tue Jan 12 1988 06:00:00 GMT+0000 (GMT)');
    });

    it('converts date object to string', function(){
        var date = new Date('1988-01-12T06:00:00');
        var string_for_date = graphlib.date_to_string(date);
        expect(string_for_date).toBe('Tues 12/01/88 06:00');
    });
});

describe('NHGraphLib - Initialisation', function(){
    var graphlib, test, phantomJSPadding;
    var data = [{
        __last_update: "2014-12-01 16:16:53",
        activity_id: [700, "NEWS Observation"],
        avpu_text: "A",
        blood_pressure_diastolic: 80,
        blood_pressure_systolic: 120,
        body_temperature: 40,
        clinical_risk: "Medium",
        concentration: false,
        cpap_peep: false,
        create_date: "2014-12-01 13:15:13",
        create_uid: [1, "Administrator"],
        date_started: "2014-12-01 16:16:42",
        date_terminated: "2014-12-01 16:16:53",
        device_id: false,
        display_name: "False",
        flow_rate: false,
        frequency: 240,
        id: 83,
        indirect_oxymetry_spo2: 90,
        is_partial: false,
        mews_score: 0,
        name: false,
        niv_backup: false,
        niv_epap: false,
        niv_ipap: false,
        none_values: "[]",
        null_values: "['niv_epap', 'concentration', 'flow_rate', 'cpap_peep', 'niv_ipap', 'niv_backup']",
        order_by: false,
        oxygen_administration_flag: false,
        partial_reason: false,
        patient_id: [11, "Littel, Alfreda"],
        pulse_rate: 80,
        respiration_rate: 18,
        score: 5,
        state: "completed",
        terminate_uid: [19, "Nadine Bullock"],
        three_in_one: true,
        write_date: "2014-12-01 16:16:53",
        write_uid: [1, "Administrator"]
    }];
    beforeEach(function () {
        test = document.createElement('div');
        test.setAttribute('id', 'test');
        var body_el = document.getElementsByTagName('body')[0];
        body_el.appendChild(test);
        if(graphlib == null){
            graphlib = new NHGraphLib('#test');
        }
    });

    it('Throws an error when no element is defined on initialisation', function(){
        graphlib = null;
        graphlib = new NHGraphLib();
        var initialise = function(){
            return graphlib.init();
        }
        expect(initialise).toThrow();
    });

    it('Initialises correctly with no data, no context and no focus', function(){
        graphlib.data.raw = [];
        // test to see if styles are working
        spyOn(graphlib, 'init').and.callThrough();
        graphlib.init();
        expect(graphlib.init).toHaveBeenCalled();
        // see if svg element is there
        var svg = test.getElementsByTagName('svg');
        expect(svg.length).toBe(1);
        svg = svg[0];
        svg_height = svg.getAttribute('height');
        svg_width = svg.getAttribute('width');
        expect(svg_height).toBe('0');
        expect(svg_width).toBe(test.clientWidth.toString());
        expect(svg.hasChildNodes()).toBe(false);

        // see if popup element is there
        var popup = document.getElementById('chart_popup');
        expect(popup.classList.contains('hidden')).toBe(true);
    });


    it('Initialises correctly with no data, no context but with a focus', function(){
        graphlib.data.raw = [];
        // create a graph
        var graph = new NHGraph();
        graph.options.keys = ['pulse_rate'];
        graph.options.label = 'HR';
        graph.options.measurement = '/min';
        graph.axes.y.min = 30;
        graph.axes.y.max = 200;
        graph.options.normal.min = 50;
        graph.options.normal.max = 100;
        graph.style.dimensions.height = 200;
        graph.style.axis.x.hide = true;
        graph.style.data_style = 'linear';
        graph.style.label_width = 60;

        // create a focus
        var focus = new NHFocus();
        focus.graphs.push(graph);
        focus.title = 'Test Graph';
        graphlib.focus = focus;
        spyOn(graphlib, 'init').and.callThrough();
        graphlib.init();
        expect(graphlib.init).toHaveBeenCalled();
        var svg = test.getElementsByTagName('svg');
        expect(svg.length).toBe(1);
        svg = svg[0];
        svg_height = svg.getAttribute('height');
        svg_width = svg.getAttribute('width');
        expect(svg_height).toBe('0');
        expect(svg_width).toBe(test.clientWidth.toString());
        expect(svg.hasChildNodes()).toBe(false);
        var popup = document.getElementById('chart_popup');
        expect(popup.classList.contains('hidden')).toBe(true);

    });

    it('Initialises correctly with no data but with a focus and a context', function(){
        graphlib.data.raw = [];
        // create a graph
        var graph = new NHGraph();
        graph.options.keys = ['pulse_rate'];
        graph.options.label = 'HR';
        graph.options.measurement = '/min';
        graph.axes.y.min = 30;
        graph.axes.y.max = 200;
        graph.options.normal.min = 50;
        graph.options.normal.max = 100;
        graph.style.dimensions.height = 200;
        graph.style.axis.x.hide = true;
        graph.style.data_style = 'linear';
        graph.style.label_width = 60;

        var cgraph = new NHGraph();
        cgraph.options.keys = ['pulse_rate'];
        cgraph.options.label = 'HR';
        cgraph.options.measurement = '/min';
        cgraph.axes.y.min = 30;
        cgraph.axes.y.max = 200;
        cgraph.options.normal.min = 50;
        cgraph.options.normal.max = 100;
        cgraph.style.dimensions.height = 200;
        cgraph.style.axis.x.hide = true;
        cgraph.style.data_style = 'linear';
        cgraph.style.label_width = 60;

        // create a focus
        var focus = new NHFocus();
        var context = new NHContext();
        focus.graphs.push(graph);
        context.graph = cgraph;
        focus.title = 'Test Graph';
        context.title = 'Test Graph';
        graphlib.focus = focus;
        graphlib.context = context;
        spyOn(graphlib, 'init').and.callThrough();
        graphlib.init();
        expect(graphlib.init).toHaveBeenCalled();
        var svg = test.getElementsByTagName('svg');
        expect(svg.length).toBe(1);
        svg = svg[0];
        svg_height = svg.getAttribute('height');
        svg_width = svg.getAttribute('width');
        expect(svg_height).toBe('0');
        expect(svg_width).toBe(test.clientWidth.toString());
        expect(svg.hasChildNodes()).toBe(false);
        var popup = document.getElementById('chart_popup');
        expect(popup.classList.contains('hidden')).toBe(true);
    });

    it('Initialises correctly with data, no focus or context', function(){
        graphlib.data.raw = data;
        // test to see if styles are working
        spyOn(graphlib, 'init').and.callThrough();
        graphlib.init();
        expect(graphlib.init).toHaveBeenCalled();
        // see if svg element is there
        var svg = test.getElementsByTagName('svg');
        expect(svg.length).toBe(1);
        svg = svg[0];
        svg_height = svg.getAttribute('height');
        svg_width = svg.getAttribute('width');
        expect(svg_height).toBe('0');
        expect(svg_width).toBe(test.clientWidth.toString());
        expect(svg.hasChildNodes()).toBe(false);

        // see if popup element is there
        var popup = document.getElementById('chart_popup');
        expect(popup.classList.contains('hidden')).toBe(true);
    });

    it('Initialises correctly with data, focus no context', function(){
        graphlib.data.raw = data;
        // test to see if styles are working
        var graph = new NHGraph();
        graph.options.keys = ['pulse_rate'];
        graph.options.label = 'HR';
        graph.options.measurement = '/min';
        graph.axes.y.min = 30;
        graph.axes.y.max = 200;
        graph.options.normal.min = 50;
        graph.options.normal.max = 100;
        graph.style.dimensions.height = 200;
        graph.style.axis.x.hide = true;
        graph.style.data_style = 'linear';
        graph.style.label_width = 60;

        // create a focus
        var focus = new NHFocus();
        focus.graphs.push(graph);
        focus.title = 'Test Graph';
        graphlib.focus = focus;
        spyOn(graphlib, 'init').and.callThrough();
        spyOn(focus, 'init').and.callThrough();
        spyOn(graph, 'init').and.callThrough();
        graphlib.init();
        expect(graphlib.init).toHaveBeenCalled();
        expect(focus.init).toHaveBeenCalled();
        expect(graph.init).toHaveBeenCalled();
        // see if svg element is there
        var svg = test.getElementsByTagName('svg');
        expect(svg.length).toBe(1);
        svg = svg[0];
        svg_height = svg.getAttribute('height');
        svg_width = svg.getAttribute('width');
        expect(svg_height).toBe('290');
        expect(svg_width).toBe(test.clientWidth.toString());
        expect(svg.hasChildNodes()).toBe(true);

        // check if title is there
        var title = svg.getElementsByClassName('title');
        expect(title.length).toBe(1);
        title = title[0];
        expect(title.textContent).toBe('Test Graph');
        expect(title.getAttribute('transform')).toBe('translate(0,10)');

        //check if focus is there
        var focusg = svg.getElementsByClassName('nhfocus');
        expect(focusg.length).toBe(1);
        focusg = focusg[0];
        expect(focusg.getAttribute('transform')).toBe('translate(40,80)');
        expect(focusg.getAttribute('width')).toBe((test.clientWidth-70).toString());

        // check if graph is there
        var gg = focusg.getElementsByClassName('nhgraph');
        expect(gg.length).toBe(1);
        gg = gg[0];
        expect(gg.getAttribute('width')).toBe((test.clientWidth-130).toString());
        expect(gg.getAttribute('height')).toBe('200');

        // see if popup element is there
        var popup = document.getElementById('chart_popup');
        expect(popup.classList.contains('hidden')).toBe(true);

    });

    it('Initialises correctly with data, focus and context', function(){
        graphlib.data.raw = data;
        // test to see if styles are working
        var graph = new NHGraph();
        graph.options.keys = ['pulse_rate'];
        graph.options.label = 'HR';
        graph.options.measurement = '/min';
        graph.axes.y.min = 30;
        graph.axes.y.max = 200;
        graph.options.normal.min = 50;
        graph.options.normal.max = 100;
        graph.style.dimensions.height = 200;
        graph.style.axis.x.hide = true;
        graph.style.data_style = 'linear';
        graph.style.label_width = 60;

        var score_graph = new NHGraph();
        score_graph.options.keys = ['score'];
        score_graph.style.dimensions.height = 200;
        score_graph.style.data_style = 'stepped';
        score_graph.axes.y.min = 0;
        score_graph.axes.y.max = 22;
        score_graph.drawables.background.data =  [
            {"class": "green",s: 1, e: 4},
            {"class": "amber",s: 4,e: 6},
            {"class": "red",s: 6,e: 22}
        ];
        score_graph.style.label_width = 60;

        // create a focus
        var focus = new NHFocus();
        var context = new NHContext();
        focus.graphs.push(graph);
        focus.title = 'Test Graph';
        graphlib.focus = focus;
        context.graph = score_graph;
        context.title = 'NEWS Score';
        graphlib.context = context;

        spyOn(graphlib, 'init').and.callThrough();
        spyOn(focus, 'init').and.callThrough();
        spyOn(graph, 'init').and.callThrough();
        spyOn(context, 'init').and.callThrough();
        spyOn(score_graph, 'init').and.callThrough();
        graphlib.init();
        expect(graphlib.init).toHaveBeenCalled();
        expect(focus.init).toHaveBeenCalled();
        expect(graph.init).toHaveBeenCalled();
        expect(context.init).toHaveBeenCalled();
        expect(score_graph.init).toHaveBeenCalled();

        // see if svg element is there
        var svg = test.getElementsByTagName('svg');
        expect(svg.length).toBe(1);
        svg = svg[0];
        svg_height = svg.getAttribute('height');
        svg_width = svg.getAttribute('width');
        expect(svg_height).toBe('694');
        expect(svg_width).toBe(test.clientWidth.toString());
        expect(svg.hasChildNodes()).toBe(true);

        // check if title is there
        var title = svg.getElementsByClassName('title');
        expect(title.length).toBe(2);
        //title = title[0];
        expect(title[0].textContent).toBe('NEWS Score');
        expect(title[1].textContent).toBe('Test Graph');
        expect(title[0].getAttribute('transform')).toBe('translate(0,60)');
        expect(title[1].getAttribute('transform')).toBe('translate(0,364)');

        //check if focus is there
        var focusg = svg.getElementsByClassName('nhfocus');
        expect(focusg.length).toBe(1);
        focusg = focusg[0];
        expect(focusg.getAttribute('transform')).toBe('translate(40,434)');
        expect(focusg.getAttribute('width')).toBe((test.clientWidth-70).toString());

        // check if graph is there
        var gg = focusg.getElementsByClassName('nhgraph');
        expect(gg.length).toBe(1);
        gg = gg[0];
        expect(gg.getAttribute('width')).toBe((test.clientWidth-130).toString());
        expect(gg.getAttribute('height')).toBe('200');

        // see if popup element is there
        var popup = document.getElementById('chart_popup');
        expect(popup.classList.contains('hidden')).toBe(true);
    });



    afterEach(function () {
        if (graphlib != null) {
            graphlib = null;
        }
        if(test != null){
            test.parentNode.removeChild(test);
        }
        var popup = document.getElementById('chart_popup');
        if(popup != null){
            popup.parentNode.removeChild(popup);
        }
    });
});



describe('NHGraphlib - Event listeners', function() {
    var graphlib, phantomJSPadding;
    beforeEach(function () {
        var test = document.getElementById('test');
        if(test != null){
            test.parentNode.removeChild(test);
        }
        var body_el = document.getElementsByTagName('body')[0];
        //create controls element
        var controls = document.createElement('div');
        controls.setAttribute('id', 'controls');

        //append start_date input
        var start_date = document.createElement('input');
        start_date.setAttribute('id', 'start_date');
        start_date.setAttribute('name', 'start_date');
        start_date.setAttribute('type', 'date');
        controls.appendChild(start_date);

        //append end_date input
        var end_date = document.createElement('input');
        end_date.setAttribute('id', 'end_date');
        end_date.setAttribute('name', 'end_date');
        end_date.setAttribute('type', 'date');
        controls.appendChild(end_date);

        // append start time input
        var start_time = document.createElement('input');
        start_time.setAttribute('id', 'start_time');
        start_time.setAttribute('name', 'start_time');
        start_time.setAttribute('type', 'time');
        controls.appendChild(start_time);

        // append end time input
        var end_time = document.createElement('input');
        end_time.setAttribute('id', 'end_time');
        end_time.setAttribute('name', 'end_time');
        end_time.setAttribute('type', 'time');
        controls.appendChild(end_time);

        // append rangify checkbox
        var rangify = document.createElement('input');
        rangify.setAttribute('id', 'rangify');
        rangify.setAttribute('name', 'rangify');
        rangify.setAttribute('type', 'checkbox');
        controls.appendChild(rangify);

        //append controls
        body_el.appendChild(controls);


        // append test area
        var test_area = document.createElement('div');
        test_area.setAttribute('id', 'test');
        body_el.appendChild(test_area);
        if (navigator.userAgent.indexOf("PhantomJS") > 0) {
            phantomJSPadding = ' ';
        }
        if(graphlib == null){
            graphlib = new NHGraphLib('#test');
        }
        graphlib.options.controls.date.start = document.getElementById('start_date');
        graphlib.options.controls.date.end = document.getElementById('end_date');
        graphlib.options.controls.time.start = document.getElementById('start_time');
        graphlib.options.controls.time.end = document.getElementById('end_time');
        graphlib.options.controls.rangify = document.getElementById('rangify');
        graphlib.data.raw = [];
    });

    afterEach(function () {
        if (graphlib != null) {
            graphlib = null;
        }
        if(controls != null){
            controls.parentNode.removeChild(controls);
        }
        var test = document.getElementById('test');
        if(test != null){
            test.parentNode.removeChild(test);
        }
        var popup = document.getElementById('chart_popup');
        if(popup != null){
            popup.parentNode.removeChild(popup);
        }
    });

    it('correctly sets up the controls', function () {
        expect(Object.keys(graphlib.options.controls.date).length).toBe(2);
        expect(graphlib.options.controls.date.start).toEqual(document.getElementById('start_date'));
        expect(graphlib.options.controls.date.end).toEqual(document.getElementById('end_date'));
        expect(Object.keys(graphlib.options.controls.time).length).toBe(2);
        expect(graphlib.options.controls.time.start).toEqual(document.getElementById('start_time'));
        expect(graphlib.options.controls.time.end).toEqual(document.getElementById('end_time'));
        expect(graphlib.options.controls.rangify).toEqual(document.getElementById('rangify'));
    });

    it('calls the start_date change function when start_date is changed', function(){
        spyOn(graphlib, 'mobile_date_start_change');
        graphlib.init();
        var start_date = document.getElementById('start_date');
        start_date.value = '1988-01-12';
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('change', false, false, false);
        start_date.dispatchEvent(change_event);
        expect(graphlib.mobile_date_start_change).toHaveBeenCalled();
    });

    it('calls the end_date change function when end_date is changed', function(){
        spyOn(graphlib, 'mobile_date_end_change');
        graphlib.init();
        var end_date = document.getElementById('end_date');
        end_date.value = '1988-01-12';
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('change', false, false, false);
        end_date.dispatchEvent(change_event);
        expect(graphlib.mobile_date_end_change).toHaveBeenCalled();
    });

    it('calls the start_time change function when start_time is changed', function(){
        spyOn(graphlib, 'mobile_time_start_change');
        graphlib.init();
        var start_time = document.getElementById('start_time');
        start_time.value = '06:00:00';
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('change', false, false, false);
        start_time.dispatchEvent(change_event);
        expect(graphlib.mobile_time_start_change).toHaveBeenCalled();
    });

    it('calls the end_time change function when end_time is changed', function(){
        spyOn(graphlib, 'mobile_time_end_change');
        graphlib.init();
        var end_time = document.getElementById('end_time');
        end_time.value = '06:00:00';
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('change', false, false, false);
        end_time.dispatchEvent(change_event);
        expect(graphlib.mobile_time_end_change).toHaveBeenCalled();
    });

    it('detects when the window is resized and redraws', function(){
        spyOn(window, 'dispatchEvent');
        spyOn(graphlib, 'redraw_resize');
        graphlib.init();
        if (document.createEvent) {
            var e = document.createEvent('HTMLEvents');
            e.initEvent('resize', true, false);
            document.body.dispatchEvent(e);
        } else if (document.createEventObject) {
            document.body.fireEvent('onresize');
        }
        expect(graphlib.redraw_resize).toHaveBeenCalled();
    });
});


