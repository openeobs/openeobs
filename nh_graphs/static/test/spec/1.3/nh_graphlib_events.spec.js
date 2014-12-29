describe('NHGraphlib - Event listeners', function() {
    var graphlib, phantomJSPadding;
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

    it('detects when the rangify checkbox has been ticked', function(){
        graphlib.data.raw = data;
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
        var focus = new NHFocus();
        focus.graphs.push(graph);
        focus.title = 'Test Graph';
        graphlib.focus = focus;

        spyOn(graph, 'rangify_graph').andCallThrough();
        spyOn(graph, 'redraw');
        spyOn(graphlib, 'init').andCallThrough();
        spyOn(focus, 'init').andCallThrough();
        spyOn(graph, 'init').andCallThrough();
        graphlib.init();
        expect(graphlib.init).toHaveBeenCalled();
        expect(focus.init).toHaveBeenCalled();
        expect(graph.init).toHaveBeenCalled();
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('click', false, false, false);
        graphlib.options.controls.rangify.dispatchEvent(change_event);
        //graphlib.options.controls.rangify.click();

        expect(graph.rangify_graph).toHaveBeenCalled();
        expect(graph.redraw).toHaveBeenCalled();
    });

    it('detects when the brush function has been triggered on the context', function(){
        graphlib.data.raw = data;
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
        spyOn(context, 'init').andCallThrough();
        spyOn(cgraph, 'init').andCallThrough();
        graphlib.init();

        spyOn(graph, 'redraw');
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('brush', false, false, false);
        cgraph.dispatchEvent(change_event);
        expect(graph.redraw).toHaveBeenCalled();
    });
});


