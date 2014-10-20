describe('NHMobile', function() {
    var mobile, request;
    beforeEach(function () {
        if(mobile == null){
            mobile = new NHMobile();
        }
        jasmine.Ajax.install();
        //spyOn(window.NHMobile.prototype, 'process_request');
        window.NHMobile.prototype.process_request = jasmine.createSpy('onSuccess');

    });

    afterEach(function () {
        if (mobile != null) {
           mobile = null;
        }
        jasmine.Ajax.uninstall();
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

    //it('triggers a ', function(){})

    //it('', function(){})


    it("allows use in a single spec", function() {


        //var doneFn = jasmine.createSpy('success');
        mobile.get_patient_info(1);
        request = jasmine.Ajax.requests.mostRecent();

        expect(request.url).toBe(mobile.urls.json_patient_info(1).url);
        //expect(doneFn).not.toHaveBeenCalled();

        //jasmine.Ajax.requests.mostRecent().response({
        //    "status": 200,
        //    "responseText": 'in spec response'
        //});

         //expect(doneFn).toHaveBeenCalledWith('in spec response');
    });

});