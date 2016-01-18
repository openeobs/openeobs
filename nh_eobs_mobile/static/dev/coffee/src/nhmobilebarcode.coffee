# NHMobileBarcode
# Handles barcode scanning on MioCare devices
### istanbul ignore next ###
class NHMobileBarcode extends NHMobile

  # on initalisation we need to:
  # - set up click event listener for trigger button
  constructor: (@trigger_button) ->
    self = @
    @trigger_button.addEventListener 'click', (event) ->
      self.handle_event(event, self.trigger_button_click, true, self)
#      self.trigger_button_click(self)
    super()

  # On trigger button being pressed:
  # - Show a modal with an input box to scan
  # - Set the focus to the input in the box
  # - Add a change event listener to the input box
  trigger_button_click: (event, self) ->
    input = '<div class="block"><textarea '+
      'name="barcode_scan" class="barcode_scan"></textarea></div>'
    cancel = '<a href="#" data-target="patient_barcode" ' +
      'data-action="close">Cancel</a>'
    new NHModal('patient_barcode', 'Scan patient wristband',
      input, [cancel], 0 ,document.getElementsByTagName('body')[0])
    self.input = document.getElementsByClassName('barcode_scan')[0]
    self.input.addEventListener 'keydown', (event) ->
      ### istanbul ignore else ###
      if event.keyCode is 13 or event.keyCode is 0 or event.keyCode is 116
        event.preventDefault()
        setTimeout( ->
          self.handle_event(event, self.barcode_scanned, true, self)
#          self.barcode_scanned(self, event)
        , 1000)

    self.input.addEventListener 'keypress', (event) ->
      ### istanbul ignore else ###
      if event.keyCode is 13 or event.keyCode is 0 or event.keyCode is 116
        self.handle_event(event, self.barcode_scanned, true, self)
#        event.preventDefault()
#        self.barcode_scanned(self, event)
    self.input.focus()

  # On barcode being scanned:
  # - get the hospital number from the input
  # - MioCare devices trigger the barcode scan event twice so return when not
  # ready
  # - use that hospital number to call the server
  # - on receiving data change the modal content
  barcode_scanned: (event, self) ->
#    event.preventDefault()
    ### istanbul ignore else ###
#    if not event.handled
#    input = if event.srcElement then event.srcElement else event.target
    input = event.src_el
    # hosp_num = input.value
    dialog = input.parentNode.parentNode
    if input.value is ''
      return
    # process hosp_num from wristband
    # hosp_num = hosp_num.split(',')[1]
    url = self.urls.json_patient_barcode(input.value.split(',')[1])
    url_meth = url.method

    Promise.when(self.process_request(url_meth, url.url))
    .then (raw_data) ->
      server_data = raw_data[0]
      data = server_data.data
      activities_string = ""
      if data.activities.length > 0
        activities_string = '<ul class="menu">'
        for activity in data.activities
          activities_string += '<li class="rightContent"><a href="'+
            self.urls.single_task(activity.id).url+'">'+
            activity.display_name+'<span class="aside">'+
            activity.time+'</span></a></li>'
        activities_string += '</ul>'
      content = self.render_patient_info(data, false, self) +
        '<h3>Tasks</h3>'+activities_string
      dialog.innerHTML = content
#        event.handled = true

### istanbul ignore if ###
if !window.NH
  window.NH = {}
### istanbul ignore else ###
window?.NH.NHMobileBarcode = NHMobileBarcode