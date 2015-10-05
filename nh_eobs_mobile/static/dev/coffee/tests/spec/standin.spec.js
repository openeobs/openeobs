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

    it('Has functionality for asking colleagues to stand in for you', function(){
       expect(typeof(NHMobileShare.prototype)).toBe('object');
    });

    it('Has functionality for accepting or rejecting stand in requests', function(){
       expect(typeof(NHMobileShareInvite.prototype)).toBe('object');
    });

    describe('Stand-in: Patient Picking', function(){
        var share, claim, all, standin;
        afterEach(function(){
            cleanUp();
        });

        beforeEach(function(){
            spyOn(NHMobileShare.prototype, 'share_button_click').and.callThrough();
            spyOn(NHMobileShare.prototype, 'claim_button_click').and.callThrough();
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
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p>Claim patients shared with colleagues</p>');
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

    describe('Stand-in: Sharing & Claiming Patients', function(){
        var share, claim, all, standin;
        afterEach(function(){
            cleanUp();
        });

        beforeEach(function(){
            spyOn(NHMobileShare.prototype, 'share_button_click').and.callThrough();
            spyOn(NHMobileShare.prototype, 'claim_button_click').and.callThrough();
            spyOn(NHMobileShare.prototype, 'assign_button_click').and.callThrough();
            spyOn(NHMobileShare.prototype, 'claim_patients_click').and.callThrough();
            spyOn(NHModal.prototype, 'create_dialog').and.callThrough();

            var test = document.getElementById('test');
            test.innerHTML = '<form id="handover_form">' +
                    '<ul class="tasklist sharelist">' +
                    '<li><a href="#" class="share_all" id="all" mode="select">All</a></li>' +
                    '<li><label><input type="checkbox" id="share_checkbox" name="patient_share_1" value="1" class="patient-share">' +
                    '<div class="level-none block">' +
                    '<div class="task-meta"><div class="task-right"><p class="aside">6:66 hours</p></div>' +
                    '<div class="task-left"><strong>Test, Test</strong><br><em>Bed 1, Ward 1</em></div>' +
                    '</div><div class="task-meta"><div class="taskInfo" id="clean_shared"><br><br></div></div></label></li>' +
                    '<li><label><input type="checkbox" id="shared_checkbox" name="patient_share_2" value="2" class="patient-share">' +
                    '<div class="level-none block">' +
                    '<div class="task-meta"><div class="task-right"><p class="aside">6:66 hours</p></div>' +
                    '<div class="task-left"><strong>Test, Test</strong><br><em>Bed 1, Ward 1</em></div>' +
                    '</div><div class="task-meta"><div class="taskInfo" id="dirty_shared">Shared with: Existing Nurse</div></div></label></li>' +
                    '<li><label><input type="checkbox" id="noshare_checkbox" name="patient_share_3" value="3" class="patient-share">' +
                    '<div class="level-none block">' +
                    '<div class="task-meta"><div class="task-right"><p class="aside">6:66 hours</p></div>' +
                    '<div class="task-left"><strong>Test, Test</strong><br><em>Bed 1, Ward 1</em></div>' +
                    '</div><div class="task-meta"><div class="taskInfo" id="no_shared"><br><br></div></div></label></li>' +
                    '</ul></form>' +
                    '<a id="share">Share</a><a id="claim">Claim</a>';
            share = document.getElementById('share');
            claim = document.getElementById('claim');
            all = document.getElementById('all');
        });

        it('Has a function to handle the assign button click', function(){
           expect(typeof(NHMobileShare.prototype.assign_button_click)).toBe('function');
        });

        it('Has a function to handle the claim patients button click', function(){
           expect(typeof(NHMobileShare.prototype.claim_patients_click)).toBe('function');
        });

        describe('Sharing a patient', function(){
            beforeEach(function(){
               spyOn(NHMobileShare.prototype, 'process_request').and.callFake(function(args){
                   var method = NHMobileShare.prototype.process_request.calls.mostRecent().args[0];
                   var url = NHMobileShare.prototype.process_request.calls.mostRecent().args[1];
                   var data = NHMobileShare.prototype.process_request.calls.mostRecent().args[2];
                   if(method == 'GET'){
                        var promise = new Promise();
                        promise.complete([[{'id': 1, 'name': 'Test Nurse', 'patients': 'Test Patient, Test Patient'}]]);
                        return promise;
                   }else{
                       if(data == 'patient_ids=1,2&user_ids=1'){
                            var promise = new Promise();
                            promise.complete([{'status': 1, 'shared_with': ['Test Nurse', 'Another Nurse']}]);
                            return promise;
                       }else {
                            var promise = new Promise();
                            promise.complete([{}]);
                            return promise;
                       }
                   }
                });
                standin = new NHMobileShare(share, claim, all);
            });

            it('On selecting patients and pressing Assign it sends the list to the server and updates the patient list with the names of people assigned', function(){
                // checkboxes
                var checkbox = document.getElementById('share_checkbox');
                checkbox.checked = true;
                var shared_checkbox = document.getElementById('shared_checkbox');
                shared_checkbox.checked = true;

                //click button
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                share.dispatchEvent(click_event);

                //check its done properly
                expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
                expect(NHMobileShare.prototype.share_button_click.calls.count()).toBe(1);
                expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();

                // get dialog and check user and assign
                var dialog = document.getElementById('assign_nurse');
                var assign_box = dialog.getElementsByClassName('patient_share_nurse')[0];
                assign_box.checked = true;
                var options = dialog.getElementsByTagName('a');
                var option = options[0];
                var assign_event = document.createEvent('CustomEvent');
                assign_event.initCustomEvent('click', false, true, false);
                option.dispatchEvent(assign_event);
                expect(NHMobileShare.prototype.assign_button_click).toHaveBeenCalled();
                expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();

                // do args to call & check all good
                expect(NHMobileShare.prototype.process_request.calls.mostRecent().args[2]).toBe('patient_ids=1,2&user_ids=1');
                var clean_share = document.getElementById('clean_shared');
                var dirty_share = document.getElementById('dirty_shared');
                var no_share = document.getElementById('no_shared');
                expect(clean_share.innerHTML).toBe('Shared with: Test Nurse, Another Nurse');
                expect(dirty_share.innerHTML).toBe('Shared with: Existing Nurse, Test Nurse, Another Nurse');
                expect(no_share.innerHTML).toBe('<br><br>');
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('share_success');
            });

            it('On selecting patients and pressing Assign it sends the list to the server and on error shows a popup to say so', function(){
                // checkboxes
                var checkbox = document.getElementById('share_checkbox');
                checkbox.checked = true;

                //click button
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                share.dispatchEvent(click_event);

                //check its done properly
                expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
                expect(NHMobileShare.prototype.share_button_click.calls.count()).toBe(1);
                expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();

                // get dialog and check user and assign
                var dialog = document.getElementById('assign_nurse');
                var assign_box = dialog.getElementsByClassName('patient_share_nurse')[0];
                assign_box.checked = true;
                var options = dialog.getElementsByTagName('a');
                var option = options[0];
                var assign_event = document.createEvent('CustomEvent');
                assign_event.initCustomEvent('click', false, true, false);
                option.dispatchEvent(assign_event);
                expect(NHMobileShare.prototype.assign_button_click).toHaveBeenCalled();
                expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();

                // do args to call & check all good
                var error = dialog.getElementsByClassName('error')[0];
                expect(error.innerHTML).toBe('Error assigning colleague(s), please try again');
            });

            it('On selecting no patients it adds a message to say add patients', function(){
                var checkbox = document.getElementById('share_checkbox');
                checkbox.checked = true;
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                share.dispatchEvent(click_event);
                expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
                expect(NHMobileShare.prototype.share_button_click.calls.count()).toBe(1);
                expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                var dialog = document.getElementById('assign_nurse');
                var options = dialog.getElementsByTagName('a');
                var option = options[0];
                var assign_event = document.createEvent('CustomEvent');
                assign_event.initCustomEvent('click', false, true, false);
                option.dispatchEvent(assign_event);
                expect(NHMobileShare.prototype.assign_button_click).toHaveBeenCalled();
                var error = dialog.getElementsByClassName('error')[0];
                expect(error.innerHTML).toBe('Please select colleague(s) to share with');
            });
        });

        describe('Claiming a patient', function() {
            beforeEach(function () {
                spyOn(NHMobileShare.prototype, 'process_request').and.callFake(function(args){
                   var method = NHMobileShare.prototype.process_request.calls.mostRecent().args[0];
                   var data = NHMobileShare.prototype.process_request.calls.mostRecent().args[2];
                   if(data == 'patient_ids=1,2'){
                        var promise = new Promise();
                        promise.complete([{'status': 1}]);
                        return promise;
                   }else {
                        var promise = new Promise();
                        promise.complete([{}]);
                        return promise;
                   }
                });
                standin = new NHMobileShare(share, claim, all);
            });

            it('On selecting patients and clicking claim it sends the patient ids to the server and tells the user the claim operation was successful', function(){
                // checkboxes
                var checkbox = document.getElementById('share_checkbox');
                checkbox.checked = true;
                var shared_checkbox = document.getElementById('shared_checkbox');
                shared_checkbox.checked = true;

                // click claim button
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                claim.dispatchEvent(click_event);
                expect(NHMobileShare.prototype.claim_button_click).toHaveBeenCalled();
                expect(NHMobileShare.prototype.claim_button_click.calls.count()).toBe(1);
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();

                // get dialog and check user and assign
                var dialog = document.getElementById('claim_patients');
                var options = dialog.getElementsByTagName('a');
                var option = options[0];
                var claim_event = document.createEvent('CustomEvent');
                claim_event.initCustomEvent('click', false, true, false);
                option.dispatchEvent(claim_event);
                expect(NHMobileShare.prototype.claim_patients_click).toHaveBeenCalled();
                expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();

                // do args to call & check all good
                expect(NHMobileShare.prototype.process_request.calls.mostRecent().args[2]).toBe('patient_ids=1,2');
                var clean_share = document.getElementById('clean_shared');
                var dirty_share = document.getElementById('dirty_shared');
                var no_share = document.getElementById('no_shared');
                expect(clean_share.innerHTML).toBe('<br>');
                expect(dirty_share.innerHTML).toBe('<br>');
                expect(no_share.innerHTML).toBe('<br><br>');
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('claim_success');
            });

            it('On selecting patients and clicking claim it sends the patient ids to the server and on error informs the user', function(){
                // checkboxes
                var checkbox = document.getElementById('share_checkbox');
                checkbox.checked = true;

                // click claim button
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                claim.dispatchEvent(click_event);
                expect(NHMobileShare.prototype.claim_button_click).toHaveBeenCalled();
                expect(NHMobileShare.prototype.claim_button_click.calls.count()).toBe(1);
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();

                // get dialog and check user and assign
                var dialog = document.getElementById('claim_patients');
                var options = dialog.getElementsByTagName('a');
                var option = options[0];
                var claim_event = document.createEvent('CustomEvent');
                claim_event.initCustomEvent('click', false, true, false);
                option.dispatchEvent(claim_event);
                expect(NHMobileShare.prototype.claim_patients_click).toHaveBeenCalled();
                expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();

                // do args to call & check all good
                expect(NHMobileShare.prototype.process_request.calls.mostRecent().args[2]).toBe('patient_ids=1');
                var clean_share = document.getElementById('clean_shared');
                var dirty_share = document.getElementById('dirty_shared');
                var no_share = document.getElementById('no_shared');
                expect(clean_share.innerHTML).toBe('<br><br>');
                expect(dirty_share.innerHTML).toBe('Shared with: Existing Nurse');
                expect(no_share.innerHTML).toBe('<br><br>');
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('claim_error');
            });
        });
    });

    describe('Stand-in: Invitation Acception or Rejection', function(){
        afterEach(function(){
            cleanUp();
        });

        beforeEach(function(){
            spyOn(NHMobileShareInvite.prototype, 'handle_invite_click').and.callThrough();
            spyOn(NHMobileShareInvite.prototype, 'handle_accept_button_click').and.callThrough();
            spyOn(NHMobileShareInvite.prototype, 'handle_reject_button_click').and.callThrough();
            spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
            var test = document.getElementById('test');
            test.innerHTML = '<ul id="list"><li class="share_invite" data-invite-id="1" id="good_invite">Invite 1</li><li class="share_invite" data-invite-id="2" id="bad_invite">Invite 2</li></ul>';
        });

        it('Has a function for handling a click on a invitation', function(){
           expect(typeof(NHMobileShareInvite.prototype.handle_invite_click)).toBe('function');
        });

        it('Has a function for handling a click on the accept button', function(){
           expect(typeof(NHMobileShareInvite.prototype.handle_accept_button_click)).toBe('function');
        });

        it('Has a function for handling a click on the reject button', function(){
           expect(typeof(NHMobileShareInvite.prototype.handle_reject_button_click)).toBe('function');
        });

        describe('Clicking an invite', function(){

           beforeEach(function(){
               spyOn(NHMobileShareInvite.prototype, 'process_request').and.callFake(function(){
                    var method = NHMobileShareInvite.prototype.process_request.calls.mostRecent().args[0];
                    var url = NHMobileShareInvite.prototype.process_request.calls.mostRecent().args[1];
                    var data = NHMobileShareInvite.prototype.process_request.calls.mostRecent().args[2];
                    if(method == 'GET'){
                        var promise = new Promise();
                        promise.complete([[{'id': 1,
                            'next_ews_time': '6:66 hours',
                            'full_name': 'Test Patient',
                            'ews_score': '1',
                            'ews_trend': 'down',
                            'location': 'Bed 1',
                            'parent_location': 'Ward 1'
                        }]]);
                        return promise;
                    }
                });
                var list = document.getElementById('list');
                mobile = new NHMobileShareInvite(list);
           });
           it('Displays a modal with the information on the stand in request', function(){
                var invite = document.getElementById('good_invite');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                invite.dispatchEvent(click_event);
                expect(NHMobileShareInvite.prototype.handle_invite_click).toHaveBeenCalled();
                expect(NHMobileShareInvite.prototype.handle_invite_click.calls.count()).toBe(1);
                expect(NHMobileShareInvite.prototype.process_request).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('accept_invite');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Accept invitation to follow patients?');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<ul class="tasklist"><li class="block"><a><div class="task-meta"><div class="task-right"><p class="aside">6:66 hours</p></div><div class="task-left"><strong>Test Patient</strong>(1 <i class="icon-down-arrow"></i> )<br><em>Bed 1, Ward 1</em></div></div></a></li></ul>');
            });
        });

        describe('Accepting an invitation', function(){
            beforeEach(function(){
               spyOn(NHMobileShareInvite.prototype, 'process_request').and.callFake(function(){
                    var method = NHMobileShareInvite.prototype.process_request.calls.mostRecent().args[0];
                    var url = NHMobileShareInvite.prototype.process_request.calls.mostRecent().args[1];
                    var data = NHMobileShareInvite.prototype.process_request.calls.mostRecent().args[2];
                    if(method == 'GET'){
                        var promise = new Promise();
                        promise.complete([[{'id': 1,
                            'next_ews_time': '6:66 hours',
                            'full_name': 'Test Patient',
                            'ews_score': '1',
                            'ews_trend': 'down',
                            'location': 'Bed 1',
                            'parent_location': 'Ward 1'
                        }]]);
                        return promise;
                    }else{
                        if(url == 'http://localhost:8069/mobile/staff/accept/1'){
                            var promise = new Promise();
                            promise.complete([{'status': 1,
                            'count': 666,
                            'user': 'Another User'
                            }])
                            return promise;
                        }else{
                            var promise = new Promise();
                            promise.complete([{}]);
                            return promise;
                        }
                    }
                });
                var list = document.getElementById('list');
                mobile = new NHMobileShareInvite(list);
           });
           it('Removes invitation from list and informs user when successfully contacting server', function(){
                // Click invite
                var invite = document.getElementById('good_invite');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                invite.dispatchEvent(click_event);
                expect(NHMobileShareInvite.prototype.handle_invite_click).toHaveBeenCalled();
                expect(NHMobileShareInvite.prototype.handle_invite_click.calls.count()).toBe(1);
                expect(NHMobileShareInvite.prototype.process_request).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();

               // Get dialog & click button
                var dialog = document.getElementById('accept_invite');
                var options = dialog.getElementsByTagName('a');
                var option = options[3]; // should be accept button
                var accept_event = document.createEvent('CustomEvent');
                accept_event.initCustomEvent('click', false, true, false);
                option.dispatchEvent(accept_event);

               // Check it calls server
               expect(NHMobileShareInvite.prototype.process_request).toHaveBeenCalled();
               expect(NHMobileShareInvite.prototype.process_request.calls.mostRecent().args[1]).toBe('http://localhost:8069/mobile/staff/accept/1');

                invite = document.getElementById('good_invite');
                expect(invite).toBe(null);
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('invite_success');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Successfully accepted patients');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p>Now following 666 patients from Another User</p>');
            });

            it('Keeps invitation and informs user of error when issue on server', function(){
                // Click invite
                var invite = document.getElementById('bad_invite');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                invite.dispatchEvent(click_event);
                expect(NHMobileShareInvite.prototype.handle_invite_click).toHaveBeenCalled();
                expect(NHMobileShareInvite.prototype.handle_invite_click.calls.count()).toBe(1);
                expect(NHMobileShareInvite.prototype.process_request).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();

               // Get dialog & click button
                var dialog = document.getElementById('accept_invite');
                var options = dialog.getElementsByTagName('a');
                var option = options[3]; // should be accept button
                var accept_event = document.createEvent('CustomEvent');
                accept_event.initCustomEvent('click', false, true, false);
                option.dispatchEvent(accept_event);

               // Check it calls server
               expect(NHMobileShareInvite.prototype.process_request).toHaveBeenCalled();
               expect(NHMobileShareInvite.prototype.process_request.calls.mostRecent().args[1]).toBe('http://localhost:8069/mobile/staff/accept/2');

                invite = document.getElementById('bad_invite');
                expect(invite).not.toBe(null);
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('invite_error');
            });
        });

        describe('Rejecting an invitation', function(){
            beforeEach(function(){
                spyOn(NHMobileShareInvite.prototype, 'process_request').and.callFake(function(){
                    var method = NHMobileShareInvite.prototype.process_request.calls.mostRecent().args[0];
                    var url = NHMobileShareInvite.prototype.process_request.calls.mostRecent().args[1];
                    var data = NHMobileShareInvite.prototype.process_request.calls.mostRecent().args[2];
                    if(method == 'GET'){
                        var promise = new Promise();
                        promise.complete([[{'id': 1,
                            'next_ews_time': '6:66 hours',
                            'full_name': 'Test Patient',
                            'ews_score': '1',
                            'ews_trend': 'down',
                            'location': 'Bed 1',
                            'parent_location': 'Ward 1'
                        }]]);
                        return promise;
                    }else{
                        if(url == 'http://localhost:8069/mobile/staff/reject/1'){
                            var promise = new Promise();
                            promise.complete([{'status': 1,
                            'count': 666,
                            'user': 'Another User'
                            }])
                            return promise;
                        }else{
                            var promise = new Promise();
                            promise.complete([{}]);
                            return promise;
                        }
                    }
                });
                var list = document.getElementById('list');
                mobile = new NHMobileShareInvite(list);
           });
           it('Removes invitation from list and informs user when successfully contacting server', function(){
                // Click invite
                var invite = document.getElementById('good_invite');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                invite.dispatchEvent(click_event);
                expect(NHMobileShareInvite.prototype.handle_invite_click).toHaveBeenCalled();
                expect(NHMobileShareInvite.prototype.handle_invite_click.calls.count()).toBe(1);
                expect(NHMobileShareInvite.prototype.process_request).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();

               // Get dialog & click button
                var dialog = document.getElementById('accept_invite');
                var options = dialog.getElementsByTagName('a');
                var option = options[2]; // should be reject button
                var accept_event = document.createEvent('CustomEvent');
                accept_event.initCustomEvent('click', false, true, false);
                option.dispatchEvent(accept_event);

               // Check it calls server
               expect(NHMobileShareInvite.prototype.process_request).toHaveBeenCalled();
               expect(NHMobileShareInvite.prototype.process_request.calls.mostRecent().args[1]).toBe('http://localhost:8069/mobile/staff/reject/1');

                invite = document.getElementById('good_invite');
                expect(invite).toBe(null);
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('reject_success');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Successfully rejected patients');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p>The invitation to follow Another User\'s patients was rejected</p>');
            });

            it('Keeps invitation and informs user of error when issue on server', function(){
                // Click invite
                var invite = document.getElementById('bad_invite');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                invite.dispatchEvent(click_event);
                expect(NHMobileShareInvite.prototype.handle_invite_click).toHaveBeenCalled();
                expect(NHMobileShareInvite.prototype.handle_invite_click.calls.count()).toBe(1);
                expect(NHMobileShareInvite.prototype.process_request).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();

               // Get dialog & click button
                var dialog = document.getElementById('accept_invite');
                var options = dialog.getElementsByTagName('a');
                var option = options[2]; // should be reject button
                var accept_event = document.createEvent('CustomEvent');
                accept_event.initCustomEvent('click', false, true, false);
                option.dispatchEvent(accept_event);

               // Check it calls server
               expect(NHMobileShareInvite.prototype.process_request).toHaveBeenCalled();
               expect(NHMobileShareInvite.prototype.process_request.calls.mostRecent().args[1]).toBe('http://localhost:8069/mobile/staff/reject/2');

                invite = document.getElementById('bad_invite');
                expect(invite).not.toBe(null);
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('reject_error');
            });
        });
    });
});