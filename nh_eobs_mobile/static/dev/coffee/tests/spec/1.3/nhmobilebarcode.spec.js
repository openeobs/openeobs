describe('NHMobileBarcode', function(){
	var mobile, test_area;
	var patient_info_data = [{
    	'full_name': 'Test Patient',
    	'gender': 'M',
    	'dob': '1988-01-12 00:00',
    	'location': 'Bed 1',
    	'parent_location': 'Ward 1',
    	'ews_score': 1,
    	'other_identifier': '012345678',
    	'patient_identifier': 'NHS012345678',
    	'activities': [
    		{
    			'display_name': 'NEWS Observation',
    			'id': 1,
                'time': 'Overdue: 00:10 hours'
    		},
    		{
    			'display_name': 'Inform Medical Team',
    			'id': 2,
                'time': ''
    		}
    	]
    }];

	beforeEach(function () {
		// set up the DOM for test
		var body_el = document.getElementsByTagName('body')[0];
		var test = document.getElementById('test');
       	if(test != null){
           test.parentNode.removeChild(test);
       	}
       	test_area = document.createElement('div');
       	test_area.setAttribute('id', 'test');
       	test_area.style.height = '500px';
       	test_area.innerHTML = '<div class="header">' +
                        	  '<div class="header-main block">'+
                              '<img src="/mobile/src/img/logo.png" class="logo">'+
                              '<ul class="header-meta">'+
                              '<li><a href="#" class="button scan">Scan</a></li>'+
                              '<li class="logout"><a href="/mobile/logout/" class="button back">Logout</a></li>'+
                              '</ul></div>'+
                        	  '<ul class="header-menu two-col">'+
                        	  '<li><a href="/mobile/tasks/" id="taskNavItem" class="selected">Tasks</a></li>'+
                              '<li><a href="/mobile/patients/" id="patientNavItem">My Patients</a></li>'+
                              '</ul></div>'
       	body_el.appendChild(test_area);
        if(mobile == null){
        	trigger_button = test_area.getElementsByClassName('scan')[0];
        	input = test_area.getElementsByClassName('barcode_input')[0];
        	input_block = test_area.getElementsByClassName('barcode_block')[0];
            mobile = new NHMobileBarcode(trigger_button);
        }

        spyOn(NHMobileBarcode.prototype, 'process_request').andCallFake(function(){
    		var promise = new Promise();
    		promise.complete(patient_info_data);
    		return promise;
    	});
    });

    afterEach(function () {
        if (mobile != null) {
           mobile = null;
        }
        var test = document.getElementById('test');
        if(test != null){
            test.parentNode.removeChild(test);
        }
        var covers = document.getElementsByClassName('cover');
        var dialog = document.getElementById('patient_barcode');
        var body = document.getElementsByTagName('body')[0];
        for(var i = 0; i < covers.length; i++){
            var cover = covers[i];
            body.removeChild(cover);
        }
        if(dialog){
            body.removeChild(dialog);
        }
    });

    it('Creates a click event listener on scan button', function(){
    	spyOn(NHMobileBarcode.prototype, 'trigger_button_click');
    	var trigger_button = test_area.getElementsByClassName('scan')[0];
    	// fire a click event at the scan button
    	var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        trigger_button.dispatchEvent(click_event);
    	// test is fires the appropriate function
    	expect(NHMobileBarcode.prototype.trigger_button_click).toHaveBeenCalled();
    });

    it('On pressing the scan button a modal is shown with input box and input box is focused', function(){
    	spyOn(NHMobileBarcode.prototype, 'trigger_button_click').andCallThrough();
        spyOn(NHModal.prototype, 'create_dialog').andCallThrough();
    	var trigger_button = test_area.getElementsByClassName('scan')[0];
    	// fire a click event on the scan button 
    	var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        trigger_button.dispatchEvent(click_event);
        expect(NHMobileBarcode.prototype.trigger_button_click).toHaveBeenCalled();
    	// check the modal is called
    	expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog.argsForCall[0][1]).toBe('patient_barcode');
        expect(NHModal.prototype.create_dialog.argsForCall[0][2]).toBe('Scan patient wristband');
        expect(NHModal.prototype.create_dialog.argsForCall[0][3]).toBe('<div class="block"><textarea name="barcode_scan" class="barcode_scan"></textarea></div>');
    	// check to see if the input is currently focused
    	var input = document.getElementsByClassName('barcode_scan')[0];
    	expect(input).toBe(document.activeElement);
    });

    it('Creates a change event listener on input', function(){
    	spyOn(NHMobileBarcode.prototype, 'trigger_button_click').andCallThrough();
        spyOn(NHModal.prototype, 'create_dialog').andCallThrough();
    	spyOn(NHMobileBarcode.prototype, 'barcode_scanned');
    	var trigger_button = test_area.getElementsByClassName('scan')[0];
    	// get input showing
    	var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        trigger_button.dispatchEvent(click_event);
        expect(NHMobileBarcode.prototype.trigger_button_click).toHaveBeenCalled();
    	// fire change event on input
        expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog.argsForCall[0][1]).toBe('patient_barcode');
        expect(NHModal.prototype.create_dialog.argsForCall[0][2]).toBe('Scan patient wristband');
        expect(NHModal.prototype.create_dialog.argsForCall[0][3]).toBe('<div class="block"><textarea name="barcode_scan" class="barcode_scan"></textarea></div>');
        var change_event = document.createEvent('CustomEvent');
    	change_event.initCustomEvent('keypress', false, true, false);
        change_event.keyCode = 13;
        var input = document.getElementsByClassName('barcode_scan')[0];
        input.dispatchEvent(change_event);
    	// test it fires appropriate function
    	expect(NHMobileBarcode.prototype.barcode_scanned).toHaveBeenCalled();
    });

    it('Takes the Hospital Number and requests patient\'s data', function(){
    	spyOn(NHMobileBarcode.prototype, 'trigger_button_click').andCallThrough();
    	spyOn(NHMobileBarcode.prototype, 'barcode_scanned').andCallThrough();
        spyOn(NHModal.prototype, 'create_dialog').andCallThrough();
    	var trigger_button = test_area.getElementsByClassName('scan')[0];
    	// get input showing
    	var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        trigger_button.dispatchEvent(click_event);
        expect(NHMobileBarcode.prototype.trigger_button_click).toHaveBeenCalled();
    	// fire change event on input
        expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog.argsForCall[0][1]).toBe('patient_barcode');
        expect(NHModal.prototype.create_dialog.argsForCall[0][2]).toBe('Scan patient wristband');
        expect(NHModal.prototype.create_dialog.argsForCall[0][3]).toBe('<div class="block"><textarea name="barcode_scan" class="barcode_scan"></textarea></div>');
        var input = document.getElementsByClassName('barcode_scan')[0];
        input.value = '123412341234,123445';
    	var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('keypress', false, true, false);
        change_event.keyCode = 13;
    	input.dispatchEvent(change_event);
    	// test function it calls asks server using hospital number
    	expect(NHMobileBarcode.prototype.barcode_scanned).toHaveBeenCalled();
    	expect(NHMobileBarcode.prototype.process_request).toHaveBeenCalled();
    });

    it('It receives patient\s data, processes it and shows popup', function(){
    	spyOn(NHMobileBarcode.prototype, 'trigger_button_click').andCallThrough();
        spyOn(NHModal.prototype, 'create_dialog').andCallThrough();
    	spyOn(NHMobileBarcode.prototype, 'barcode_scanned').andCallThrough();
    	var trigger_button = test_area.getElementsByClassName('scan')[0];
    	// get input showing
    	var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        trigger_button.dispatchEvent(click_event);
        expect(NHMobileBarcode.prototype.trigger_button_click).toHaveBeenCalled();
    	// fire change event on input
        expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog.argsForCall[0][1]).toBe('patient_barcode');
        expect(NHModal.prototype.create_dialog.argsForCall[0][2]).toBe('Scan patient wristband');
        expect(NHModal.prototype.create_dialog.argsForCall[0][3]).toBe('<div class="block"><textarea name="barcode_scan" class="barcode_scan"></textarea></div>');
        var input = document.getElementsByClassName('barcode_scan')[0];
        input.value = '123412341234,123445';
    	var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('keypress', false, true, false);
        change_event.keyCode = 13;
    	input.dispatchEvent(change_event);
    	// go get data from server 
    	expect(NHMobileBarcode.prototype.barcode_scanned).toHaveBeenCalled();
    	expect(NHMobileBarcode.prototype.process_request).toHaveBeenCalled();
        var content = '<dl><dt>Name:</dt><dd>Test Patient</dd><dt>Gender:</dt><dd>M</dd><dt>DOB:</dt><dd>1988-01-12</dd><dt>Location:</dt><dd>Bed 1,Ward 1</dd><dt class="twoline">Latest Score:</dt><dd class="twoline">1</dd><dt>Hospital ID:</dt><dd>012345678</dd><dt>NHS Number:</dt><dd>NHS012345678</dd></dl><h3>Tasks</h3><ul class="menu"><li class="rightContent"><a href="http://localhost:8069/mobile/task/1">NEWS Observation<span class="aside">Overdue: 00:10 hours</span></a></li><li class="rightContent"><a href="http://localhost:8069/mobile/task/2">Inform Medical Team<span class="aside"></span></a></li></ul>';

    	//Modal content is updated to content
        var modal = document.getElementById('patient_barcode');
        var modal_content = modal.getElementsByClassName('dialogContent')[0];
        expect(modal_content.innerHTML).toBe(content);
    });
});