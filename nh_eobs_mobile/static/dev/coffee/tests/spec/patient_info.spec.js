/**
 * Created by colinwren on 24/08/15.
 */
describe('Patient Information Functionality', function(){
    var mobile;
    var patient_info_data = new NHMobileData({
        status: 'success',
        title: 'Test Patient',
        description: 'Information on Test Patient',
        data: {
            full_name: 'Test Patient',
            gender: 'M',
            dob: '1988-01-12 00:00',
            location: 'Bed 1',
            ews_score: 1,
            other_identifier: '012345678',
            patient_identifier: 'NHS012345678'
        }
    });
    beforeEach(function(){
        var body_el = document.getElementsByTagName('body')[0];
        var test = document.getElementById('test');
        if (test != null) {
            test.parentNode.removeChild(test);
        }
        var test_area = document.createElement('div');
        test_area.setAttribute('id', 'test');
        test_area.style.height = '500px';
        test_area.innerHTML = '';
        body_el.appendChild(test_area);
        if (mobile == null) {
            mobile = new NHMobile();
        }
        var dialogs = document.getElementsByClassName('dialog');
        for(var i = 0; i < dialogs.length; i++){
            var dialog = dialogs[i];
            dialog.parentNode.removeChild(dialog);
        }
        var covers = document.getElementsByClassName('cover');
        for(var i = 0; i < covers.length; i++){
            var cover = covers[i];
            cover.parentNode.removeChild(cover);
        }
        mobile.urls.base_url = 'http://localhost:9876/mobile/';
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

    // it('Has a function for drawing a patient observation chart', function(){
    //    expect(typeof(NHMobilePatient.prototype.draw_graph)).toBe('function');
    // });

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
            expect(NHModal.prototype.create_dialog.calls.argsFor(0)[2]).toBe('Test Patient<span class="alignright">M</span>');
            expect(NHModal.prototype.create_dialog.calls.argsFor(0)[3]).toBe('<dl><dt>DOB:</dt><dd>1988-01-12</dd><dt>Location:</dt><dd>Bed 1</dd><dt class="twoline">Latest Score:</dt><dd class="twoline">1</dd><dt>Hospital ID:</dt><dd>012345678</dd><dt>NHS Number:</dt><dd>NHS012345678</dd></dl><p><a href="http://localhost:8069/mobile/patient/3" id="patient_obs_fullscreen" class="button patient_obs">View Patient Observation Data</a></p>');
        });
    });

    describe('Rendering patient information using patient data from server', function(){
        var test_pat;
        beforeEach(function(){
            test_pat = patient_info_data.data;
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
            spyOn(NHMobile.prototype, 'fullscreen_patient_info').and.callThrough();
            spyOn(NHMobile.prototype, 'close_fullscreen_patient_info').and.callThrough();
            NHMobile.prototype.fullscreen_patient_info.calls.reset();
            NHMobile.prototype.close_fullscreen_patient_info.calls.reset();
            if(mobile != null){
                mobile = null;
            }
            mobile = new NHMobile();
            spyOn(NHMobile.prototype, 'process_request').and.callFake(function(){
                var promise = new Promise();
                promise.complete(patient_info_data);
                return promise;
            });
            mobile.get_patient_info(3, mobile);
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
            expect(NHMobile.prototype.fullscreen_patient_info).toHaveBeenCalled();
            var full_screen_modals = document.getElementsByClassName('full-modal');
            expect(full_screen_modals.length).toBe(1);
        });

        it('Dismisses a fullscreen modal on pressing the fullscreen modal\'s close button', function(){
            var full_obs_button = document.getElementById('patient_obs_fullscreen');
            expect(full_obs_button).not.toBe(null);
            var click_event = document.createEvent('CustomEvent');
            click_event.initCustomEvent('click', false, true, false);
            full_obs_button.dispatchEvent(click_event);
            expect(NHMobile.prototype.fullscreen_patient_info).toHaveBeenCalled();
            var full_screen_modals = document.getElementsByClassName('full-modal');
            expect(full_screen_modals.length).toBe(1);
            var full_screen_modal = full_screen_modals[0];
            var close_full_obs = full_screen_modal.getElementsByTagName('a')[0];
            var close_click_event = document.createEvent('CustomEvent');
            close_click_event.initCustomEvent('click', false, true, false);
            close_full_obs.dispatchEvent(close_click_event);
            expect(NHMobile.prototype.close_fullscreen_patient_info).toHaveBeenCalled();
            full_screen_modals = document.getElementsByClassName('full-modal');
            expect(full_screen_modals.length).toBe(0);
        });

        it('User should not be able to see the floating menu options when in the fullscreen modal view', function(){
            var full_obs_button = document.getElementById('patient_obs_fullscreen');
            expect(full_obs_button).not.toBe(null);
            var click_event = document.createEvent('CustomEvent');
            click_event.initCustomEvent('click', false, true, false);
            full_obs_button.dispatchEvent(click_event);
            expect(NHMobile.prototype.fullscreen_patient_info).toHaveBeenCalled();
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
        var barcode, test_area, barcode_data;
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
            barcode = new NHMobileBarcode(trigger_button);
            barcode_data = new NHMobileData({
                status: 'success',
                title: 'Test Patient',
                description: 'Information on Test Patient',
                data: {
                    full_name: 'Test Patient',
                    gender: 'M',
                    dob: '1988-01-12 00:00',
                    location: 'Bed 1',
                    //parent_location: 'Ward 1',
                    ews_score: 1,
                    ews_trend: 'up',
                    other_identifier: '012345678',
                    patient_identifier: 'NHS012345678',
                    activities: [
                        {
                            display_name: 'NEWS Observation',
                            id: 1,
                            time: 'Overdue: 00:10 hours'
                        },
                        {
                            display_name: 'Inform Medical Team',
                            id: 2,
                            time: ''
                        }
                    ]
                }
            });
            spyOn(NHMobileBarcode.prototype, 'process_request').and.callFake(function(){
                var promise = new Promise();
                promise.complete(barcode_data);
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
            barcode_data.data.activities = [];
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
            var covers = document.getElementsByClassName('cover');
            for(var i = 0; i < covers.length; i++){
                var cover = covers[i];
                cover.parentNode.removeChild(cover);
            }
        });
    });

    describe('Displaying the patient\'s observation in a chart', function(){
        var nhpatient;
        beforeEach(function(){
            window.drawEwsChart = null;
            window.drawNeuroChart = function(){
                    return {
                        init: function(){ return 'a'; },
                        draw: function(){ return 'b'; }
                    };
                };
            window.drawNeuroTable = function(){ return null; };
            var test = document.getElementById('test');
            test.innerHTML = '<a class="patientInfo" href="#" id="obsButton">' +
                '<h3 class="name"><strong>Test Patient</strong></h3>' +
                '<h3 class="obs">Obs</h3></a>' +
                '<ul id="obsMenu"><li><a>Obs one</a></li><li><a>Obs two</a></li></ul>' +
                '<select name="chart_select" id="chart_select">' +
                '<option value="ews" selected="selected">NEWS</option>' +
                '<option value="neuro">Neurological observation</option>' +
                '</select>' +
                '<ul class="two-col tabs">' +
                '<li><a href="#graph-content" class="selected tab">Graph</a></li>' +
                '<li><a href="#table-content" class="tab">Table</a></li>' +
                '</ul>' +
                '<div id="graph-content" data-id="1">' +
                '<div id="controls">' +
                '<div id="start">' +
                '<h4>Start date</h4>' +
                '<label for="start_date">' +
                'Date: <input type="date" name="start_date" id="start_date"/>' +
                '</label>' +
                '<label for="start_time">' +
                'Time: <input type="time" name="start_time" id="start_time"/>' +
                '</label>' +
                '</div>' +
                '<div id="end">' +
                '<h4>End date</h4>' +
                '<label for="end_date">' +
                'Date: <input type="date" name="end_date" id="end_date"/>' +
                '</label>' +
                '<label for="end_time">' +
                'Time: <input type="time" name="end_time" id="end_time"/>' +
                '</label>' +
                '</div>' +
                '<div id="range">' +
                '<label for="rangify">' +
                '<h4>Ranged values</h4> <input type="checkbox" name="rangify" id="rangify"/>' +
                '</label>' +
                '</div>' +
                '</div>' +
                '<div id="chart"></div>' +
                '</div>' +
                '<div id="table-content"></div>';
        });

        it('Loads NEWS by default', function() {
            spyOn(NHMobilePatient.prototype, 'call_resource').and.callFake(function(){
               var promise = new Promise();
                var empty_graph = new NHMobileData({
                    status: 'success',
                    title: 'Test Patient',
                    description: 'Observations for Test Patient',
                    data: {
                            obs: []
                    }
                });
                promise.complete(empty_graph);
                return promise;
            });
            spyOn(NHMobilePatient.prototype, 'draw_graph').and.callThrough();
            nhpatient = new NHMobilePatient();
            expect(NHMobilePatient.prototype.draw_graph.calls.mostRecent().args[2]).toBe('ews');
        });

        it('Hides tabs and shows message when no observation data found', function(){
            spyOn(NHMobilePatient.prototype, 'call_resource').and.callFake(function(){
               var promise = new Promise();
                var empty_graph = new NHMobileData({
                    status: 'success',
                    title: 'Test Patient',
                    description: 'Observations for Test Patient',
                    data: {
                            obs: []
                    }
                });
                promise.complete(empty_graph);
                return promise;
            });
            spyOn(NHMobilePatient.prototype, 'draw_graph').and.callThrough();
            nhpatient = new NHMobilePatient();
            expect(NHMobilePatient.prototype.draw_graph).toHaveBeenCalled();
            var tabs = document.getElementsByClassName('tabs');
            expect(tabs[0].style.display).toBe('none');
            var controls = document.getElementById('controls');
            expect(controls.style.display).toBe('none');
            var chart = document.getElementById('chart');
            expect(chart.innerHTML).toBe('<h2>No observation data available for patient</h2>');
        });

        it('Hides tabs when only needs to draw chart or table and not both', function(){
            spyOn(NHMobilePatient.prototype, 'call_resource').and.callFake(function(){
               var promise = new Promise();
                var graph_data = new NHMobileData({
                    status: 'success',
                    title: 'Test Patient',
                    description: 'Observations for Test Patient',
                    data: {
                            obs: [ {
                            respiration_rate: 18,
                            indirect_oxymetry_spo2: 99,
                            body_temperature: 37.5,
                            pulse_rate: 80,
                            blood_pressure_systolic: 120,
                            blood_pressure_diastolic: 80,
                            score: 0,
                            avpu_text: 'A',
                            oxygen_administration_flag: false,
                            flow_rate: false,
                            concentration: false,
                            device_id: false,
                            cpap_peep: false,
                            niv_backup: false,
                            niv_ipap: false,
                            niv_epap: false
                        }]
                    }
                });
                promise.complete(graph_data);
                return promise;
            });
            spyOn(NHMobilePatient.prototype, 'draw_graph').and.callThrough();
            nhpatient = new NHMobilePatient();
            expect(NHMobilePatient.prototype.draw_graph).toHaveBeenCalled();
            var tabs = document.getElementsByClassName('tabs');
            expect(tabs[0].style.display).toBe('none');
            var controls = document.getElementById('controls');
            expect(controls.style.display).toBe('block');
        });

        it('Shows tabs, form controls and chart when observation data is found', function(){
            spyOn(NHMobilePatient.prototype, 'process_request').and.callFake(function(){
                // change obs on endpoint called
                var url = NHMobilePatient.prototype.process_request.calls.mostRecent().args[1];
                var obs = [];
                if(url.indexOf('neuro') > -1){
                    obs = [
                        {
                            respiration_rate: 18,
                            indirect_oxymetry_spo2: 99,
                            body_temperature: 37.5,
                            pulse_rate: 80,
                            blood_pressure_systolic: 120,
                            blood_pressure_diastolic: 80,
                            score: 0,
                            avpu_text: 'A',
                            oxygen_administration_flag: false,
                            flow_rate: false,
                            concentration: false,
                            device_id: false,
                            cpap_peep: false,
                            niv_backup: false,
                            niv_ipap: false,
                            niv_epap: false
                        }
                    ]
                }
               var promise = new Promise();
                var empty_graph = new NHMobileData({
                    status: 'success',
                    title: 'Test Patient',
                    description: 'Observations for Test Patient',
                    data: {
                       obs: obs
                    }
                });
                promise.complete(empty_graph);
                return promise;
            });
            spyOn(NHMobilePatient.prototype, 'change_chart').and.callThrough();
            spyOn(NHMobilePatient.prototype, 'draw_graph').and.callThrough();
            nhpatient = new NHMobilePatient();

            // Initial load with no obs
            expect(NHMobilePatient.prototype.draw_graph).toHaveBeenCalled();
            var tabs = document.getElementsByClassName('tabs');
            expect(tabs[0].style.display).toBe('none');
            var controls = document.getElementById('controls');
            expect(controls.style.display).toBe('none');
            var chart = document.getElementById('chart');
            expect(chart.innerHTML).toBe('<h2>No observation data available for patient</h2>');

            var chart_select = document.getElementById('chart_select');
            chart_select.value = 'neuro';

            var change_event = document.createEvent('CustomEvent');
            change_event.initCustomEvent('change', false, true, false);
            chart_select.dispatchEvent(change_event);

            // After change to obs with data
            expect(NHMobilePatient.prototype.change_chart).toHaveBeenCalled()
            expect(NHMobilePatient.prototype.draw_graph.calls.mostRecent().args[2]).toBe('neuro');
            var tabs = document.getElementsByClassName('tabs');
            expect(tabs[0].style.display).toBe('block');
            var controls = document.getElementById('controls');
            expect(controls.style.display).toBe('block');
            var chart = document.getElementById('chart');
            expect(chart.innerHTML).not.toBe('<h2>No observation data available for patient</h2>');

            chart_select.value = 'ews';

            var change_event = document.createEvent('CustomEvent');
            change_event.initCustomEvent('change', false, true, false);
            chart_select.dispatchEvent(change_event);

            // After change to obs with no data
            expect(NHMobilePatient.prototype.change_chart).toHaveBeenCalled()
            expect(NHMobilePatient.prototype.draw_graph.calls.mostRecent().args[2]).toBe('ews');
            var tabs = document.getElementsByClassName('tabs');
            expect(tabs[0].style.display).toBe('none');
            var controls = document.getElementById('controls');
            expect(controls.style.display).toBe('none');
            var chart = document.getElementById('chart');
            expect(chart.innerHTML).toBe('<h2>No observation data available for patient</h2>');

        });

        it('Fetches data for the selected observation when the \'See observation data for:\' dropdown is changed', function(){
            spyOn(NHMobilePatient.prototype, 'call_resource').and.callFake(function(){
               var promise = new Promise();
                var empty_graph = new NHMobileData({
                    status: 'success',
                    title: 'Test Patient',
                    description: 'Observations for Test Patient',
                    data: {
                            obs: []
                    }
                });
                promise.complete(empty_graph);
                return promise;
            });
            spyOn(NHMobilePatient.prototype, 'change_chart').and.callThrough();
            spyOn(NHMobilePatient.prototype, 'draw_graph').and.callThrough();
            nhpatient = new NHMobilePatient();
            expect(NHMobilePatient.prototype.draw_graph).toHaveBeenCalled();

            var chart_select = document.getElementById('chart_select');
            chart_select.value = 'neuro';

            var change_event = document.createEvent('CustomEvent');
            change_event.initCustomEvent('change', false, true, false);
            chart_select.dispatchEvent(change_event);

            expect(NHMobilePatient.prototype.change_chart).toHaveBeenCalled()
            expect(NHMobilePatient.prototype.draw_graph.calls.mostRecent().args[2]).toBe('neuro')
        });

        it('On receiving data from the server calls the relevant function to draw the charts', function(){
            spyOn(NHMobilePatient.prototype, 'call_resource').and.callFake(function(){
               var promise = new Promise();
                var graph_data = new NHMobileData({
                    status: 'success',
                    title: 'Test Patient',
                    description: 'Observations for Test Patient',
                    data: {
                       obs: [{
                        respiration_rate: 18,
                        indirect_oxymetry_spo2: 99,
                        body_temperature: 37.5,
                        pulse_rate: 80,
                        blood_pressure_systolic: 120,
                        blood_pressure_diastolic: 80,
                        score: 0,
                        avpu_text: 'A',
                        oxygen_administration_flag: false,
                        flow_rate: false,
                        concentration: false,
                        device_id: false,
                        cpap_peep: false,
                        niv_backup: false,
                        niv_ipap: false,
                        niv_epap: false
                    },
                    {
                        respiration_rate: 18,
                        indirect_oxymetry_spo2: 99,
                        body_temperature: 37.5,
                        pulse_rate: 80,
                        blood_pressure_systolic: 120,
                        blood_pressure_diastolic: 80,
                        score: 0,
                        avpu_text: 'A',
                        oxygen_administration_flag: true,
                        flow_rate: 0.5,
                        concentration: false,
                        device_id: [1, 'Test CPAP Device'],
                        cpap_peep: 2,
                        niv_backup: false,
                        niv_ipap: false,
                        niv_epap: false
                    },
                    {
                        respiration_rate: 18,
                        indirect_oxymetry_spo2: 99,
                        body_temperature: 37.5,
                        pulse_rate: 80,
                        blood_pressure_systolic: 120,
                        blood_pressure_diastolic: 80,
                        score: 0,
                        avpu_text: 'A',
                        oxygen_administration_flag: true,
                        flow_rate: false,
                        concentration: 2,
                        device_id: [1, 'Test NIV Device'],
                        cpap_peep: false,
                        niv_backup: 1,
                        niv_ipap: 2,
                        niv_epap: 3
                    }
                    ]
                }});
                promise.complete(graph_data);
                return promise;
            });
            spyOn(window, 'drawEwsChart');
            nhpatient = new NHMobilePatient();
            expect(window.drawEwsChart).toHaveBeenCalled()
        });

        it('Changes the displayed content when I press a tab', function(){
            spyOn(NHMobilePatient.prototype, 'handle_tabs').and.callThrough();
            spyOn(NHMobilePatient.prototype, 'call_resource').and.callFake(function(){
                var promise = new Promise();
                var empty_graph = new NHMobileData({
                    status: 'success',
                    title: 'Test Patient',
                    description: 'Observations for Test Patient',
                    data: {
                        obs: []
                    }});
                promise.complete(empty_graph);
                return promise;
            });
            nhpatient = new NHMobilePatient();
            var test_buttons = document.getElementsByClassName('tab');
            expect(test_buttons[0].classList.contains('selected')).toBe(true);
            expect(test_buttons[1].classList.contains('selected')).toBe(false);
            var click_event1 = document.createEvent('CustomEvent');
            click_event1.initCustomEvent('click', false, true, false);
            test_buttons[1].dispatchEvent(click_event1);
            expect(NHMobilePatient.prototype.handle_tabs).toHaveBeenCalled();
            expect(test_buttons[0].classList.contains('selected')).toBe(false);
            expect(test_buttons[1].classList.contains('selected')).toBe(true);
            expect(document.getElementById('graph-content').style.display).toBe('none');
            expect(document.getElementById('table-content').style.display).toBe('block');
            var click_event = document.createEvent('CustomEvent');
            click_event.initCustomEvent('click', false, true, false);
            test_buttons[0].dispatchEvent(click_event);
            expect(NHMobilePatient.prototype.handle_tabs.calls.count()).toBe(2);
            expect(test_buttons[0].classList.contains('selected')).toBe(true);
            expect(test_buttons[1].classList.contains('selected')).toBe(false);
            expect(document.getElementById('graph-content').style.display).toBe('block');
            expect(document.getElementById('table-content').style.display).toBe('none');
        });

        it('Show the obs list in a modal when I press the obs menu button', function(){
            spyOn(NHMobilePatient.prototype, 'show_obs_menu').and.callThrough();
            spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
            spyOn(NHMobilePatient.prototype, 'draw_graph');
            spyOn(NHMobilePatient.prototype, 'call_resource').and.callFake(function(){
                var promise = new Promise();
                var empty_graph = new NHMobileData({
                    status: 'success',
                    title: 'Test Patient',
                    description: 'Observations for Test Patient',
                    data: {
                        obs: []
                    }});
                promise.complete(empty_graph);
                return promise;
            });
            nhpatient = new NHMobilePatient();
            var test_button = document.getElementsByClassName('obs')[0];
            var click_event = document.createEvent('CustomEvent');
            click_event.initCustomEvent('click', false, true, false);
            test_button.dispatchEvent(click_event);
            var body = document.getElementsByTagName('body')[0];
            expect(NHMobilePatient.prototype.show_obs_menu).toHaveBeenCalled();
            expect(NHMobilePatient.prototype.show_obs_menu.calls.count()).toBe(1);
            expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
            expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('obs_menu');
            expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Pick an observation for ' + patient_info_data.data.full_name);
            expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<ul class="menu"><li><a>Obs one</a></li><li><a>Obs two</a></li></ul>');
        });

        afterEach(function(){
            cleanUp();
            var test = document.getElementById('test');
            test.innerHTML = '';
            if(nhpatient != null){
                nhpatient = null;
            }
        });
    });

    afterEach(function () {
        mobile.urls.base_url = 'http://localhost:8069/mobile/';
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