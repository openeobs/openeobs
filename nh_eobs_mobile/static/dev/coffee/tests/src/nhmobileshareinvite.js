
/* istanbul ignore next */
var NHMobileShareInvite,
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

NHMobileShareInvite = (function(superClass) {
  extend(NHMobileShareInvite, superClass);

  function NHMobileShareInvite(patient_list) {
    var invite, invite_list, j, len, self;
    self = this;
    invite_list = patient_list.getElementsByClassName('share_invite');
    for (j = 0, len = invite_list.length; j < len; j++) {
      invite = invite_list[j];
      invite.addEventListener('click', function(event) {
        var activity_id, btn;
        if (!event.handled) {
          btn = event.srcElement ? event.srcElement : event.target;
          activity_id = btn.getAttribute('data-invite-id');
          self.handle_invite_click(self, activity_id);
          return event.handled = true;
        }
      });
    }
    document.addEventListener('accept_invite', function(event) {
      var activity_id;
      if (!event.handled) {
        activity_id = event.detail.invite_id;
        self.handle_accept_button_click(self, activity_id);
        return event.handled = true;
      }
    });
    document.addEventListener('reject_invite', function(event) {
      var activity_id;
      if (!event.handled) {
        activity_id = event.detail.invite_id;
        self.handle_reject_button_click(self, activity_id);
        return event.handled = true;
      }
    });
    NHMobileShareInvite.__super__.constructor.call(this);
  }

  NHMobileShareInvite.prototype.handle_invite_click = function(self, activity_id) {
    var url, urlmeth;
    url = self.urls.json_invite_patients(activity_id);
    urlmeth = url.method;
    Promise.when(self.process_request(urlmeth, url.url)).then(function(server_data) {
      var acpt_btn, body, btns, can_btn, cls_btn, data, j, len, pt, pt_list, pt_obj;
      data = server_data[0][0];
      pt_list = '<ul class="tasklist">';
      for (j = 0, len = data.length; j < len; j++) {
        pt = data[j];
        pt_obj = '<li class="block"><a>' + '<div class="task-meta">' + '<div class="task-right">' + '<p class="aside">' + pt['next_ews_time'] + '</p></div>' + '<div class="task-left">' + '<strong>' + pt['full_name'] + '</strong>' + '(' + pt['ews_score'] + ' <i class="icon-' + pt['ews_trend'] + '-arrow"></i> )' + '<br><em>' + pt['location'] + ', ' + pt['parent_location'] + '</em>' + '</div>' + '</div>' + '</a></li>';
        pt_list += pt_obj;
      }
      pt_list += '</ul>';
      cls_btn = '<a href="#" data-action="close" data-target="accept_invite"' + '>Close</a>';
      can_btn = '<a href="#" data-action="reject" data-target="accept_invite"' + 'data-ajax-action="json_reject_invite" ' + 'data-invite-id="' + activity_id + '">Reject</a>';
      acpt_btn = '<a href="#" data-action="accept" data-target="accept_invite"' + 'data-ajax-action="json_accept_invite" ' + 'data-invite-id="' + activity_id + '">Accept</a>';
      btns = [cls_btn, can_btn, acpt_btn];
      body = document.getElementsByTagName('body')[0];
      return new window.NH.NHModal('accept_invite', 'Accept invitation to follow patients?', pt_list, btns, 0, body);
    });
    return true;
  };

  NHMobileShareInvite.prototype.handle_accept_button_click = function(self, activity_id) {
    var body, url, urlmeth;
    url = self.urls.json_accept_patients(activity_id);
    urlmeth = url.method;
    body = document.getElementsByTagName('body')[0];
    return Promise.when(self.process_request(urlmeth, url.url)).then(function(server_data) {
      var btns, cover, covers, data, i, invite, invite_modal, invites, j, k, len, len1;
      data = server_data[0][0];
      if (data['status']) {
        invites = document.getElementsByClassName('share_invite');
        invite = ((function() {
          var j, len, results;
          results = [];
          for (j = 0, len = invites.length; j < len; j++) {
            i = invites[j];
            if (i.getAttribute('data-invite-id') === activity_id) {
              results.push(i);
            }
          }
          return results;
        })())[0];
        invite.parentNode.removeChild(invite);
        btns = ['<a href="#" data-action="close" data-target="invite_success"' + '>Cancel</a>'];
        covers = document.getElementsByClassName('cover');
        for (j = 0, len = covers.length; j < len; j++) {
          cover = covers[j];
          if (cover != null) {
            cover.parentNode.removeChild(cover);
          }
        }
        invite_modal = document.getElementById('accept_invite');
        invite_modal.parentNode.removeChild(invite_modal);
        return new window.NH.NHModal('invite_success', 'Successfully accepted patients', '<p class="block">Now following ' + data['count'] + ' patients from ' + data['user'] + '</p>', btns, 0, body);
      } else {
        btns = ['<a href="#" data-action="close" data-target="invite_error"' + '>Cancel</a>'];
        covers = document.getElementsByClassName('cover');
        for (k = 0, len1 = covers.length; k < len1; k++) {
          cover = covers[k];
          if (cover != null) {
            cover.parentNode.removeChild(cover);
          }
        }
        invite_modal = document.getElementById('accept_invite');
        invite_modal.parentNode.removeChild(invite_modal);
        return new window.NH.NHModal('invite_error', 'Error accepting patients', '<p class="block">There was an error accepting the invite to follow,' + 'Please try again</p>', btns, 0, body);
      }
    });
  };

  NHMobileShareInvite.prototype.handle_reject_button_click = function(self, activity_id) {
    var body, url, urlmeth;
    url = self.urls.json_reject_patients(activity_id);
    urlmeth = url.method;
    body = document.getElementsByTagName('body')[0];
    return Promise.when(self.process_request(urlmeth, url.url)).then(function(server_data) {
      var btns, cover, covers, data, i, invite, invite_modal, invites, j, k, len, len1;
      data = server_data[0][0];
      if (data['status']) {
        invites = document.getElementsByClassName('share_invite');
        invite = ((function() {
          var j, len, results;
          results = [];
          for (j = 0, len = invites.length; j < len; j++) {
            i = invites[j];
            if (i.getAttribute('data-invite-id') === activity_id) {
              results.push(i);
            }
          }
          return results;
        })())[0];
        invite.parentNode.removeChild(invite);
        btns = ['<a href="#" data-action="close" data-target="reject_success"' + '>Cancel</a>'];
        covers = document.getElementsByClassName('cover');
        for (j = 0, len = covers.length; j < len; j++) {
          cover = covers[j];
          if (cover != null) {
            cover.parentNode.removeChild(cover);
          }
        }
        invite_modal = document.getElementById('accept_invite');
        invite_modal.parentNode.removeChild(invite_modal);
        return new window.NH.NHModal('reject_success', 'Successfully rejected patients', '<p class="block">The invitation to follow ' + data['user'] + '\'s ' + 'patients was rejected</p>', btns, 0, body);
      } else {
        btns = ['<a href="#" data-action="close" data-target="reject_success"' + '>Cancel</a>'];
        covers = document.getElementsByClassName('cover');
        for (k = 0, len1 = covers.length; k < len1; k++) {
          cover = covers[k];
          if (cover != null) {
            cover.parentNode.removeChild(cover);
          }
        }
        invite_modal = document.getElementById('accept_invite');
        invite_modal.parentNode.removeChild(invite_modal);
        return new window.NH.NHModal('reject_error', 'Error rejecting patients', '<p class="block">There was an error rejecting the invite to follow,' + ' Please try again</p>', btns, 0, body);
      }
    });
  };

  return NHMobileShareInvite;

})(NHMobile);


/* istanbul ignore else */

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobileShareInvite = NHMobileShareInvite;
}
