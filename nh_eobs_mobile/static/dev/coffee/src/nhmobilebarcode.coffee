# NHMobileBarcode
# Handles barcode scanning on MioCare devices

class NHMobileBarcode extends NHMobile

  # on initalisation we need to:
  # - hide the input block
  # - set up click event listener for trigger button
  # - set up change event listener for input
  constructor: (@trigger_button, @input, @input_block) ->
    self = @
    @input_block.style.display = 'none'
    @trigger_button.addEventListener 'click', (event) ->
      self.trigger_button_click(self)
    @input.addEventListener 'change', (event) ->
      self.barcode_scanned(self, event)
    super()

  # On trigger button being pressed:
  # - Either show or hide tehe input block depending on current visibility
  # - If showing input then focus on it
  trigger_button_click: (self) ->
    if self.input_block.style.display is 'none'
      self.input_block.style.display = 'block'
      self.input.focus()
    else
      self.input_block.style.display = 'none'

  # On barcode being scanned:
  # - get the hospital number from the input
  # - use that hospital number to call the server
  # - on receiving data from server process it and display in a modal
  barcode_scanned: (self, event) ->
    event.preventDefault()
    input = if event.srcElement then event.srcElement else event.target
    hosp_num = input.value
    url = self.urls.json_patient_barcode(hosp_num)
    url_meth = url.method
    Promise.when(self.process_request(url_meth, url.url)).then (server_data) ->
      data = server_data[0][0]
      patient_name = ''
      patient_details = ''
      if data.full_name
        patient_name += " " + data.full_name
      if data.gender
        patient_name += '<span class="alignright">' + data.gender + '</span>'
      if data.dob
        patientDOB = self.date_from_string(data.dob)
        patient_details += "<dt>DOB:</dt><dd>" +
          self.date_to_dob_string(patientDOB) + "</dd>"
      if data.location
        patient_details += "<dt>Location:</dt><dd>" + data.location
      if data.parent_location
        patient_details += ',' + data.parent_location + '</dd>'
      else
        patient_details += '</dd>'
      if data.ews_score
        patient_details += '<dt class="twoline">Latest Score:</dt>' +
          '<dd class="twoline">' + data.ews_score + '</dd>'
      if data.other_identifier
        patient_details += "<dt>Hospital ID:</dt><dd>" + data.other_identifier +
          "</dd>"
      if data.patient_identifier
        patient_details += "<dt>NHS Number:</dt><dd>" + data.patient_identifier+
          "</dd>"
      content = '<dl>'+patient_details+'</dl><p><a href="'+
        self.urls['single_patient'](data.other_identifier).url+
        '" id="patient_obs_fullscreen" class="button patient_obs">'+
        'View Patient Observation Data</a></p>'
      cancel = '<a href="#" data-target="patient_barcode" ' +
        'data-action="close">Cancel</a>'
      new NHModal('patient_barcode', 'Perform Action', content,
        [cancel], 0,  document.getElementsByTagName('body')[0])

if !window.NH
  window.NH = {}
window?.NH.NHMobileBarcode = NHMobileBarcode