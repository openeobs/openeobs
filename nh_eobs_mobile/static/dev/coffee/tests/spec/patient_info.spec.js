/**
 * Created by colinwren on 24/08/15.
 */
describe('Patient Information Functionality', function(){
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
        var test_area = document.createElement('div');
        test_area.setAttribute('id', 'test');
        test_area.style.height = '500px';
        test_area.innerHTML = test_dom;
        body_el.appendChild(test_area);
        if (mobile == null) {
            mobile = new NHMobile();
        }
    });

    it('Has a function for getting patient information from the server using a patient id', function(){
       expect(typeof(NHMobile.prototype.get_patient_info)).toBe('function');
    });

    it('Has a function for rendering patient information from the server into a definition list', function(){
       expect(typeof(NHMobile.prototype.render_patient_info)).toBe('function');
    });

    it('Has a function for creating a fullscreen modal when pressing a button in the patient information popup', function(){
       expect(typeof(NHMobile.prototype.fullscreen_patient_info)).toBe('function');
    });

    it('Has a function for scanning a barcode for a patient id and displaying the patient information', function(){
       expect(typeof(NHMobileBarcode.prototype.barcode_scanned)).toBe('function');
    });

    describe('Getting patient information by sending patient ID to server', function(){
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
    });

    describe('Rendering patient information using patient data from server', function(){
        var test_pat;
        beforeEach(function(){
            var raw_test_pat = eval(patient_info_data);
            test_pat = raw_test_pat[0];
        });
        it('Renders name and gender in body if nameless flag set to false', function(){
            var test_pat_info = mobile.render_patient_info(test_pat, false, mobile)
            expect(test_pat_info).toBe('<dl><dt>Name:</dt><dd>Test Patient</dd><dt>Gender:</dt><dd>M</dd><dt>DOB:</dt><dd>1988-01-12</dd><dt>Location:</dt><dd>Bed 1</dd><dt class="twoline">Latest Score:</dt><dd class="twoline">1</dd><dt>Hospital ID:</dt><dd>012345678</dd><dt>NHS Number:</dt><dd>NHS012345678</dd></dl>');
        });

        it('Does not render name and gender in body if nameless flag set to true', function(){
            var test_pat_info = mobile.render_patient_info(test_pat, true, mobile)
            expect(test_pat_info).toBe('<dl><dt>DOB:</dt><dd>1988-01-12</dd><dt>Location:</dt><dd>Bed 1</dd><dt class="twoline">Latest Score:</dt><dd class="twoline">1</dd><dt>Hospital ID:</dt><dd>012345678</dd><dt>NHS Number:</dt><dd>NHS012345678</dd></dl>');
        });
    });

    describe('Displaying the patient\'s chart in a full screen modal', function(){
        beforeEach(function(){
            spyOn(NHMobile.prototype, 'process_request').and.callFake(function(){
                var promise = new Promise();
                promise.complete(patient_info_data);
                return promise;
            });
            mobile.get_patient_info(3, mobile);
            //spyOn(NHMobile.prototype, 'fullscreen_patient_info').and.callThrough();
        });
        afterEach(function(){
            var full_screen_modals = document.getElementsByClassName('full-modal');
            for(var i = 0; i < full_screen_modals.length; i++){
                var modal = full_screen_modals[i];
                modal.parentNode.removeChild(modal);
            }
            var patient_popup = document.getElementById('patient_info');
            if(patient_popup != null){
                patient_popup.parentNode.removeChild(patient_popup);
            }
        });
        it('Adds a fullscreen modal to the DOM on pressing the patient observations button', function(){
            var full_obs_button = document.getElementById('patient_obs_fullscreen');
            expect(full_obs_button).not.toBe(null);
            var click_event = document.createEvent('CustomEvent');
            click_event.initCustomEvent('click', false, true, false);
            full_obs_button.dispatchEvent(click_event);
            //expect(NHMobile.prototype.fullscreen_patient_info).toHaveBeenCalled();
            var full_screen_modals = document.getElementsByClassName('full-modal');
            expect(full_screen_modals.length).toBe(1);
        });

        it('Dismisses a fullscreen modal on pressing the fullscreen modal\'s close button', function(){
            var full_obs_button = document.getElementById('patient_obs_fullscreen');
            expect(full_obs_button).not.toBe(null);
            var click_event = document.createEvent('CustomEvent');
            click_event.initCustomEvent('click', false, true, false);
            full_obs_button.dispatchEvent(click_event);
            //expect(NHMobile.prototype.fullscreen_patient_info).toHaveBeenCalled();
            var full_screen_modals = document.getElementsByClassName('full-modal');
            expect(full_screen_modals.length).toBe(1);
            var close_full_obs = document.getElementById('closeFullModal');
            var click_event = document.createEvent('CustomEvent');
            click_event.initCustomEvent('click', false, true, false);
            close_full_obs.dispatchEvent(click_event);
            full_screen_modals = document.getElementsByClassName('full-modal');
            expect(full_screen_modals.length).toBe(0);
        });

        it('User should not be able to see the floating menu options when in the fullscreen modal view', function(){
            var full_obs_button = document.getElementById('patient_obs_fullscreen');
            expect(full_obs_button).not.toBe(null);
            var click_event = document.createEvent('CustomEvent');
            click_event.initCustomEvent('click', false, true, false);
            full_obs_button.dispatchEvent(click_event);
            //expect(NHMobile.prototype.fullscreen_patient_info).toHaveBeenCalled();
            var full_screen_modals = document.getElementsByClassName('full-modal');
            expect(full_screen_modals.length).toBe(1);
            var modal = full_screen_modals[0];
            var iframe = modal.getElementsByTagName('iframe')[0];
            var contents = iframe.contentDocument ? iframe.contentDocument : iframe.contentWindow.document;
            var headers = contents.getElementsByClassName('header');
            expect(headers.length).toBe(0);
            var obs = contents.getElementsByClassName('obs');
            expect(obs.length).toBe(0);

        });
    });

    describe('Getting patient information by scanning a barcode on patient\'s wristband', function(){
        var barcode, test_area;
        beforeEach(function(){
            test_area = document.getElementById('test');
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
            trigger_button = test_area.getElementsByClassName('scan')[0];
            //input = test_area.getElementsByClassName('barcode_input')[0];
            //input_block = test_area.getElementsByClassName('barcode_block')[0];
            barcode = new NHMobileBarcode(trigger_button);
            patient_info_data[0] = {
                'full_name': 'Test Patient',
                'gender': 'M',
                'dob': '1988-01-12 00:00',
                'location': 'Bed 1',
                'ews_score': 1,
                'ews_trend': 'up',
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
            };
            spyOn(NHMobileBarcode.prototype, 'process_request').and.callFake(function(){
                var promise = new Promise();
                promise.complete(patient_info_data);
                return promise;
            });
        });

        it('On pressing the scan button a modal is shown with input box and input box is focused', function(){
            spyOn(NHMobileBarcode.prototype, 'trigger_button_click').and.callThrough();
            spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
            var trigger_button = test_area.getElementsByClassName('scan')[0];
            // fire a click event on the scan button
            var click_event = document.createEvent('CustomEvent');
            click_event.initCustomEvent('click', false, true, false);
            trigger_button.dispatchEvent(click_event);
            expect(NHMobileBarcode.prototype.trigger_button_click).toHaveBeenCalled();
            // check the modal is called
            expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
            expect(NHModal.prototype.create_dialog.calls.argsFor(0)[1]).toBe('patient_barcode');
            expect(NHModal.prototype.create_dialog.calls.argsFor(0)[2]).toBe('Scan patient wristband');
            expect(NHModal.prototype.create_dialog.calls.argsFor(0)[3]).toBe('<div class="block"><textarea name="barcode_scan" class="barcode_scan"></textarea></div>');
            // check to see if the input is currently focused
            var input = document.getElementsByClassName('barcode_scan')[0];
            expect(input).toBe(document.activeElement);
        });


        it('Takes the Hospital Number and requests patient\'s data', function(){
            spyOn(NHMobileBarcode.prototype, 'trigger_button_click').and.callThrough();
            spyOn(NHMobileBarcode.prototype, 'barcode_scanned').and.callThrough();
            spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
            var trigger_button = test_area.getElementsByClassName('scan')[0];
            // get input showing
            var click_event = document.createEvent('CustomEvent');
            click_event.initCustomEvent('click', false, true, false);
            trigger_button.dispatchEvent(click_event);
            expect(NHMobileBarcode.prototype.trigger_button_click).toHaveBeenCalled();
            // fire change event on input
            expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
            expect(NHModal.prototype.create_dialog.calls.argsFor(0)[1]).toBe('patient_barcode');
            expect(NHModal.prototype.create_dialog.calls.argsFor(0)[2]).toBe('Scan patient wristband');
            expect(NHModal.prototype.create_dialog.calls.argsFor(0)[3]).toBe('<div class="block"><textarea name="barcode_scan" class="barcode_scan"></textarea></div>');
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

        it('It receives patient\'s data, without parent_location but news trend, processes it and shows popup via keypress with keycode 116', function(){
            spyOn(NHMobileBarcode.prototype, 'trigger_button_click').and.callThrough();
            spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
            spyOn(NHMobileBarcode.prototype, 'barcode_scanned').and.callThrough();
            var trigger_button = test_area.getElementsByClassName('scan')[0];
            // get input showing
            var click_event = document.createEvent('CustomEvent');
            click_event.initCustomEvent('click', false, true, false);
            trigger_button.dispatchEvent(click_event);
            expect(NHMobileBarcode.prototype.trigger_button_click).toHaveBeenCalled();
            // fire change event on input
            expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
            expect(NHModal.prototype.create_dialog.calls.argsFor(0)[1]).toBe('patient_barcode');
            expect(NHModal.prototype.create_dialog.calls.argsFor(0)[2]).toBe('Scan patient wristband');
            expect(NHModal.prototype.create_dialog.calls.argsFor(0)[3]).toBe('<div class="block"><textarea name="barcode_scan" class="barcode_scan"></textarea></div>');
            var input = document.getElementsByClassName('barcode_scan')[0];
            input.value = '123412341234,123445';
            var change_event = document.createEvent('CustomEvent');
            change_event.initCustomEvent('keypress', false, true, false);
            change_event.keyCode = 116;
            input.dispatchEvent(change_event);
            // go get data from server
            expect(NHMobileBarcode.prototype.barcode_scanned).toHaveBeenCalled();
            expect(NHMobileBarcode.prototype.process_request).toHaveBeenCalled();
            var content = '<dl><dt>Name:</dt><dd>Test Patient</dd><dt>Gender:</dt><dd>M</dd><dt>DOB:</dt><dd>1988-01-12</dd><dt>Location:</dt><dd>Bed 1</dd><dt class="twoline">Latest Score:</dt><dd class="twoline">1</dd><dt>NEWS Trend:</dt><dd>up</dd><dt>Hospital ID:</dt><dd>012345678</dd><dt>NHS Number:</dt><dd>NHS012345678</dd></dl><h3>Tasks</h3><ul class="menu"><li class="rightContent"><a href="http://localhost:8069/mobile/task/1">NEWS Observation<span class="aside">Overdue: 00:10 hours</span></a></li><li class="rightContent"><a href="http://localhost:8069/mobile/task/2">Inform Medical Team<span class="aside"></span></a></li></ul>';

            //Modal content is updated to content
            var modal = document.getElementById('patient_barcode');
            var modal_content = modal.getElementsByClassName('dialogContent')[0];
            expect(modal_content.innerHTML).toBe(content); //currently failing due to async issue?
        });

        it('It shows nothing if input value was nothing', function(){
            spyOn(NHMobileBarcode.prototype, 'trigger_button_click').and.callThrough();
            spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
            spyOn(NHMobileBarcode.prototype, 'barcode_scanned').and.callThrough();
            var trigger_button = test_area.getElementsByClassName('scan')[0];
            // get input showing
            var click_event = document.createEvent('CustomEvent');
            click_event.initCustomEvent('click', false, true, false);
            trigger_button.dispatchEvent(click_event);
            expect(NHMobileBarcode.prototype.trigger_button_click).toHaveBeenCalled();
            // fire change event on input
            expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
            expect(NHModal.prototype.create_dialog.calls.argsFor(0)[1]).toBe('patient_barcode');
            expect(NHModal.prototype.create_dialog.calls.argsFor(0)[2]).toBe('Scan patient wristband');
            expect(NHModal.prototype.create_dialog.calls.argsFor(0)[3]).toBe('<div class="block"><textarea name="barcode_scan" class="barcode_scan"></textarea></div>');
            var input = document.getElementsByClassName('barcode_scan')[0];
            input.value = '';
            var change_event = document.createEvent('CustomEvent');
            change_event.initCustomEvent('keypress', false, true, false);
            change_event.keyCode = 116;
            input.dispatchEvent(change_event);
            // go get data from server
            expect(NHMobileBarcode.prototype.barcode_scanned).toHaveBeenCalled();
            expect(NHMobileBarcode.prototype.process_request).not.toHaveBeenCalled();
        });

        it('It receives patient\'s data, without activities and render it', function(){
            patient_info_data[0]["activities"] = [];
            spyOn(NHMobileBarcode.prototype, 'trigger_button_click').and.callThrough();
            spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
            spyOn(NHMobileBarcode.prototype, 'barcode_scanned').and.callThrough();
            var trigger_button = test_area.getElementsByClassName('scan')[0];
            // get input showing
            var click_event = document.createEvent('CustomEvent');
            click_event.initCustomEvent('click', false, true, false);
            trigger_button.dispatchEvent(click_event);
            expect(NHMobileBarcode.prototype.trigger_button_click).toHaveBeenCalled();
            // fire change event on input
            expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
            expect(NHModal.prototype.create_dialog.calls.argsFor(0)[1]).toBe('patient_barcode');
            expect(NHModal.prototype.create_dialog.calls.argsFor(0)[2]).toBe('Scan patient wristband');
            expect(NHModal.prototype.create_dialog.calls.argsFor(0)[3]).toBe('<div class="block"><textarea name="barcode_scan" class="barcode_scan"></textarea></div>');
            var input = document.getElementsByClassName('barcode_scan')[0];
            input.value = '123412341234,123445';
            var change_event = document.createEvent('CustomEvent');
            change_event.initCustomEvent('keypress', false, true, false);
            change_event.keyCode = 116;
            input.dispatchEvent(change_event);
            // go get data from server
            expect(NHMobileBarcode.prototype.barcode_scanned).toHaveBeenCalled();
            expect(NHMobileBarcode.prototype.process_request).toHaveBeenCalled();
            var content = '<dl><dt>Name:</dt><dd>Test Patient</dd><dt>Gender:</dt><dd>M</dd><dt>DOB:</dt><dd>1988-01-12</dd><dt>Location:</dt><dd>Bed 1</dd><dt class="twoline">Latest Score:</dt><dd class="twoline">1</dd><dt>NEWS Trend:</dt><dd>up</dd><dt>Hospital ID:</dt><dd>012345678</dd><dt>NHS Number:</dt><dd>NHS012345678</dd></dl><h3>Tasks</h3>';

            //Modal content is updated to content
            var modal = document.getElementById('patient_barcode');
            var modal_content = modal.getElementsByClassName('dialogContent')[0];
            expect(modal_content.innerHTML).toBe(content); //currently failing due to async issue?
        });

        afterEach(function(){
            var test_area = document.getElementById('test');
            test_area.innerHTML = '';
            if(barcode != null){
                barcode = null;
            }
            var modals = document.getElementsByClassName('dialog');
            for(var i = 0; i < modals.length; i++){
                var modal = modals[i];
                modal.parentNode.removeChild(modal);
            }
            var covers = document.getElementsByClassName('dialog');
            for(var i = 0; i < covers.length; i++){
                var cover = covers[i];
                cover.parentNode.removeChild(cover);
            }
        });
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