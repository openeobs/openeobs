# NHMobileShareInvite
# Allows user to accept invitations to follow another user's patients via a
# notification in patient list

class NHMobileShareInvite extends NHMobile

  # On initialisation
  # - Find all invitations to follow a patient in the patient list
  # - Add an EventListener to the invite's element to present modal for invite
  constructor: (@patient_list) ->
    self = @
    invite_list = @patient_list.getElementsByClassName('share_invite')
    for invite in invite_list
      invite.addEventListener 'click', (event) ->
        if not event.handled
          self.handle_invite_click(self, event)
          event.handled = true

  handle_invite_click: (self, event) ->
    return true