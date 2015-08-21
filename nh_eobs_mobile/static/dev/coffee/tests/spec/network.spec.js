/**
 * Created by colinwren on 15/06/15.
 */
describe('Network Functionality', function(){
    var mobile;
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

    it('Has a function for sending HTTP requests', function(){
       expect(typeof(mobile.process_request)).toBe('function');
    });

    it('Has a function for converting Route objects into Requests', function(){
       expect(typeof(mobile.call_resource)).toBe('function');
    });

    describe('call_resource calls underlying process_request function', function(){
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
        }];

        beforeEach(function(){
            if (mobile == null) {
                mobile = new NHMobile();
            }
            spyOn(NHMobile.prototype, 'process_request').and.callFake(function(){
                var promise = new Promise();
                promise.complete(patient_info_data);
                return promise;
            });

            spyOn(XMLHttpRequest.prototype, 'send');
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

        //if(navigator.userAgent.indexOf('Trident') < 0){
        //    it("is calling process_request which is triggering the XMLHTTPRequest", function() {
        //        var mobile = new NHMobile();
        //        mobile.get_patient_info(1);
        //        expect(XMLHttpRequest.prototype.send).toHaveBeenCalled();
        //    });
        //
        //    it('is calling process_request which is sending args', function(){
        //        var mobile = new NHMobile();
        //        mobile.call_resource(mobile.urls.calculate_obs_score('gcs'), 'eyes=1&verbal=1&motor=1');
        //        expect(XMLHttpRequest.prototype.send).toHaveBeenCalledWith('eyes=1&verbal=1&motor=1');
        //    });
        //}

        afterEach(function () {
            if (mobile != null) {
                mobile = null;
            }
        });
    });

    describe("Network error handling", function(){
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
        it('Shows modal when invalid AJAX', function(done){
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
});

