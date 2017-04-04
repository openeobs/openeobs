# NHModal creates a modal popup and handles events triggered via modal buttons
### istanbul ignore next ###
class NHModal extends NHLib

  # creates a dialog, adds it to the DOM and resizes to fit in window
  # Params:
  #  - `id` - CSS ID to use for the popup
  #  - `title` - HTML String to use for the popup title
  #  - `content` - HTML String to use for the popup message, can be any content
  #  - `options` - An array of HTML Strings that will act as buttons
  #  - `popupTime` - time it takes for popup to appear
  #  - 'el' - The element in the DOM to put popup under
  constructor: (@id, @title, @content, @options, @popupTime, @el) ->
    self = @
    # create the dialog
    dialog = @create_dialog(self, @id, @title, @content, @options)
    body = document.getElementsByTagName('body')[0]
    cover = document.createElement('div')
    cover.setAttribute('class', 'cover')
    cover.setAttribute('id', 'cover')
    cover.setAttribute('data-action', 'close')
    if @id is 'submit_observation' or @id is 'partial_reasons'
      cover.setAttribute('data-action', 'renable')
    if @id is 'rapid_tranq_check'
      cover.setAttribute('data-action', 'close_reload')
    cover.setAttribute('data-target', @id)
    cover.addEventListener('click', (e) ->
      self.handle_event(e, self.handle_button_events, false)
    )

    # append it to the DOM
    @lock_scrolling()
    body.appendChild(cover)
    @el.appendChild(dialog)
   
    # calculate the size of the modal and adjust
    @calculate_dimensions(dialog,
      dialog.getElementsByClassName('dialogContent')[0], @el)
   
   
  # helper function to create the dialog object
  create_dialog: (self, popup_id, popup_title, popup_content, popup_options) ->
   
    # create the dialog div
    dialog_div = (id) ->
      div = document.createElement('div')
      div.setAttribute('class', 'dialog')
      div.setAttribute('id', id)
      return div
   
    # create the h2 header
    dialog_header = (title) ->
      header = document.createElement('h2')
      header.innerHTML = title
      return header
   
    # create the content div
    dialog_content = (message) ->
      content = document.createElement('div')
      content.setAttribute('class', 'dialogContent')
      content.innerHTML = message
      return content
   
    # create the option buttons
    dialog_options = (self, buttons) ->
      option_list = document.createElement('ul')
      switch buttons.length
        when 1 then option_list.setAttribute('class', 'options one-col')
        when 2 then option_list.setAttribute('class', 'options two-col')
        when 3 then option_list.setAttribute('class', 'options three-col')
      for button in buttons
        do (self) ->
          option_button = document.createElement('li')
          option_button.innerHTML = button
          a_button = option_button.getElementsByTagName('a')?[0]
          a_button.addEventListener('click', (e) ->
            self.handle_event(e, self.handle_button_events, false)
          )
          option_list.appendChild(option_button)
      return option_list
   
    # create the elements and set up DOM
    container = dialog_div(popup_id)
    header = dialog_header(popup_title)
    content = dialog_content(popup_content)
    options = dialog_options(self, popup_options)
    container.appendChild(header)
    container.appendChild(content)
    container.appendChild(options)
    return container
   
  # calculate the correct size of the dialog
  # uses clientHeight to calculate the height of objects
  calculate_dimensions: (dialog, dialog_content, el) ->
    margins = {
      top: 80,
      bottom: 300,
      right: 0,
      left: 0
    }
    available_space = (dialog, el, dialog_content) ->
      dh = dialog.getElementsByTagName('h2')
      # dialog_header_height = dialog_header?[0]?.clientHeight
      dhh = parseInt(document.defaultView.getComputedStyle(dh?[0], \
        '').getPropertyValue('height').replace('px', ''))
      dopt = dialog.getElementsByClassName('options')
      # dialog_opt_first = dialog_options?[0]?.getElementsByTagName('li')
      dopth = parseInt(document.defaultView.getComputedStyle(dopt?[0], \
        '').getPropertyValue('height').replace('px', ''))
      # el_height = el.clientHeight
      elh = parseInt(document.defaultView.getComputedStyle(el, \
        '').getPropertyValue('height').replace('px', ''))
      dialog_height = ((dhh + dopth) + (margins.top + margins.bottom))
      dc_height = parseInt(document.defaultView.getComputedStyle(
        dialog_content, '').getPropertyValue('height').replace('px', ''))
      dialog_total = dialog_height + dc_height
      if elh > window.innerHeight
        return window.innerHeight - dialog_height
      if dialog_total > window.innerHeight
        return window.innerHeight - dialog_height

    max_height = available_space(dialog, el, dialog_content)
    top_offset = el.offsetTop + margins.top
    dialog.style.top = top_offset+'px'
    dialog.style.display = 'inline-block'
    if max_height
      dialog_content.style.maxHeight = max_height+'px'
    return

  # Remove a modal and it's cover from DOM
  # Takes the ID of the modal
  close_modal: (modal_id) =>
    self = @
    dialog_id = document.getElementById(modal_id)
    if typeof dialog_id isnt 'undefined' and dialog_id
      cover = document.querySelectorAll('#cover[data-target="'+
        modal_id+'"]')[0]
      document.getElementsByTagName('body')[0].removeChild(cover)
      dialog_id.parentNode.removeChild(dialog_id)
      self.unlock_scrolling()

  reloadPage: () ->
    location.reload()

  # Handle events from buttons created in options array
  # Currently offers
  # - close (closes modal)
  # - submit (submits observation)
  # - partial submit (submits partial observation)
  # - assign (assigns nurses to patients)
  # NOTE: Don't preventDefault() straight away as will disable all button clicks
  handle_button_events: (event) =>
#    if not event.handled
#      target_el = if event.srcElement then event.srcElement else event.target
    target_el = event.src_el
    data_target = target_el.getAttribute('data-target')
    data_action = target_el.getAttribute('data-ajax-action')
    switch target_el.getAttribute('data-action')
      when 'close'
        event.preventDefault()
        @close_modal(data_target)
      when 'close_reload'
        event.preventDefault()
        @reloadPage()
      when 'renable'
        event.preventDefault()
        forms = document.getElementsByTagName('form')
        for form in forms
          action_buttons = (element for element in form.elements \
            when element.getAttribute('type') in ['submit', 'reset'])
          for button in action_buttons
            button.removeAttribute('disabled')
        @close_modal(data_target)
      when 'confirm_submit'
        event.preventDefault()
        confirmEvent = document.createEvent "CustomEvent"
        confirmEvent.initCustomEvent("confirm_change", false, true, false)
        document.dispatchEvent confirmEvent
        @close_modal(data_target)
      when 'submit'
        event.preventDefault()
        submit_event = document.createEvent 'CustomEvent'
        submit_detail = {
          'endpoint': target_el.getAttribute('data-ajax-action')
        }
        submit_event.initCustomEvent('post_score_submit', true, false,
          submit_detail)
        document.dispatchEvent submit_event
        @close_modal(data_target)
      when 'partial_submit'
        event.preventDefault()
#        if not event.handled
        submit_event = document.createEvent 'CustomEvent'
        submit_detail = {
          'action':data_action,
          'target': data_target
        }
        submit_event.initCustomEvent('partial_submit',false,
          true,submit_detail)
        document.dispatchEvent submit_event
      when 'display_partial_reasons'
        event.preventDefault()
        @close_modal(data_target)
        submit_event = document.createEvent 'CustomEvent'
        submit_detail = {
          'action': data_action,
          'target': data_target
        }
        submit_event.initCustomEvent('display_partial_reasons', false,
          true, submit_detail)
        document.dispatchEvent submit_event
      when 'assign'
        event.preventDefault()
        dialog = document.getElementById(data_target)
        dialog_form = dialog.getElementsByTagName('form')[0]
        nurses = (el.value for el in dialog_form.elements when el.checked)
        assign_event = document.createEvent 'CustomEvent'
        assign_detail = {
          'action':data_action,
          'target': data_target,
          'nurses': nurses
        }
        assign_event.initCustomEvent('assign_nurse', false, true,
          assign_detail)
        document.dispatchEvent assign_event
      when 'claim'
        event.preventDefault()
        claim_event = document.createEvent 'CustomEvent'
        claim_event.initCustomEvent('claim_patients', false, true, false)
        document.dispatchEvent claim_event
      when 'accept'
        event.preventDefault()
        accept_event = document.createEvent 'CustomEvent'
        accept_detail = {
          'invite_id': target_el.getAttribute('data-invite-id')
        }
        accept_event.initCustomEvent('accept_invite', false, true,
          accept_detail)
        document.dispatchEvent accept_event
      when 'reject'
        event.preventDefault()
        reject_event = document.createEvent 'CustomEvent'
        reject_detail = {
          'invite_id': target_el.getAttribute('data-invite-id')
        }
        reject_event.initCustomEvent('reject_invite', false, true,
          reject_detail)
        document.dispatchEvent reject_event
#      event.handled = true


  # Function to prevent scrolling via locking body size to defined height and
  # setting overflow to none
  lock_scrolling: () ->
    body = document.getElementsByTagName('body')[0]
    body.classList.add('no-scroll')

  # Function to reinstate scrolling via unlocking body size and setting
  # overflow to scroll
  unlock_scrolling: () ->
    body = document.getElementsByTagName('body')[0]
    dialogs = document.getElementsByClassName('dialog')
    if dialogs.length < 1
      body.classList.remove('no-scroll')

### istanbul ignore if ###
if !window.NH
  window.NH = {}

### istanbul ignore else ###
window?.NH.NHModal = NHModal