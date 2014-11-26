# NHMobileForm contains utilities for working with the nh_eobs_mobile observation form
class NHMobileForm extends NHMobile

 constructor: () ->
   # find the form on the page
   @form = document.getElementsByTagName('form')?[0]
   @form_timeout = 240*1000
   @patient_name_el = document.getElementById('patientName').getElementsByTagName('a')[0]
   @patient_name = () ->
     @patient_name_el.text
   self = @
   @setup_event_listeners(self)
   super()

 setup_event_listeners: (self) ->
   
   # for each input in the form set up the event listeners
   for input in @form.elements
     do () ->
       switch input.localName
         when 'input'
           switch input.type
             when 'number' then input.addEventListener('change', self.validate)
             when 'submit' then input.addEventListener('click', self.submit)
             when 'reset' then input.addEventListener('click', self.cancel_notification)
             when 'radio' then input.addEventListener('click', self.trigger_actions)
         when 'select' then input.addEventListener('change', self.trigger_actions)


   document.addEventListener 'form_timeout', (event) ->
     self.handle_timeout(self, self.form.getAttribute('task-id'))
   window.timeout_func = () ->
     timeout = new CustomEvent('form_timeout', {'detail': 'form timed out'})
     document.dispatchEvent(timeout)
   window.form_timeout = setTimeout(window.timeout_func, @form_timeout)

   document.addEventListener 'post_score_submit', (event) ->
     form_elements = (element for element in self.form.elements when not element.classList.contains('exclude'))
     endpoint = event.detail
     self.submit_observation(self, form_elements, endpoint, self.form.getAttribute('ajax-args'))

   document.addEventListener 'partial_submit', (event) ->
     form_elements = (element for element in self.form.elements when not element.classList.contains('exclude'))
     reason = document.getElementsByName('partial_reason')[0]
     if reason
       form_elements.push(reason)
     details = event.detail
     self.submit_observation(self, form_elements, details.action, self.form.getAttribute('ajax-args'))
     dialog_id = document.getElementById(details.target)
     cover = document.getElementById('cover')
     dialog_id.parentNode.removeChild(cover)
     dialog_id.parentNode.removeChild(dialog_id)

   @patient_name_el.addEventListener 'click', (event) ->
     event.preventDefault()
     patient_id = event.srcElement.getAttribute('patient-id')
     if patient_id then self.get_patient_info(patient_id, self) else new window.NH.NHModal('patient_info_error', 'Error getting patient information', '', ['<a href="#" data-action="close" data-target="patient_info_error">Cancel</a>'], 0, document.getElementsByTagName('body')[0])



 validate: (event) =>
   event.preventDefault()
   @.reset_form_timeout(@)
   input = event.srcElement
   @reset_input_errors(input)
   value = parseFloat(input.value)
   min = parseFloat(input.min)
   max = parseFloat(input.max)
   if typeof(value) isnt 'undefined' and not isNaN(value) and value isnt ''
     if input.type is 'number'
       if input.step is '1' and value % 1 isnt 0
         @.add_input_errors(input, 'Must be whole number')
         return
       if value < min
         @.add_input_errors(input, 'Input too low')
         return
       if value > max
         @.add_input_errors(input, 'Input too high')
         return
       if input.getAttribute('data-validation')
         criteria = eval(input.getAttribute('data-validation'))[0]
         other_input = document.getElementById(criteria[1])?.value
         if document.getElementById(criteria[1])?.type is 'number'
           other_input = parseFloat(other_input)
         if eval(value + ' ' + criteria[0] + ' ' + other_input)
           @.reset_input_errors(document.getElementById(criteria[1]))
           return
         if typeof(other_input) isnt 'undefined' and not isNaN(other_input) and other_input isnt ''
           other_validation_event = new Event('change')
           document.getElementById(criteria[1]).dispatchEvent(other_validation_event)
           @.add_input_errors(input, 'Input must be ' + criteria[0] + ' ' + criteria[1])
           return
         else
           return
   else
     # to be continued

 trigger_actions: (event) =>
   # event.preventDefault()
   @.reset_form_timeout(@)
   input = event.srcElement
   value = input.value
   if input.type is 'radio'
     for el in document.getElementsByName(input.name)
       if el.value isnt value
         el.classList.add('exclude')
       else
         el.classList.remove('exclude')
   if value is ''
     value = 'Default'
   if input.getAttribute('data-onchange')
     actions = eval(input.getAttribute('data-onchange'))[0]
     for field in actions[value]?['hide']
       @.hide_triggered_elements(field)
     for field in actions[value]?['show']
       @.show_triggered_elements(field)
   
 submit: (event) =>
   event.preventDefault()
   @.reset_form_timeout(@)
   form_elements = (element for element in @form.elements when not element.classList.contains('exclude'))
   invalid_elements = (element for element in form_elements when element.classList.contains('error'))
   empty_elements = (element for element in form_elements when not element.value)
   if invalid_elements.length<1 and empty_elements.length<1
     # do something with the form
     @submit_observation(@, form_elements, @form.getAttribute('ajax-action'), @form.getAttribute('ajax-args'))
     console.log('submit')
   else if invalid_elements.length>0
     new window.NH.NHModal('invalid_form', 'Form contains errors', '<p class="block">The form contains errors, please correct the errors and resubmit</p>', ['<a href="#" data-action="close" data-target="invalid_form">Cancel</a>'], 0, @.form)
   else
     # display the partial obs dialog
     @display_partial_reasons(@)

 display_partial_reasons: (self) =>
   Promise.when(@call_resource(@.urls.json_partial_reasons())).then (data) ->
     options = ''
     for option in data[0][0]
       option_val = option[0]
       option_name = option[1]
       options += '<option value="'+option_val+'">'+option_name+'</option>'
     select = '<select name="partial_reason">'+options+'</select>'
     new window.NH.NHModal('partial_reasons', 'Submit partial observation', '<p class="block">Please state reason for submitting partial observation</p>'+select, ['<a href="#" data-action="close" data-target="partial_reasons">Cancel</a>', '<a href="#" data-target="partial_reasons" data-action="partial_submit" data-ajax-action="json_task_form_action">Confirm</a>'], 0, self.form)

 submit_observation: (self, elements, endpoint, args) =>
   # turn form data in to serialised string and ping off to server
   serialised_string = (el.name+'='+el.value for el in elements).join("&")
   url = @.urls[endpoint].apply(this, args.split(','))
   Promise.when(@call_resource(url, serialised_string)).then (server_data) ->
     data = server_data[0][0]
     if data.status is 3
       new window.NH.NHModal('submit_observation', data.modal_vals['title'] + ' for ' + self.patient_name() + '?', data.modal_vals['content'], ['<a href="#" data-action="close" data-target="submit_observation">Cancel</a>', '<a href="#" data-target="submit_observation" data-action="submit" data-ajax-action="'+data.modal_vals['next_action']+'">Submit</a>'], 0, self.form)
       if 'clinical_risk' of data.score
         document.getElementById('submit_observation').classList.add('clinicalrisk-'+data.score['clinical_risk'].toLowerCase())
     else if data.status is 1
       triggered_tasks = ''
       buttons = ['<a href="'+self.urls['task_list']().url+'" data-action="confirm">Go to My Tasks</a>']
       if data.related_tasks.length is 1
         triggered_tasks = '<p>' + data.related_tasks[0].summary + '</p>'
         buttons.push('<a href="'+self.urls['single_task'](data.related_tasks[0].id).url+'">Confirm</a>')
       else if data.related_tasks.length > 1
         tasks = ''
         for task in data.related_tasks
           tasks += '<li><a href="'+self.urls['single_task'](task.id).url+'">'+task.summary+'</a></li>'
         triggered_tasks = '<ul class="menu">'+tasks+'</ul>'
       task_list = if triggered_tasks then triggered_tasks else '<p>Observation was submitted</p>'
       title = if triggered_tasks then 'Action required' else 'Observation successfully submitted'
       new window.NH.NHModal('submit_success', title , task_list, buttons, 0, self.form)
     else if data.status is 4
       new window.NH.NHModal('cancel_success', 'Task successfully cancelled', '', ['<a href="'+self.urls['task_list']().url+'" data-action="confirm" data-target="cancel_success">Go to My Tasks</a>'], 0, self.form)
     else
       new window.NH.NHModal('submit_error', 'Error submitting observation', data.error, ['<a href="#" data-action="close" data-target="submit_error">Cancel</a>'], 0, self.form)

 handle_timeout: (self, id) =>
   Promise.when(self.call_resource(self.urls['json_cancel_take_task'](id))).then (server_data) ->
     new window.NH.NHModal('form_timeout', 'Task window expired', '<p class="block">Please pick the task again from the task list if you wish to complete it</p>', ['<a href="'+self.urls['task_list']().url+'" data-action="confirm">Go to My Tasks</a>'], 0, document.getElementsByTagName('body')[0])

 cancel_notification: (self) =>
   Promise.when(@call_resource(@.urls.ajax_task_cancellation_options())).then (data) ->
     options = ''
     for option in data[0][0]
       option_val = option.id
       option_name = option.name
       options += '<option value="'+option_val+'">'+option_name+'</option>'
     select = '<select name="reason">'+options+'</select>'
     new window.NH.NHModal('cancel_reasons', 'Cancel task', '<p>Please state reason for cancelling task</p>'+select, ['<a href="#" data-action="close" data-target="cancel_reasons">Cancel</a>', '<a href="#" data-target="cancel_reasons" data-action="partial_submit" data-ajax-action="cancel_clinical_notification">Confirm</a>'], 0, document.getElementsByTagName('form')[0])

 reset_form_timeout: (self) =>
   clearTimeout(window.form_timeout)
   window.form_timeout = setTimeout(window.timeout_func, self.form_timeout)

 reset_input_errors: (input) =>
   container_el = input.parentNode.parentNode
   error_el = container_el.getElementsByClassName('errors')[0]
   container_el.classList.remove('error')
   input.classList.remove('error')
   error_el.innerHTML = ''

 add_input_errors: (input, error_string) =>
   container_el = input.parentNode.parentNode
   error_el = container_el.getElementsByClassName('errors')[0]
   container_el.classList.add('error')
   input.classList.add('error')
   error_el.innerHTML = '<label for="'+input.name+'" class="error">'+error_string+'</label>'

 hide_triggered_elements: (field) =>
   el = document.getElementById('parent_'+field)
   el.style.display = 'none'
   inp = document.getElementById(field)
   inp.classList.add('exclude')

 show_triggered_elements: (field) =>
   el = document.getElementById('parent_'+field)
   el.style.display = 'block'
   inp = document.getElementById(field)
   inp.classList.remove('exclude')



if !window.NH
  window.NH = {}
window?.NH.NHMobileForm = NHMobileForm

