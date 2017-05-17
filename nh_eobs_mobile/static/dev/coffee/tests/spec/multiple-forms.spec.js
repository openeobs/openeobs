/**
 * Created by Colin.Wren on 16/05/2017.
 */
describe("Data Entry Functionality when multiple forms are present in view", function(){
    beforeEach(function(){
        var bodyEl = document.getElementsByTagName('body')[0];
        var test = document.getElementById('test');
        if (test != null) {
            test.parentNode.removeChild(test);
        }
        var testArea = document.createElement('div');
        testArea.setAttribute('id', 'test');
        testArea.style.height = '500px';
        testArea.innerHTML = '';
        bodyEl.appendChild(testArea);
    });

    afterEach(function(){
       cleanUp();
    });

    describe("Form Validation when multiple forms are present in view", function(){
        it("Runs validation against all forms when submit it pressed", function(){
           fail();
        });
        it("Informs user of fields with validation errors across all forms when submitting", function(){
           fail();
        });
        it("Adds error messages to the form elements when validation errors occur", function(){
           fail();
        });
    });
    describe("Form Timeout when multiple forms are present in view", function(){
       it("Has one form timeout counter across all forms", function(){
          fail();
       });
       it("Resets the counter when fields are changed on any of the forms", function(){
          fail();
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