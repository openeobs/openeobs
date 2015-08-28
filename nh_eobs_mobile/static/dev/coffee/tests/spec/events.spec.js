/**
 * Created by colinwren on 25/08/15.
 */

function cleanUp(){
    var modals = document.getElementsByClassName('dialog');
    var full_modals = document.getElementsByClassName('full-modal');
    var covers = document.getElementsByClassName('cover');
    for(var i = 0; i < modals.length; i++){
        var modal = modals[i];
        modal.parentNode.removeChild(modal);
    }
    for(var i = 0; i < covers.length; i++){
        var cover = covers[i];
        cover.parentNode.removeChild(cover);
    }
    for(var i = 0; i < full_modals.length; i++){
        var full_modal = full_modals[i];
        full_modal.parentNode.removeChild(full_modal);
    }
    var test = document.getElementById('test');
    test.innerHTML = '';
}

describe("Event Handling", function(){
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
        cleanUp();
    });
    afterEach(function(){
        var test = document.getElementById('test');
        if (test != null) {
            test.parentNode.removeChild(test);
        }
    });

    it('Has a function to help manage events', function(){
       //expect(typeof(NHLib.prototype.handle_event)).toBe('function');
        expect(true).toBe(true);
    });

    describe('Click events', function(){
        beforeEach(function(){
            var test = document.getElementById('test');
            test.innerHTML = '<a href="#" id="test_button">Test</a>';
        });

        afterEach(function(){
            var test = document.getElementById('test');
            test.innerHTML = '';
        });

        it('HTMLElement has onclick property', function(){
            var test_button = document.getElementById('test_button');
            expect(typeof(test_button.onclick)).toBe('object');
        });

        it('HTMLElement has addEventListener property', function(){
            var test_button = document.getElementById('test_button');
            expect(typeof(test_button.addEventListener)).toBe('function');
        });

        describe('Patient Information', function(){
            var mobile;
            afterEach(function(){
                cleanUp();
            });

            beforeEach(function(){
                var test = document.getElementById('test');
                test.innerHTML = '';
                spyOn(NHMobile.prototype, 'fullscreen_patient_info').and.callThrough();
                spyOn(NHMobile.prototype, 'close_fullscreen_patient_info');
                NHMobile.prototype.fullscreen_patient_info.calls.reset();
                mobile = new NHMobile();
                spyOn(NHMobile.prototype, 'process_request').and.callFake(function(){
                   var promise = new Promise();
                   promise.complete([{
                        'full_name': 'Test Patient',
                        'gender': 'M',
                        'dob': '1988-01-12 00:00',
                        'location': 'Bed 1',
                        'ews_score': 1,
                        'other_identifier': '012345678',
                        'patient_identifier': 'NHS012345678'
                    }]);
                   return promise;
                });
            });

            it('Has a function for displaying fullscreen patient info when button is pressed', function(){
                expect(typeof(NHMobile.prototype.fullscreen_patient_info)).toBe('function');
            });

            it('Has a function for removing fullscreen patient info when close button is pressed', function(){
               expect(typeof(NHMobile.prototype.close_fullscreen_patient_info)).toBe('function');
            });

            it('Captures and handles the Patient Observation button being pressed', function(){
                mobile.get_patient_info(3, mobile);
                var body = document.getElementsByTagName('body')[0];
                var full_obs_button = document.getElementById('patient_obs_fullscreen');
                expect(full_obs_button).not.toBe(null);
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                full_obs_button.dispatchEvent(click_event);
                expect(NHMobile.prototype.fullscreen_patient_info).toHaveBeenCalled();
                expect(NHMobile.prototype.fullscreen_patient_info.calls.count()).toBe(1);
            });

            it('Captures and handles the close Patient Observation fullscreen modal button being pressed', function(){
                mobile.get_patient_info(3, mobile);
                var body = document.getElementsByTagName('body')[0];
                var full_obs_button = document.getElementById('patient_obs_fullscreen');
                expect(full_obs_button).not.toBe(null);
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                full_obs_button.dispatchEvent(click_event);
                expect(NHMobile.prototype.fullscreen_patient_info).toHaveBeenCalled();
                expect(NHMobile.prototype.fullscreen_patient_info.calls.count()).toBe(1);
                var close_button = document.getElementById('closeFullModal');
                expect(close_button).not.toBe(null);
                var click_close_event = document.createEvent('CustomEvent');
                click_close_event.initCustomEvent('click', false, true, false);
                close_button.dispatchEvent(click_close_event);
                expect(NHMobile.prototype.close_fullscreen_patient_info).toHaveBeenCalled();
                expect(NHMobile.prototype.close_fullscreen_patient_info.calls.count()).toBe(1);
            });
        });

        describe('Barcode Scanning', function(){
            var mobile;
            afterEach(function(){
                cleanUp();
            });

            beforeEach(function(){
                spyOn(NHMobileBarcode.prototype, 'trigger_button_click');
                var test_button = document.getElementById('test_button');
                mobile = new NHMobileBarcode(test_button);
            });

            it('Has a function for displaying the barcode scanning dialog when the scan button is pressed', function(){
               expect(typeof(NHMobileBarcode.prototype.trigger_button_click)).toBe('function');
            });

            it('Captures and handles the button click for the barcode scanner', function(){
                var test_button = document.getElementById('test_button');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                test_button.dispatchEvent(click_event);
                expect(NHMobileBarcode.prototype.trigger_button_click).toHaveBeenCalled();
                expect(NHMobileBarcode.prototype.trigger_button_click.calls.count()).toBe(1);
            });
        });

        describe('Form', function(){
            var mobile;
            afterEach(function(){
                cleanUp();

            });

            beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit');
                spyOn(NHMobileForm.prototype, 'cancel_notification');
                spyOn(NHMobileForm.prototype, 'trigger_actions');
                spyOn(NHMobileForm.prototype, 'show_reference');
                spyOn(NHMobileForm.prototype, 'get_patient_info');
                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                        '<input type="submit" value="Test Submit" id="submit">' +
                        '<input type="reset" value="Test Reset" id="reset">' +
                        '<input type="radio" value="test_radio" id="radio">' +
                        '<button id="reference">Test Button</button>' +
                        '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                        '</form>'
                mobile = new NHMobileForm();
            });

            it('Has a function for sending form data to a server when the submit button is pressed', function(){
               expect(typeof(NHMobileForm.prototype.submit)).toBe('function');
            });

            it('Has a function for sending form data to a server when the reset button is pressed', function(){
               expect(typeof(NHMobileForm.prototype.cancel_notification)).toBe('function');
            });

            it('Has a function for triggering actions on other inputs when a radio button is clicked', function(){
               expect(typeof(NHMobileForm.prototype.trigger_actions)).toBe('function');
            });

             it('Has a function for showing a reference popup when a reference button is clicked', function(){
               expect(typeof(NHMobileForm.prototype.show_reference)).toBe('function');
            });

            it('Has a function for showing patient information when pressing the patient name on a form', function(){
               expect(typeof(NHMobileForm.prototype.get_patient_info)).toBe('function');
            });

            it('Captures and handles form submission button click', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var test_button = document.getElementById('submit');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                test_button.dispatchEvent(click_event);
                expect(NHMobileForm.prototype.submit).toHaveBeenCalled();
                expect(NHMobileForm.prototype.submit.calls.count()).toBe(1);
            });

            it('Captures and handles form reset button click', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('reset', function(){
                    event.preventDefault();
                    return false;
                });
                var test_button = document.getElementById('reset');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                test_button.dispatchEvent(click_event);
                expect(NHMobileForm.prototype.cancel_notification).toHaveBeenCalled();
                expect(NHMobileForm.prototype.cancel_notification.calls.count()).toBe(1);
            });

            it('Captures and handles form radio input click', function(){
                var test_button = document.getElementById('radio');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                test_button.dispatchEvent(click_event);
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(NHMobileForm.prototype.trigger_actions.calls.count()).toBe(1);
            });

            it('Captures and handles form reference button click', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var test_button = document.getElementById('reference');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                test_button.dispatchEvent(click_event);
                expect(NHMobileForm.prototype.show_reference).toHaveBeenCalled();
                expect(NHMobileForm.prototype.show_reference.calls.count()).toBe(1);
            });

            it('Captures and handles patient name click', function(){
                var test_button_parent = document.getElementById('patientName');
                var test_button = test_button_parent.getElementsByTagName('a')[0];
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                test_button.dispatchEvent(click_event);
                expect(NHMobileForm.prototype.get_patient_info).toHaveBeenCalled();
                expect(NHMobileForm.prototype.get_patient_info.calls.count()).toBe(1);
            });
        });

        describe('Patient Chart', function(){

            afterEach(function(){
                cleanUp();
            });

            beforeEach(function(){
                spyOn(NHMobilePatient.prototype, 'show_obs_menu');
                spyOn(NHMobilePatient.prototype, 'handle_tabs');
                spyOn(NHMobilePatient.prototype, 'call_resource').and.callFake(function(){
                   var promise = new Promise();
                    promise.complete([{'obs': []}]);
                    return promise;
                });
                var test = document.getElementById('test');
                test.innerHTML = '<a href="#" class="obs">Obs</a>' +
                    '<ul id="obsMenu"><li><a>Obs one</a></li><li><a>Obs two</a></li></ul>' +
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
                mobile = new NHMobilePatient();
            });

            it('Has a function for showing the observation menu when pressing the adhoc observation button', function(){
               expect(typeof(NHMobilePatient.prototype.show_obs_menu)).toBe('function');
            });

            it('Has a function for handling the tabbing behaviour when pressing the tabs', function(){
               expect(typeof(NHMobilePatient.prototype.handle_tabs)).toBe('function');
            });

            it('Captures and handles Take Observation menu button click', function(){
                var test_button = document.getElementsByClassName('obs')[0];
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                test_button.dispatchEvent(click_event);
                expect(NHMobilePatient.prototype.show_obs_menu).toHaveBeenCalled();
                expect(NHMobilePatient.prototype.show_obs_menu.calls.count()).toBe(1);
            });

            it('Captures and handles tab click', function(){
                var test_buttons = document.getElementsByClassName('tab');
                var click_event1 = document.createEvent('CustomEvent');
                click_event1.initCustomEvent('click', false, true, false);
                test_buttons[0].dispatchEvent(click_event1);
                expect(NHMobilePatient.prototype.handle_tabs).toHaveBeenCalled();
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                test_buttons[1].dispatchEvent(click_event);
                expect(NHMobilePatient.prototype.handle_tabs.calls.count()).toBe(2);
            });
        });

        describe('Stand-in: Patient Picking', function(){
            var share, claim, all;
            afterEach(function(){
                cleanUp();
            });

            beforeEach(function(){
                spyOn(NHMobileShare.prototype, 'share_button_click');
                spyOn(NHMobileShare.prototype, 'claim_button_click');
                spyOn(NHMobileShare.prototype, 'assign_button_click');
                spyOn(NHMobileShare.prototype, 'select_all_patients');
                spyOn(NHMobileShare.prototype, 'unselect_all_patients');
                var test = document.getElementById('test');
                test.innerHTML = '<a id="share">Share</a><a id="claim">Claim</a><a id="all" mode="select">All</a>';
                share = document.getElementById('share');
                claim = document.getElementById('claim');
                all = document.getElementById('all');
                mobile = new NHMobileShare(share, claim, all);
            });

            it('Has a function for handling a click on the share button', function(){
               expect(typeof(NHMobileShare.prototype.share_button_click)).toBe('function');
            });

            it('Has a function for handling a click on the claim button', function(){
               expect(typeof(NHMobileShare.prototype.claim_button_click)).toBe('function');
            });

            //it('Has a function for handling a click on the invite', function(){
            //   expect(typeof(NHMobileShare.prototype.assign_button_click)).toBe('function');
            //});

            it('Captures and handles share button click', function(){
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                share.dispatchEvent(click_event);
                expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
                expect(NHMobileShare.prototype.share_button_click.calls.count()).toBe(1);
            });

            it('Captures and handles claim button click', function(){
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                claim.dispatchEvent(click_event);
                expect(NHMobileShare.prototype.claim_button_click).toHaveBeenCalled();
                expect(NHMobileShare.prototype.claim_button_click.calls.count()).toBe(1);
            });

            it('Captures and handles all button clicks', function(){
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                all.dispatchEvent(click_event);
                expect(NHMobileShare.prototype.select_all_patients).toHaveBeenCalled();
                expect(NHMobileShare.prototype.select_all_patients.calls.count()).toBe(1);
                var click_event1 = document.createEvent('CustomEvent');
                click_event1.initCustomEvent('click', false, true, false);
                all.dispatchEvent(click_event1);
                expect(NHMobileShare.prototype.unselect_all_patients).toHaveBeenCalled();
                expect(NHMobileShare.prototype.unselect_all_patients.calls.count()).toBe(1);
                var click_event2 = document.createEvent('CustomEvent');
                click_event2.initCustomEvent('click', false, true, false);
                all.dispatchEvent(click_event2);
                expect(NHMobileShare.prototype.select_all_patients).toHaveBeenCalled();
                expect(NHMobileShare.prototype.select_all_patients.calls.count()).toBe(2);
            });
        });

        describe('Stand-in: Invitation', function(){
            afterEach(function(){
                cleanUp();
            });

            beforeEach(function(){
                spyOn(NHMobileShareInvite.prototype, 'handle_invite_click');
                var test = document.getElementById('test');
                test.innerHTML = '<ul id="list"><li class="share_invite">Invite 1</li><li class="share_invite">Invite 2</li></ul>';
                var list = document.getElementById('list');
                mobile = new NHMobileShareInvite(list);
            });

            it('Has a function for handling a click on an invite', function(){
               expect(typeof(NHMobileShareInvite.prototype.handle_invite_click)).toBe('function');
            });

            it('Captures and handles all button clicks', function(){
                var invites = document.getElementsByClassName('share_invite');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                invites[0].dispatchEvent(click_event);
                expect(NHMobileShareInvite.prototype.handle_invite_click).toHaveBeenCalled();
                expect(NHMobileShareInvite.prototype.handle_invite_click.calls.count()).toBe(1);
                var click_event1 = document.createEvent('CustomEvent');
                click_event1.initCustomEvent('click', false, true, false);
                invites[1].dispatchEvent(click_event1);
                expect(NHMobileShareInvite.prototype.handle_invite_click).toHaveBeenCalled();
                expect(NHMobileShareInvite.prototype.handle_invite_click.calls.count()).toBe(2);
            });
        });

        describe('Modal', function(){
            afterEach(function(){
                cleanUp();
            });

            beforeEach(function(){
                spyOn(NHModal.prototype, 'handle_button_events');
                var body = document.getElementsByTagName('body')[0];
                new NHModal('test', 'Test', '<p>Test</p>', [
                    '<a data-action="close" id="close">Close</a>'
                ], 0, body);
            });

            it('Has a function for handling a click on a modal cover', function(){
               expect(typeof(NHModal.prototype.handle_button_events)).toBe('function');
            });

            it('Has a function for handling a click on a modal option button', function(){
               expect(typeof(NHModal.prototype.handle_button_events)).toBe('function');
            });

            it('Captures and handles cover click', function(){
                var cover = document.getElementsByClassName('cover')[0];
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                cover.dispatchEvent(click_event);
                expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
                expect(NHModal.prototype.handle_button_events.calls.count()).toBe(1);
            });

            it('Captures and handles cover click', function(){
                var close = document.getElementById('close');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                close.dispatchEvent(click_event);
                expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
                expect(NHModal.prototype.handle_button_events.calls.count()).toBe(1);
            });
        });
    });

    describe('Change events', function(){
        afterEach(function(){
            cleanUp();
        });

        beforeEach(function(){
            var test = document.getElementById('test');
            test.innerHTML = '';
        });

        describe('Form', function(){

            afterEach(function(){
                cleanUp();
            });

            beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'validate');
                spyOn(NHMobileForm.prototype, 'trigger_actions');
                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                    '<input type="number" id="number">' +
                    '<select id="select"><option value="">Please Select</option><option value="test">Test</option></select>' +
                    '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                    '</form>';
                mobile = new NHMobileForm();
            });

            it('Has a function for validating form input when a number input is changed', function(){
               expect(typeof(NHMobileForm.prototype.validate)).toBe('function');
            });

            it('Has a function for triggering actions on other inputs when a number input is changed', function(){
               expect(typeof(NHMobileForm.prototype.trigger_actions)).toBe('function');
            });

            it('Has a function for triggering actions on other inputs when a select box is changed', function(){
               expect(typeof(NHMobileForm.prototype.trigger_actions)).toBe('function');
            });

            it('Captures and handles the change event when a number input it changed', function(){
                var test_input = document.getElementById('number');
                test_input.value = 666;
                var change_event = document.createEvent('CustomEvent');
                change_event.initCustomEvent('change', false, true, false);
                test_input.dispatchEvent(change_event);
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(NHMobileForm.prototype.validate.calls.count()).toBe(1);
                expect(NHMobileForm.prototype.trigger_actions.calls.count()).toBe(1);
            });

            it('Captures and handles the change event when a number input it changed', function(){
                var test_input = document.getElementById('select');
                test_input.value = 'test';
                var change_event = document.createEvent('CustomEvent');
                change_event.initCustomEvent('change', false, true, false);
                test_input.dispatchEvent(change_event);
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(NHMobileForm.prototype.trigger_actions.calls.count()).toBe(1);
            });
        });
    });

    describe('Key events', function(){
        beforeEach(function(){
            var test = document.getElementById('test');
            test.innerHTML = '<a id="test_button">Test</a><textarea id="test_textarea"></textarea>';
        });

        afterEach(function(){
            var test = document.getElementById('test');
            test.innerHTML = '';
        });

        it('HTMLElement has onkeydown property', function(){
            var test_textarea = document.getElementById('test_textarea');
            expect(typeof(test_textarea.onkeydown)).toBe('object');
        });

        it('HTMLElement has onkeypress property', function(){
            var test_textarea = document.getElementById('test_textarea');
            expect(typeof(test_textarea.onkeypress)).toBe('object');
        });

        it('HTMLElement has addEventListener property', function(){
            var test_textarea = document.getElementById('test_textarea');
            expect(typeof(test_textarea.addEventListener)).toBe('function');
        });

        describe('Barcode Scanning', function(){
            var mobile;
            afterEach(function(){
                jasmine.clock().uninstall();
                cleanUp();
            });

            beforeEach(function(){
                spyOn(NHMobileBarcode.prototype, 'trigger_button_click').and.callThrough();
                spyOn(NHMobileBarcode.prototype, 'barcode_scanned');
                spyOn(NHMobile.prototype, 'process_request');
                var test_button = document.getElementById('test_button');
                mobile = new NHMobileBarcode(test_button);
                jasmine.clock().install();
            });

            it('Has a function for sending the scanned patient ID to the server on the MioCare sending the finish key', function(){
                expect(typeof(NHMobileBarcode.prototype.barcode_scanned)).toBe('function');
            });

            it('Captures and handles the keypress event for keyCode 0 for the barcode scanner', function(){
                var test_button = document.getElementById('test_button');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                test_button.dispatchEvent(click_event);
                expect(NHMobileBarcode.prototype.trigger_button_click).toHaveBeenCalled();
                expect(NHMobileBarcode.prototype.trigger_button_click.calls.count()).toBe(1);
                var test_textarea = document.getElementsByClassName('barcode_scan')[0];
                test_textarea.value = 'this is a test';
                var key_event = document.createEvent('CustomEvent');
                key_event.initCustomEvent('keypress', false, true, false);
                key_event.keyCode = 0;
                test_textarea.dispatchEvent(key_event);
                expect(NHMobileBarcode.prototype.barcode_scanned).toHaveBeenCalled();
                expect(NHMobileBarcode.prototype.barcode_scanned.calls.count()).toBe(1);
            });

            it('Captures and handles the keypress event for keyCode 13 for the barcode scanner', function(){
                var test_button = document.getElementById('test_button');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                test_button.dispatchEvent(click_event);
                expect(NHMobileBarcode.prototype.trigger_button_click).toHaveBeenCalled();
                expect(NHMobileBarcode.prototype.trigger_button_click.calls.count()).toBe(1);
                var test_textarea = document.getElementsByClassName('barcode_scan')[0];
                test_textarea.value = 'this is a test';
                var key_event = document.createEvent('CustomEvent');
                key_event.initCustomEvent('keypress', false, true, false);
                key_event.keyCode = 13;
                test_textarea.dispatchEvent(key_event);
                expect(NHMobileBarcode.prototype.barcode_scanned).toHaveBeenCalled();
                expect(NHMobileBarcode.prototype.barcode_scanned.calls.count()).toBe(1);
            });

            it('Captures and handles the keypress event for keyCode 116 for the barcode scanner', function(){
                var test_button = document.getElementById('test_button');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                test_button.dispatchEvent(click_event);
                expect(NHMobileBarcode.prototype.trigger_button_click).toHaveBeenCalled();
                expect(NHMobileBarcode.prototype.trigger_button_click.calls.count()).toBe(1);
                var test_textarea = document.getElementsByClassName('barcode_scan')[0];
                test_textarea.value = 'this is a test';
                var key_event = document.createEvent('CustomEvent');
                key_event.initCustomEvent('keypress', false, true, false);
                key_event.keyCode = 116;
                test_textarea.dispatchEvent(key_event);
                expect(NHMobileBarcode.prototype.barcode_scanned).toHaveBeenCalled();
                expect(NHMobileBarcode.prototype.barcode_scanned.calls.count()).toBe(1);
            });

            it('Captures and handles the keydown event for keyCode 0 for the barcode scanner', function(){
                var test_button = document.getElementById('test_button');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                test_button.dispatchEvent(click_event);
                expect(NHMobileBarcode.prototype.trigger_button_click).toHaveBeenCalled();
                expect(NHMobileBarcode.prototype.trigger_button_click.calls.count()).toBe(1);
                var test_textarea = document.getElementsByClassName('barcode_scan')[0];
                test_textarea.value = 'this is a test';
                var key_event = document.createEvent('CustomEvent');
                key_event.initCustomEvent('keydown', false, true, false);
                key_event.keyCode = 0;
                test_textarea.dispatchEvent(key_event);
                jasmine.clock().tick(1500);
                expect(NHMobileBarcode.prototype.barcode_scanned).toHaveBeenCalled();
                expect(NHMobileBarcode.prototype.barcode_scanned.calls.count()).toBe(1);
            });

            it('Captures and handles the keydown event for keyCode 13 for the barcode scanner', function(){
                var test_button = document.getElementById('test_button');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                test_button.dispatchEvent(click_event);
                expect(NHMobileBarcode.prototype.trigger_button_click).toHaveBeenCalled();
                expect(NHMobileBarcode.prototype.trigger_button_click.calls.count()).toBe(1);
                var test_textarea = document.getElementsByClassName('barcode_scan')[0];
                test_textarea.value = 'this is a test';
                var key_event = document.createEvent('CustomEvent');
                key_event.initCustomEvent('keydown', false, true, false);
                key_event.keyCode = 13;
                test_textarea.dispatchEvent(key_event);
                jasmine.clock().tick(1500);
                expect(NHMobileBarcode.prototype.barcode_scanned).toHaveBeenCalled();
                expect(NHMobileBarcode.prototype.barcode_scanned.calls.count()).toBe(1);
            });

            it('Captures and handles the keydown event for keyCode 116 for the barcode scanner', function(){
                var test_button = document.getElementById('test_button');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                test_button.dispatchEvent(click_event);
                expect(NHMobileBarcode.prototype.trigger_button_click).toHaveBeenCalled();
                expect(NHMobileBarcode.prototype.trigger_button_click.calls.count()).toBe(1);
                var test_textarea = document.getElementsByClassName('barcode_scan')[0];
                test_textarea.value = 'this is a test';
                var key_event = document.createEvent('CustomEvent');
                key_event.initCustomEvent('keydown', false, true, false);
                key_event.keyCode = 116;
                test_textarea.dispatchEvent(key_event);
                jasmine.clock().tick(1500);
                expect(NHMobileBarcode.prototype.barcode_scanned).toHaveBeenCalled();
                expect(NHMobileBarcode.prototype.barcode_scanned.calls.count()).toBe(1);
            });
        });


    });

    describe('Messaging events', function(){
        afterEach(function(){
            cleanUp();
        });

        beforeEach(function(){
            var test = document.getElementById('test');
            test.innerHTML = '';
        });

        describe('Form', function() {

            afterEach(function () {
                cleanUp();
            });

            beforeEach(function () {
                spyOn(NHMobileForm.prototype, 'handle_timeout');
                spyOn(NHMobileForm.prototype, 'process_post_score_submit');
                spyOn(NHMobileForm.prototype, 'process_partial_submit');
                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                    '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                    '</form>';
                mobile = new NHMobileForm();
            });

            it('Has a function for handling a form_timeout event', function(){
               expect(typeof(NHMobileForm.prototype.handle_timeout)).toBe('function');
            });

            it('Has a function for handling a submission after a score has been generated', function(){
               expect(typeof(NHMobileForm.prototype.process_post_score_submit)).toBe('function');
            });

            it('Has a function for handling a partial observation submission', function(){
               expect(typeof(NHMobileForm.prototype.process_partial_submit)).toBe('function');
            });

            it('Capture and handle form timeout event', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var change_event = document.createEvent('CustomEvent');
                change_event.initCustomEvent('form_timeout', false, true, false);
                document.dispatchEvent(change_event);
                expect(NHMobileForm.prototype.handle_timeout).toHaveBeenCalled();
            });

            it('Capture and handle post_score_submit event', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var change_event = document.createEvent('CustomEvent');
                change_event.initCustomEvent('post_score_submit', false, true, false);
                document.dispatchEvent(change_event);
                expect(NHMobileForm.prototype.process_post_score_submit).toHaveBeenCalled();
                expect(NHMobileForm.prototype.process_post_score_submit.calls.count()).toBe(1);
            });

            it('Capture and handle partial_submit event', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var change_event = document.createEvent('CustomEvent');
                change_event.initCustomEvent('partial_submit', false, true, false);
                document.dispatchEvent(change_event);
                expect(NHMobileForm.prototype.process_partial_submit).toHaveBeenCalled();
                expect(NHMobileForm.prototype.process_partial_submit.calls.count()).toBe(1);
            });
        });

        describe('Stand-in: Patient Picking', function(){
            var share, claim, all;
            afterEach(function(){
                cleanUp();
            });

            beforeEach(function(){
                spyOn(NHMobileShare.prototype, 'assign_button_click');
                spyOn(NHMobileShare.prototype, 'claim_patients_click');
                spyOn(NHMobile.prototype, 'process_request');
                var test = document.getElementById('test');
                test.innerHTML = '<a id="share">Share</a><a id="claim">Claim</a><a id="all" mode="select">All</a>';
                share = document.getElementById('share');
                claim = document.getElementById('claim');
                all = document.getElementById('all');
                mobile = new NHMobileShare(share, claim, all);
            });

            it('Has a function for handling a call back for assign_nurse', function(){
               expect(typeof(NHMobileShare.prototype.assign_button_click)).toBe('function');
            });

            it('Has a function for handling a call back for claim_patients', function(){
               expect(typeof(NHMobileShare.prototype.claim_patients_click)).toBe('function');
            });

            it('Captures and handles assign_nurse event', function(){
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('assign_nurse', false, true, false);
                document.dispatchEvent(click_event);
                expect(NHMobileShare.prototype.assign_button_click).toHaveBeenCalled();
                expect(NHMobileShare.prototype.assign_button_click.calls.count()).toBe(1);
            });

            it('Captures and handles claim_patients event', function(){
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('claim_patients', false, true, false);
                document.dispatchEvent(click_event);
                expect(NHMobileShare.prototype.claim_patients_click).toHaveBeenCalled();
                expect(NHMobileShare.prototype.claim_patients_click.calls.count()).toBe(1);
            });

        });

        describe('Stand-in: Invitation', function(){
            afterEach(function(){
                cleanUp();
            });

            beforeEach(function(){
                spyOn(NHMobileShareInvite.prototype, 'handle_accept_button_click');
                spyOn(NHMobileShareInvite.prototype, 'handle_reject_button_click');
                spyOn(NHMobile.prototype, 'process_request');
                var test = document.getElementById('test');
                test.innerHTML = '<ul id="list"><li class="share_invite">Invite 1</li><li class="share_invite">Invite 2</li></ul>';
                var list = document.getElementById('list');
                mobile = new NHMobileShareInvite(list);
            });

            it('Has a function for handling a call back for accept_invite', function(){
               expect(typeof(NHMobileShareInvite.prototype.handle_accept_button_click)).toBe('function');
            });

            it('Has a function for handling a call back for reject_invite', function(){
               expect(typeof(NHMobileShareInvite.prototype.handle_reject_button_click)).toBe('function');
            });

            it('Captures and handles accept_invite event', function(){
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('accept_invite', false, true, false);
                document.dispatchEvent(click_event);
                expect(NHMobileShareInvite.prototype.handle_accept_button_click).toHaveBeenCalled();
                expect(NHMobileShareInvite.prototype.handle_accept_button_click.calls.count()).toBe(1);
            });

            it('Captures and handles reject_invite event', function(){
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('reject_invite', false, true, false);
                document.dispatchEvent(click_event);
                expect(NHMobileShareInvite.prototype.handle_reject_button_click).toHaveBeenCalled();
                expect(NHMobileShareInvite.prototype.handle_reject_button_click.calls.count()).toBe(1);
            });
        });
    });
});