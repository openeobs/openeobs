/**
 * Created by colinwren on 25/08/15.
 */
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
        var modals = document.getElementsByClassName('modal');
        var covers = document.getElementsByClassName('cover');
        for(var i = 0; i < modals.length; i++){
            var modal = modals[i];
            modal.parentNode.removeChild(modal);
        }
        for(var i = 0; i < covers.length; i++){
            var cover = covers[i];
            cover.parentNode.removeChild(cover);
        }
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
                var modals = document.getElementsByClassName('modal');
                var covers = document.getElementsByClassName('cover');
                for(var i = 0; i < modals.length; i++){
                    var modal = modals[i];
                    modal.parentNode.removeChild(modal);
                }
                for(var i = 0; i < covers.length; i++){
                    var cover = covers[i];
                    cover.parentNode.removeChild(cover);
                }
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
            it('Has a function for displaying the barcode scanning dialog when the scan button is pressed', function(){
               expect(typeof(NHMobileBarcode.prototype.trigger_button_click)).toBe('function');
            });
        });

        describe('Form', function(){
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
        });

        describe('Patient Chart', function(){
             it('Has a function for showing the observation menu when pressing the adhoc observation button', function(){
               expect(typeof(NHMobilePatient.prototype.show_obs_menu)).toBe('function');
            });

            it('Has a function for handling the tabbing behaviour when pressing the tabs', function(){
               expect(typeof(NHMobilePatient.prototype.handle_tabs)).toBe('function');
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