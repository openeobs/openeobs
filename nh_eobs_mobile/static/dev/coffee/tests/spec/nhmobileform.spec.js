describe('NHMobileForm - Patient Information', function(){
    var mobile_form;

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
    beforeEach(function(){
       var test = document.getElementById('test');
       if(test != null){
           test.parentNode.removeChild(test);
       }
       var test_area = document.createElement('div');
       test_area.setAttribute('id', 'test');
       test_area.style.height = '500px';
       test_area.innerHTML = '<h2 id="patientName" patient-id="11"><a href="#" patient-id="11">Test Patient</a></h2>'+
         '<form action="" method="POST" data-type="ews" task-id="704" patient-id="11" id="obsForm" data-source="task" ajax-action="json_task_form_action" ajax-args="ews,7309">'+
         '<div>'+
         '<div class="block obsField" id="parent_respiration_rate">'+
         '<div class="input-header">'+
         '<label for="respiration_rate">Respiration Rate</label>'+
         '<input type="number" name="respiration_rate" id="respiration_rate" min="1" max="59" step="1">'+
         '</div>'+
         '<div class="input-body">'+
         '<span class="errors"></span><span class="help"></span>'+
         '</div></div></div>'+
         '<div><div class="block obsSelectField" id="parent_oxygen_administration_flag">'+
         '<div class="input-header">'+
         '<label for="oxygen_administration_flag">Patient on supplemental O2</label></div>'+
         '<div class="input-body">'+
         '<select id="oxygen_administration_flag" name="oxygen_administration_flag" data-onchange="[{\'False\': {\'hide\': [\'device_id\', \'flow_rate\', \'concentration\', \'cpap_peep\', \'niv_backup\', \'niv_ipap\', \'niv_epap\'], \'show\': []}, \'True\': {\'hide\': [], \'show\': [\'device_id\']}}]">'+
         '<option value="">Please Select</option>'+
         '<option value="False">No</option>'+
         '<option value="True">Yes</option>'+
         '</select>'+
         '<span class="errors"></span><span class="help"></span>'+
         '</div></div>'+
         '</div>'+
         '<div class="block obsSubmit">'+
         '<input type="submit" value="Submit" id="submitButton" class="exclude"></div></form>';
       document.getElementsByTagName('body')[0].appendChild(test_area);
       mobile_form = new window.NHMobileForm();
    });
    
    it('Get\'s the patient\'s name via the self.patient_name method', function(){
        expect(mobile_form.patient_name()).toBe('Test Patient');
    });

    it('Calls get_patient_info when Patient Name clicked', function(){
        spyOn(NHMobileForm.prototype, 'get_patient_info').and.callThrough();
        spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
            var promise = new Promise();
                promise.complete(patient_info_data);
                return promise;
        });
        var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        mobile_form.patient_name_el.dispatchEvent(click_event);
        //expect(NHMobileForm.prototype.get_patient_info).toHaveBeenCalled();
        expect(NHMobileForm.prototype.process_request).toHaveBeenCalled();
        expect(document.getElementById('patient_info')).not.toBe(null);
    });

     it('shows error popup when unable to get patient id', function(){
            spyOn(NHMobileForm.prototype, 'get_patient_info').and.callThrough();
            spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                var promise = new Promise();
                promise.complete(patient_info_data);
                return promise;
            });
            var click_event = document.createEvent('CustomEvent');
            click_event.initCustomEvent('click', false, true, false);
            mobile_form.patient_name_el.removeAttribute('patient-id');
            mobile_form.patient_name_el.dispatchEvent(click_event);
            //expect(NHMobileForm.prototype.get_patient_info).toHaveBeenCalled();
            expect(NHMobileForm.prototype.process_request).not.toHaveBeenCalled();
            expect(document.getElementById('patient_info_error')).not.toBe(null);
        });



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

describe('NHMobileForm - EventListeners', function(){
   var partial_reasons_data = [
        [1, 'Asleep'],
        [2, 'Unable to stand']
   ];
   beforeEach(function(){
       var test = document.getElementById('test');
       if(test != null){
           test.parentNode.removeChild(test);
       }
       var test_area = document.createElement('div');
       test_area.setAttribute('id', 'test');
       test_area.style.height = '500px';
       test_area.innerHTML = '<h2 id="patientName"><a href="#">Test Patient</a></h2>'+
         '<form action="" method="POST" data-type="ews" task-id="704" patient-id="11" id="obsForm" data-source="task" ajax-action="json_task_form_action" ajax-args="ews,7309">'+
         '<div>'+
         '<div class="block obsField" id="parent_respiration_rate">'+
         '<div class="input-header">'+
         '<label for="respiration_rate">Respiration Rate</label>'+
         '<input type="number" name="respiration_rate" id="respiration_rate" min="1" max="59" step="1">'+
         '</div>'+
         '<div class="input-body">'+
         '<span class="errors"></span><span class="help"></span>'+
         '</div></div></div>'+
         '<div><div class="block obsSelectField" id="parent_oxygen_administration_flag">'+
         '<div class="input-header">'+
         '<label for="oxygen_administration_flag">Patient on supplemental O2</label></div>'+
         '<div class="input-body">'+
         '<select id="oxygen_administration_flag" name="oxygen_administration_flag" data-onchange="[{\'False\': {\'hide\': [\'device_id\', \'flow_rate\', \'concentration\', \'cpap_peep\', \'niv_backup\', \'niv_ipap\', \'niv_epap\'], \'show\': []}, \'True\': {\'hide\': [], \'show\': [\'device_id\']}}]">'+
         '<option value="">Please Select</option>'+
         '<option value="False">No</option>'+
         '<option value="True">Yes</option>'+
         '</select>'+
         '<span class="errors"></span><span class="help"></span>'+
         '</div></div>'+
         '</div>'+
         '<div class="block obsSubmit">'+
         '<input type="submit" value="Submit" id="submitButton" class="exclude"></div></form>';
       document.getElementsByTagName('body')[0].appendChild(test_area);
   });

   it('validate event is triggered on input change', function(){
       spyOn(window.NHMobileForm.prototype, "validate");
       var mobile_form = new window.NHMobileForm();
       var test_input = document.getElementById('respiration_rate');
       test_input.value = 18;
	   var change_event = document.createEvent('CustomEvent');
	   change_event.initCustomEvent('change', false, false, false);
	   test_input.dispatchEvent(change_event);
       expect(window.NHMobileForm.prototype.validate).toHaveBeenCalled();
   });

   it('trigger_actions event is triggered on select change', function(){
       spyOn(window.NHMobileForm.prototype, "trigger_actions");
       var mobile_form = new window.NHMobileForm();
       var test_input = document.getElementById('oxygen_administration_flag');
       //var change_event = new Event('change');
       var change_event = document.createEvent('CustomEvent');
	   change_event.initCustomEvent('change', false, false, false);	
	   test_input.dispatchEvent(change_event)
       //test_input.dispatchEvent(change_event);
       expect(window.NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
   });

    it('submit partial is triggered', function(){
        spyOn(window.NHMobileForm.prototype, "display_partial_reasons");
        spyOn(window.NHMobileForm.prototype, "submit_observation");
        var mobile_form = new window.NHMobileForm();
        var test_input = document.getElementById('submitButton');
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('click', false, true, false);
        test_input.dispatchEvent(change_event);
        //test_input.click();
        expect(window.NHMobileForm.prototype.submit_observation).not.toHaveBeenCalled();
        expect(window.NHMobileForm.prototype.display_partial_reasons).toHaveBeenCalled();
    });

    it('submit partial is triggered and partial reasons are displayed', function(){
        spyOn(window.NHMobileForm.prototype, "display_partial_reasons").and.callThrough();
        spyOn(window.NHMobileForm.prototype, "submit_observation");
        spyOn(window.NHMobileForm.prototype, 'process_request').and.callFake(function(){
            var promise = new Promise();
            promise.complete(partial_reasons_data);
            return promise;
        });
        var mobile_form = new window.NHMobileForm();
        var test_input = document.getElementById('submitButton');
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('click', false, true, false);
        test_input.dispatchEvent(change_event);
        //test_input.click();
        expect(window.NHMobileForm.prototype.submit_observation).not.toHaveBeenCalled();
        expect(window.NHMobileForm.prototype.display_partial_reasons).toHaveBeenCalled();
        expect(window.NHMobileForm.prototype.process_request).toHaveBeenCalled();
        var partial_reasons = document.getElementById('partial_reasons');
        expect(partial_reasons).not.toBe(null);
        var reason_list = partial_reasons.getElementsByTagName('select')[0];
        var reason_list_reasons = reason_list.getElementsByTagName('option');
        expect(reason_list_reasons.length).toBe(2);
    });

    it('submit full is triggered', function(){
        spyOn(window.NHMobileForm.prototype, "submit_observation");
        var mobile_form = new window.NHMobileForm();
        var rr_el = document.getElementById('respiration_rate');
        rr_el.value = 18;
        var supp_el = document.getElementById('oxygen_administration_flag');
        supp_el.value  = 'False';
        var test_input = document.getElementById('submitButton');
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('click', false, true, false);
        test_input.dispatchEvent(change_event);
        expect(window.NHMobileForm.prototype.submit_observation).toHaveBeenCalled();
    });

    it('sets up the form  timeout', function() {
        var mobile_form = new window.NHMobileForm();
        expect(typeof(window.form_timeout)).toBe('number');
    });
    


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


describe('NHMobileForm - Validation', function(){
    beforeEach(function(){
        var test = document.getElementById('test');
        if(test != null){
            test.parentNode.removeChild(test);
        }
        var test_area = document.createElement('div');
        test_area.setAttribute('id', 'test');
        test_area.style.height = '500px';
        test_area.innerHTML = '<h2 id="patientName"><a href="#">Test Patient</a></h2>'+
        '<form action="/mobile/task/submit/716" method="POST" data-type="ews" task-id="716" patient-id="18" id="obsForm" data-source="task" ajax-action="calculate_obs_score" ajax-args="ews,716">'+
        '<div>'+
        '<div class="block obsField" id="parent_respiration_rate">'+
        '<div class="input-header">'+
        '<label for="respiration_rate">Respiration Rate</label>'+
        '<input type="number" name="respiration_rate" id="respiration_rate" min="1" max="59" step="1"/>'+
        '</div>'+
        '<div class="input-body"><span class="errors"></span><span class="help"></span>'+
        '</div></div></div>'+
        '<div><div class="block obsField" id="parent_indirect_oxymetry_spo2">'+
        '<div class="input-header">'+
        '<label for="indirect_oxymetry_spo2">O2 Saturation</label>'+
        '<input type="number" name="indirect_oxymetry_spo2" id="indirect_oxymetry_spo2" min="51" max="100" step="1"/>'+
        '</div>'+
        '<div class="input-body"><span class="errors"></span><span class="help"></span></div>'+
        '</div></div>'+
        '<div><div class="block obsField" id="parent_body_temperature">'+
        '<div class="input-header"><label for="body_temperature">Body Temperature</label>'+
        '<input type="number" name="body_temperature" id="body_temperature" min="27.1" max="44.9" step="0.1"/>'+
        '</div><div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div>'+
        '<div><div class="block obsField" id="parent_blood_pressure_systolic">'+
        '<div class="input-header"><label for="blood_pressure_systolic">Blood Pressure Systolic</label>'+
        '<input type="number" name="blood_pressure_systolic" id="blood_pressure_systolic" min="1" max="300" step="1" data-validation="[{\'message\': {\'target\': \'Systolic BP must be more than Diastolic BP\', \'value\': \'Diastolic BP must be less than Systolic BP\'}, \'condition\': {\'operator\': \'>\', \'target\': \'blood_pressure_systolic\', \'value\': \'blood_pressure_diastolic\'}}]"/></div>'+
        '<div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div>'+
        '<div><div class="block obsField" id="parent_blood_pressure_diastolic"><div class="input-header">'+
        '<label for="blood_pressure_diastolic">Blood Pressure Diastolic</label>'+
        '<input type="number" name="blood_pressure_diastolic" id="blood_pressure_diastolic" min="1" max="280" step="1" data-validation="[{\'message\': {\'target\': \'Diastolic BP must be less than Systolic BP\', \'value\': \'Systolic BP must be more than Diastolic BP\'}, \'condition\': {\'operator\': \'<\', \'target\': \'blood_pressure_diastolic\', \'value\': \'blood_pressure_systolic\'}}]"/></div>'+
        '<div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div><div>'+
        '<div class="block obsField" id="parent_pulse_rate"><div class="input-header"><label for="pulse_rate">Pulse Rate</label>'+
        '<input type="number" name="pulse_rate" id="pulse_rate" min="1" max="250" step="1"/></div>'+
        '<div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div>'+
        '<div><div class="block obsSelectField" id="parent_avpu_text"><div class="input-header"><label for="avpu_text">AVPU</label></div>'+
        '<div class="input-body"><select id="avpu_text" name="avpu_text">'+
        '<option value="">Please Select</option>'+
        '<option value="A">Alert</option>'+
        '<option value="V">Voice</option>'+
        '<option value="P">Pain</option>'+
        '<option value="U">Unresponsive</option></select>'+
        '<span class="errors"></span><span class="help"></span></div></div></div>'+
        '<div><div class="block obsSelectField" id="parent_oxygen_administration_flag">'+
        '<div class="input-header"><label for="oxygen_administration_flag">Patient on supplemental O2</label></div><div class="input-body">'+
        '<select id="oxygen_administration_flag" name="oxygen_administration_flag" data-onchange="[{\'action\': \'show\', \'fields\': [\'device_id\'], \'condition\': [[\'oxygen_administration_flag\', \'==\', \'True\']]}, {\'action\': \'hide\', \'fields\': [\'device_id\', \'flow_rate\', \'concentration\', \'cpap_peep\', \'niv_backup\', \'niv_ipap\', \'niv_epap\'], \'condition\': [[\'oxygen_administration_flag\', \'!=\', \'True\']]}]">'+
        '<option value="">Please Select</option>'+
        '<option value="False">No</option>'+
        '<option value="True">Yes</option> </select> '+
        '<span class="errors"></span><span class="help"></span></div></div></div>'+
        '<div><div class="block obsSelectField valHide" id="parent_device_id"><div class="input-header">'+
        '<label for="device_id">O2 Device</label></div>'+
        '<div class="input-body"><select id="device_id" name="device_id" class="exclude" data-onchange="[{\'action\': \'show\', \'fields\': [\'flow_rate\', \'concentration\'], \'condition\': [[\'device_id\', \'!=\', \'\']]}, {\'action\': \'hide\', \'fields\': [\'flow_rate\', \'concentration\'], \'condition\': [[\'device_id\', \'==\', \'\']]}, {\'action\': \'show\', \'fields\': [\'cpap_peep\'], \'condition\': [[\'device_id\', \'==\', 44]]}, {\'action\': \'hide\', \'fields\': [\'cpap_peep\'], \'condition\': [[\'device_id\', \'!=\', 44]]}, {\'action\': \'show\', \'fields\': [\'niv_backup\', \'niv_ipap\', \'niv_epap\'], \'condition\': [[\'device_id\', \'==\', 45]]}, {\'action\': \'hide\', \'fields\': [\'niv_backup\', \'niv_ipap\', \'niv_epap\'], \'condition\': [[\'device_id\', \'!=\', 45]]}]">'+
        '<option value="">Please Select</option>'+
        '<option value="36">Nasal Cannula</option>'+
        '<option value="37">Simple Mask</option>'+
        '<option value="38">With Reservoir</option>'+
        '<option value="39">Aerosol/Neb</option>'+
        '<option value="40">Venturi Mask</option>'+
        '<option value="41">Humidified System</option>'+
        '<option value="42">Tracheostomy</option>'+
        '<option value="43">Intubated</option>'+
        '<option value="44">CPAP</option>'+
        '<option value="45">NIV BiPAP</option>'+
        '</select><span class="errors"></span><span class="help"></span></div> </div></div>'+
        '<div><div class="block obsField valHide" id="parent_flow_rate">'+
        '<div class="input-header"><label for="flow_rate">Flow Rate</label>'+
        '<input type="number" name="flow_rate" id="flow_rate" max="100.0" step="0.1" class="exclude"/></div>'+
        '<div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div>'+
        '<div><div class="block obsField valHide" id="parent_concentration">'+
        '<div class="input-header"><label for="concentration">Concentration</label>'+
        '<input type="number" name="concentration" id="concentration" max="100" step="1" class="exclude"/></div>'+
        '<div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div>'+
        '<div><div class="block obsField valHide" id="parent_cpap_peep"><div class="input-header">'+
        '<label for="cpap_peep">CPAP: PEEP (cmH2O)</label><input type="number" name="cpap_peep" id="cpap_peep" max="1000" step="1" class="exclude"/></div>'+
        '<div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div><div>'+
        '<div class="block obsField valHide" id="parent_niv_backup"><div class="input-header">'+
        '<label for="niv_backup">NIV: Back-up rate (br/min)</label>'+
        '<input type="number" name="niv_backup" id="niv_backup" max="100" step="1" class="exclude"/></div>'+
        '<div class="input-body"> <span class="errors"></span><span class="help"></span></div></div></div>'+
        '<div><div class="block obsField valHide" id="parent_niv_ipap"><div class="input-header">'+
        '<label for="niv_ipap">NIV: IPAP (cmH2O)</label><input type="number" name="niv_ipap" id="niv_ipap" max="100" step="1" class="exclude"/></div>'+
        '<div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div>'+
        '<div><div class="block obsField valHide" id="parent_niv_epap"><div class="input-header">'+
        '<label for="niv_epap">NIV: EPAP (cmH2O)</label><input type="number" name="niv_epap" id="niv_epap" max="100" step="1" class="exclude"/></div>'+
        '<div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div><input type="hidden" name="taskId" value="716"/>'+
        '<input type="hidden" name="startTimestamp" id="startTimestamp" value="1418642726"/><div class="block obsSubmit">'+
        '<input type="submit" value="Submit" class="exclude" id="submitButton"/></div></form>';
        document.getElementsByTagName('body')[0].appendChild(test_area);
    });

    it('triggers a validation error when respiration rate is too low', function(){
        spyOn(window.NHMobileForm.prototype, "validate").and.callThrough();
        var mobile_form = new window.NHMobileForm();
        var test_input = document.getElementById('respiration_rate');
        test_input.value = -1;
        //var change_event = new Event('change');
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('change', false, false, false);
        test_input.dispatchEvent(change_event)
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
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('change', false, false, false);
        test_input.dispatchEvent(change_event)
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
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('change', false, false, false);
        test_input.dispatchEvent(change_event)
        //test_input.dispatchEvent(change_event);
        expect(window.NHMobileForm.prototype.validate).toHaveBeenCalled();
        expect(test_input.classList.contains('error')).toBe(true);
        var parent_el = test_input.parentNode.parentNode;
        expect(parent_el.classList.contains('error')).toBe(true);
        var error_el = parent_el.getElementsByClassName('errors')[0];
        expect(error_el.textContent).toBe('Must be whole number');
    });

    it('triggers a validation error when a diastolic BP is entered and no systolic BP input is entered', function(){
        spyOn(window.NHMobileForm.prototype, "validate").and.callThrough();
        var mobile_form = new window.NHMobileForm();
        var test_input = document.getElementById('blood_pressure_diastolic');
        test_input.value = 80;
        //var change_event = new Event('change');
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('change', false, false, false);
        test_input.dispatchEvent(change_event)
        //test_input.dispatchEvent(change_event);
        expect(window.NHMobileForm.prototype.validate).toHaveBeenCalled();
        expect(test_input.classList.contains('error')).toBe(true);
        var parent_el = test_input.parentNode.parentNode;
        expect(parent_el.classList.contains('error')).toBe(true);
        var error_el = parent_el.getElementsByClassName('errors')[0];
        expect(error_el.textContent).toBe('Diastolic BP must be less than Systolic BP');
        var other_input = document.getElementById('blood_pressure_systolic');
        expect(other_input.classList.contains('error')).toBe(true);
        var other_input_parent = other_input.parentNode.parentNode;
        expect(other_input_parent.classList.contains('error')).toBe(true);
        var other_input_error = other_input_parent.getElementsByClassName('errors')[0];
        expect(other_input_error.textContent).toBe('Please enter a value');
    });

    it('triggers a validation error when a diastolic BP is entered that is higher than the systolic BP value', function(){
        spyOn(window.NHMobileForm.prototype, "validate").and.callThrough();
        var mobile_form = new window.NHMobileForm();
        var test_input = document.getElementById('blood_pressure_diastolic');
        var other_input = document.getElementById('blood_pressure_systolic');
        test_input.value = 120;
        other_input.value = 80;
        //var change_event = new Event('change');
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('change', false, false, false);
        test_input.dispatchEvent(change_event)
        //test_input.dispatchEvent(change_event);
        expect(window.NHMobileForm.prototype.validate).toHaveBeenCalled();
        expect(test_input.classList.contains('error')).toBe(true);
        var parent_el = test_input.parentNode.parentNode;
        expect(parent_el.classList.contains('error')).toBe(true);
        var error_el = parent_el.getElementsByClassName('errors')[0];
        expect(error_el.textContent).toBe('Diastolic BP must be less than Systolic BP');
        expect(other_input.classList.contains('error')).toBe(true);
        var other_input_parent = other_input.parentNode.parentNode;
        expect(other_input_parent.classList.contains('error')).toBe(true);
        var other_input_error = other_input_parent.getElementsByClassName('errors')[0];
        expect(other_input_error.textContent).toBe('Systolic BP must be more than Diastolic BP');
    });

    it('clears the validation error when the diastolic BP input is updated to a valid value', function(){
        spyOn(window.NHMobileForm.prototype, "validate").and.callThrough();
        var mobile_form = new window.NHMobileForm();
        var test_input = document.getElementById('blood_pressure_diastolic');
        var other_input = document.getElementById('blood_pressure_systolic');
        test_input.value = 120;
        other_input.value = 80;
        //var change_event = new Event('change');
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('change', false, false, false);
        test_input.dispatchEvent(change_event)
        //test_input.dispatchEvent(change_event);
        expect(window.NHMobileForm.prototype.validate).toHaveBeenCalled();
        expect(test_input.classList.contains('error')).toBe(true);
        var parent_el = test_input.parentNode.parentNode;
        expect(parent_el.classList.contains('error')).toBe(true);
        var error_el = parent_el.getElementsByClassName('errors')[0];
        expect(error_el.textContent).toBe('Diastolic BP must be less than Systolic BP');
        expect(other_input.classList.contains('error')).toBe(true);
        var other_input_parent = other_input.parentNode.parentNode;
        expect(other_input_parent.classList.contains('error')).toBe(true);
        var other_input_error = other_input_parent.getElementsByClassName('errors')[0];
        expect(other_input_error.textContent).toBe('Systolic BP must be more than Diastolic BP');


        // update to test cleared
        test_input.value = 80;
        other_input.value = 120;
        var update_event = document.createEvent('CustomEvent');
        update_event.initCustomEvent('change', false, false, false);
        test_input.dispatchEvent(update_event);
        expect(window.NHMobileForm.prototype.validate).toHaveBeenCalled();
        expect(test_input.classList.contains('error')).toBe(false);
        var parent_el = test_input.parentNode.parentNode;
        expect(parent_el.classList.contains('error')).toBe(false);
        var error_el = parent_el.getElementsByClassName('errors')[0];
        expect(error_el.textContent).toBe('');
        expect(other_input.classList.contains('error')).toBe(false);
        var other_input_parent = other_input.parentNode.parentNode;
        expect(other_input_parent.classList.contains('error')).toBe(false);
        var other_input_error = other_input_parent.getElementsByClassName('errors')[0];
        expect(other_input_error.textContent).toBe('');
    });
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



describe('NHMobileForm - Triggered Actions', function(){
    beforeEach(function(){
        var test = document.getElementById('test');
        if(test != null){
            test.parentNode.removeChild(test);
        }
        var test_area = document.createElement('div');
        test_area.setAttribute('id', 'test');
        test_area.style.height = '500px';
        test_area.innerHTML = '<h2 id="patientName"><a href="#">Test Patient</a></h2><form action="/mobile/task/submit/716" method="POST" data-type="ews" task-id="716" patient-id="18" id="obsForm" data-source="task" ajax-action="calculate_obs_score" ajax-args="ews,716"><div><div class="block obsField" id="parent_respiration_rate"><div class="input-header"><label for="respiration_rate">Respiration Rate</label><input type="number" name="respiration_rate" id="respiration_rate" min="1" max="59" step="1"/></div><div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div><div><div class="block obsField" id="parent_indirect_oxymetry_spo2"><div class="input-header"><label for="indirect_oxymetry_spo2">O2 Saturation</label><input type="number" name="indirect_oxymetry_spo2" id="indirect_oxymetry_spo2" min="51" max="100" step="1"/></div><div class="input-body"><span class="errors"></span><span class="help"></span></div> </div></div><div><div class="block obsField" id="parent_body_temperature"><div class="input-header"><label for="body_temperature">Body Temperature</label><input type="number" name="body_temperature" id="body_temperature" min="27.1" max="44.9" step="0.1"/></div><div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div><div><div class="block obsField" id="parent_blood_pressure_systolic"><div class="input-header"><label for="blood_pressure_systolic">Blood Pressure Systolic</label><input type="number" name="blood_pressure_systolic" id="blood_pressure_systolic" min="1" max="300" step="1" data-validation="[[\'<\', \'blood_pressure_diastolic\']]"/></div><div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div><div><div class="block obsField" id="parent_blood_pressure_diastolic"><div class="input-header"><label for="blood_pressure_diastolic">Blood Pressure Diastolic</label><input type="number" name="blood_pressure_diastolic" id="blood_pressure_diastolic" min="1" max="280" step="1" data-validation="[[\'>\', \'blood_pressure_systolic\']]"/></div><div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div><div><div class="block obsField" id="parent_pulse_rate"><div class="input-header"><label for="pulse_rate">Pulse Rate</label><input type="number" name="pulse_rate" id="pulse_rate" min="1" max="250" step="1"/></div><div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div><div><div class="block obsSelectField" id="parent_avpu_text"><div class="input-header"><label for="avpu_text">AVPU</label></div><div class="input-body"><select id="avpu_text" name="avpu_text"><option value="">Please Select</option> <option value="A">Alert</option><option value="V">Voice</option><option value="P">Pain</option><option value="U">Unresponsive</option></select><span class="errors"></span><span class="help"></span></div></div></div><div><div class="block obsSelectField" id="parent_oxygen_administration_flag"><div class="input-header"><label for="oxygen_administration_flag">Patient on supplemental O2</label></div><div class="input-body"><select id="oxygen_administration_flag" name="oxygen_administration_flag" data-onchange="[{\'action\': \'show\', \'fields\': [\'device_id\'], \'condition\': [[\'oxygen_administration_flag\', \'==\', \'True\']]}, {\'action\': \'hide\', \'fields\': [\'device_id\', \'flow_rate\', \'concentration\', \'cpap_peep\', \'niv_backup\', \'niv_ipap\', \'niv_epap\'], \'condition\': [[\'oxygen_administration_flag\', \'!=\', \'True\']]}]"><option value="">Please Select</option><option value="False">No</option><option value="True">Yes</option> </select> <span class="errors"></span><span class="help"></span></div></div></div><div><div class="block obsSelectField valHide" id="parent_device_id"><div class="input-header"><label for="device_id">O2 Device</label></div><div class="input-body"><select id="device_id" name="device_id" class="exclude" data-onchange="[{\'action\': \'show\', \'fields\': [\'flow_rate\', \'concentration\'], \'condition\': [[\'device_id\', \'!=\', \'\']]}, {\'action\': \'hide\', \'fields\': [\'flow_rate\', \'concentration\'], \'condition\': [[\'device_id\', \'==\', \'\']]}, {\'action\': \'show\', \'fields\': [\'cpap_peep\'], \'condition\': [[\'device_id\', \'==\', 44]]}, {\'action\': \'hide\', \'fields\': [\'cpap_peep\'], \'condition\': [[\'device_id\', \'!=\', 44]]}, {\'action\': \'show\', \'fields\': [\'niv_backup\', \'niv_ipap\', \'niv_epap\'], \'condition\': [[\'device_id\', \'==\', 45]]}, {\'action\': \'hide\', \'fields\': [\'niv_backup\', \'niv_ipap\', \'niv_epap\'], \'condition\': [[\'device_id\', \'!=\', 45]]}]"><option value="">Please Select</option><option value="36">Nasal Cannula</option><option value="37">Simple Mask</option><option value="38">With Reservoir</option><option value="39">Aerosol/Neb</option><option value="40">Venturi Mask</option><option value="41">Humidified System</option><option value="42">Tracheostomy</option><option value="43">Intubated</option><option value="44">CPAP</option><option value="45">NIV BiPAP</option></select><span class="errors"></span><span class="help"></span></div> </div></div><div><div class="block obsField valHide" id="parent_flow_rate"><div class="input-header"><label for="flow_rate">Flow Rate</label><input type="number" name="flow_rate" id="flow_rate" max="100.0" step="0.1" class="exclude"/></div><div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div><div><div class="block obsField valHide" id="parent_concentration"><div class="input-header"><label for="concentration">Concentration</label><input type="number" name="concentration" id="concentration" max="100" step="1" class="exclude"/></div><div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div><div><div class="block obsField valHide" id="parent_cpap_peep"><div class="input-header"><label for="cpap_peep">CPAP: PEEP (cmH2O)</label><input type="number" name="cpap_peep" id="cpap_peep" max="1000" step="1" class="exclude"/></div><div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div><div><div class="block obsField valHide" id="parent_niv_backup"><div class="input-header"><label for="niv_backup">NIV: Back-up rate (br/min)</label><input type="number" name="niv_backup" id="niv_backup" max="100" step="1" class="exclude"/></div><div class="input-body"> <span class="errors"></span><span class="help"></span></div></div></div><div><div class="block obsField valHide" id="parent_niv_ipap"><div class="input-header"><label for="niv_ipap">NIV: IPAP (cmH2O)</label><input type="number" name="niv_ipap" id="niv_ipap" max="100" step="1" class="exclude"/></div><div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div><div><div class="block obsField valHide" id="parent_niv_epap"><div class="input-header"><label for="niv_epap">NIV: EPAP (cmH2O)</label><input type="number" name="niv_epap" id="niv_epap" max="100" step="1" class="exclude"/></div><div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div><input type="hidden" name="taskId" value="716"/><input type="hidden" name="startTimestamp" id="startTimestamp" value="1418642726"/><div class="block obsSubmit"><input type="submit" value="Submit" class="exclude" id="submitButton"/></div></form>';
        document.getElementsByTagName('body')[0].appendChild(test_area);
    });

    it('shows supplementary o2 device list when oxygen administration flag is set to true', function(){
        spyOn(window.NHMobileForm.prototype, "trigger_actions").and.callThrough();
        var mobile_form = new window.NHMobileForm();
        var test_input = document.getElementById('oxygen_administration_flag');
        var other_input = document.getElementById('device_id');
        test_input.value = 'True';
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('change', false, false, false);
        test_input.dispatchEvent(change_event);
        expect(window.NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
        // other_input to have exclude class
        expect(other_input.classList.contains('exclude')).toBe(false);
        // other input parent to have hide class
        var other_input_parent = other_input.parentNode.parentNode;
        expect(other_input_parent.style.display).toBe('block');
    });

    it('hides supplementary o2 device list when oxygen administration flag is set to false', function(){
        spyOn(window.NHMobileForm.prototype, "trigger_actions").and.callThrough();
        var mobile_form = new window.NHMobileForm();
        var test_input = document.getElementById('oxygen_administration_flag');
        var other_input = document.getElementById('device_id');
        test_input.value = 'False';
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('change', false, false, false);
        test_input.dispatchEvent(change_event);
        expect(window.NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
        // other_input to have exclude class
        expect(other_input.classList.contains('exclude')).toBe(true);
        // other input parent to have hide class
        var other_input_parent = other_input.parentNode.parentNode;
        expect(other_input_parent.style.display).toBe('none');
    });



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


describe('NHMobileForm - Triggered Actions PBP', function(){

    beforeEach(function(){
        var test = document.getElementById('test');
        if(test != null){
            test.parentNode.removeChild(test);
        }
        var test_area = document.createElement('div');
        test_area.setAttribute('id', 'test');
        test_area.style.height = '500px';
        test_area.innerHTML = '<h2 id="patientName"><a href="#">Test Patient</a></h2>'+
        '<form action="/mobile/patient/submit/pbp/11" method="POST" data-type="pbp" patient-id="11" id="obsForm" data-source="patient" ajax-action="json_patient_form_action" ajax-args="pbp,11">'+
        '<div><h3 class="block">Lying/Sitting Blood Pressure</h3>'+
        '<div class="block obsField" id="parent_systolic_sitting">'+
        '<div class="input-header"><label for="systolic_sitting">Sitting Blood Pressure Systolic</label>'+
        '<input type="number" name="systolic_sitting" id="systolic_sitting" min="1" max="300" step="1" data-validation="[{\'message\': {\'target\': \'Sitting Systolic BP must be more than Sitting Diastolic BP\', \'value\': \'Sitting Diastolic BP must be less than Sitting Systolic BP\'}, \'condition\': {\'operator\': \'>\', \'target\': \'systolic_sitting\', \'value\': \'diastolic_sitting\'}}]" data-onchange="[{\'action\': \'show\', \'fields\': [\'systolic_standing\', \'diastolic_standing\'], \'condition\': [[\'systolic_sitting\', \'!=\', \'\'], [\'diastolic_sitting\', \'!=\', \'\']]}, {\'action\': \'hide\', \'fields\': [\'systolic_standing\', \'diastolic_standing\'], \'condition\': [\'||\', [\'systolic_sitting\', \'==\', \'\'], [\'diastolic_sitting\', \'==\', \'\']]}]">'+
        '</div><div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div>'+
        '<div><div class="block obsField" id="parent_diastolic_sitting"><div class="input-header">'+
        '<label for="diastolic_sitting">Sitting Blood Pressure Diastolic</label>'+
        '<input type="number" name="diastolic_sitting" id="diastolic_sitting" min="1" max="280" step="1" data-validation="[{\'message\': {\'target\': \'Sitting Diastolic BP must be less than Sitting Systolic BP\', \'value\': \'Sitting Systolic BP must be more than Sitting Diastolic BP\'}, \'condition\': {\'operator\': \'<\', \'target\': \'diastolic_sitting\', \'value\': \'systolic_sitting\'}}]" data-onchange="[{\'action\': \'show\', \'fields\': [\'systolic_standing\', \'diastolic_standing\'], \'condition\': [[\'systolic_sitting\', \'!=\', \'\'], [\'diastolic_sitting\', \'!=\', \'\']]}, {\'action\': \'hide\', \'fields\': [\'systolic_standing\', \'diastolic_standing\'], \'condition\': [\'||\', [\'systolic_sitting\', \'==\', \'\'], [\'diastolic_sitting\', \'==\', \'\']]}]">'+
        '</div><div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div>'+
        '<div><h3 class="block valHide" id="standing_title">Standing Blood Pressure</h3>'+
        '<div class="block obsField valHide" id="parent_systolic_standing"><div class="input-header">'+
        '<label for="systolic_standing">Standing Blood Pressure Systolic</label>'+
        '<input type="number" name="systolic_standing" id="systolic_standing" min="1" max="300" step="1" class="exclude" data-validation="[{\'message\': {\'target\': \'Standing Systolic BP must be more than Standing Diastolic BP\', \'value\': \'Standing Diastolic BP must be less than Standing Systolic BP\'}, \'condition\': {\'operator\': \'>\', \'target\': \'systolic_standing\', \'value\': \'diastolic_standing\'}}]">'+
        '</div><div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div>'+
        '<div><div class="block obsField valHide" id="parent_diastolic_standing">'+
        '<div class="input-header"><label for="diastolic_standing">Standing Blood Pressure Diastolic</label>'+
        '<input type="number" name="diastolic_standing" id="diastolic_standing" min="1" max="280" step="1" class="exclude" data-validation="[{\'message\': {\'target\': \'Standing Diastolic BP must be less than Standing Systolic BP\', \'value\': \'Standing Systolic BP must be more than Standing Diastolic BP\'}, \'condition\': {\'operator\': \'<\', \'target\': \'diastolic_standing\', \'value\': \'systolic_standing\'}}]">'+
        '</div><div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div>'+
        '<input type="hidden" name="startTimestamp" id="startTimestamp" value="1418646365"><div class="block obsSubmit">'+
        '<input type="submit" value="Submit" class="exclude" id="submitButton"></div></form>';
        document.getElementsByTagName('body')[0].appendChild(test_area);
    });

    it('shows standing BP fields when sitting BP fields are both entered', function(){
        spyOn(window.NHMobileForm.prototype, "trigger_actions").and.callThrough();
        var mobile_form = new window.NHMobileForm();
        var ss_input = document.getElementById('systolic_sitting');
        var sd_input = document.getElementById('diastolic_sitting');
        var s_input = document.getElementById('systolic_standing');
        var d_input = document.getElementById('diastolic_standing');
        ss_input.value = 120;
        sd_input.value = 80;
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('change', false, false, false);
        sd_input.dispatchEvent(change_event);
        expect(window.NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
        // other_input to have exclude class
        expect(s_input.classList.contains('exclude')).toBe(false);
        expect(d_input.classList.contains('exclude')).toBe(false);
        // other input parent to have hide class
        var s_input_parent = s_input.parentNode.parentNode;
        expect(s_input_parent.style.display).toBe('block');
        var d_input_parent = d_input.parentNode.parentNode;
        expect(d_input_parent.style.display).toBe('block');
    });

    it('hides standing BP fields when sitting BP field is cleared', function(){
        spyOn(window.NHMobileForm.prototype, "trigger_actions").and.callThrough();
        var mobile_form = new window.NHMobileForm();
        var ss_input = document.getElementById('systolic_sitting');
        var sd_input = document.getElementById('diastolic_sitting');
        var s_input = document.getElementById('systolic_standing');
        var d_input = document.getElementById('diastolic_standing');
        ss_input.value = 120;
        sd_input.value = 80;
        var change_event = document.createEvent('CustomEvent');
        change_event.initCustomEvent('change', false, false, false);
        sd_input.dispatchEvent(change_event);
        expect(window.NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
        // other_input to have exclude class
        expect(s_input.classList.contains('exclude')).toBe(false);
        expect(d_input.classList.contains('exclude')).toBe(false);
        // other input parent to have hide class
        var s_input_parent = s_input.parentNode.parentNode;
        expect(s_input_parent.style.display).toBe('block');
        var d_input_parent = d_input.parentNode.parentNode;
        expect(d_input_parent.style.display).toBe('block');

        // clear and retrigger

        ss_input.value = '';
        var update_event = document.createEvent('CustomEvent');
        update_event.initCustomEvent('change', false, false, false);
        ss_input.dispatchEvent(update_event);
        expect(window.NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
        // other_input to have exclude class
        expect(s_input.classList.contains('exclude')).toBe(true);
        expect(d_input.classList.contains('exclude')).toBe(true);
        // other input parent to have hide class
        expect(s_input_parent.style.display).toBe('none');
        expect(d_input_parent.style.display).toBe('none');
    });

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