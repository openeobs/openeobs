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

    it('Has a function for sending the scanned patient ID to the server on the MioCare sending the finish key', function(){
        expect(typeof(NHMobileBarcode.prototype.barcode_scanned)).toBe('function');
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

    it('Has a function for handling a form_timeout event', function(){
       expect(typeof(NHMobileForm.prototype.handle_timeout)).toBe('function');
    });

    it('Has a function for handling a submission after a score has been generated', function(){
       expect(typeof(NHMobileForm.prototype.process_post_score_submit)).toBe('function');
    });

    it('Has a function for handling a partial observation submission', function(){
       expect(typeof(NHMobileForm.prototype.process_partial_submit)).toBe('function');
    });

    it('Has a function for handling a call back for assign_nurse', function(){
       expect(typeof(NHMobileShare.prototype.assign_button_click)).toBe('function');
    });

    it('Has a function for handling a call back for claim_patients', function(){
       expect(typeof(NHMobileShare.prototype.claim_patients_click)).toBe('function');
    });

    it('Has a function for handling a call back for accept_invite', function(){
       expect(typeof(NHMobileShareInvite.prototype.handle_accept_button_click)).toBe('function');
    });

    it('Has a function for handling a call back for reject_invite', function(){
       expect(typeof(NHMobileShareInvite.prototype.handle_reject_button_click)).toBe('function');
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
                var test = document.getElementById('test');
                test.innerHTML = '<a class="obs">Test</a><ul id="obsMenu"><li><a>Test Observation</a></li></ul>' +
                    '<ul class="tabs"><li><a class="tab">One</a></li><li><a class="tab">Two</a></li></ul><div id="table-content"></div><div id="graph-content" data-id="3"></div>';
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

        describe('Stand-in', function(){
            it('Has a function for handling a click on the share button', function(){
               expect(typeof(NHMobileShare.prototype.share_button_click)).toBe('function');
            });

            it('Has a function for handling a click on the claim button', function(){
               expect(typeof(NHMobileShare.prototype.claim_button_click)).toBe('function');
            });

            it('Has a function for handling a click on the invite', function(){
               expect(typeof(NHMobileShare.prototype.assign_button_click)).toBe('function');
            });
        });

        describe('Modal', function(){
            it('Has a function for handling a click on a modal cover', function(){
               expect(typeof(NHModal.prototype.handle_button_events)).toBe('function');
            });

            it('Has a function for handling a click on a modal option button', function(){
               expect(typeof(NHModal.prototype.handle_button_events)).toBe('function');
            });
        });
    });

    describe('Change events', function(){

    });

    describe('Key events', function(){

    });

    describe('Messaging events', function(){

    });
});