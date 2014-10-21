describe('NHMobile', function() {
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

describe('NHMobile AJAX - method', function(){
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
        mobile.call_resource(mobile.urls.calculate_obs_score('gcs'), {'eyes': 1, 'verbal': 1, 'motor': 1});
        expect(NHMobile.prototype.process_request).toHaveBeenCalledWith('POST', 'http://localhost:8169/mobile/observation/score/gcs', {'eyes': 1, 'verbal': 1, 'motor': 1});
    });

    afterEach(function () {
        if (mobile != null) {
            mobile = null;
        }
        jasmine.Ajax.uninstall();
    });
});

describe("NHMobile AJAX - XHR request", function(){
    beforeEach(function(){
        spyOn(XMLHttpRequest.prototype, 'send');
        spyOn(NHModal.prototype, 'create_dialog');
    });

    it("is calling process_request which is triggering the XMLHTTPRequest", function() {
        mobile = new NHMobile();
        mobile.get_patient_info(1);
        expect(XMLHttpRequest.prototype.send).toHaveBeenCalled();
    });

    it("is triggering NHModal when AJAX fails", function() {
        mobile = new NHMobile();
        mobile.get_patient_info(1);
        expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
    });
});