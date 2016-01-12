describe('NHMobile - Object', function() {
    var mobile, request;
    beforeEach(function () {
        if(mobile == null){
            mobile = new NHMobile();
        }
    });

    afterEach(function () {
        if (mobile != null) {
           mobile = null;
        }
         var covers = document.getElementsByClassName('cover');
        var body = document.getElementsByTagName('body')[0];
         for(var i = 0; i < covers.length; i++){
	        var cover = covers[i];
	        body.removeChild(cover);
        }
    });

    it('creates a NHMobile object with version number', function () {
        expect(mobile.version).toEqual('0.0.1')
    });

    it('gives us the correct timestamp in seconds', function () {
        expect(mobile.get_timestamp()).toEqual(Math.round(new Date().getTime() / 1000))
    });

    it('has a list of urls based on the routes object', function(){
       expect(typeof(mobile.urls)).toBe('object');
       expect(mobile.urls).toEqual(frontend_routes);
    });


//    it('tells me what the useragent string is', function(){
////        expect(navigator.userAgent.indexOf('iPhone') > 0).toBe(true);
////        expect(navigator.userAgent.indexOf('7_0_') < 0).toBe(true);
//        expect(navigator.userAgent).toBe('meh');
////        Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_3 like Mac OS X) Apple/WebKit/547.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B508 Safari/9537.53
//    }) ;

    
    it('converts date string to date object', function(){
	    var date_string = '1988-01-12 06:00:00';
	    var date_for_string = mobile.date_from_string(date_string);
	    expect(typeof(date_for_string)).toBe('object');
        if(navigator.userAgent.indexOf('MSIE') < 0 && navigator.userAgent.indexOf('Trident') < 0) {
            expect(date_for_string.constructor.name).toBe('Date');
        }


        // if((navigator.userAgent.indexOf('Chrome') < 0  && navigator.userAgent.indexOf('Linux') < 0) && (navigator.userAgent.indexOf('iPhone OS') < 0)){
        //     if((navigator.userAgent.indexOf('MSIE') > 0 || navigator.userAgent.indexOf('Trident') > 0) && navigator.userAgent.indexOf('11') < 0){
        //         expect(date_for_string.toString()).toBe('Tue Jan 12 06:00:00 UTC 1988');
        //     }else{
        //         expect(date_for_string.toString()).toBe('Tue Jan 12 1988 06:00:00 GMT+0000 (Coordinated Universal Time)');
        //     }
        // }else{
        //     if(navigator.userAgent.indexOf('Chrome') > 0){
        //         expect(date_for_string.toString()).toBe('Tue Jan 12 1988 06:00:00 GMT+0000 (Coordinated Universal Time)');
        //     }else{
        //         expect(date_for_string.toString()).toBe('Tue Jan 12 1988 06:00:00 GMT+0000 (GMT)');
        //     }
        // }
    });
    
    it('converts date object to string', function(){
	   var date = new Date('1988-01-12T06:00:00');
	   var string_for_date = mobile.date_to_string(date);
	   expect(string_for_date).toBe('1988-01-12 06:00:00');
    });
    
    it('converts date to dob string', function(){
	   var date = new Date('1988-01-12T06:00:00');
	   var string_for_date = mobile.date_to_dob_string(date);
	   expect(string_for_date).toBe('1988-01-12'); 
    });

});

describe('NHMobile - Calls process_request function', function(){
    var mobile;
    var patient_info_data = [{
    	'full_name': 'Test Patient',
    	'gender': 'M',
    	'dob': '1988-01-12 00:00',
    	'location': 'Bed 1',
    	'parent_location': 'Ward 1',
    	'ews_score': 1,
    	'other_identifier': '012345678',
    	'patient_identifier': 'NHS012345678'
    }]

    beforeEach(function(){
        if (mobile == null) {
            mobile = new NHMobile();
        }
        //jasmine.Ajax.install();
        spyOn(NHMobile.prototype, 'process_request').and.callFake(function(){
    		var promise = new Promise();
    		promise.complete(patient_info_data);
    		//promise.complete(false);
    		return promise;
    		//return patient_info_data;
    	});
    });

    it("should call process_request when getting patient info ", function() {
        mobile.get_patient_info(1, mobile);
        expect(NHMobile.prototype.process_request).toHaveBeenCalledWith('GET', 'http://localhost:8069/mobile/patient/info/1');
    });

    it("should call process_request when calling ajax_get_patient_obs", function(){
       mobile.call_resource(mobile.urls.ajax_get_patient_obs(1));
       expect(NHMobile.prototype.process_request).toHaveBeenCalledWith('GET', 'http://localhost:8069/mobile/patient/ajax_obs/1', undefined);
    });

    it("should call process_request when calling ajax_task_cancellation_options", function(){
        mobile.call_resource(mobile.urls.ajax_task_cancellation_options());
        expect(NHMobile.prototype.process_request).toHaveBeenCalledWith('GET', 'http://localhost:8069/mobile/tasks/cancel_reasons/', undefined);
    });

    it("should call process_request when calling calculate_obs_score", function(){
        mobile.call_resource(mobile.urls.calculate_obs_score('gcs'), 'eyes=1&verbal=1&motor=1');
        expect(NHMobile.prototype.process_request).toHaveBeenCalledWith('POST', 'http://localhost:8069/mobile/observation/score/gcs', 'eyes=1&verbal=1&motor=1');
    });

    afterEach(function () {
        if (mobile != null) {
            mobile = null;
        }
        //jasmine.Ajax.uninstall();
    });
});

if(navigator.userAgent.indexOf('Trident') < 0){
    describe("NHMobile AJAX - process request is calling xhr send", function(){

        beforeEach(function(){
            spyOn(XMLHttpRequest.prototype, 'send');

        });



        it("is calling process_request which is triggering the XMLHTTPRequest", function() {
            var mobile = new NHMobile();
            mobile.get_patient_info(1);
            expect(XMLHttpRequest.prototype.send).toHaveBeenCalled();
        });

        it('is calling process_request which is sending args', function(){
            var mobile = new NHMobile();
            mobile.call_resource(mobile.urls.calculate_obs_score('gcs'), 'eyes=1&verbal=1&motor=1');
            expect(XMLHttpRequest.prototype.send).toHaveBeenCalledWith('eyes=1&verbal=1&motor=1');
        });

    });
}

describe("NHMobile AJAX - Invalid URL / server error", function(){
    var resp, resp_val;

    beforeEach(function(done){
        spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
        var mobile = new NHMobile();
        resp = Promise.when(mobile.call_resource({url: 'meh', method: 'GET'})).then(function(data){
            resp_val = data;
            done();
        }, function(fail){
            console.log('promise failed');
            done();
        });

    });
    it('is showing modal when invalid ajax', function(done){
        expect(window.NHModal.prototype.create_dialog).toHaveBeenCalled();
        done();
    });

    afterEach(function(done){
        var test = document.getElementById('data_error');
        if(test != null){
            test.parentNode.removeChild(test);
        }
        done();
    });
});

describe("NHMobile AJAX - Promise", function(){
    var resp, resp_val;

    
    var patient_info_data = [{
    	'full_name': 'Test Patient',
    	'gender': 'M',
    	'dob': '1988-01-12 00:00',
    	'location': 'Bed 1',
    	'parent_location': 'Ward 1',
    	'ews_score': 1,
    	'other_identifier': '012345678',
    	'patient_identifier': 'NHS012345678'
    }]
    
    beforeEach(function(done){
    	spyOn(NHMobile.prototype, 'get_patient_info').and.callFake(function(){
    		var promise = new Promise();
    		promise.complete(patient_info_data);
    		//promise.complete(false);
    		return promise;
    		//return patient_info_data;
    	});
        var mobile = new NHMobile();
        resp = Promise.when(mobile.get_patient_info(1, mobile)).then(function(data){
            resp_val = data[0];
            done();
        }, function(fail){
            console.log('promise failed');
            done();
        });
    });
    it("promise resolves ", function(done) {
        expect(typeof(resp_val)).toEqual('object');
        expect(resp_val[0].full_name).toEqual('Test Patient');
        expect(resp_val[0].gender).toEqual('M');
        expect(resp_val[0].dob).toEqual('1988-01-12 00:00');
        expect(resp_val[0].location).toEqual('Bed 1');
        expect(resp_val[0].parent_location).toEqual('Ward 1');
        expect(resp_val[0].ews_score).toEqual(1);
        expect(resp_val[0].other_identifier).toEqual('012345678');
        expect(resp_val[0].patient_identifier).toEqual('NHS012345678');
        done();
    });
    
   afterEach(function(done){
	    var covers = document.getElementsByClassName('cover');
	    var popup = document.getElementById('patient_info');
        var body = document.getElementsByTagName('body')[0];
        body.removeChild(popup);
         for(var i = 0; i < covers.length; i++){
	        var cover = covers[i];
	        body.removeChild(cover);
        }
       done();
    });

});

describe('NHMobile - Patient Info', function(){
    var mobile;
    var patient_info_data = [{
        'full_name': 'Test Patient',
        'gender': 'M',
        'dob': '1988-01-12 00:00',
        'location': 'Bed 1',
        'ews_score': 1,
        'other_identifier': '012345678',
        'patient_identifier': 'NHS012345678'
    }];
    beforeEach(function(){
        var body_el = document.getElementsByTagName('body')[0];
        var test = document.getElementById('test');
        if (test != null) {
            test.parentNode.removeChild(test);
        }
        test_area = document.createElement('div');
        test_area.setAttribute('id', 'test');
        test_area.style.height = '500px';
        test_area.innerHTML = test_dom;
        body_el.appendChild(test_area);
        if (mobile == null) {
            mobile = new NHMobile();
        }
        var full_screen_modals = document.getElementsByClassName('full-modal');
        for(var i = 0; i < full_screen_modals.length; i++){
            var modal = full_screen_modals[i];
            modal.parentNode.removeChild(modal);
        }
    });

    it('Calls the server for patient information and displays in modal', function(){
        spyOn(NHMobile.prototype, 'process_request').and.callFake(function(){
            var promise = new Promise();
            promise.complete(patient_info_data);
            return promise;
        });
        spyOn(NHMobile.prototype, 'get_patient_info').and.callThrough();
        spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
        mobile.get_patient_info(3, mobile);
        expect(NHMobile.prototype.process_request).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog.calls.argsFor(0)[1]).toBe('patient_info');
        expect(NHModal.prototype.create_dialog.calls.argsFor(0)[2]).toBe(' Test Patient<span class="alignright">M</span>');
        expect(NHModal.prototype.create_dialog.calls.argsFor(0)[3]).toBe('<dl><dt>DOB:</dt><dd>1988-01-12</dd><dt>Location:</dt><dd>Bed 1</dd><dt class="twoline">Latest Score:</dt><dd class="twoline">1</dd><dt>Hospital ID:</dt><dd>012345678</dd><dt>NHS Number:</dt><dd>NHS012345678</dd></dl><p><a href="http://localhost:8069/mobile/patient/3" id="patient_obs_fullscreen" class="button patient_obs">View Patient Observation Data</a></p>');
    });

    it('Opens a fullscreen modal on pressing the View full patient obs button', function(){
        spyOn(NHMobile.prototype, 'process_request').and.callFake(function(){
            var promise = new Promise();
            promise.complete(patient_info_data);
            return promise;
        });
        spyOn(NHMobile.prototype, 'get_patient_info').and.callThrough();
        spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
        spyOn(NHMobile.prototype, 'fullscreen_patient_info').and.callThrough();
        mobile.get_patient_info(3, mobile);
        expect(NHMobile.prototype.process_request).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog.calls.argsFor(0)[1]).toBe('patient_info');
        expect(NHModal.prototype.create_dialog.calls.argsFor(0)[2]).toBe(' Test Patient<span class="alignright">M</span>');
        expect(NHModal.prototype.create_dialog.calls.argsFor(0)[3]).toBe('<dl><dt>DOB:</dt><dd>1988-01-12</dd><dt>Location:</dt><dd>Bed 1</dd><dt class="twoline">Latest Score:</dt><dd class="twoline">1</dd><dt>Hospital ID:</dt><dd>012345678</dd><dt>NHS Number:</dt><dd>NHS012345678</dd></dl><p><a href="http://localhost:8069/mobile/patient/3" id="patient_obs_fullscreen" class="button patient_obs">View Patient Observation Data</a></p>');
        var full_obs_button = document.getElementById('patient_obs_fullscreen');
        var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        full_obs_button.dispatchEvent(click_event);
        expect(NHMobile.prototype.fullscreen_patient_info).toHaveBeenCalled();
    });

    it('Closes a fullscreen modal on close button being pressed', function(){
        spyOn(NHMobile.prototype, 'process_request').and.callFake(function(){
            var promise = new Promise();
            promise.complete(patient_info_data);
            return promise;
        });
        spyOn(NHMobile.prototype, 'get_patient_info').and.callThrough();
        spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
        spyOn(NHMobile.prototype, 'fullscreen_patient_info').and.callThrough();
        mobile.get_patient_info(3, mobile);
        expect(NHMobile.prototype.process_request).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog.calls.argsFor(0)[1]).toBe('patient_info');
        expect(NHModal.prototype.create_dialog.calls.argsFor(0)[2]).toBe(' Test Patient<span class="alignright">M</span>');
        expect(NHModal.prototype.create_dialog.calls.argsFor(0)[3]).toBe('<dl><dt>DOB:</dt><dd>1988-01-12</dd><dt>Location:</dt><dd>Bed 1</dd><dt class="twoline">Latest Score:</dt><dd class="twoline">1</dd><dt>Hospital ID:</dt><dd>012345678</dd><dt>NHS Number:</dt><dd>NHS012345678</dd></dl><p><a href="http://localhost:8069/mobile/patient/3" id="patient_obs_fullscreen" class="button patient_obs">View Patient Observation Data</a></p>');
        var full_obs_button = document.getElementById('patient_obs_fullscreen');
        var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        full_obs_button.dispatchEvent(click_event);
        expect(NHMobile.prototype.fullscreen_patient_info).toHaveBeenCalled();

        var close_full_obs = document.getElementById('closeFullModal');
        var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        close_full_obs.dispatchEvent(click_event);
        var fullmodals = document.getElementsByClassName('full-modal');
        expect(fullmodals.length).toBe(0);

    });

    afterEach(function () {
        if (mobile != null) {
            mobile = null;
        }
        var test = document.getElementById('test');
        if (test != null) {
            test.parentNode.removeChild(test);
        }
        var full_screen_modals = document.getElementsByClassName('full-modal');
        for(var i = 0; i < full_screen_modals.length; i++){
            var modal = full_screen_modals[i];
            modal.parentNode.removeChild(modal);
        }
    });

});