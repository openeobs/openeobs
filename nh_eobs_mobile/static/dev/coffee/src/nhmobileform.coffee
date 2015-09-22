# NHMobileForm contains utilities for working with the nh_eobs_mobile
# observation form
### istanbul ignore next ###
class NHMobileForm extends NHMobile

  constructor: () ->
    # find the form on the page
    @form = document.getElementsByTagName('form')?[0]
    @form_timeout = 240*1000
    ptn_name = document.getElementById('patientName')
    @patient_name_el = ptn_name.getElementsByTagName('a')[0]
    @patient_name = () ->
      @patient_name_el.text
    self = @
    @setup_event_listeners(self)
    super()

  setup_event_listeners: (self) ->
   
    # for each input in the form set up the event listeners
    for input in self.form.elements
      do () ->
        switch input.localName
          when 'input'
            switch input.getAttribute('type')
              when 'number'
                input.addEventListener('change', self.validate)
                input.addEventListener('change', self.trigger_actions)
              when 'submit' then input.addEventListener('click', self.submit)
              when 'reset' then input.addEventListener('click',
                  self.cancel_notification)
              when 'radio' then input.addEventListener('click',
                  self.trigger_actions)
              when 'text'
                input.addEventListener('change', self.validate)
                input.addEventListener('change', self.trigger_actions)
          when 'select' then input.addEventListener('change',
            self.trigger_actions)
          when 'button' then input.addEventListener('click',
            self.show_reference)

    # Set up form timeout so that the task is put back in the task list after
    # a certain time
    document.addEventListener 'form_timeout', (event) ->
      task_id = self.form.getAttribute('task-id')
      ### istanbul ignore else ###
      if task_id
        self.handle_timeout(self, task_id)
    window.timeout_func = () ->
      timeout = document.createEvent('CustomEvent')
      timeout.initCustomEvent('form_timeout', false, true,
        {'detail': 'form timed out'})
      document.dispatchEvent(timeout)
    window.form_timeout = setTimeout(window.timeout_func, self.form_timeout)

    document.addEventListener 'post_score_submit', (event) ->
      if not event.handled
        self.process_post_score_submit(self, event)
        event.handled = true

    document.addEventListener 'partial_submit', (event) ->
      if not event.handled
        self.process_partial_submit(self,event)
        event.handled = true

    @patient_name_el.addEventListener 'click', (event) ->
      event.preventDefault()
      input = if event.srcElement then event.srcElement else event.target
      patient_id = input.getAttribute('patient-id')
      if patient_id
        self.get_patient_info(patient_id, self)
      else
        can_btn = '<a href="#" data-action="close" '+
          'data-target="patient_info_error">Cancel</a>'
        new window.NH.NHModal('patient_info_error',
        'Error getting patient information',
        '',
        [can_btn],
        0, document.getElementsByTagName('body')[0])


  # Validate the form - need to add basic validation messages to DOM so set
  # by server
  # inputs with a data-validation attribute already do this
  # TODO: Currently only caters for number inputs
  validate: (event) =>
    event.preventDefault()
    @.reset_form_timeout(@)
    input = if event.srcElement then event.srcElement else event.target
    input_type = input.getAttribute('type')
    value = if input_type is 'number' then parseFloat(input.value) else
      input.value
    @reset_input_errors(input)
    if typeof(value) isnt 'undefined' and value isnt ''
      if input.getAttribute('type') is 'number' and not isNaN(value)
        min = parseFloat(input.getAttribute('min'))
        max = parseFloat(input.getAttribute('max'))
        if input.getAttribute('step') is '1' and value % 1 isnt 0
          @.add_input_errors(input, 'Must be whole number')
          return
        if value < min
          @.add_input_errors(input, 'Input too low')
          return
        if value > max
          @.add_input_errors(input, 'Input too high')
          return
        if input.getAttribute('data-validation')
          criterias = eval(input.getAttribute('data-validation'))
          for criteria in criterias
            crit_target = criteria['condition']['target']
            crit_val = criteria['condition']['value']
            target_input = document.getElementById(crit_target)
            target_input_value = target_input?.value
            other_input = document.getElementById(crit_val)
            other_input_value = other_input?.value
            operator = criteria['condition']['operator']
            if target_input?.getAttribute('type') is 'number'
              other_input_value = parseFloat(other_input_value)
            cond = target_input_value + ' ' + operator + ' ' + other_input_value
            if eval(cond)
              @.reset_input_errors(other_input)
              continue
            if typeof(other_input_value) isnt 'undefined' and
            not isNaN(other_input_value) and other_input_value isnt ''
              @.add_input_errors(target_input, criteria['message']['target'])
              @.add_input_errors(other_input, criteria['message']['value'])
              continue
            else
              @.add_input_errors(target_input, criteria['message']['target'])
              @.add_input_errors(other_input, 'Please enter a value')
              continue
      if input.getAttribute('type') is 'text'
        if input.getAttribute('pattern')
          regex_res = input.validity.patternMismatch
          if regex_res
            @.add_input_errors(input, 'Invalid value')
            return

  
  # Certain inputs will affect other inputs, this function takes the JSON string
  # in the input's data-onchange attribute and does the appropriate action
  trigger_actions: (event) =>
    @.reset_form_timeout(@)
    input = if event.srcElement then event.srcElement else event.target
    value = input.value
    if input.getAttribute('type') is 'radio'
      for el in document.getElementsByName(input.name)
        if el.value isnt value
          el.classList.add('exclude')
        else
          el.classList.remove('exclude')
    if value is ''
      value = 'Default'
    if input.getAttribute('data-onchange')
      actions = eval(input.getAttribute('data-onchange'))
      # TODO: needs a refactor if passing over a select value that is string
      # this blows up
      for action in actions
        for condition in action['condition']
          if condition[0] not in ['True', 'False'] and
          typeof condition[0] is 'string'
            condition[0] = 'document.getElementById("'+condition[0]+'").value'
          if condition[2] not in ['True', 'False'] and
          typeof condition[2] is 'string' and condition[2] isnt ''
            condition[2] = 'document.getElementById("'+condition[2]+'").value'
          if condition[2] in ['True', 'False', '']
            condition[2] = "'"+condition[2]+"'"
        mode = ' && '
        conditions = []
        for condition in action['condition']
          ### istanbul ignore else ###
          if typeof condition is 'object'
            conditions.push(condition.join(' '))
          else
            mode = condition
        conditions = conditions.join(mode)
        # TODO: doesn't work with comparative number inputs i.e. a > b
        if eval(conditions)
          if action['action'] is 'hide'
            for field in action['fields']
              @.hide_triggered_elements(field)
          if action['action'] is 'show'
            for field in action['fields']
              @.show_triggered_elements(field)
          if action['action'] is 'disable'
            for field in action['fields']
              @.disable_triggered_elements(field)
          if action['action'] is 'enable'
            for field in action['fields']
              @.enable_triggered_elements(field)
    return
   
  submit: (event) =>
    event.preventDefault()
    @.reset_form_timeout(@)
    ajax_act = @form.getAttribute('ajax-action')
    form_elements =
      (element for element in @form.elements \
        when not element.classList.contains('exclude'))
    invalid_elements =
      (element for element in form_elements \
        when element.classList.contains('error'))
    empty_elements =
      (element for element in form_elements when not element.value or \
      element.value is '')
    if invalid_elements.length<1 and empty_elements.length<1
      # do something with the form
      action_buttons = (element for element in @form.elements \
        when element.getAttribute('type') in ['submit', 'reset'])
      for button in action_buttons
        button.setAttribute('disabled', 'disabled')
      @submit_observation(@, form_elements, @form.getAttribute('ajax-action'),
        @form.getAttribute('ajax-args'))
    else if empty_elements.length>0 and ajax_act.indexOf('notification') > 0
      msg = '<p>The form contains empty fields, please enter '+
        'data into these fields and resubmit</p>'
      btn = '<a href="#" data-action="close" data-target="invalid_form">'+
        'Cancel</a>'
      new window.NH.NHModal('invalid_form', 'Form contains empty fields',
        msg, [btn], 0, @.form)
    else if invalid_elements.length>0
      msg = '<p>The form contains errors, please correct '+
        'the errors and resubmit</p>'
      btn = '<a href="#" data-action="close" data-target="invalid_form">'+
        'Cancel</a>'
      new window.NH.NHModal('invalid_form', 'Form contains errors',
        msg, [btn], 0, @.form)
    else
      # display the partial obs dialog
      action_buttons = (element for element in @form.elements \
        when element.getAttribute('type') in ['submit', 'reset'])
      for button in action_buttons
        button.setAttribute('disabled', 'disabled')
      @display_partial_reasons(@)

  show_reference: (event) =>
    event.preventDefault()
    @.reset_form_timeout(@)
    input = if event.srcElement then event.srcElement else event.target
    ref_type = input.getAttribute('data-type')
    ref_url = input.getAttribute('data-url')
    ref_title = input.getAttribute('data-title')
    if ref_type is 'image'
      img = '<img src="' + ref_url + '"/>'
      btn = '<a href="#" data-action="close" data-target="popup_image">'+
        'Cancel</a>'
      new window.NH.NHModal('popup_image', ref_title, img, [btn], 0, @.form)
    if ref_type is 'iframe'
      iframe = '<iframe src="'+ ref_url + '"></iframe>'
      btn = '<a href="#" data-action="close" data-target="popup_iframe">'+
        'Cancel</a>'
      new window.NH.NHModal('popup_iframe', ref_title, iframe, [btn], 0, @.form)


  display_partial_reasons: (self) =>
    form_type = self.form.getAttribute('data-source')
    Promise.when(@call_resource(@.urls.json_partial_reasons())).then (rdata) ->
      server_data = rdata[0]
      data = server_data.data
      options = ''
      for option in data
        option_val = option[0]
        option_name = option[1]
        options += '<option value="'+option_val+'">'+option_name+'</option>'
      select = '<select name="partial_reason">'+options+'</select>'
      con_btn = if form_type is 'task' then '<a href="#" ' +
        'data-target="partial_reasons" data-action="partial_submit" '+
        'data-ajax-action="json_task_form_action">Confirm</a>'
        else '<a href="#" data-target="partial_reasons" '+
        'data-action="partial_submit" '+
        'data-ajax-action="json_patient_form_action">Confirm</a>'
      can_btn = '<a href="#" data-action="renable" '+
        'data-target="partial_reasons">Cancel</a>'
      msg = '<p>' + server_data.desc + '</p>'
      new window.NH.NHModal('partial_reasons', server_data.title,
        msg+select, [can_btn, con_btn], 0, self.form)

  submit_observation: (self, elements, endpoint, args) =>
    # turn form data in to serialised string and ping off to server
    serialised_string = (el.name+'='+el.value for el in elements).join("&")
    url = @.urls[endpoint].apply(this, args.split(','))
    # Disable the action buttons
    Promise.when(@call_resource(url, serialised_string)).then (raw_data) ->
      server_data = raw_data[0]
      data = server_data.data
      body = document.getElementsByTagName('body')[0]
      if server_data.status is 'success' and data.status is 3
        can_btn = '<a href="#" data-action="renable" '+
          'data-target="submit_observation">Cancel</a>'
        act_btn = '<a href="#" data-target="submit_observation" '+
          'data-action="submit" data-ajax-action="'+
          data.next_action+'">Submit</a>'
        new window.NH.NHModal('submit_observation',
          server_data.title + ' for ' + self.patient_name() + '?',
          server_data.desc,
          [can_btn, act_btn], 0, body)
        if 'clinical_risk' of data.score
          sub_ob = document.getElementById('submit_observation')
          cls = 'clinicalrisk-'+data.score.clinical_risk.toLowerCase()
          sub_ob.classList.add(cls)
      else if server_data.status is 'success' and data.status is 1
        triggered_tasks = ''
        buttons = ['<a href="'+self.urls['task_list']().url+
          '" data-action="confirm">Go to My Tasks</a>']
        if data.related_tasks.length is 1
          triggered_tasks = '<p>' + data.related_tasks[0].summary + '</p>'
          rt_url = self.urls['single_task'](data.related_tasks[0].id).url
          buttons.push('<a href="'+rt_url+'">Confirm</a>')
        else if data.related_tasks.length > 1
          tasks = ''
          for task in data.related_tasks
            st_url = self.urls['single_task'](task.id).url
            tasks += '<li><a href="'+st_url+'">'+task.summary+'</a></li>'
          triggered_tasks = '<ul class="menu">'+tasks+'</ul>'
        pos = '<p>' + server_data.desc + '</p>'
        os = 'Observation successfully submitted'
        task_list = if triggered_tasks then triggered_tasks else pos
        new window.NH.NHModal('submit_success', server_data.title ,
          task_list, buttons, 0, body)
      else if server_data.status is 'success' and data.status is 4
        btn = '<a href="'+self.urls['task_list']().url+
          '" data-action="confirm" data-target="cancel_success">'+
          'Go to My Tasks</a>'
        new window.NH.NHModal('cancel_success', server_data.title,
          '<p>' + server_data.desc + '</p>', [btn], 0, self.form)
      else
        action_buttons = (element for element in self.form.elements \
          when element.getAttribute('type') in ['submit', 'reset'])
        for button in action_buttons
          button.removeAttribute('disabled')
        btn = '<a href="#" data-action="close" '+
          'data-target="submit_error">Cancel</a>'
        new window.NH.NHModal('submit_error', 'Error submitting observation',
          'Server returned an error', [btn], 0, body)

  handle_timeout: (self, id) ->
    can_id = self.urls['json_cancel_take_task'](id)
    Promise.when(self.call_resource(can_id)).then (server_data) ->
      ### Should be checking server data ###
      msg = '<p>Please pick the task again from the task list '+
        'if you wish to complete it</p>'
      btn = '<a href="'+self.urls['task_list']().url+
        '" data-action="confirm">Go to My Tasks</a>'
      new window.NH.NHModal('form_timeout', 'Task window expired', msg,
        [btn], 0, document.getElementsByTagName('body')[0])

  cancel_notification: (self) =>
    opts = @.urls.ajax_task_cancellation_options()
    Promise.when(@call_resource(opts)).then (raw_data) ->
      server_data = raw_data[0]
      data = server_data.data
      options = ''
      for option in data
        option_val = option.id
        option_name = option.name
        options += '<option value="'+option_val+'">'+option_name+'</option>'
      select = '<select name="reason">'+options+'</select>'
      msg = '<p>' + server_data.desc + '</p>'
      can_btn = '<a href="#" data-action="close" '+
        'data-target="cancel_reasons">Cancel</a>'
      con_btn = '<a href="#" data-target="cancel_reasons" '+
        'data-action="partial_submit" '+
        'data-ajax-action="cancel_clinical_notification">Confirm</a>'
      new window.NH.NHModal('cancel_reasons', server_data.title, msg+select,
        [can_btn, con_btn], 0, document.getElementsByTagName('form')[0])

  reset_form_timeout: (self) ->
    clearTimeout(window.form_timeout)
    window.form_timeout = setTimeout(window.timeout_func, self.form_timeout)

  reset_input_errors: (input) ->
    container_el = input.parentNode.parentNode
    error_el = container_el.getElementsByClassName('errors')[0]
    container_el.classList.remove('error')
    input.classList.remove('error')
    error_el.innerHTML = ''

  add_input_errors: (input, error_string) ->
    container_el = input.parentNode.parentNode
    error_el = container_el.getElementsByClassName('errors')[0]
    container_el.classList.add('error')
    input.classList.add('error')
    error_el.innerHTML = '<label for="'+input.name+'" class="error">'+
      error_string+'</label>'

  hide_triggered_elements: (field) ->
    el = document.getElementById('parent_'+field)
    el.style.display = 'none'
    inp = document.getElementById(field)
    inp.classList.add('exclude')

  show_triggered_elements: (field) ->
    el = document.getElementById('parent_'+field)
    el.style.display = 'block'
    inp = document.getElementById(field)
    inp.classList.remove('exclude')

  disable_triggered_elements: (field) ->
    inp = document.getElementById(field)
    inp.classList.add('exclude')
    inp.disabled = true

  enable_triggered_elements: (field) ->
    inp = document.getElementById(field)
    inp.classList.remove('exclude')
    inp.disabled = false

  process_partial_submit: (self, event) ->
    form_elements = (element for element in self.form.elements when not
      element.classList.contains('exclude'))
    reason_to_use = false
    reason = document.getElementsByName('partial_reason')[0]
    cancel_reason = document.getElementsByName('reason')[0]
    if reason
      reason_to_use = reason
    if cancel_reason
      reason_to_use = cancel_reason
    # TODO: Add an error catch if no value entered
    if reason_to_use
      form_elements.push(reason_to_use)
      self.submit_observation(self, form_elements, event.detail.action,
        self.form.getAttribute('ajax-args'))
      dialog_id = document.getElementById(event.detail.target)
      cover = document.getElementById('cover')
      document.getElementsByTagName('body')[0].removeChild(cover)
      dialog_id.parentNode.removeChild(dialog_id)

  process_post_score_submit: (self, event) ->
    form  = document.getElementsByTagName('form')?[0]
    form_elements = (element for element in form.elements when not
      element.classList.contains('exclude'))
    endpoint = event.detail.endpoint
    self.submit_observation(self,
      form_elements, endpoint, self.form.getAttribute('ajax-args'))

### istanbul ignore if ###
if !window.NH
  window.NH = {}

### istanbul ignore else ###
window?.NH.NHMobileForm = NHMobileForm

