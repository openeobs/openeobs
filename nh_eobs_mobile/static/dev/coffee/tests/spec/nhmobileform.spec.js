describe('NHMobileForm - EventListeners', function(){
   beforeEach(function(){
       var test = document.getElementById('test');
       if(test != null){
           test.parentNode.removeChild(test);
       }
       var test_area = document.createElement('div');
       test_area.setAttribute('id', 'test');
       test_area.style.height = '500px';
       test_area.innerHTML = '<form action="" method="POST" data-type="ews" task-id="704" patient-id="11" id="obsForm" data-source="task" ajax-action="json_task_form_action" ajax-args="ews,7309"><div><div class="block obsField" id="parent_respiration_rate"><div class="input-header"><label for="respiration_rate">Respiration Rate</label><input type="number" name="respiration_rate" id="respiration_rate" min="1" max="59" step="1"></div><div class="input-body"><span class="errors"></span><span class="help"></span></div></div></div><div><div class="block obsSelectField" id="parent_oxygen_administration_flag"><div class="input-header"><label for="oxygen_administration_flag">Patient on supplemental O2</label></div><div class="input-body"><select id="oxygen_administration_flag" name="oxygen_administration_flag" data-onchange="[{\'False\': {\'hide\': [\'device_id\', \'flow_rate\', \'concentration\', \'cpap_peep\', \'niv_backup\', \'niv_ipap\', \'niv_epap\'], \'show\': []}, \'True\': {\'hide\': [], \'show\': [\'device_id\']}}]"><option value="">Please Select</option><option value="False">No</option><option value="True">Yes</option></select><span class="errors"></span><span class="help"></span></div></div></div><div class="block obsSubmit"><input type="submit" value="Submit" id="submitButton" class="exclude"></div></form>';
       document.getElementsByTagName('body')[0].appendChild(test_area);
   });

   it('validate event is triggered on input change', function(){
       spyOn(window.NHMobileForm.prototype, "validate");
       var mobile_form = new window.NHMobileForm();
       var test_input = document.getElementById('respiration_rate');
       var change_event = new Event('change');
       test_input.dispatchEvent(change_event);
       expect(window.NHMobileForm.prototype.validate).toHaveBeenCalled();
   });

   it('trigger_actions event is triggered on select change', function(){
       spyOn(window.NHMobileForm.prototype, "trigger_actions");
       var mobile_form = new window.NHMobileForm();
       var test_input = document.getElementById('oxygen_administration_flag');
       var change_event = new Event('change');
       test_input.dispatchEvent(change_event);
       expect(window.NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
   });

    it('submit event is triggered on submit button click', function(){
        spyOn(window.NHMobileForm.prototype, "submit");
        var mobile_form = new window.NHMobileForm();
        var test_input = document.getElementById('submitButton');
        test_input.click()
        expect(window.NHMobileForm.prototype.submit).toHaveBeenCalled();
    });


    afterEach(function(){
        var test = document.getElementById('test');
        if(test != null){
            test.parentNode.removeChild(test);
        }
    });
});