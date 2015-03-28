describe('NHMobileShare', function() {
    var mobile, test_area;
    var patient_info_data = [
        {
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
        }
    ];

    var nurse_list_data = [[
        {
            'name': 'Norah',
            'id': 1,
            'patients': 3
        },
        {
            'name': 'Nadine',
            'id': 2,
            'patients': 4
        }
    ]]

    var assign_server_resp = [
        {
            'status': true,
            'ids': [1],
            'shared_with': ['Norah']
        }
    ]

    beforeEach(function () {
        // set up the DOM for test
        var body_el = document.getElementsByTagName('body')[0];
        var test = document.getElementById('test');
        if (test != null) {
            test.parentNode.removeChild(test);
        }
        test_area = document.createElement('div');
        test_area.setAttribute('id', 'test');
        test_area.style.height = '500px';
        test_area.innerHTML = '<div class="header">' +
            '<div class="header-main block">' +
            '<img src="/mobile/src/img/logo.png" class="logo">' +
            '<ul class="header-meta">' +
            '<li><a href="/mobile/patient/handover" class="button handover">Handover</a></li>' +
            '<li class="logout"><a href="/mobile/logout/" class="button back">Logout</a></li>' +
            '</ul></div>' +
            '<ul class="header-menu two-col">' +
            '<li><a href="/mobile/tasks/" id="taskNavItem" class="selected">Tasks</a></li>' +
            '<li><a href="/mobile/patients/" id="patientNavItem">My Patients</a></li>' +
            '</ul></div>'+
            '<div class="content">'+
            '<form id="handover_form">'+
            '<ul class="tasklist">'+
            '<li>' +
            '<input type="checkbox" name="patient_share_74" class="patient_share_checkbox"  value="74"/>'+
            '<a href="/mobile/patient/74" class="level-none block">' +
            '<div class="task-meta">' +
            '<div class="task-right">' +
            '<p class="aside">overdue: 17:01 hours</p>' +
            ' </div>' +
            '<div class="task-left">' +
            '<strong>Rodriguez, Audrina </strong> ( <i class="icon-none-arrow"></i>)<br>' +
            ' <em>Bed 05,Ward A</em>' +
            '</div>' +
            '</div>' +
            '<div class="task-meta">' +
            '<p class="taskInfo"><br></p>' +
            '</div>' +
            '</a>' +
            '</li><li>' +
            '<input type="checkbox" name="patient_share_73" class="patient_share_checkbox"  value="73"/>'+
            '<a href="/mobile/patient/73" class="level-none block">' +
            '<div class="task-meta">' +
            '<div class="task-right">' +
            '<p class="aside">overdue: 17:01 hours</p>' +
            '</div>' +
            ' <div class="task-left">' +
            '<strong>Kreiger, Concha </strong> ( <i class="icon-none-arrow"></i>)<br>' +
            '<em>Bed 06,Ward A</em>' +
            '</div>' +
            '</div>' +
            '<div class="task-meta">' +
            '<p class="taskInfo"><br></p>' +
            '</div>' +
            '</a>' +
            '</li><li>' +
            '<input type="checkbox" name="patient_share_75" class="patient_share_checkbox" value="75"/>'+
            '<a href="/mobile/patient/75" class="level-none block">' +
            '<div class="task-meta">' +
            '<div class="task-right">' +
            '<p class="aside">overdue: 17:01 hours</p>' +
            '</div>' +
            '<div class="task-left">' +
            '<strong>Stokes, Josue </strong> ( <i class="icon-none-arrow"></i>)<br>' +
            '<em>Bed 07,Ward A</em>' +
            '</div>' +
            '</div>' +
            '<div class="task-meta">' +
            '<p class="taskInfo"><br></p>' +
            '</div>' +
            '</a>' +
            '</li><li>' +
            '<input type="checkbox" name="patient_share_76" class="patient_share_checkbox" value="76"/>'+
            '<a href="/mobile/patient/76" class="level-two block">' +
            '<div class="task-meta">' +
            '<div class="task-right">' +
            '<p class="aside">overdue: 16:15 hours</p>' +
            '</div>' +
            '<div class="task-left">' +
            '<strong>Crooks, Montgomery </strong> (5 <i class="icon-first-arrow"></i>)<br>' +
            '<em>Bed 09,Ward A</em>' +
            '</div>' +
            '</div>' +
            '<div class="task-meta">' +
            '<p class="taskInfo"><br></p>' +
            '</div>' +
            '</a>' +
            '</li>'+
            '</ul>' +
            '</form>'+
            '</div>'+
            '<div class="footer">'+
            '<p class="user">Norah</p>'+
            '<ul class="footer-menu three-col">' +
            '<li><a href="#" class="share" data-nurse="3">Share</a></li>' +
            '<li><a href="#" class="claim" data-nurse="3">Claim</a></li>' +
            '<li><a href="/mobile/patients/">Cancel</a></li>' +
            '</ul></div>';
        body_el.appendChild(test_area);
        if (mobile == null) {
            share_button = test_area.getElementsByClassName('share')[0];
            claim_button = test_area.getElementsByClassName('claim')[0];
            mobile = new NHMobileShare(share_button, claim_button);
        }

        spyOn(NHMobileShare.prototype, 'process_request').and.callFake(function(method, url){
            if(url=='http://localhost:8069/mobile/staff/colleagues/'){
                var promise = new Promise();
                promise.complete(nurse_list_data);
                return promise;
            }else if(url=='http://localhost:8069/mobile/staff/assign/'){
                var promise = new Promise();
                promise.complete(assign_server_resp);
                return promise;
            }
        })
    });

    afterEach(function () {
        if (mobile != null) {
            mobile = null;
        }
        var test = document.getElementById('test');
        if (test != null) {
            test.parentNode.removeChild(test);
        }
//        var covers = document.getElementsByClassName('cover');
//        var dialog = document.getElementById('patient_share');
        var body = document.getElementsByTagName('body')[0];
//        for (var i = 0; i < covers.length; i++) {
//            var cover = covers[i];
//            body.removeChild(cover);
//        }
//        if (dialog) {
//            body.removeChild(dialog);
//        }
    });

    it('Creates a click event listener on share button', function(){
    	spyOn(NHMobileShare.prototype, 'share_button_click');
    	var share_button = test_area.getElementsByClassName('share')[0];
    	// fire a click event at the scan button
    	var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        share_button.dispatchEvent(click_event);
    	// test is fires the appropriate function
    	expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
    });

    it('Creates a click event listener on claim button', function(){
        spyOn(NHMobileShare.prototype, 'claim_button_click');
        var claim_button = test_area.getElementsByClassName('claim')[0];
        // fire a click event at the scan button
        var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        claim_button.dispatchEvent(click_event);
        // test is fires the appropriate function
        expect(NHMobileShare.prototype.claim_button_click).toHaveBeenCalled();
    });

    it('On selecting patients and pressing share button the list of available nurses is fetched', function(){
        spyOn(NHMobileShare.prototype, 'share_button_click').and.callThrough();
        // go select some patients
        var test_patient = document.getElementsByClassName('patient_share_checkbox')[0];
        test_patient.checked = true;

        var share_button = test_area.getElementsByClassName('share')[0];
        // fire a click event at the scan button
        var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        share_button.dispatchEvent(click_event);
        // test is fires the appropriate function
        expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request.calls.argsFor(0)[1]).toBe('http://localhost:8069/mobile/staff/colleagues/')
    });

    it('On selecting patients and pressing share button the list of available nurses is displayed in a modal', function(){
        spyOn(NHMobileShare.prototype, 'share_button_click').and.callThrough();
        // go select some patients
        var test_patient = document.getElementsByClassName('patient_share_checkbox')[0];
        test_patient.checked = true;


        var share_button = test_area.getElementsByClassName('share')[0];
        // fire a click event at the scan button
        var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        share_button.dispatchEvent(click_event);
        // test is fires the appropriate function
        expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();

        // test for full screen modal being called with nurse data
    });

    it('On selecting no patients and pressing the share button I am shown a modal with an error message', function(){
        spyOn(NHMobileShare.prototype, 'share_button_click').and.callThrough();
        spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
        // send click event to the share button
        var share_button = test_area.getElementsByClassName('share')[0];
        // fire a click event at the scan button
        var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        share_button.dispatchEvent(click_event);
        
        // assert that modal is called with error message
        expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog.calls.argsFor(0)[1]).toBe('invalid_form');
        expect(NHModal.prototype.create_dialog.calls.argsFor(0)[2]).toBe('No Patients selected');
    });

    it('The modal\'s Assign button event listener is set up', function(){
        spyOn(NHMobileShare.prototype, 'share_button_click').and.callThrough();
        spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
        spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
        spyOn(NHMobileShare.prototype, 'assign_button_click')
        // // go select some patients
        var test_patient = document.getElementsByClassName('patient_share_checkbox')[0];
        test_patient.checked = true;


        var share_button = test_area.getElementsByClassName('share')[0];
        // fire a click event at the scan button
        var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        share_button.dispatchEvent(click_event);
        // test is fires the appropriate function
        expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
        // send a click event to the assign button

        var dialog = document.getElementById('assign_nurse');
        var dialog_options = dialog.getElementsByClassName('options')[0];
        var assign_button = dialog_options.getElementsByTagName('a')[0];

        var assign_click = document.createEvent('CustomEvent');
        assign_click.initCustomEvent('click', false, true, false);
        assign_button.dispatchEvent(assign_click);
        expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
        expect(NHMobileShare.prototype.assign_button_click).toHaveBeenCalled();
    });

    it('The modal\'s Cancel button event listener is set up', function(){
        spyOn(NHMobileShare.prototype, 'share_button_click').and.callThrough();
        spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
        spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
        spyOn(NHMobileShare.prototype, 'assign_button_click')
        // // go select some patients
        var test_patient = document.getElementsByClassName('patient_share_checkbox')[0];
        test_patient.checked = true;


        var share_button = test_area.getElementsByClassName('share')[0];
        // fire a click event at the scan button
        var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        share_button.dispatchEvent(click_event);
        // test is fires the appropriate function
        expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
        // send a click event to the assign button

        var dialog = document.getElementById('assign_nurse');
        var dialog_options = dialog.getElementsByClassName('options')[0];
        var cancel_button = dialog_options.getElementsByTagName('a')[1];

        var cancel_click = document.createEvent('CustomEvent');
        cancel_click.initCustomEvent('click', false, true, false);
        cancel_button.dispatchEvent(cancel_click);
        expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
    });

    it('in the modal, pressing the cancel button dismisses the modal', function(){
        spyOn(NHMobileShare.prototype, 'share_button_click').and.callThrough();
        spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
        spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
        spyOn(NHMobileShare.prototype, 'assign_button_click')
        // // go select some patients
        var test_patient = document.getElementsByClassName('patient_share_checkbox')[0];
        test_patient.checked = true;


        var share_button = test_area.getElementsByClassName('share')[0];
        // fire a click event at the scan button
        var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        share_button.dispatchEvent(click_event);
        // test is fires the appropriate function
        expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
        // send a click event to the assign button

        var dialog = document.getElementById('assign_nurse');
        var dialog_options = dialog.getElementsByClassName('options')[0];
        var cancel_button = dialog_options.getElementsByTagName('a')[1];

        var cancel_click = document.createEvent('CustomEvent');
        cancel_click.initCustomEvent('click', false, true, false);
        cancel_button.dispatchEvent(cancel_click);
        expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();

        var dialog1 = document.getElementById('assign_nurse');
        expect(dialog1).toBe(null)

    });

    it('in the modal, on selecting a nurse to Assign a patient to and pressing the assign button the server is sent the nurse ID and the patients IDs', function(){
        // get the modal popping up
        // select a nurse
        // send a click event to teh assign button
        // assert the server is sent the IDs
        spyOn(NHMobileShare.prototype, 'share_button_click').and.callThrough();
        spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
        spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
        spyOn(NHMobileShare.prototype, 'assign_button_click').and.callThrough();
        // // go select some patients
        var test_patient = document.getElementsByClassName('patient_share_checkbox')[0];
        test_patient.checked = true;



        var share_button = test_area.getElementsByClassName('share')[0];
        // fire a click event at the scan button
        var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        share_button.dispatchEvent(click_event);
        // test is fires the appropriate function
        expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog).toHaveBeenCalled();

        // Select a nurse to share
        var test_nurse = document.getElementsByClassName('patient_share_nurse')[0];
        test_nurse.checked = true;

        // send a click event to the assign button

        var dialog = document.getElementById('assign_nurse');
        var dialog_options = dialog.getElementsByClassName('options')[0];
        var assign_button = dialog_options.getElementsByTagName('a')[0];

        var assign_click = document.createEvent('CustomEvent');
        assign_click.initCustomEvent('click', false, true, false);
        assign_button.dispatchEvent(assign_click);
        expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
        expect(NHMobileShare.prototype.assign_button_click).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request.calls.count()).toBe(2)
        expect(NHMobileShare.prototype.process_request.calls.argsFor(1)[2]).toBe('patient_ids=74&user_ids=1')
    });

    it('in the modal, on selecting no nurses and pressing the assign button I am shown an error stating that no nurse was selected', function(){
        // get the model popping up
        // select no nurses
        // send a click event ot the assign button
        spyOn(NHMobileShare.prototype, 'share_button_click').and.callThrough();
        spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
        spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
        spyOn(NHMobileShare.prototype, 'assign_button_click').and.callThrough();
        // // go select some patients
        var test_patient = document.getElementsByClassName('patient_share_checkbox')[0];
        test_patient.checked = true;



        var share_button = test_area.getElementsByClassName('share')[0];
        // fire a click event at the scan button
        var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        share_button.dispatchEvent(click_event);
        // test is fires the appropriate function
        expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog).toHaveBeenCalled();

        // send a click event to the assign button

        var dialog = document.getElementById('assign_nurse');
        var dialog_options = dialog.getElementsByClassName('options')[0];
        var assign_button = dialog_options.getElementsByTagName('a')[0];

        var assign_click = document.createEvent('CustomEvent');
        assign_click.initCustomEvent('click', false, true, false);
        assign_button.dispatchEvent(assign_click);
        expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
        expect(NHMobileShare.prototype.assign_button_click).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request.calls.count()).toBe(1)
        // assert that an error message is present
        dialog = document.getElementById('assign_nurse');
        error_message = dialog.getElementsByClassName('error')[0];
        expect(error_message.innerHTML).toBe('Please select colleague(s) to share with')
    });

    it('On the server returning that the assign operation was successful grey out the patients that were shared', function(){
        // get the modal popping up
        // select a nurse
        // send a client event to teh assign butotn
        // assert that those patients now have a class that greys them out
        spyOn(NHMobileShare.prototype, 'share_button_click').and.callThrough();
        spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
        spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
        spyOn(NHMobileShare.prototype, 'assign_button_click').and.callThrough();
        // // go select some patients
        var test_patient = document.getElementsByClassName('patient_share_checkbox')[0];
        test_patient.checked = true;



        var share_button = test_area.getElementsByClassName('share')[0];
        // fire a click event at the scan button
        var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        share_button.dispatchEvent(click_event);
        // test is fires the appropriate function
        expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog).toHaveBeenCalled();

        // Select a nurse to share
        var test_nurse = document.getElementsByClassName('patient_share_nurse')[0];
        test_nurse.checked = true;

        // send a click event to the assign button

        var dialog = document.getElementById('assign_nurse');
        var dialog_options = dialog.getElementsByClassName('options')[0];
        var assign_button = dialog_options.getElementsByTagName('a')[0];

        var assign_click = document.createEvent('CustomEvent');
        assign_click.initCustomEvent('click', false, true, false);
        assign_button.dispatchEvent(assign_click);
        expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
        expect(NHMobileShare.prototype.assign_button_click).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request.calls.count()).toBe(2)
        expect(NHMobileShare.prototype.process_request.calls.argsFor(1)[2]).toBe('patient_ids=74&user_ids=1')
        test_patient = document.getElementsByClassName('patient_share_checkbox')[0];
        test_patient_item = test_patient.parentNode.getElementsByClassName('block')[0];
        expect(test_patient_item.parentNode.classList.contains('shared')).toBe(true)
        test_patient_item_info = test_patient_item.getElementsByClassName('taskInfo')[0];
        expect(test_patient_item_info.innerHTML).toBe('Shared with: Norah');
        test_patient = document.getElementsByClassName('patient_share_checkbox')[0];
        expect(test_patient.checked).toBe(false);
        var dialog1 = document.getElementById('assign_nurse');
        expect(dialog1).toBe(null)
    });

    it('On the server returning that the assign operation was successful twice it doesn\'t remove names', function(){
        // get the modal popping up
        // select a nurse
        // send a client event to teh assign butotn
        // assert that those patients now have a class that greys them out
        spyOn(NHMobileShare.prototype, 'share_button_click').and.callThrough();
        spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
        spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
        spyOn(NHMobileShare.prototype, 'assign_button_click').and.callThrough();
        // // go select some patients
        var test_patient = document.getElementsByClassName('patient_share_checkbox')[0];
        test_patient.checked = true;



        var share_button = test_area.getElementsByClassName('share')[0];
        // fire a click event at the scan button
        var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        share_button.dispatchEvent(click_event);
        // test is fires the appropriate function
        expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog).toHaveBeenCalled();

        // Select a nurse to share
        var test_nurse = document.getElementsByClassName('patient_share_nurse')[0];
        test_nurse.checked = true;

        // send a click event to the assign button

        var dialog = document.getElementById('assign_nurse');
        var dialog_options = dialog.getElementsByClassName('options')[0];
        var assign_button = dialog_options.getElementsByTagName('a')[0];

        var assign_click = document.createEvent('CustomEvent');
        assign_click.initCustomEvent('click', false, true, false);
        assign_button.dispatchEvent(assign_click);
        expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
        expect(NHMobileShare.prototype.assign_button_click).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request.calls.count()).toBe(2)
        expect(NHMobileShare.prototype.process_request.calls.argsFor(1)[2]).toBe('patient_ids=74&user_ids=1')
        test_patient = document.getElementsByClassName('patient_share_checkbox')[0];
        test_patient_item = test_patient.parentNode.getElementsByClassName('block')[0];
        expect(test_patient_item.parentNode.classList.contains('shared')).toBe(true)
        test_patient_item_info = test_patient_item.getElementsByClassName('taskInfo')[0];
        expect(test_patient_item_info.innerHTML).toBe('Shared with: Norah');

        var dialog1 = document.getElementById('assign_nurse');
        expect(dialog1).toBe(null)

        test_patient = document.getElementsByClassName('patient_share_checkbox')[0];
        test_patient.checked = true;



        share_button = test_area.getElementsByClassName('share')[0];
        // fire a click event at the scan button
        click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        share_button.dispatchEvent(click_event);
        // test is fires the appropriate function
        expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog).toHaveBeenCalled();

        // Select a nurse to share
        test_nurse = document.getElementsByClassName('patient_share_nurse')[0];
        test_nurse.checked = true;

        // send a click event to the assign button

        dialog = document.getElementById('assign_nurse');
        dialog_options = dialog.getElementsByClassName('options')[0];
        assign_button = dialog_options.getElementsByTagName('a')[0];

        assign_click = document.createEvent('CustomEvent');
        assign_click.initCustomEvent('click', false, true, false);
        assign_button.dispatchEvent(assign_click);
        expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
        expect(NHMobileShare.prototype.assign_button_click).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request.calls.count()).toBe(4)
        expect(NHMobileShare.prototype.process_request.calls.argsFor(3)[2]).toBe('patient_ids=74&user_ids=1')
        test_patient = document.getElementsByClassName('patient_share_checkbox')[0];
        test_patient_item = test_patient.parentNode.getElementsByClassName('block')[0];
        expect(test_patient_item.parentNode.classList.contains('shared')).toBe(true)
        test_patient_item_info = test_patient_item.getElementsByClassName('taskInfo')[0];
        expect(test_patient_item_info.innerHTML).toBe('Shared with: Norah, Norah');
    });
});

describe('NHMobileShare - server unable to assign patient to colleague', function(){
    var mobile, test_area;
    var patient_info_data = [
        {
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
        }
    ];

    var nurse_list_data = [[
        {
            'name': 'Norah',
            'id': 1,
            'patients': 3
        },
        {
            'name': 'Nadine',
            'id': 2,
            'patients': 4
        }
    ]]

    var assign_server_resp = [
        {
            'status': true,
            'ids': [1],
            'shared_with': ['Norah']
        }
    ]

    beforeEach(function () {
        // set up the DOM for test
        var body_el = document.getElementsByTagName('body')[0];
        var test = document.getElementById('test');
        if (test != null) {
            test.parentNode.removeChild(test);
        }
        test_area = document.createElement('div');
        test_area.setAttribute('id', 'test');
        test_area.style.height = '500px';
        test_area.innerHTML = '<div class="header">' +
            '<div class="header-main block">' +
            '<img src="/mobile/src/img/logo.png" class="logo">' +
            '<ul class="header-meta">' +
            '<li><a href="/mobile/patient/handover" class="button handover">Handover</a></li>' +
            '<li class="logout"><a href="/mobile/logout/" class="button back">Logout</a></li>' +
            '</ul></div>' +
            '<ul class="header-menu two-col">' +
            '<li><a href="/mobile/tasks/" id="taskNavItem" class="selected">Tasks</a></li>' +
            '<li><a href="/mobile/patients/" id="patientNavItem">My Patients</a></li>' +
            '</ul></div>'+
            '<div class="content">'+
            '<form id="handover_form">'+
            '<ul class="tasklist">'+
            '<li>' +
            '<input type="checkbox" name="patient_share_74" class="patient_share_checkbox"  value="74"/>'+
            '<a href="/mobile/patient/74" class="level-none block">' +
            '<div class="task-meta">' +
            '<div class="task-right">' +
            '<p class="aside">overdue: 17:01 hours</p>' +
            ' </div>' +
            '<div class="task-left">' +
            '<strong>Rodriguez, Audrina </strong> ( <i class="icon-none-arrow"></i>)<br>' +
            ' <em>Bed 05,Ward A</em>' +
            '</div>' +
            '</div>' +
            '<div class="task-meta">' +
            '<p class="taskInfo"><br></p>' +
            '</div>' +
            '</a>' +
            '</li><li>' +
            '<input type="checkbox" name="patient_share_73" class="patient_share_checkbox"  value="73"/>'+
            '<a href="/mobile/patient/73" class="level-none block">' +
            '<div class="task-meta">' +
            '<div class="task-right">' +
            '<p class="aside">overdue: 17:01 hours</p>' +
            '</div>' +
            ' <div class="task-left">' +
            '<strong>Kreiger, Concha </strong> ( <i class="icon-none-arrow"></i>)<br>' +
            '<em>Bed 06,Ward A</em>' +
            '</div>' +
            '</div>' +
            '<div class="task-meta">' +
            '<p class="taskInfo"><br></p>' +
            '</div>' +
            '</a>' +
            '</li><li>' +
            '<input type="checkbox" name="patient_share_75" class="patient_share_checkbox" value="75"/>'+
            '<a href="/mobile/patient/75" class="level-none block">' +
            '<div class="task-meta">' +
            '<div class="task-right">' +
            '<p class="aside">overdue: 17:01 hours</p>' +
            '</div>' +
            '<div class="task-left">' +
            '<strong>Stokes, Josue </strong> ( <i class="icon-none-arrow"></i>)<br>' +
            '<em>Bed 07,Ward A</em>' +
            '</div>' +
            '</div>' +
            '<div class="task-meta">' +
            '<p class="taskInfo"><br></p>' +
            '</div>' +
            '</a>' +
            '</li><li>' +
            '<input type="checkbox" name="patient_share_76" class="patient_share_checkbox" value="76"/>'+
            '<a href="/mobile/patient/76" class="level-two block">' +
            '<div class="task-meta">' +
            '<div class="task-right">' +
            '<p class="aside">overdue: 16:15 hours</p>' +
            '</div>' +
            '<div class="task-left">' +
            '<strong>Crooks, Montgomery </strong> (5 <i class="icon-first-arrow"></i>)<br>' +
            '<em>Bed 09,Ward A</em>' +
            '</div>' +
            '</div>' +
            '<div class="task-meta">' +
            '<p class="taskInfo"><br></p>' +
            '</div>' +
            '</a>' +
            '</li>'+
            '</ul>' +
            '</form>'+
            '</div>'+
            '<div class="footer">'+
            '<p class="user">Norah</p>'+
            '<ul class="footer-menu three-col">' +
            '<li><a href="#" class="share" data-nurse="3">Share</a></li>' +
            '<li><a href="#" class="claim" data-nurse="3">Claim</a></li>' +
            '<li><a href="/mobile/patients/">Cancel</a></li>' +
            '</ul></div>';
        body_el.appendChild(test_area);
        if (mobile == null) {
            share_button = test_area.getElementsByClassName('share')[0];
            claim_button = test_area.getElementsByClassName('claim')[0];
            mobile = new NHMobileShare(share_button, claim_button);
        }

        spyOn(NHMobileShare.prototype, 'process_request').and.callFake(function(method, url){
            if(url=='http://localhost:8069/mobile/staff/colleagues/'){
                var promise = new Promise();
                promise.complete(nurse_list_data);
                return promise;
            }else if(url=='http://localhost:8069/mobile/staff/assign/'){
                var promise = new Promise();
                promise.complete([{'status': false}]);
                return promise;
            }
        })
    });

    afterEach(function () {
        if (mobile != null) {
            mobile = null;
        }
        var test = document.getElementById('test');
        if (test != null) {
            test.parentNode.removeChild(test);
        }
//        var covers = document.getElementsByClassName('cover');
//        var dialog = document.getElementById('patient_share');
        var body = document.getElementsByTagName('body')[0];
//        for (var i = 0; i < covers.length; i++) {
//            var cover = covers[i];
//            body.removeChild(cover);
//        }
//        if (dialog) {
//            body.removeChild(dialog);
//        }
    });

    it('On the server returning that the assign operation was unsuccessfull show an error message', function(){
        // get the modal popping up
        // select a nurse
        // send a client event to teh assign butotn
        // assert that those patients now have a class that greys them out
        spyOn(NHMobileShare.prototype, 'share_button_click').and.callThrough();
        spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
        spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
        spyOn(NHMobileShare.prototype, 'assign_button_click').and.callThrough();


        // // go select some patients
        var test_patient = document.getElementsByClassName('patient_share_checkbox')[0];
        test_patient.checked = true;



        var share_button = test_area.getElementsByClassName('share')[0];
        // fire a click event at the scan button
        var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        share_button.dispatchEvent(click_event);
        // test is fires the appropriate function
        expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request).toHaveBeenCalled();
        expect(NHModal.prototype.create_dialog).toHaveBeenCalled();

        // Select a nurse to share
        var test_nurse = document.getElementsByClassName('patient_share_nurse')[0];
        test_nurse.checked = true;

        // send a click event to the assign button

        var dialog = document.getElementById('assign_nurse');
        var dialog_options = dialog.getElementsByClassName('options')[0];
        var assign_button = dialog_options.getElementsByTagName('a')[0];

        var assign_click = document.createEvent('CustomEvent');
        assign_click.initCustomEvent('click', false, true, false);
        assign_button.dispatchEvent(assign_click);
        expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
        expect(NHMobileShare.prototype.assign_button_click).toHaveBeenCalled();
        expect(NHMobileShare.prototype.process_request.calls.count()).toBe(2)
        expect(NHMobileShare.prototype.process_request.calls.argsFor(1)[2]).toBe('patient_ids=74&user_ids=1')
        test_patient = document.getElementsByClassName('patient_share_checkbox')[0];
        test_patient_item = test_patient.parentNode.getElementsByClassName('block')[0];
        expect(test_patient_item.classList.contains('shared')).toBe(false)
        test_patient_item_info = test_patient_item.getElementsByClassName('taskInfo')[0];
        expect(test_patient_item_info.innerHTML).toBe('<br>');

        var dialog1 = document.getElementById('assign_nurse');
        var error_message = dialog1.getElementsByClassName('error')[0]
        expect(error_message.innerHTML).toBe('Error assigning colleague(s), please try again')
    });
});