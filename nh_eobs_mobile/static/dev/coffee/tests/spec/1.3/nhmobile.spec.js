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
//        expect(navigator.userAgent.indexOf('iPhone') > 0).toBe(true);
//        expect(navigator.userAgent.indexOf('7_0_') < 0).toBe(true);
//        //expect(navigator.userAgent).toBe('meh');
//        Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_3 like Mac OS X) Apple/WebKit/547.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B508 Safari/9537.53
//    }) ;

    
    it('converts date string to date object', function(){
	    var date_string = '1988-01-12 06:00:00';
	    var date_for_string = mobile.date_from_string(date_string);
	    expect(typeof(date_for_string)).toBe('object');
        if(navigator.userAgent.indexOf('MSIE') < 0 && navigator.userAgent.indexOf('Trident') < 0) {
            expect(date_for_string.constructor.name).toBe('Date');
        }
        if((navigator.userAgent.indexOf('Chrome') < 0  && navigator.userAgent.indexOf('Linux') < 0) && (navigator.userAgent.indexOf('iPhone OS') < 0)){
            if((navigator.userAgent.indexOf('MSIE') > 0 || navigator.userAgent.indexOf('Trident') > 0) && navigator.userAgent.indexOf('11') < 0){
                expect(date_for_string.toString()).toBe('Tue Jan 12 06:00:00 UTC 1988');
            }else{
                expect(date_for_string.toString()).toBe('Tue Jan 12 1988 06:00:00 GMT+0000 (Coordinated Universal Time)');
            }
        }else{
            expect(date_for_string.toString()).toBe('Tue Jan 12 1988 06:00:00 GMT+0000 (GMT)');
        }
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
        spyOn(NHMobile.prototype, 'process_request').andCallFake(function(){
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
    var async = new AsyncSpec(this);
    async.beforeEach(function(done){
        spyOn(NHModal.prototype, 'create_dialog').andCallThrough();
        var mobile = new NHMobile();
        resp = Promise.when(mobile.call_resource({url: 'meh', method: 'GET'})).then(function(data){
            resp_val = data;
            done();
        }, function(fail){
            console.log('promise failed');
            done();
        });

    });
    async.it('is showing modal when invalid ajax', function(done){
        expect(window.NHModal.prototype.create_dialog).toHaveBeenCalled();
        done();
    });

    async.afterEach(function(done){
        var test = document.getElementById('data_error');
        if(test != null){
            test.parentNode.removeChild(test);
        }
        done();
    });
});

describe("NHMobile AJAX - Promise", function(){
    var resp, resp_val;

    var async = new AsyncSpec(this);
    
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
    
    async.beforeEach(function(done){
    	spyOn(NHMobile.prototype, 'get_patient_info').andCallFake(function(){
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
    async.it("promise resolves ", function(done) {
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
    
   async.afterEach(function(done){
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