# NHMobileForm contains utilities for working with the nh_eobs_mobile
# observation form
### istanbul ignore next ###
class NHMobileForm extends NHMobile

  constructor: () ->
    # find the form on the page
    @forms = document.getElementsByTagName('form')
    @form = @forms?[0]
    @form_timeout = 600*1000
    ptn_name = document.getElementById('patientName')
    @patient_name_el = ptn_name.getElementsByTagName('a')[0]
    @patient_name = () ->
      @patient_name_el.text
    self = @
    @setup_event_listeners(self)
    super()

  setup_event_listeners: (self) ->
   
    # for each input in the form set up the event listeners
    for form in self.forms
      for input in form.elements
        do () ->
          switch input.localName
            when 'input'
              switch input.getAttribute('type')
                when 'number'
                  input.addEventListener('change', (e) ->
                    self.handle_event(e, self.validate, true)
                    e.handled = false
                    self.handle_event(e, self.trigger_actions, true)
                  )
  #                input.addEventListener('change', self.trigger_actions)
                when 'radio' then input.addEventListener('click', (e) ->
                  self.handle_event(e, self.trigger_actions, true)
                )
                when 'checkbox'
                  input.addEventListener('click', (e) ->
                    self.handle_event(e, self.validate, false)
                    e.handled = false
                    self.handle_event(e, self.trigger_actions, false)
                  )
                  input.addEventListener('change', (e) ->
                    self.handle_event(e, self.validate, false)
                    e.handled = false
                    self.handle_event(e, self.trigger_actions, false)
                  )
                when 'text'
                  input.addEventListener('change', (e) ->
                    self.handle_event(e, self.validate, true)
                    e.handled = false
                    self.handle_event(e, self.trigger_actions, true)
                  )
            when 'select' then input.addEventListener('change', (e) ->
              self.handle_event(e, self.validate, true)
              e.handled = false
              self.handle_event(e, self.trigger_actions, true)
            )
            when 'button' then input.addEventListener('click', (e) ->
              self.handle_event(e, self.show_reference, true)
            )
            when 'textarea'
              input.addEventListener('change', (e) ->
                self.handle_event(e, self.validate, true)
                e.handled = false
                self.handle_event(e, self.trigger_actions, true)
              )
    submitButton = document.querySelector('input[type="submit"]')
    submitButton?.addEventListener('click', (e) ->
      forms = document.getElementsByTagName('form')
      elements = []
      for form in forms
        for element in form.elements
          elements.push(element)
      errored_els = (el for el in elements \
        when el.classList.contains('error'))
      for inp in errored_els
        self.reset_input_errors(inp)
      form_elements = (element for element in elements \
        when not element.classList.contains('exclude'))
      for el in form_elements
        change_event = document.createEvent('CustomEvent')
        change_event.initCustomEvent('change', false, true, false)
        el.dispatchEvent(change_event)
      self.handle_event(e, self.submit, true)
    )
    resetButton = document.querySelector('input[type="reset"]')
    resetButton?.addEventListener('click', (e) ->
      self.handle_event(e, self.cancel_notification, true)
    )

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
      self.handle_event(event, self.process_post_score_submit, true, self)

    document.addEventListener 'partial_submit', (event) ->
      self.handle_event(event, self.process_partial_submit, true, self)

    document.addEventListener(
      'display_partial_reasons',
      self.handle_display_partial_reasons.bind(self)
    )

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
#    event.preventDefault()
    @.reset_form_timeout(@)
#    input = if event.srcElement then event.srcElement else event.target
    input = event.src_el
    input_type = input.getAttribute('type')
    value = if input_type is 'number' then parseFloat(input.value) else
      input.value
    @reset_input_errors(input)
    if typeof(value) isnt 'undefined' and value isnt ''
      if input_type is 'number'
        @validate_number_input(input)
        if input.getAttribute('data-validation') and not isNaN(value)
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
            else if typeof(other_input_value) isnt 'undefined' and
            not isNaN(other_input_value) and other_input_value isnt ''
              @.add_input_errors(target_input, criteria['message']['target'])
              @.add_input_errors(other_input, criteria['message']['value'])
            else
              @.add_input_errors(target_input, criteria['message']['target'])
              @.add_input_errors(other_input, 'Please enter a value')
          @validate_number_input(other_input)
          @validate_number_input(target_input)
      if input_type is 'text'
        if input.getAttribute('pattern')
          regex_res = input.validity.patternMismatch
          if regex_res
            @.add_input_errors(input, 'Invalid value')
            return
    else
      if input.getAttribute('data-required').toLowerCase() is 'true'
        @.add_input_errors(input, 'Missing value')
        return


  # Validate number input to make sure it fits within the defined range and is
  # float or int
  validate_number_input: (input) =>
    min = parseFloat(input.getAttribute('min'))
    max = parseFloat(input.getAttribute('max'))
    value = parseFloat(input.value)
    if typeof(value) isnt 'undefined' and value isnt '' and not isNaN(value)
      if input.getAttribute('step') is '1' and value % 1 isnt 0
        @.add_input_errors(input, 'Must be whole number')
        return
      if value < min
        @.add_input_errors(input, 'Input too low')
        return
      if value > max
        @.add_input_errors(input, 'Input too high')
        return
    else
      if input.getAttribute('data-required').toLowerCase() is 'true'
        @.add_input_errors(input, 'Missing value')
  
  # Certain inputs will affect other inputs, this function takes the JSON string
  # in the input's data-onchange attribute and does the appropriate action
  trigger_actions: (event) =>
    @.reset_form_timeout(@)
#    input = if event.srcElement then event.srcElement else event.target
    input = event.src_el
    value = input.value
    type = input.getAttribute('type')
    if type is 'radio'
      for el in document.getElementsByName(input.name)
        if el.value isnt value
          el.classList.add('exclude')
        else
          el.classList.remove('exclude')
    if type is 'checkbox'
      for el in document.getElementsByName(input.name)
        if not el.checked
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
        type = action['type']
        for condition in action['condition']
          condition[0] = 'document.getElementById("'+condition[0]+'").value'
          condition[2] = switch
            when type is 'value' then "'"+condition[2]+"'"
            when type is 'field' then \
              'document.getElementById("'+condition[2]+'").value'
            else "'"+condition[2]+"'"
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
          actionToTrigger = action['action']
          fieldsToAffect = action['fields']
          if actionToTrigger is 'hide'
            for field in fieldsToAffect
              @.hide_triggered_elements(field)
          if actionToTrigger is 'show'
            for field in fieldsToAffect
              @.show_triggered_elements(field)
          if actionToTrigger is 'disable'
            for field in fieldsToAffect
              @.disable_triggered_elements(field)
          if actionToTrigger is 'enable'
            for field in fieldsToAffect
              @.enable_triggered_elements(field)
          if actionToTrigger is 'require'
            for field in fieldsToAffect
              @.require_triggered_elements(field)
          if actionToTrigger is 'unrequire'
            for field in fieldsToAffect
              @.unrequire_triggered_elements(field)
    return
   
  submit: (event) =>
#    event.preventDefault()
    @.reset_form_timeout(@)
    body_el = document.getElementsByTagName('body')[0]
    form_elements = []
    for form in @forms
      for element in form.elements
        if not element.classList.contains('exclude')
          form_elements.push(element)
    invalid_elements =
      (element for element in form_elements \
        when element.classList.contains('error'))
    empty_mandatory =
      (el for el in form_elements when not el.value and \
        (el.getAttribute('data-required').toLowerCase() is 'true') \
        or el.value is '' \
        and (el.getAttribute('data-required').toLowerCase() is 'true'))
    if empty_mandatory.length > 0
      msg = '<p>The form contains empty fields, please enter '+
        'data into these fields and resubmit</p>'
      btn = '<a href="#" data-action="close" data-target="invalid_form">'+
        'Cancel</a>'
      new window.NH.NHModal('invalid_form', 'Form contains empty fields',
        msg, [btn], 0, body_el)
    else if invalid_elements.length>0
      msg = '<p>The form contains errors, please correct '+
        'the errors and resubmit</p>'
      btn = '<a href="#" data-action="close" data-target="invalid_form">'+
        'Cancel</a>'
      new window.NH.NHModal('invalid_form', 'Form contains errors',
        msg, [btn], 0, body_el)
    else
      @submit_forms()

  submit_forms: () ->
    forms = document.getElementsByTagName('form')
    @disable_action_buttons()
    form_submissions = Promise.when()
    for form in forms
      formElements = []
      for element in form.elements
        if not element.classList.contains('exclude')
          formElements.push(element)
      ajaxAct = form.getAttribute('ajax-action')
      ajaxPartialAct = form.getAttribute('ajax-partial-action')
      ajaxArgs = form.getAttribute('ajax-args')
      emptyElements =
      (el for el in formElements when not el.value and \
        (el.getAttribute('data-necessary').toLowerCase() is 'true') or \
        el.value is '' and \
        (el.getAttribute('data-necessary').toLowerCase() is 'true'))
      if emptyElements.length > 0
        self = @
        if ajaxPartialAct is 'score'
          form_submissions.then( () ->
            self.submit_observation(
              form, formElements, ajaxAct, ajaxArgs, true)
          )
        else
          form_submissions.then( () ->
            self.display_partial_reasons(form)
          )
      else
         form_submissions.then( () ->
          self.submit_observation(form, formElements, ajaxAct, ajaxArgs)
         )
    form_submissions.complete()

  disable_action_buttons: () ->
    action_buttons = document.querySelectorAll(
      'input[type="submit"], input[type="reset"]')
    for button in action_buttons
      button.setAttribute('disabled', 'disabled')

  enableActionButtons: () ->
    action_buttons = document.querySelectorAll(
      'input[type="submit"], input[type="reset"]')
    for button in action_buttons
      button.removeAttribute('disabled')

  show_reference: (event) =>
#    event.preventDefault()
    @.reset_form_timeout(@)
    input = event.src_el
#    input = if event.srcElement then event.srcElement else event.target
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
      new window.NH.NHModal(
        'popup_iframe', ref_title, iframe, [btn], 0, @.form)

  display_partial_reasons: (form) =>
    form_type = form.getAttribute('data-source')
    observation = form.getAttribute('data-type')
    partials_url = @.urls.json_partial_reasons(observation)
    Promise.when(@call_resource(partials_url)).then (rdata) ->
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
        msg+select, [can_btn, con_btn], 0, form)

  submit_observation: (form, elements, endpoint, args, partial = false) =>
    # turn form data in to serialised string and ping off to server
    formValues = {}
    for el in elements
      type = el.getAttribute('type')
      if not formValues.hasOwnProperty(el.name)
        if type is 'checkbox'
          formValues[el.name] = [el.value]
        else
          formValues[el.name] = el.value
      else
        if type is 'checkbox'
          formValues[el.name].push(el.value)
    serialised_string = (key+'='+encodeURIComponent(value) \
      for key, value of formValues).join("&")
    url = @.urls[endpoint].apply(this, args.split(','))
    self = @
    # Disable the action buttons
    Promise.when(@call_resource(url, serialised_string)).then (raw_data) ->
      server_data = raw_data[0]
      data = server_data.data
      body = document.getElementsByTagName('body')[0]
      if server_data.status is 'success' and data.status is 3
        data_action = if not partial then \
          'submit' else 'display_partial_reasons'
        can_btn = '<a href="#" data-action="renable" '+
          'data-target="submit_observation">Cancel</a>'
        act_btn = '<a href="#" data-target="submit_observation" '+
          'data-action="' + data_action + '" data-ajax-action="'+
          data.next_action+'">Submit</a>'
        new window.NH.NHModal('submit_observation',
          server_data.title + ' for ' + self.patient_name() + '?',
          server_data.desc,
          [can_btn, act_btn], 0, form)
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
        triggered_tasks = ''
        buttons = ['<a href="'+self.urls['task_list']().url+
          '" data-action="confirm" data-target="cancel_success">'+
          'Go to My Tasks</a>']
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
        task_list = if triggered_tasks then triggered_tasks else pos
        new window.NH.NHModal('cancel_success', server_data.title,
          task_list, buttons, 0, body)
      else
        self.enableActionButtons()
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
    container_el = @.findParentWithClass(input, 'block')
    error_el = container_el.getElementsByClassName('errors')[0]
    container_el.classList.remove('error')
    input.classList.remove('error')
    error_el.innerHTML = ''

  add_input_errors: (input, error_string) ->
    container_el = @.findParentWithClass(input, 'block')
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
    inp.setAttribute('data-necessary', 'false')

  show_triggered_elements: (field) ->
    el = document.getElementById('parent_'+field)
    el.style.display = 'block'
    inp = document.getElementById(field)
    inp.classList.remove('exclude')
    inp.setAttribute('data-necessary', 'true')

  disable_triggered_elements: (field) ->
    inp = document.getElementById(field)
    inp.classList.add('exclude')
    inp.setAttribute('data-necessary', 'false')
    inp.disabled = true

  enable_triggered_elements: (field) ->
    inp = document.getElementById(field)
    inp.classList.remove('exclude')
    inp.setAttribute('data-necessary', 'true')
    inp.disabled = false

  require_triggered_elements: (field) ->
    inp = document.getElementById(field)
    inp.classList.remove('exclude')
    inp.setAttribute('data-required', 'true')

  unrequire_triggered_elements: (field) ->
    inp = document.getElementById(field)
    inp.classList.add('exclude')
    inp.setAttribute('data-required', 'false')

  process_partial_submit: (event, self) ->
    form = event.detail.parent_node
    form_elements = (element for element in form.elements when not
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
      self.submit_observation(self.form, form_elements, event.detail.action,
        self.form.getAttribute('ajax-args'))
      dialog_id = document.getElementById(event.detail.target)
      cover = document.getElementById('cover')
      document.getElementsByTagName('body')[0].removeChild(cover)
      dialog_id.parentNode.removeChild(dialog_id)

  process_post_score_submit: (event, self) ->
    form = event.detail.parent_node
    form_elements = (element for element in form.elements when not
      element.classList.contains('exclude'))
    endpoint = event.detail.endpoint
    self.submit_observation(form,
      form_elements, endpoint, form.getAttribute('ajax-args'))

  handle_display_partial_reasons: (event) ->
    if not event.handled
      form = event.detail.parent_node
      this.display_partial_reasons(form)
      event.handled = true

  findParentWithClass: (el, className) ->
    while el.parentNode
      el = el.parentNode
      if el and className in el.classList
        return el
    return null

### istanbul ignore if ###
if !window.NH
  window.NH = {}

### istanbul ignore else ###
window?.NH.NHMobileForm = NHMobileForm

