# NHMobileShare
# Allows users to share patients with other users when they are not on ward

class NHMobileShare extends NHMobile

  # on initalisation we need to:
  # - set up click event listener for share button
  # - set up click event listener for claim button
  constructor: (@share_button, @claim_button) ->
    self = @
    @form = document.getElementById('handover_form')
    @share_button.addEventListener 'click', (event) ->
      share_button = if event.srcElement then event.srcElement else event.target
      nurse_id = share_button.getAttribute('data-nurse')
      self.share_button_click(self, nurse_id)
    @claim_button.addEventListener 'click', (event) ->
      claim_button = if event.srcElement then event.srcElement else event.target
      nurse_id = claim_button.getAttribute('data-nurse')
      self.claim_button_click(self, nurse_id)
    super()

  # On share button being pressed:
  # - Create an array of IDs for patients to be shared
  # - Get the list of nurses available to assign patients to
  # - Popup the nurse selection screen in a fullscreen modal
  share_button_click: (self, current_nurse_id) ->
    patients = (el.value for el in @form.elements \
        when el.checked and not el.classList.contains('exclude'))
    if patients.length > 0
      url = self.urls.json_nurse_list(current_nurse_id)
      urlmeth = url.method
      Promise.when(self.process_request(urlmeth, url.url)).then (server_data) ->
        data = server_data[0]
        nurse_list = '<form id="nurse_list"><ul>'
        for nurse in data
          nurse_list += '<li><input type="checkbox" name="nurse_select_'+
            nurse['id'] + '" value="'+nurse['id']+'"/>' + nurse['display_name']+
             ' (' +nurse['current_allocation'] + ')</li>'
        nurse_list += '</ul></form>'
        assign_btn = '<a href="#" data-action="assign" '+
          'data-target="assign_nurse" data-ajax-action="json_assign_nurse">'+
          'Assign</a>'
        can_btn = '<a href="#" data-action="close" data-target="assign_nurse"'+
          '>Cancel</a>'
        btns = [assign_btn, can_btn]
        new window.NH.NHModal('assign_nurse', 'Assign patient to colleague',
          nurse_list, btns, 0, self.form)
    else
      msg = '<p class="block">Please select patients to hand'+
        ' to another staff member</p>'
      btn = '<a href="#" data-action="close" data-target="invalid_form">'+
        'Cancel</a>'
      new window.NH.NHModal('invalid_form', 'No Patients selected',
        msg, [btn], 0, self.form)

  # On claim button being pressed:
  # - Create an array of IDs for patients to be claimed
  # - Send list of selected ids to server
  # - Update UI to reflect the change
  claim_button_click: (self, current_nurse_id) ->
    return true

if !window.NH
  window.NH = {}
window?.NH.NHMobileShare = NHMobileShare