# NHMobileShare
# Allows users to share patients with other users when they are not on ward
### istanbul ignore next ###
class NHMobileShare extends NHMobile

  # on initalisation we need to:
  # - set up click event listener for share button
  # - set up click event listener for claim button
  constructor: (@share_button, @claim_button, @all_button) ->
    self = @
    @form = document.getElementById('handover_form')
    @share_button.addEventListener 'click', (event) ->
      self.handle_event(event, self.share_button_click, true, self)
#      event.preventDefault()
#     share_button = if event.srcElement then event.srcElement else event.target
#      self.share_button_click(self)
    @claim_button.addEventListener 'click', (event) ->
#      event.preventDefault()
#     claim_button = if event.srcElement then event.srcElement else event.target
#      self.claim_button_click(self)
      self.handle_event(event, self.claim_button_click, true, self)
    @all_button.addEventListener 'click', (event) ->
#      event.preventDefault()
#      ### istanbul ignore else ###
#      if not event.handled
      button = if event.srcElement then event.srcElement else event.target
      button_mode = button.getAttribute('mode')
      if button_mode is 'select'
        self.handle_event(event, self.select_all_patients, true, self)
        button.textContent = 'Unselect all'
        button.setAttribute('mode', 'unselect')
      else
        self.handle_event(event, self.unselect_all_patients, true, self)
        button.textContent = 'Select all'
        button.setAttribute('mode', 'select')
#      event.handled = true
    document.addEventListener 'assign_nurse', (event) ->
#      event.preventDefault()
#      if not event.handled
#        self.assign_button_click(self, event)
#        event.handled = true
      self.handle_event(event, self.assign_button_click, true, self)
    document.addEventListener 'claim_patients', (event) ->
#      event.preventDefault()
#      if not event.handled
#        self.claim_patients_click(self, event)
#        event.handled = true
      self.handle_event(event, self.claim_patients_click, true, self)
    super()

  # On share button being pressed:
  # - Create an array of IDs for patients to be shared
  # - Get the list of nurses available to assign patients to
  # - Popup the nurse selection screen in a fullscreen modal
  share_button_click: (event, self) ->
    patients = (el.value for el in self.form.elements \
        when el.checked and not el.classList.contains('exclude'))
    if patients.length > 0
      url = self.urls.json_colleagues_list()
      urlmeth = url.method
      Promise.when(self.process_request(urlmeth, url.url)).then (raw_data) ->
        server_data = raw_data[0]
        data = server_data.data
        nurse_list = '<form id="nurse_list"><ul class="sharelist">'
        for nurse in data.colleagues
          nurse_list += '<li><input type="checkbox" name="nurse_select_'+
            nurse.id+'" class="patient_share_nurse" value="'+
            nurse.id+'"/><label for="nurse_select_' + nurse.id + '">'+
            nurse.name+' ('+nurse.patients+')</label></li>'
        nurse_list += '</ul><p class="error"></p></form>'
        assign_btn = '<a href="#" data-action="assign" '+
          'data-target="assign_nurse" data-ajax-action="json_assign_nurse">'+
          'Assign</a>'
        can_btn = '<a href="#" data-action="close" data-target="assign_nurse"'+
          '>Cancel</a>'
        btns = [assign_btn, can_btn]
        new window.NH.NHModal('assign_nurse', server_data.title,
          nurse_list, btns, 0, self.form)
    else
      msg = '<p>Please select patients to hand'+
        ' to another staff member</p>'
      btn = ['<a href="#" data-action="close" data-target="invalid_form">'+
        'Cancel</a>']
      new window.NH.NHModal('invalid_form', 'No Patients selected',
        msg, btn, 0, self.form)

  # On claim button being pressed:
  # - Create an array of IDs for patients to be claimed
  # - Send list of selected ids to server
  # - Update UI to reflect the change
  claim_button_click: (event, self) ->
    form = document.getElementById('handover_form')
    patients = (el.value for el in form.elements \
      when el.checked and not el.classList.contains('exclude'))
    if patients.length > 0
      assign_btn = '<a href="#" data-action="claim" '+
        'data-target="claim_patients" data-ajax-action="json_claim_patients">'+
        'Claim</a>'
      can_btn = '<a href="#" data-action="close" data-target="claim_patients"'+
        '>Cancel</a>'
      claim_msg = '<p>Claim patients shared with colleagues</p>'
      btns = [assign_btn, can_btn]
      new window.NH.NHModal('claim_patients', 'Claim Patients?',
        claim_msg, btns, 0, self.form)
    else
      msg = '<p>Please select patients to claim back</p>'
      btn = ['<a href="#" data-action="close" data-target="invalid_form">'+
        'Cancel</a>']
      new window.NH.NHModal('invalid_form', 'No Patients selected',
        msg, btn, 0, self.form)
    return true

  # On Assign button being click in the modal:
  # - Check to see if nurses are selected
  # - If so then send data over to the server
  # - If not then show an error message
  assign_button_click: (event, self) ->
    nurses = event.detail.nurses
    form = document.getElementById('handover_form')
    popup = document.getElementById('assign_nurse')
    error_message = popup.getElementsByClassName('error')[0]
    body = document.getElementsByTagName('body')[0]
    patients = (el.value for el in form.elements \
        when el.checked and not el.classList.contains('exclude'))
    if nurses.length < 1 or patients.length < 1
      error_message.innerHTML = 'Please select colleague(s) to share with'
    else
      error_message.innerHTML = ''
      url = self.urls.json_share_patients()
      data_string = ''
      nurse_ids = 'user_ids='+nurses
      patient_ids = 'patient_ids='+patients
      data_string = patient_ids + '&'+ nurse_ids
      Promise.when(self.call_resource(url, data_string)).then (raw_data) ->
        server_data = raw_data[0]
        data = server_data.data
        if server_data.status is 'success'
          pts = (el for el in form.elements when el.value in patients)
          for pt in pts
            pt.checked = false
            pt_el = pt.parentNode.getElementsByClassName('block')[0]
            pt_el.parentNode.classList.add('shared')
            ti = pt_el.getElementsByClassName('taskInfo')[0]
            if ti.innerHTML.indexOf('Shared') < 0
              ti.innerHTML = 'Shared with: ' + data.shared_with.join(', ')
            else
              ti.innerHTML += ', ' + data.shared_with.join(', ')

          cover = document.getElementById('cover')
          document.getElementsByTagName('body')[0].removeChild(cover)
          popup.parentNode.removeChild(popup)
          can_btn = '<a href="#" data-action="close" '+
            'data-target="share_success">Close</a>'
          share_msg = '<p>'+ server_data.desc +
            data.shared_with.join(', ') + '</p>'
          btns = [can_btn]
          new window.NH.NHModal('share_success', server_data.title,
            share_msg, btns, 0, body)
        else
          error_message.innerHTML = 'Error assigning colleague(s),'+
            ' please try again'
    return true

  claim_patients_click: (event, self) ->
    form = document.getElementById('handover_form')
    patients = (el.value for el in form.elements \
      when el.checked and not el.classList.contains('exclude'))
    data_string = 'patient_ids=' + patients
    url = self.urls.json_claim_patients()
    Promise.when(self.call_resource(url, data_string)).then (raw_data) ->
      server_data = raw_data[0]
      data = server_data.data
      popup = document.getElementById('claim_patients')
      cover = document.getElementById('cover')
      body = document.getElementsByTagName('body')[0]
      body.removeChild(cover)
      popup.parentNode.removeChild(popup)
      if server_data.status is 'success'
        pts = (el for el in form.elements when el.value in patients)
        for pt in pts
          pt.checked = false
          pt_el = pt.parentNode.getElementsByClassName('block')[0]
          pt_el.parentNode.classList.remove('shared')
          ti = pt_el.getElementsByClassName('taskInfo')[0]
          ti.innerHTML = '<br>'
        can_btn = '<a href="#" data-action="close" '+
            'data-target="claim_success">Close</a>'
        claim_msg = '<p>' + server_data.desc + '</p>'
        btns = [can_btn]
        new window.NH.NHModal('claim_success', server_data.title,
          claim_msg, btns, 0, body)
      else
        can_btn = '<a href="#" data-action="close" data-target="claim_error"'+
          '>Close</a>'
        claim_msg = '<p>There was an error claiming back your'+
          ' patients, please contact your Shift Coordinator</p>'
        btns = [can_btn]
        new window.NH.NHModal('claim_error', 'Error claiming patients',
          claim_msg, btns, 0, body)
    return true

  select_all_patients: (event, self) ->
    form = document.getElementById('handover_form')
    (el.checked = true for el in form.elements \
      when not el.classList.contains('exclude'))
    return true

  unselect_all_patients: (event, self) ->
    form = document.getElementById('handover_form')
    (el.checked = false for el in form.elements \
      when not el.classList.contains('exclude'))
    return true

### istanbul ignore if ###
if !window.NH
  window.NH = {}
### istanbul ignore else ###
window?.NH.NHMobileShare = NHMobileShare