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

});

describe('NHMobile - Calls process_request function', function(){
    var mobile;
    beforeEach(function(){
        if (mobile == null) {
            mobile = new NHMobile();
        }
        jasmine.Ajax.install();
        spyOn(NHMobile.prototype, 'process_request');
    });

    it("should call process_request when getting patient info ", function() {
        mobile.get_patient_info(1);
        expect(NHMobile.prototype.process_request).toHaveBeenCalledWith('GET', 'http://localhost:8169/mobile/patient/info/1');
    });

    it("should call process_request when calling ajax_get_patient_obs", function(){
       mobile.call_resource(mobile.urls.ajax_get_patient_obs(1));
       expect(NHMobile.prototype.process_request).toHaveBeenCalledWith('GET', 'http://localhost:8169/mobile/patient/ajax_obs/1', undefined);
    });

    it("should call process_request when calling ajax_task_cancellation_options", function(){
        mobile.call_resource(mobile.urls.ajax_task_cancellation_options());
        expect(NHMobile.prototype.process_request).toHaveBeenCalledWith('GET', 'http://localhost:8169/mobile/tasks/cancel_reasons/', undefined);
    });

    it("should call process_request when calling calculate_obs_score", function(){
        mobile.call_resource(mobile.urls.calculate_obs_score('gcs'), 'eyes=1&verbal=1&motor=1');
        expect(NHMobile.prototype.process_request).toHaveBeenCalledWith('POST', 'http://localhost:8169/mobile/observation/score/gcs', 'eyes=1&verbal=1&motor=1');
    });

    afterEach(function () {
        if (mobile != null) {
            mobile = null;
        }
        jasmine.Ajax.uninstall();
    });
});

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
    it('is showing modal when invalid ajax', function(){
        expect(window.NHModal.prototype.create_dialog).toHaveBeenCalled();
    });

    afterEach(function(){
        var test = document.getElementById('data_error');
        if(test != null){
            test.parentNode.removeChild(test);
        }
    });
});

describe("NHMobile AJAX - Promise", function(){
    var resp, resp_val;
    beforeEach(function(done){
        var mobile = new NHMobile();
        resp = Promise.when(mobile.get_patient_info(1)).then(function(data){
            resp_val = data;
            done();
        }, function(fail){
            console.log('promise failed');
            done();
        });
    });
    it("promise resolves ", function() {
        expect(typeof(resp_val)).toEqual('object');
    });

});