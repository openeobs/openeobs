# NHMobileShareInvite
# Allows user to accept invitations to follow another user's patients via a
# notification in patient list
### istanbul ignore next ###
class NHMobileShareInvite extends NHMobile

  # On initialisation
  # - Find all invitations to follow a patient in the patient list
  # - Add an EventListener to the invite's element to present modal for invite
  # - Add an EventListener to document to capture the NHModal callback
  constructor: (patient_list) ->
    self = @
    invite_list = patient_list.getElementsByClassName('share_invite')
    for invite in invite_list
      invite.addEventListener 'click', (event) ->
        ### istanbul ignore else ###
        if not event.handled
          btn = if event.srcElement then event.srcElement else event.target
          activity_id = btn.getAttribute('data-invite-id')
          self.handle_invite_click(self, activity_id)
          event.handled = true
    document.addEventListener 'accept_invite', (event) ->
      if not event.handled
        activity_id = event.detail.invite_id
        self.handle_accept_button_click(self, activity_id)
        event.handled = true
    document.addEventListener 'reject_invite', (event) ->
      if not event.handled
        activity_id = event.detail.invite_id
        self.handle_reject_button_click(self, activity_id)
        event.handled = true
    super()

  # On the user clicking the invitation to follow another user's patients
  # - Contact the server with the ID of the invite activity
  # - The server will return a list of patients that are to be shared
  # - Show the patients in a modal with a button accept the invitation
  handle_invite_click: (self, activity_id) ->
    url = self.urls.json_invite_patients(activity_id)
    urlmeth = url.method
    Promise.when(self.process_request(urlmeth, url.url)).then (server_data) ->
      data = server_data[0][0]
      pt_list = '<ul class="tasklist">'
      for pt in data
        pt_obj = '<li class="block"><a>'+
          '<div class="task-meta">'+
          '<div class="task-right">'+
          '<p class="aside">'+pt['next_ews_time']+'</p></div>'+
          '<div class="task-left">'+
          '<strong>'+pt['full_name']+'</strong>'+
          '('+pt['ews_score']+' <i class="icon-'+
          pt['ews_trend']+'-arrow"></i> )'+
          '<br><em>'+pt['location']+', '+pt['parent_location']+'</em>'+
          '</div>'+
          '</div>'+
          '</a></li>'
        pt_list += pt_obj
      pt_list += '</ul>'
      cls_btn = '<a href="#" data-action="close" data-target="accept_invite"'+
        '>Close</a>'
      can_btn = '<a href="#" data-action="reject" data-target="accept_invite"'+
        'data-ajax-action="json_reject_invite" '+
        'data-invite-id="'+activity_id+'">Reject</a>'
      acpt_btn = '<a href="#" data-action="accept" data-target="accept_invite"'+
        'data-ajax-action="json_accept_invite" '+
        'data-invite-id="'+activity_id+'">Accept</a>'
      btns = [cls_btn, can_btn, acpt_btn]
      body = document.getElementsByTagName('body')[0]
      return new window.NH.NHModal('accept_invite',
        'Accept invitation to follow patients?',
        pt_list, btns, 0, body)
    return true

  # On the accept button being clicked
  # - Hit up the server to accept the invitation to follow
  # - If successful remove the invite from DOM and show modal
  # - If not successful inform the user of error
  handle_accept_button_click: (self, activity_id) ->
    url = self.urls.json_accept_patients(activity_id)
    urlmeth = url.method
    body = document.getElementsByTagName('body')[0]
    Promise.when(self.process_request(urlmeth, url.url)).then (server_data) ->
      data = server_data[0][0]
      if data['status']
        invites = document.getElementsByClassName('share_invite')
        invite = (i for i in invites when \
          i.getAttribute('data-invite-id') is activity_id)[0]
        invite.parentNode.removeChild(invite)
        btns = ['<a href="#" data-action="close" data-target="invite_success"'+
        '>Cancel</a>']
        covers = document.getElementsByClassName('cover')
        for cover in covers
          ### istanbul ignore else ###
          cover?.parentNode.removeChild(cover)
        invite_modal = document.getElementById('accept_invite')
        invite_modal.parentNode.removeChild(invite_modal)
        return new window.NH.NHModal('invite_success',
          'Successfully accepted patients',
          '<p class="block">Now following '+data['count']+' patients from '+
            data['user'] + '</p>',
          btns, 0, body)
      else
        btns = ['<a href="#" data-action="close" data-target="invite_error"'+
        '>Cancel</a>']
        covers = document.getElementsByClassName('cover')
        for cover in covers
          ### istanbul ignore else ###
          cover?.parentNode.removeChild(cover)
        invite_modal = document.getElementById('accept_invite')
        invite_modal.parentNode.removeChild(invite_modal)
        return new window.NH.NHModal('invite_error',
          'Error accepting patients',
          '<p class="block">There was an error accepting the invite to follow,'+
            'Please try again</p>',
          btns, 0, body)

  # On the reject button being clicked
  # - Hit up the server to reject the invitation to follow
  # - If successful remove the invite from DOM and show modal
  # - If not successful inform the user of error
  handle_reject_button_click: (self, activity_id) ->
    url = self.urls.json_reject_patients(activity_id)
    urlmeth = url.method
    body = document.getElementsByTagName('body')[0]
    Promise.when(self.process_request(urlmeth, url.url)).then (server_data) ->
      data = server_data[0][0]
      if data['status']
        invites = document.getElementsByClassName('share_invite')
        invite = (i for i in invites when \
          i.getAttribute('data-invite-id') is activity_id)[0]
        invite.parentNode.removeChild(invite)
        btns = ['<a href="#" data-action="close" data-target="reject_success"'+
        '>Cancel</a>']
        covers = document.getElementsByClassName('cover')
        for cover in covers
          ### istanbul ignore else ###
          cover?.parentNode.removeChild(cover)
        invite_modal = document.getElementById('accept_invite')
        invite_modal.parentNode.removeChild(invite_modal)
        return new window.NH.NHModal('reject_success',
          'Successfully rejected patients',
          '<p class="block">The invitation to follow '+data['user']+'\'s '+
            'patients was rejected</p>',
          btns, 0, body)
      else
        btns = ['<a href="#" data-action="close" data-target="reject_success"'+
        '>Cancel</a>']
        covers = document.getElementsByClassName('cover')
        for cover in covers
          ### istanbul ignore else ###
          cover?.parentNode.removeChild(cover)
        invite_modal = document.getElementById('accept_invite')
        invite_modal.parentNode.removeChild(invite_modal)
        return new window.NH.NHModal('reject_error',
          'Error rejecting patients',
          '<p class="block">There was an error rejecting the invite to follow,'+
            ' Please try again</p>',
          btns, 0, body)
### istanbul ignore if ###
if !window.NH
  window.NH = {}

### istanbul ignore else ###
window?.NH.NHMobileShareInvite = NHMobileShareInvite