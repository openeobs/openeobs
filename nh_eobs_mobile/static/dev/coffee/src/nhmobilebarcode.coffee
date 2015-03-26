# NHMobileBarcode
# Handles barcode scanning on MioCare devices

class NHMobileBarcode extends NHMobile

  # on initalisation we need to:
  # - set up click event listener for trigger button
  constructor: (@trigger_button) ->
    self = @
    @trigger_button.addEventListener 'click', (event) ->
      self.trigger_button_click(self)
    super()

  # On trigger button being pressed:
  # - Show a modal with an input box to scan
  # - Set the focus to the input in the box
  # - Add a change event listener to the input box
  trigger_button_click: (self) ->
    input = '<div class="block"><textarea '+
      'name="barcode_scan" class="barcode_scan"></textarea></div>'
    cancel = '<a href="#" data-target="patient_barcode" ' +
      'data-action="close">Cancel</a>'
    new NHModal('patient_barcode', 'Scan patient wristband',
      input, [cancel], 0 ,document.getElementsByTagName('body')[0])
    self.input = document.getElementsByClassName('barcode_scan')[0]
    self.input.addEventListener 'keydown', (event) ->
      if event.keyCode is 13 or event.keyCode is 0
        self.barcode_scanned(self, event)

    self.input.addEventListener 'keypress', (event) ->
      if event.keyCode is 13 or event.keyCode is 0
        self.barcode_scanned(self, event)
    self.input.focus()

  # On barcode being scanned:
  # - get the hospital number from the input
  # - use that hospital number to call the server
  # - on receiving data change the modal content
  barcode_scanned: (self, event) ->
    event.preventDefault()
    input = if event.srcElement then event.srcElement else event.target
    hosp_num = input.value
    dialog = input.parentNode.parentNode
    # process hosp_num from wristband
    hosp_num = hosp_num.split(',')[1]
    url = self.urls.json_patient_barcode(hosp_num)
    url_meth = url.method
    Promise.when(self.process_request(url_meth, url.url)).then (server_data) ->
      data = server_data[0][0]
      patient_details = ''
      if data.full_name
        patient_details += "<dt>Name:</dt><dd>" + data.full_name + "</dd>"
      if data.gender
        patient_details += '<dt>Gender:</dt><dd>' + data.gender + '</dd>'
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
      if data.ews_trend
        patient_details += '<dt>NEWS Trend:</dt><dd>'+data.ews_trend+'</dd>'
      if data.other_identifier
        patient_details += "<dt>Hospital ID:</dt><dd>" + data.other_identifier +
          "</dd>"
      if data.patient_identifier
        patient_details += "<dt>NHS Number:</dt><dd>" + data.patient_identifier+
          "</dd>"
      activties_string = ""
      if data.activities.length > 0
        activities_string = '<ul class="menu">'
        for activity in data.activities
          activities_string += '<li class="rightContent"><a href="'+
            self.urls.single_task(activity.id).url+'">'+
            activity.display_name+'<span class="aside">'+
            activity.time+'</span></a></li>'
        activities_string += '</ul>'
      content = '<dl>'+patient_details+'</dl><h3>Tasks</h3>'+activities_string
      dialog.innerHTML = content

if !window.NH
  window.NH = {}
window?.NH.NHMobileBarcode = NHMobileBarcode