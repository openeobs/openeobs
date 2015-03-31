describe('NHMobileShareInvite', function(){
    var mobile, test_area;
    var test_dom = '<div class="content">'+
        '<ul class="tasklist">'+
        '<li>'+
        '<div class="block share_invite" data-invite-id="1">'+
        '<p>This is an invite</p>'+
        '</div>'+
        '</li>'+
        '<li>'+
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
        '</li>'+
        '</ul>'+
        '</div>';

    beforeEach(function(){
        // create base template with test area
        var body_el = document.getElementsByTagName('body')[0];
        var test_area = document.getElementById('test');
        if (test_area != null) {
            test_area.parentNode.removeChild(test);
        }
        test_area = document.createElement('div');
        test_area.setAttribute('id', 'test');
        test_area.style.height = '500px';
        test_area.innerHTML = test_dom;
        body_el.appendChild(test_area);

    });

    describe('Constructor', function(){

        // create test for one invite
        describe('Constructor - One invite', function(){
            beforeEach(function(){
                // create instance of NHMobileShareInvite
                if(mobile == null){
                    var patient_list = test.getElementsByClassName('tasklist')[0];
                    mobile = new NHMobileShareInvite(patient_list);
                }
                spyOn(NHMobileShareInvite.prototype, 'handle_invite_click');
            });

            it('attaches an event listener to the only invite in patient list', function(){
                var invites = document.getElementsByClassName('share_invite');
                for(var i = 0; i < invites.length; i++){
                    var invite = invites[i];
                    var click_event = document.createEvent('CustomEvent');
                    click_event.initCustomEvent('click', true, false, true);
                    invite.dispatchEvent(click_event);
                }
                expect(NHMobileShareInvite.prototype.handle_invite_click).toHaveBeenCalled();
                expect(NHMobileShareInvite.prototype.handle_invite_click.calls.argsFor(0)[1]).toBe('1');
            });
        });

        // create test for two invites
        describe('Constructor - Two invites', function(){
            beforeEach(function(){
                var list = document.getElementsByClassName('tasklist')[0];
                for(var i =0; i < 1; i++){
                    var obj = document.createElement('li');
                    var counter = i + 2;
                    obj.innerHTML = '<div class="block share_invite" data-invite-id="'+counter+'"><p>This is an invite</p></div>';
                    list.appendChild(obj);
                }

                // create instance of NHMobileShareInvite
                if(mobile == null){
                    mobile = new NHMobileShareInvite(list);
                }
                spyOn(NHMobileShareInvite.prototype, 'handle_invite_click');
            });

            it('attaches an event listener to the only invite in patient list', function(){
                var invites = document.getElementsByClassName('share_invite');
                for(var i = 0; i < invites.length; i++){
                    var invite = invites[i];
                    var click_event = document.createEvent('CustomEvent');
                    click_event.initCustomEvent('click', true, false, true);
                    invite.dispatchEvent(click_event);
                    var counter = i + 1;
                    expect(NHMobileShareInvite.prototype.handle_invite_click.calls.argsFor(i)[1]).toBe(counter.toString())
                }
                expect(NHMobileShareInvite.prototype.handle_invite_click.calls.count()).toBe(2);
            });
        });

        // create test for twenty invites
        describe('Constructor - Twenty invites', function(){
            beforeEach(function(){
                var list = document.getElementsByClassName('tasklist')[0];
                for(var i =0; i < 19; i++){
                    var obj = document.createElement('li');
                    var counter = i + 2;
                    obj.innerHTML = '<div class="block share_invite" data-invite-id="'+counter+'"><p>This is an invite</p></div>';
                    list.appendChild(obj);
                }

                // create instance of NHMobileShareInvite
                if(mobile == null){
                    mobile = new NHMobileShareInvite(list);
                }
                spyOn(NHMobileShareInvite.prototype, 'handle_invite_click');
            });

            it('attaches an event listener to the only invite in patient list', function(){
                var invites = document.getElementsByClassName('share_invite');
                for(var i = 0; i < invites.length; i++){
                    var invite = invites[i];
                    var click_event = document.createEvent('CustomEvent');
                    click_event.initCustomEvent('click', true, false, true);
                    invite.dispatchEvent(click_event);
                    var counter = i + 1;
                    expect(NHMobileShareInvite.prototype.handle_invite_click.calls.argsFor(i)[1]).toBe(counter.toString())
                }
                expect(NHMobileShareInvite.prototype.handle_invite_click.calls.count()).toBe(20);
            });
        });
    });

    describe('Clicking on an invite', function(){
        var patient_list_data = [
                {
                    'full_name': 'Patient, Test A',
                    'ews_deadline': '01:00 hours',
                    'ews_score': 5,
                    'ews_trend': 'first',
                    'parent_location': 'Ward A',
                    'location': 'Bed 5'
                },
                {
                    'full_name': 'Patient, Test B',
                    'ews_deadline': '02:00 hours',
                    'ews_score': 4,
                    'ews_trend': 'up',
                    'parent_location': 'Ward A',
                    'location': 'Bed 4'
                }
            ];

        beforeEach(function(){
            // create instance of NHMobileShareInvite
            if(mobile == null){
                var patient_list = test.getElementsByClassName('tasklist')[0];
                mobile = new NHMobileShareInvite(patient_list);
            }
            spyOn(NHMobileShareInvite.prototype, 'handle_invite_click').and.callThrough();
            spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
            spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
        });

        describe('Displaying the modal', function(){

            beforeEach(function(){
               spyOn(NHMobileShareInvite.prototype, 'process_request').and.callFake(function(){
                    var promise = new Promise();
                    promise.complete(patient_list_data);
                    return promise;
                });
                var invites = document.getElementsByClassName('share_invite');
                for(var i = 0; i < invites.length; i++){
                    var invite = invites[i];
                    var click_event = document.createEvent('CustomEvent');
                    click_event.initCustomEvent('click', true, false, true);
                    invite.dispatchEvent(click_event);
                }
                expect(NHMobileShareInvite.prototype.handle_invite_click).toHaveBeenCalled();
                expect(NHMobileShareInvite.prototype.process_request).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.argsFor(0)[1]).toBe('accept_invite');
                expect(NHModal.prototype.create_dialog.calls.argsFor(0)[2]).toBe('Accept invitation to follow patients?');
            });

            it('Shows a modal with the list of patients', function(){
                var dialog = document.getElementById('accept_invite');
                var dialog_options = dialog.getElementsByClassName('options')[0];
                var dialog_content = dialog.getElementsByClassName('dialogContent')[0];
                var patients = dialog_content.getElementsByTagName('li');
                var patient_list = dialog_content.getElementsByTagName('ul')[0];
                expect(patients.length).toBe(2);
                expect(patient_list.innerHTML).toBe('<li><div class="task-meta"><div class="task-right"><p class="aside">01:00 hours</p></div><div class="task-left"><strong>Patient, Test A</strong>(5 <i class="icon-first-arrow"></i> )<em>Bed 5, Ward A</em></div></div></li><li><div class="task-meta"><div class="task-right"><p class="aside">02:00 hours</p></div><div class="task-left"><strong>Patient, Test B</strong>(4 <i class="icon-up-arrow"></i> )<em>Bed 4, Ward A</em></div></div></li>')
            });
        });
        describe('Accepting invite - success', function(){
            var accept_button;
            beforeEach(function(){
                spyOn(NHMobileShareInvite.prototype, 'process_request').and.callFake(function(method, url){
                    if(method=='GET'){
                        var promise = new Promise();
                        promise.complete(patient_list_data);
                        return promise;
                    }else if (method=='POST'){
                       var promise = new Promise();
                        promise.complete([{
                            'status': true,
                            'count': 3,
                            'user': 'Norah'
                        }]);
                        return promise;
                    }
                });
                var invites = document.getElementsByClassName('share_invite');
                for(var i = 0; i < invites.length; i++){
                    var invite = invites[i];
                    var click_event = document.createEvent('CustomEvent');
                    click_event.initCustomEvent('click', true, false, true);
                    invite.dispatchEvent(click_event);
                }
                expect(NHMobileShareInvite.prototype.handle_invite_click).toHaveBeenCalled();
                expect(NHMobileShareInvite.prototype.process_request).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.argsFor(0)[1]).toBe('accept_invite');
                expect(NHModal.prototype.create_dialog.calls.argsFor(0)[2]).toBe('Accept invitation to follow patients?');
                var dialog = document.getElementById('accept_invite');
                var dialog_options = dialog.getElementsByClassName('options')[0];
                accept_button = dialog_options.getElementsByTagName('a')[0];
                spyOn(NHMobileShareInvite.prototype, 'handle_accept_button_click').and.callThrough();
            });

            it('Sends a request to the server on pressing Accept button in modal', function(){
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', true, false, true);
                accept_button.dispatchEvent(click_event);
                //expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
                expect(NHMobileShareInvite.prototype.handle_accept_button_click).toHaveBeenCalled();
                expect(NHMobileShareInvite.prototype.handle_accept_button_click.calls.argsFor(0)[1]).toBe('1');
                expect(NHMobileShareInvite.prototype.process_request.calls.count()).toBe(2);
                expect(NHModal.prototype.create_dialog.calls.count()).toBe(2);
                expect(NHModal.prototype.create_dialog.calls.argsFor(1)[1]).toBe('invite_success');
                var success_dialog = document.getElementById('invite_success');
                expect(success_dialog).not.toBe(null);
            });
        });

        describe('Accepting invite - Error', function(){
            var accept_button;
            beforeEach(function(){
                spyOn(NHMobileShareInvite.prototype, 'process_request').and.callFake(function(method, url){
                    if(method=='GET'){
                        var promise = new Promise();
                        promise.complete(patient_list_data);
                        return promise;
                    }else if (method=='POST'){
                       var promise = new Promise();
                        promise.complete([{
                            'status': false,
                            'count': 3,
                            'user': 'Norah'
                        }]);
                        return promise;
                    }
                });
                var invites = document.getElementsByClassName('share_invite');
                for(var i = 0; i < invites.length; i++){
                    var invite = invites[i];
                    var click_event = document.createEvent('CustomEvent');
                    click_event.initCustomEvent('click', true, false, true);
                    invite.dispatchEvent(click_event);
                }
                expect(NHMobileShareInvite.prototype.handle_invite_click).toHaveBeenCalled();
                expect(NHMobileShareInvite.prototype.process_request).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.argsFor(0)[1]).toBe('accept_invite');
                expect(NHModal.prototype.create_dialog.calls.argsFor(0)[2]).toBe('Accept invitation to follow patients?');
                var dialog = document.getElementById('accept_invite');
                var dialog_options = dialog.getElementsByClassName('options')[0];
                accept_button = dialog_options.getElementsByTagName('a')[0];
                spyOn(NHMobileShareInvite.prototype, 'handle_accept_button_click').and.callThrough();
            });

            it('Sends a request to the server on pressing Accept button in modal', function(){
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', true, false, true);
                accept_button.dispatchEvent(click_event);
                //expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
                expect(NHMobileShareInvite.prototype.handle_accept_button_click).toHaveBeenCalled();
                expect(NHMobileShareInvite.prototype.handle_accept_button_click.calls.argsFor(0)[1]).toBe('1');
                expect(NHMobileShareInvite.prototype.process_request.calls.count()).toBe(2);
                expect(NHModal.prototype.create_dialog.calls.count()).toBe(2);
                expect(NHModal.prototype.create_dialog.calls.argsFor(1)[1]).toBe('invite_error');
                var error_dialog = document.getElementById('invite_error');
                expect(error_dialog).not.toBe(null);
            });
        });
    });

    afterEach(function(){
        if (mobile != null) {
            mobile = null;
        }
        var test = document.getElementById('test');
        if (test != null) {
            test.parentNode.removeChild(test);
        }
        var covers = document.getElementsByClassName('cover');
        var dialogs = document.getElementsByClassName('dialog');
        for(var i = 0; i < covers.length; i++){
            var cover = covers[i];
            cover.parentNode.removeChild(cover);
        }
        for(var i = 0; i < dialogs.length; i++){
            var dialog = dialogs[i];
            dialog.parentNode.removeChild(dialog);
        }
        var body = document.getElementsByTagName('body')[0];
    });

});