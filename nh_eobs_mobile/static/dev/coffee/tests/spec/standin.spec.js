/**
 * Created by colinwren on 28/08/15.
 */

describe('Stand in Functionality', function(){
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
    });

    afterEach(function(){
       cleanUp();
    });


    describe('Stand-in: Patient Picking', function(){
        var share, claim, all, standin;
        afterEach(function(){
            cleanUp();
        });

        beforeEach(function(){
            spyOn(NHMobileShare.prototype, 'share_button_click').and.callThrough();
            spyOn(NHMobileShare.prototype, 'claim_button_click').and.callThrough();
            spyOn(NHMobileShare.prototype, 'assign_button_click');
            spyOn(NHMobileShare.prototype, 'select_all_patients').and.callThrough();
            spyOn(NHMobileShare.prototype, 'unselect_all_patients').and.callThrough();
            spyOn(NHModal.prototype, 'create_dialog').and.callThrough();

            var test = document.getElementById('test');
            test.innerHTML = '<form id="handover_form">' +
                    '<ul class="tasklist sharelist">' +
                    '<li><a href="#" class="share_all" id="all" mode="select">All</a></li>' +
                    '<li><label><input type="checkbox" id="share_checkbox" name="patient_share_1" value="1" class="patient-share">' +
                    '<div class="level-none block">' +
                    '<div class="task-meta"><div class="task-right"><p class="aside">6:66 hours</p></div>' +
                    '<div class="task-left"><strong>Test, Test</strong><br><em>Bed 1, Ward 1</em></div>' +
                    '</div><div class="task-meta"><div class="taskInfo"><br><br></div></div></label></li>' +
                    '<li><label><input type="checkbox" id="noshare_checkbox" name="patient_share_2" value="2" class="patient-share exclude">' +
                    '<div class="level-none block">' +
                    '<div class="task-meta"><div class="task-right"><p class="aside">6:66 hours</p></div>' +
                    '<div class="task-left"><strong>Test, Test</strong><br><em>Bed 1, Ward 1</em></div>' +
                    '</div><div class="task-meta"><div class="taskInfo"><br><br></div></div></label></li>' +
                    '</ul></form>' +
                    '<a id="share">Share</a><a id="claim">Claim</a>';
            share = document.getElementById('share');
            claim = document.getElementById('claim');
            all = document.getElementById('all');
        });

        it('Has a function for handling a click on the share button', function(){
           expect(typeof(NHMobileShare.prototype.share_button_click)).toBe('function');
        });

        it('Has a function for handling a click on the claim button', function(){
           expect(typeof(NHMobileShare.prototype.claim_button_click)).toBe('function');
        });

        describe('Selecting and pressing the share button', function(){
            beforeEach(function(){
               spyOn(NHMobileShare.prototype, 'process_request').and.callFake(function(){
                    var promise = new Promise();
                    promise.complete([[{'id': 1, 'name': 'Test Nurse', 'patients': 'Test Patient, Test Patient'}]]);
                    return promise;
                });
                standin = new NHMobileShare(share, claim, all);
            });

            it('Shows a modal with a list of colleagues to send a stand in invite to', function(){
                var checkbox = document.getElementById('share_checkbox');
                checkbox.checked = true;
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                share.dispatchEvent(click_event);
                expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
                expect(NHMobileShare.prototype.share_button_click.calls.count()).toBe(1);
                expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('assign_nurse')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Assign patient to colleague')
                var modal_form = '<form id="nurse_list"><ul class="sharelist"><li><input type="checkbox" name="nurse_select_1" class="patient_share_nurse" value="1"/><label for="nurse_select_1">Test Nurse (Test Patient, Test Patient)</label></li></ul><p class="error"></p></form>';
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe(modal_form);
            });

            it('Shows a modal to say we need to select patients when we don\'t select patients', function(){
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                share.dispatchEvent(click_event);
                expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
                expect(NHMobileShare.prototype.share_button_click.calls.count()).toBe(1);
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('invalid_form');
            });
        });

        describe('Selecting and pressing the claim button', function() {
            beforeEach(function () {
                standin = new NHMobileShare(share, claim, all);
            });

            it('Shows a modal asking if user wants to claim patients on click', function(){
                 var checkbox = document.getElementById('share_checkbox');
                checkbox.checked = true;
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                claim.dispatchEvent(click_event);
                expect(NHMobileShare.prototype.claim_button_click).toHaveBeenCalled();
                expect(NHMobileShare.prototype.claim_button_click.calls.count()).toBe(1);
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('claim_patients')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Claim Patients?')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p class="block">Claim patients shared with colleagues</p>');
            });

            it('Shows a modal to say we need to select patients when we don\'t select patients', function(){
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                claim.dispatchEvent(click_event);
                expect(NHMobileShare.prototype.claim_button_click).toHaveBeenCalled();
                expect(NHMobileShare.prototype.claim_button_click.calls.count()).toBe(1);
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('invalid_form');
            });
        });

        describe('Selecting and deselecting all patients using the select all button', function(){
            var standin;
            beforeEach(function () {
                standin = new NHMobileShare(share, claim, all);
            });

             it('Has a function to handle the select all patients in the list', function(){
               expect(typeof(NHMobileShare.prototype.select_all_patients)).toBe('function');
            });

            it('Has a function to handle the unselect all patients in the list', function(){
               expect(typeof(NHMobileShare.prototype.unselect_all_patients)).toBe('function');
            });


            it('Captures and handles all button clicks', function(){
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                all.dispatchEvent(click_event);
                expect(NHMobileShare.prototype.select_all_patients).toHaveBeenCalled();
                expect(NHMobileShare.prototype.select_all_patients.calls.count()).toBe(1);
                var checkbox = document.getElementById('share_checkbox');
                var nocheckbox = document.getElementById('noshare_checkbox');
                expect(checkbox.checked).toBe(true);
                expect(nocheckbox.checked).toBe(false);
                var click_event1 = document.createEvent('CustomEvent');
                click_event1.initCustomEvent('click', false, true, false);
                all.dispatchEvent(click_event1);
                expect(NHMobileShare.prototype.unselect_all_patients).toHaveBeenCalled();
                expect(NHMobileShare.prototype.unselect_all_patients.calls.count()).toBe(1);
                checkbox = document.getElementById('share_checkbox');
                nocheckbox = document.getElementById('noshare_checkbox');
                expect(checkbox.checked).toBe(false);
                expect(nocheckbox.checked).toBe(false);
                var click_event2 = document.createEvent('CustomEvent');
                click_event2.initCustomEvent('click', false, true, false);
                all.dispatchEvent(click_event2);
                expect(NHMobileShare.prototype.select_all_patients).toHaveBeenCalled();
                expect(NHMobileShare.prototype.select_all_patients.calls.count()).toBe(2);
                checkbox = document.getElementById('share_checkbox');
                nocheckbox = document.getElementById('noshare_checkbox');
                expect(checkbox.checked).toBe(true);
                expect(nocheckbox.checked).toBe(false);
            });
        });
    });

    it('Has a function to handle the assign button click', function(){
       expect(typeof(NHMobileShare.prototype.assign_button_click)).toBe('function');
    });

    it('Has a function to handle the claim patients button click', function(){
       expect(typeof(NHMobileShare.prototype.claim_patients_click)).toBe('function');
    });

});