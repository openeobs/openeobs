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


describe('NHGraphlib - Event listeners for Mobile Controls', function() {
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
