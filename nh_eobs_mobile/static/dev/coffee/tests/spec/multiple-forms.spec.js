/**
 * Created by Colin.Wren on 16/05/2017.
 */
describe("Data Entry Functionality when multiple forms are present in view", function(){
    var mobile = null;
    beforeEach(function(){
        var bodyEl = document.getElementsByTagName('body')[0];
        var test = document.getElementById('test');
        if (test != null) {
            test.parentNode.removeChild(test);
        }
        var testArea = document.createElement('div');
        testArea.setAttribute('id', 'test');
        testArea.style.height = '500px';
        testArea.innerHTML =
            '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
            '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
            '<div class="block obsField" id="parent_test_int">' +
            '<div class="input-header">' +
            '<label for="test_int_1">Test Integer Form 1</label>' +
            '<input type="number" name="test_int_1" id="test_int_1" min="10" max="20" step="1" data-required="false" data-necessary="true">' +
            '</div>' +
            '<div class="input-body">' +
            '<span class="errors"></span>' +
            '<span class="help"></span>' +
            '</div>' +
            '</div>' +
            '</form>' +
            '<form action="test" method="POST" data-type="test" task-id="1" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,1">' +
            '<div class="block obsField" id="parent_test_int">' +
            '<div class="input-header">' +
            '<label for="test_int_2">Test Integer Form 2</label>' +
            '<input type="number" name="test_int_2" id="test_int_2" min="10" max="20" step="1" data-required="false" data-necessary="true">' +
            '</div>' +
            '<div class="input-body">' +
            '<span class="errors"></span>' +
            '<span class="help"></span>' +
            '</div>' +
            '</div>' +
            '</form>' +
            '<input type="submit" value="Submit" id="submit_button"/>';
        bodyEl.appendChild(testArea);
        mobile = new NHMobileForm();
    });

    afterEach(function(){
       cleanUp();
    });

    describe("Form Validation when multiple forms are present in view", function(){

        it("Runs validation against all forms when submit it pressed", function(){
            spyOn(NHMobileForm.prototype, 'handle_event').and.callThrough();
            spyOn(mobile, 'validate');
            spyOn(mobile, 'trigger_actions');
            spyOn(mobile, 'submit');
            var submit = document.getElementById('submit_button');
            var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                submit.dispatchEvent(clickEvent);
            expect(mobile.validate).toHaveBeenCalledTimes(2)
        });
        it("Informs user of fields with validation errors across all forms when submitting", function(){
            spyOn(NHMobileForm.prototype, 'handle_event').and.callThrough();
            spyOn(mobile, 'submit').and.callThrough();
            spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
            var submit = document.getElementById('submit_button');
            var test_int_1 = document.getElementById('test_int_1');
            var test_int_2 = document.getElementById('test_int_2');
            test_int_1.value = 666;
            test_int_2.value = 666;
            var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                submit.dispatchEvent(clickEvent);
            expect(mobile.submit).toHaveBeenCalled();
            expect(NHModal.prototype.create_dialog).toHaveBeenCalledTimes(1);
            expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('invalid_form');
            expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Form contains errors');

        });
        it("Adds error messages to the form elements when validation errors occur", function(){
            spyOn(NHMobileForm.prototype, 'handle_event').and.callThrough();
            spyOn(mobile, 'validate').and.callThrough();
            spyOn(mobile, 'submit');
            var submit = document.getElementById('submit_button');
            var test_int_1 = document.getElementById('test_int_1');
            var test_int_2 = document.getElementById('test_int_2');
            test_int_1.value = 666;
            test_int_2.value = 666;
            var clickEvent = document.createEvent('CustomEvent');
            clickEvent.initCustomEvent('click', false, true, false);
            submit.dispatchEvent(clickEvent);
            expect(mobile.validate).toHaveBeenCalled();
            expect(test_int_1.parentNode.parentNode.classList.contains('error')).toBe(true);
            expect(test_int_2.parentNode.parentNode.classList.contains('error')).toBe(true);
        });
    });

    describe("Form Timeout when multiple forms are present in view", function(){
       it("Resets the counter when fields are changed on any of the forms", function(){
            spyOn(NHMobileForm.prototype, 'reset_form_timeout').and.callThrough();
            var test_int_1 = document.getElementById('test_int_1');
            var test_int_2 = document.getElementById('test_int_2');
            test_int_1.value = 666;
            var changeEvent = document.createEvent('CustomEvent');
            changeEvent.initCustomEvent('change', false, true, false);
            test_int_1.dispatchEvent(changeEvent);
            expect(NHMobileForm.prototype.reset_form_timeout).toHaveBeenCalledTimes(2);

            test_int_2.value = 666;
            var changeEvent = document.createEvent('CustomEvent');
            changeEvent.initCustomEvent('change', false, true, false);
            test_int_2.dispatchEvent(changeEvent);
            expect(NHMobileForm.prototype.reset_form_timeout).toHaveBeenCalledTimes(4);
       });
    });

    describe("Form Submissions when multiple forms are present in view", function(){
       it("Submits each form separately in order", function(){
          fail();
       });
       it("Removes escalation tasks from the form once they have been successfully completed", function(){
          fail();
       });
       it("Stops submitting the forms if one of the forms returns an error", function(){
          fail();
       });
    });
});