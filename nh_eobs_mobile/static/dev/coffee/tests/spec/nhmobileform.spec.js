describe('NHMobileForm - EventListeners', function(){
   beforeEach(function(){
       var test = document.getElementById('test');
       if(test != null){
           test.parentNode.removeChild(test);
       }
       var test_area = document.createElement('div');
       test_area.setAttribute('id', 'test');
       test_area.style.height = '500px';
       test_area.innerHTML = '<h2 id="patientName"><a href="#">Test Patient</a></h2><form action="" method="POST" data-type="ews" task-id="704" patient-id="11" id="obsForm" data-source="task" ajax-action="json_task_form_action" ajax-args="ews,7309"><div><div class="block obsField" id="parent_respiration_rate"><div class="input-header"><label for="respiration_rate">Respiration Rate</label><input type="number" name="respiration_rate" id="respiration_rate" min="1" max="59" step="1"></div><div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div><div><div class="block obsSelectField" id="parent_oxygen_administration_flag"><div class="input-header"><label for="oxygen_administration_flag">Patient on supplemental O2</label></div><div class="input-body"><select id="oxygen_administration_flag" name="oxygen_administration_flag" data-onchange="[{\'False\': {\'hide\': [\'device_id\', \'flow_rate\', \'concentration\', \'cpap_peep\', \'niv_backup\', \'niv_ipap\', \'niv_epap\'], \'show\': []}, \'True\': {\'hide\': [], \'show\': [\'device_id\']}}]"><option value="">Please Select</option><option value="False">No</option><option value="True">Yes</option></select><span class="errors"></span><span class="help"></span></div></div></div><div class="block obsSubmit"><input type="submit" value="Submit" id="submitButton" class="exclude"></div></form>';
       document.getElementsByTagName('body')[0].appendChild(test_area);
   });

   it('validate event is triggered on input change', function(){
       spyOn(window.NHMobileForm.prototype, "validate");
       var mobile_form = new window.NHMobileForm();
       var test_input = document.getElementById('respiration_rate');
       //var change_event = new Event('change');
       if(document.createEvent){
	       var change_event = new Event('change');
	       test_input.dispatchEvent(change_event);
       }else{
	       var change_event = document.createEventObject();
	       test_input.fireEvent('change', change_event)
       }       expect(window.NHMobileForm.prototype.validate).toHaveBeenCalled();
   });

   it('trigger_actions event is triggered on select change', function(){
       spyOn(window.NHMobileForm.prototype, "trigger_actions");
       var mobile_form = new window.NHMobileForm();
       var test_input = document.getElementById('oxygen_administration_flag');
       //var change_event = new Event('change');
       if(document.createEvent){
	       var change_event = new Event('change');
	       test_input.dispatchEvent(change_event);
       }else{
	       var change_event = document.createEventObject();
	       test_input.fireEvent('change', change_event)
       }
       //test_input.dispatchEvent(change_event);
       expect(window.NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
   });

    /* it('submit event is triggered on submit button click', function(){
        spyOn(window.NHMobileForm.prototype, "submit");
        var mobile_form = new window.NHMobileForm();
        var test_input = document.getElementById('submitButton');
        test_input.click()
        expect(window.NHMobileForm.prototype.submit).toHaveBeenCalled();
    }); */

    it('submit partial is triggered', function(){
       spyOn(window.NHMobileForm.prototype, "display_partial_reasons");
        var mobile_form = new window.NHMobileForm();
        var test_input = document.getElementById('submitButton');
        test_input.click();
        expect(window.NHMobileForm.prototype.display_partial_reasons).toHaveBeenCalled();
    });

    it('submit full is triggered', function(){
        spyOn(window.NHMobileForm.prototype, "submit_observation");
        var mobile_form = new window.NHMobileForm();
        var rr_el = document.getElementById('respiration_rate');
        rr_el.value = 18;
        var supp_el = document.getElementById('oxygen_administration_flag');
        supp_el.value  = 'False';
        var test_input = document.getElementById('submitButton');
        test_input.click();
        expect(window.NHMobileForm.prototype.submit_observation).toHaveBeenCalled();
    });

    it('sets up the form  timeout', function() {
        var mobile_form = new window.NHMobileForm();
        expect(typeof(window.form_timeout)).toBe('number');
    });
    
    it('triggers a validation error when respiration rate is too low', function(){
    	spyOn(window.NHMobileForm.prototype, "validate").and.callThrough();
    	var mobile_form = new window.NHMobileForm();
    	var test_input = document.getElementById('respiration_rate');
    	test_input.value = -1;
    	//var change_event = new Event('change');
       if(document.createEvent){
	       var change_event = new Event('change');
	       test_input.dispatchEvent(change_event);
       }else{
	       var change_event = document.createEventObject();
	       test_input.fireEvent('change', change_event)
       }
		//test_input.dispatchEvent(change_event);
	    expect(window.NHMobileForm.prototype.validate).toHaveBeenCalled();
	    expect(test_input.classList.contains('error')).toBe(true);
	    var parent_el = test_input.parentNode.parentNode;
	    expect(parent_el.classList.contains('error')).toBe(true);
	    var error_el = parent_el.getElementsByClassName('errors')[0];
	    expect(error_el.textContent).toBe('Input too low');
    });
    
    it('triggers a validation error when respiration rate is too high', function(){
	   spyOn(window.NHMobileForm.prototype, "validate").and.callThrough();
    	var mobile_form = new window.NHMobileForm();
    	var test_input = document.getElementById('respiration_rate');
    	test_input.value = 9000;
    	//var change_event = new Event('change');
       if(document.createEvent){
	       var change_event = new Event('change');
	       test_input.dispatchEvent(change_event);
       }else{
	       var change_event = document.createEventObject();
	       test_input.fireEvent('change', change_event)
       }
		//test_input.dispatchEvent(change_event);
	    expect(window.NHMobileForm.prototype.validate).toHaveBeenCalled();
	    expect(test_input.classList.contains('error')).toBe(true);
	    var parent_el = test_input.parentNode.parentNode;
	    expect(parent_el.classList.contains('error')).toBe(true);
	    var error_el = parent_el.getElementsByClassName('errors')[0];
	    expect(error_el.textContent).toBe('Input too high');
    });
    
    /*it('triggers a validation error when a alphabetical value is entered in a number input', function(){
	   spyOn(window.NHMobileForm.prototype, "validate").and.callThrough();
    	var mobile_form = new window.NHMobileForm();
    	var test_input = document.getElementById('respiration_rate');
    	test_input.value = "abcd";
    	var change_event = new Event('change');
		test_input.dispatchEvent(change_event);
	    expect(window.NHMobileForm.prototype.validate).toHaveBeenCalled();
	    expect(test_input.classList.contains('error')).toBe(true);
	    var parent_el = test_input.parentNode.parentNode;
	    expect(parent_el.classList.contains('error')).toBe(true);
	    var error_el = parent_el.getElementsByClassName('errors')[0];
	    expect(error_el.textContent).toBe('Input must be a number');
    });*/
    
    it('triggers a validation error when a float is entered into an integer field', function(){
	   spyOn(window.NHMobileForm.prototype, "validate").and.callThrough();
    	var mobile_form = new window.NHMobileForm();
    	var test_input = document.getElementById('respiration_rate');
    	test_input.value = 45.57;
    	//var change_event = new Event('change');
       if(document.createEvent){
	       var change_event = new Event('change');
	       test_input.dispatchEvent(change_event);
       }else{
	       var change_event = document.createEventObject();
	       test_input.fireEvent('change', change_event)
       }
		//test_input.dispatchEvent(change_event);
	    expect(window.NHMobileForm.prototype.validate).toHaveBeenCalled();
	    expect(test_input.classList.contains('error')).toBe(true);
	    var parent_el = test_input.parentNode.parentNode;
	    expect(parent_el.classList.contains('error')).toBe(true);
	    var error_el = parent_el.getElementsByClassName('errors')[0];
	    expect(error_el.textContent).toBe('Must be whole number');
    });
    
    /* it('triggers a validation error when a diastolic BP is entered and no systolic BP input is entered', function(){
	   expect(1).toBe(0); 
    });
    
    it('triggers a validation error when a diastolic BP is entered that is higher than the systolic BP value', function(){
	   expect(1).toBe(0); 
    });
    
    it('clears the validation error when the diastolic BP input is updated to a valid value', function(){
	   expect(1).toBe(0); 
    });
    
    it('shows supplementary o2 device list when oxygen administration flag is set to true', function(){
	   expect(1).toBe(0); 
    });
    
    it('hides supplementary o2 device list when oxygen administration flag is set to false', function(){
	   expect(1).toBe(0); 
    });
    
    it('shows standing BP fields when sitting BP fields are both entered', function(){
	   expect(1).toBe(0); 
    });
    
    it('hides standing BP fields when sitting BP field is cleared', function(){
	   expect(1).toBe(0); 
    });
*/

    afterEach(function(){
        var test = document.getElementById('test');
        if(test != null){
            test.parentNode.removeChild(test);
        }
         var covers = document.getElementsByClassName('cover');
        var body = document.getElementsByTagName('body')[0];
         for(var i = 0; i < covers.length; i++){
	        var cover = covers[i];
	        body.removeChild(cover);
        }
        clearInterval(window.form_timeout);
    });


});