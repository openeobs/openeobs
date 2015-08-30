/**
 * Created by colinwren on 30/08/15.
 */
describe('Data Entry Functionality', function(){
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

    it('Has functionality to handle forms', function(){
       expect(typeof(NHMobileForm.prototype)).toBe('object');
    });

    describe('Form Interaction', function(){
        afterEach(function(){
           cleanUp();
        });

        it('Has functionality to trigger actions based on interactions with a form', function(){
           expect(typeof(NHMobileForm.prototype.trigger_actions)).toBe('function');
        });

        it('Has functionality to show a reference image or iframe for a form input', function(){
           expect(typeof(NHMobileForm.prototype.show_reference)).toBe('function');
        });

        it('Has functionality to hide inputs if a triggered action says we need to', function(){
           expect(typeof(NHMobileForm.prototype.hide_triggered_elements)).toBe('function');
        });

        it('Has functionality to show inputs if a triggered action says we need to', function(){
           expect(typeof(NHMobileForm.prototype.show_triggered_elements)).toBe('function');
        });

        it('Has functionality to disable inputs if a triggered action says we need to', function(){
           expect(typeof(NHMobileForm.prototype.disable_triggered_elements)).toBe('function');
        });

        it('Has functionality to enable inputs if a triggered action says we need to', function(){
           expect(typeof(NHMobileForm.prototype.enable_triggered_elements)).toBe('function');
        });

        describe('Showing and Hiding elements based on triggered actions', function(){
            var mobile;
             beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit');
                spyOn(NHMobileForm.prototype, 'handle_timeout');
                spyOn(NHMobileForm.prototype, 'trigger_actions').and.callThrough();
                spyOn(NHMobileForm.prototype, 'hide_triggered_elements').and.callThrough();
                spyOn(NHMobileForm.prototype, 'show_triggered_elements').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                    var promise = new Promise();
                    promise.complete([{}]);
                    return promise;
                });

                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                    '<select name="origin_element" id="origin_element" data-onchange="[{\'action\': \'show\', \'fields\': [\'hidden_affected_element\'], \'condition\': [[\'origin_element\', \'==\', 2]]}, {\'action\': \'hide\', \'fields\': [\'affected_element\'], \'condition\': [[\'origin_element\', \'==\', 1]]}, {\'action\': \'hide\', \'fields\': [\'affected_element\', \'hidden_affected_element\'], \'condition\': [[\'origin_element\', \'==\', \'\']]}]">' +
                    '<option value="">Default</option>' +
                    '<option value="1">Hide</option>' +
                    '<option value="2">Show</option>' +
                    '</select>' +
                    '<div id="parent_affected_element"><input type="number" id="affected_element"></div>' +
                    '<div id="parent_hidden_affected_element" style="display: none;"><input type="number" id="hidden_affected_element" class="exclude"></div>' +
                    '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                    '</form>';
                mobile = new NHMobileForm();
            });

            afterEach(function(){
               cleanUp();
            });

            it('Hides the input mentioned in the data-onchange attribute when the hide condition is met', function(){
                var origin_element = document.getElementById('origin_element');
                var parent_element = document.getElementById('parent_affected_element');
                var element = document.getElementById('affected_element');
                expect(parent_element.style.display).not.toBe('none');
                expect(element.classList.contains('exclude')).not.toBe(true);
                origin_element.value = 1;
                var change_event = document.createEvent('CustomEvent');
                change_event.initCustomEvent('change', false, true, false);
                origin_element.dispatchEvent(change_event);
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(NHMobileForm.prototype.hide_triggered_elements).toHaveBeenCalled();
                expect(NHMobileForm.prototype.hide_triggered_elements.calls.mostRecent().args[0]).toBe('affected_element');
                expect(parent_element.style.display).toBe('none');
                expect(element.classList.contains('exclude')).toBe(true);
            });

            it('Hides input mentioned in the data-onchange attribute when the hide condition is met (no value set)', function(){
                var origin_element = document.getElementById('origin_element');
                var parent_element = document.getElementById('parent_affected_element');
                var element = document.getElementById('affected_element');
                var parent_hidden_element = document.getElementById('parent_hidden_affected_element');
                var hidden_element = document.getElementById('hidden_affected_element');
                expect(parent_element.style.display).not.toBe('none');
                expect(parent_hidden_element.style.display).toBe('none');
                expect(element.classList.contains('exclude')).not.toBe(true);
                expect(hidden_element.classList.contains('exclude')).toBe(true);
                origin_element.value = '';
                var change_event = document.createEvent('CustomEvent');
                change_event.initCustomEvent('change', false, true, false);
                origin_element.dispatchEvent(change_event);
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(NHMobileForm.prototype.hide_triggered_elements).toHaveBeenCalled();
                expect(parent_element.style.display).toBe('none');
                expect(parent_hidden_element.style.display).toBe('none');
                expect(element.classList.contains('exclude')).toBe(true);
                expect(hidden_element.classList.contains('exclude')).toBe(true);
            });

            it('Shows the input mentioned in the data-onchange attribute when the show condition is met', function(){
                var origin_element = document.getElementById('origin_element');
                var parent_element = document.getElementById('parent_hidden_affected_element');
                var element = document.getElementById('hidden_affected_element');
                expect(parent_element.style.display).toBe('none');
                expect(element.classList.contains('exclude')).toBe(true);
                origin_element.value = 2;
                var change_event = document.createEvent('CustomEvent');
                change_event.initCustomEvent('change', false, true, false);
                origin_element.dispatchEvent(change_event);
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(NHMobileForm.prototype.show_triggered_elements).toHaveBeenCalled();
                expect(NHMobileForm.prototype.show_triggered_elements.calls.mostRecent().args[0]).toBe('hidden_affected_element');
                expect(parent_element.style.display).not.toBe('none');
                expect(element.classList.contains('exclude')).not.toBe(true);
            });
        });

        describe('Enabling and Disabling elements based on triggered actions', function(){
            var mobile;
             beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit');
                spyOn(NHMobileForm.prototype, 'handle_timeout');
                spyOn(NHMobileForm.prototype, 'trigger_actions').and.callThrough();
                spyOn(NHMobileForm.prototype, 'disable_triggered_elements').and.callThrough();
                spyOn(NHMobileForm.prototype, 'enable_triggered_elements').and.callThrough();
                spyOn(NHMobileForm.prototype, 'validate');
                spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                    var promise = new Promise();
                    promise.complete([{}]);
                    return promise;
                });
                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                    '<select name="origin_element" id="origin_element" data-onchange="[{\'action\': \'enable\', \'fields\': [\'disabled_affected_element\'], \'condition\': [[\'origin_element\', \'==\', \'True\']]}, {\'action\': \'disable\', \'fields\': [\'affected_element\'], \'condition\': [[\'origin_element\', \'==\', \'False\']]}]">' +
                    '<option value="">Default</option>' +
                    '<option value="False">Disable</option>' +
                    '<option value="True">Enable</option>' +
                    '</select>' +
                    '<input type="number" id="affected_element">' +
                    '<input type="number" id="disabled_affected_element" class="exclude" disabled="disabled">' +
                    '<input type="number" id="value_change" data-onchange="[{\'action\': \'disable\', \'fields\': [\'origin_element\'], \'condition\': [[\'value_change\', \'!=\', \'affected_element\']]}]">'+
                    '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                    '</form>';
                mobile = new NHMobileForm();
            });

            afterEach(function(){
               cleanUp();
            });

            it('Disables the input mentioned in the data-onchange attribute when the disable condition is met', function(){
                var origin_element = document.getElementById('origin_element');
                var element = document.getElementById('affected_element');
                expect(element.classList.contains('exclude')).not.toBe(true);
                expect(element.disabled).not.toBe(true);
                origin_element.value = "False";
                var change_event = document.createEvent('CustomEvent');
                change_event.initCustomEvent('change', false, true, false);
                origin_element.dispatchEvent(change_event);
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(NHMobileForm.prototype.disable_triggered_elements).toHaveBeenCalled();
                expect(NHMobileForm.prototype.disable_triggered_elements.calls.mostRecent().args[0]).toBe('affected_element');
                expect(element.classList.contains('exclude')).toBe(true);
                expect(element.disabled).toBe(true);
            });

            it('Disables the input mentioned in the data-onchange attribute when the disable condition is met (comparative value)', function(){
                var origin_element = document.getElementById('origin_element');
                var element = document.getElementById('affected_element');
                var value_change = document.getElementById('value_change');
                element.value = 666;
                value_change.value = 1337;
                expect(origin_element.classList.contains('exclude')).not.toBe(true);
                expect(origin_element.disabled).not.toBe(true);
                var change_event = document.createEvent('CustomEvent');
                change_event.initCustomEvent('change', false, true, false);
                value_change.dispatchEvent(change_event);
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(NHMobileForm.prototype.disable_triggered_elements).toHaveBeenCalled();
                expect(NHMobileForm.prototype.disable_triggered_elements.calls.mostRecent().args[0]).toBe('origin_element');
                expect(origin_element.classList.contains('exclude')).toBe(true);
                expect(origin_element.disabled).toBe(true);
            });

            it('Enables the input mentioned in the data-onchange attribute when the enable condition is met', function(){
                var origin_element = document.getElementById('origin_element');
                var element = document.getElementById('disabled_affected_element');
                expect(element.classList.contains('exclude')).toBe(true);
                expect(element.disabled).toBe(true);
                origin_element.value = "True";
                var change_event = document.createEvent('CustomEvent');
                change_event.initCustomEvent('change', false, true, false);
                origin_element.dispatchEvent(change_event);
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(NHMobileForm.prototype.enable_triggered_elements).toHaveBeenCalled();
                expect(NHMobileForm.prototype.enable_triggered_elements.calls.mostRecent().args[0]).toBe('disabled_affected_element');
                expect(element.classList.contains('exclude')).not.toBe(true);
                expect(element.disabled).not.toBe(true);
            });
        });

        describe('Reference buttons', function(){
            var mobile;
             beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit');
                spyOn(NHMobileForm.prototype, 'handle_timeout');
                spyOn(NHMobileForm.prototype, 'show_reference').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                    var promise = new Promise();
                    promise.complete([{}]);
                    return promise;
                });
                spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                    '<button id="image_reference" data-type="image" data-url="/" data-title="Test Reference Image">Test Button</button>' +
                    '<button id="iframe_reference" data-type="iframe" data-url="/" data-title="Test Reference Iframe">Test Button</button>' +
                    '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                    '</form>';
                mobile = new NHMobileForm();
            });

            afterEach(function(){
               cleanUp();
            });

            it('Shows a reference image in a modal on pressing the button', function(){
               var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var test_button = document.getElementById('image_reference');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                test_button.dispatchEvent(click_event);
                expect(NHMobileForm.prototype.show_reference).toHaveBeenCalled();
                expect(NHMobileForm.prototype.show_reference.calls.count()).toBe(1);
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('popup_image');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Test Reference Image');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<img src="/"/>');
            });

            it('Shows a reference iframe in a modal on pressing the button', function(){
               var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var test_button = document.getElementById('iframe_reference');
                var click_event = document.createEvent('CustomEvent');
                click_event.initCustomEvent('click', false, true, false);
                test_button.dispatchEvent(click_event);
                expect(NHMobileForm.prototype.show_reference).toHaveBeenCalled();
                expect(NHMobileForm.prototype.show_reference.calls.count()).toBe(1);
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('popup_iframe');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Test Reference Iframe');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<iframe src="/"></iframe>');
            });
        })

        describe('Setting exclude classes on unselected radio inputs', function(){
            var mobile;
             beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit');
                spyOn(NHMobileForm.prototype, 'handle_timeout');
                spyOn(NHMobileForm.prototype, 'trigger_actions').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                    var promise = new Promise();
                    promise.complete([{}]);
                    return promise;
                });

                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                    '<input type="radio" name="radio_1" id="radio_1" value="1">' +
                    '<input type="radio" name="radio_1" id="radio_2" value="2">' +
                    '<input type="radio" name="radio_1" id="radio_3" value="3">' +
                    '<input type="radio" name="radio_jackie" id="radio_jackie" value="3">' +
                    '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                    '</form>';
                mobile = new NHMobileForm();
            });

            afterEach(function(){
               cleanUp();
            });

            it('Adds a class of exclude to all radio inputs with the same name that do not have the same value', function(){
                var radio_1 = document.getElementById('radio_1');
                var radio_2 = document.getElementById('radio_2');
                var radio_3 = document.getElementById('radio_3');
                var radio_jackie = document.getElementById('radio_jackie');
                radio_1.checked = true;
                var change_event = document.createEvent('CustomEvent');
                change_event.initCustomEvent('click', false, true, false);
                radio_1.dispatchEvent(change_event);
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(radio_1.classList.contains('exclude')).not.toBe(true);
                expect(radio_2.classList.contains('exclude')).toBe(true);
                expect(radio_3.classList.contains('exclude')).toBe(true);
                expect(radio_jackie.classList.contains('exclude')).not.toBe(true);
            });
        });
    });

    describe('Form Validation', function() {
        beforeEach(function () {

        });

        afterEach(function () {
            cleanUp();
        });

        it('Has functionality to validate a form', function(){
           expect(typeof(NHMobileForm.prototype.validate)).toBe('function');
        });

        it('Has functionality to reset input errors so we can correct invalid inputs', function(){
           expect(typeof(NHMobileForm.prototype.reset_input_errors)).toBe('function');
        });

        it('Has functionality to add input errors so we can flag up invalid inputs', function(){
           expect(typeof(NHMobileForm.prototype.add_input_errors)).toBe('function');
        });
    });

    describe('Form Timeout', function() {
        var mobile;
        beforeEach(function () {
            spyOn(NHMobileForm.prototype, 'submit');
            spyOn(NHMobileForm.prototype, 'handle_timeout').and.callThrough();
            spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                var promise = new Promise();
                promise.complete([{}]);
                return promise;
            });
            spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
            var test = document.getElementById('test');
            test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                '<input type="submit" value="Test Submit" id="submit">' +
                '<input type="reset" value="Test Reset" id="reset">' +
                '<input type="radio" value="test_radio" id="radio">' +
                '<button id="reference">Test Button</button>' +
                '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                '</form>';
            mobile = new NHMobileForm();
        });

        afterEach(function () {
            cleanUp();
        });

        it('Has functionality to handle a form timeout', function(){
           expect(typeof(NHMobileForm.prototype.handle_timeout)).toBe('function');
        });

        it('Has functionality to reset the form timeout so form is kept alive when entering data', function(){
           expect(typeof(NHMobileForm.prototype.reset_form_timeout)).toBe('function');
        });

        it('Returns the task back to the server and informs the user that the form timed out', function(){
            var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
            var change_event = document.createEvent('CustomEvent', {
                'detail': 'form timed out'
            });
            change_event.initCustomEvent('form_timeout', false, true, false);
            document.dispatchEvent(change_event);
            expect(NHMobileForm.prototype.handle_timeout).toHaveBeenCalled();
            expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
            expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('form_timeout');
            expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Task window expired');
            expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p class="block">Please pick the task again from the task list if you wish to complete it</p>');
        });
    });

    describe('Form Submission', function() {
        beforeEach(function () {

        });

        afterEach(function () {
            cleanUp();
        });
        it('Has functionality to submit a form', function(){
           expect(typeof(NHMobileForm.prototype.submit)).toBe('function');
        });

        it('Has functionality to display partial reasons if a form is partially filled in', function(){
           expect(typeof(NHMobileForm.prototype.display_partial_reasons)).toBe('function');
        });

        it('Has functionality to submit a completed form to the server', function(){
           expect(typeof(NHMobileForm.prototype.submit_observation)).toBe('function');
        });

        it('Has functionality to display cancellation reasons if cancelling a notification', function(){
           expect(typeof(NHMobileForm.prototype.cancel_notification)).toBe('function');
        });

        it('Has functionality to submit a partially filled form to the server', function(){
           expect(typeof(NHMobileForm.prototype.process_partial_submit)).toBe('function');
        });

        it('Has functionality to submit a form that has a score', function(){
           expect(typeof(NHMobileForm.prototype.process_post_score_submit)).toBe('function');
        });
    });
});