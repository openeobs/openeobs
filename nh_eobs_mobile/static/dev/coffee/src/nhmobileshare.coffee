# NHMobileShare
# Allows users to share patients with other users when they are not on ward

class NHMobileShare extends NHMobile

  # on initalisation we need to:
  # - set up click event listener for trigger button
  constructor: (@share_button) ->
    self = @
    @share_button.addEventListener 'click', (event) ->
      self.share_button_click(self)
    super()

  # On share button being pressed:
  # - Show check boxes for each item in patient list
  # - Popup the nurse selection screen
  share_button_click: (self) ->
    patient_list = document.getElementsByClassName('tasklist')[0]
    patients = patient_list.getElementsByTagName('li')
    for patient in patients
      patient.classList.add('patient_share_active')

if !window.NH
  window.NH = {}
window?.NH.NHMobileShare = NHMobileShare