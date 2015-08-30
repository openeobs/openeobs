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
        beforeEach(function(){

        });

        afterEach(function(){
           cleanUp();
        });

        it('Has functionality to trigger actions based on interactions with a form', function(){
           expect(typeof(NHMobileForm.prototype.trigger_actions)).toBe('function');
        });

        it('Has functionality to show a reference image for a form input', function(){
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