var NHMobileShare,
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty,
  indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

NHMobileShare = (function(superClass) {
  extend(NHMobileShare, superClass);

  function NHMobileShare(share_button1, claim_button1, all_button) {
    var self;
    this.share_button = share_button1;
    this.claim_button = claim_button1;
    this.all_button = all_button;
    self = this;
    this.form = document.getElementById('handover_form');
    this.share_button.addEventListener('click', function(event) {
      var share_button;
      event.preventDefault();
      share_button = event.srcElement ? event.srcElement : event.target;
      return self.share_button_click(self);
    });
    this.claim_button.addEventListener('click', function(event) {
      var claim_button;
      event.preventDefault();
      claim_button = event.srcElement ? event.srcElement : event.target;
      return self.claim_button_click(self);
    });
    this.all_button.addEventListener('click', function(event) {
      var button, button_mode;
      event.preventDefault();
      if (!event.handled) {
        button = event.srcElement ? event.srcElement : event.target;
        button_mode = button.getAttribute('mode');
        if (button_mode === 'select') {
          self.select_all_patients(self, event);
          button.textContent = 'Unselect all';
          button.setAttribute('mode', 'unselect');
        } else {
          self.unselect_all_patients(self, event);
          button.textContent = 'Select all';
          button.setAttribute('mode', 'select');
        }
        return event.handled = true;
      }
    });
    document.addEventListener('assign_nurse', function(event) {
      event.preventDefault();
      if (!event.handled) {
        self.assign_button_click(self, event);
        return event.handled = true;
      }
    });
    document.addEventListener('claim_patients', function(event) {
      event.preventDefault();
      if (!event.handled) {
        self.claim_patients_click(self, event);
        return event.handled = true;
      }
    });
    NHMobileShare.__super__.constructor.call(this);
  }

  NHMobileShare.prototype.share_button_click = function(self) {
    var btn, el, msg, patients, url, urlmeth;
    patients = (function() {
      var i, len, ref, results;
      ref = self.form.elements;
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        el = ref[i];
        if (el.checked && !el.classList.contains('exclude')) {
          results.push(el.value);
        }
      }
      return results;
    })();
    if (patients.length > 0) {
      url = self.urls.json_colleagues_list();
      urlmeth = url.method;
      return Promise.when(self.process_request(urlmeth, url.url)).then(function(server_data) {
        var assign_btn, btns, can_btn, data, i, len, nurse, nurse_list;
        data = server_data[0][0];
        nurse_list = '<form id="nurse_list"><ul class="sharelist">';
        for (i = 0, len = data.length; i < len; i++) {
          nurse = data[i];
          nurse_list += '<li><input type="checkbox" name="nurse_select_' + nurse['id'] + '" class="patient_share_nurse" value="' + nurse['id'] + '"/><label for="nurse_select_' + nurse['id'] + '">' + nurse['name'] + ' (' + nurse['patients'] + ')</label></li>';
        }
        nurse_list += '</ul><p class="error"></p></form>';
        assign_btn = '<a href="#" data-action="assign" ' + 'data-target="assign_nurse" data-ajax-action="json_assign_nurse">' + 'Assign</a>';
        can_btn = '<a href="#" data-action="close" data-target="assign_nurse"' + '>Cancel</a>';
        btns = [assign_btn, can_btn];
        return new window.NH.NHModal('assign_nurse', 'Assign patient to colleague', nurse_list, btns, 0, self.form);
      });
    } else {
      msg = '<p class="block">Please select patients to hand' + ' to another staff member</p>';
      btn = ['<a href="#" data-action="close" data-target="invalid_form">' + 'Cancel</a>'];
      return new window.NH.NHModal('invalid_form', 'No Patients selected', msg, btn, 0, self.form);
    }
  };

  NHMobileShare.prototype.claim_button_click = function(self) {
    var assign_btn, btn, btns, can_btn, claim_msg, el, form, msg, patients;
    form = document.getElementById('handover_form');
    patients = (function() {
      var i, len, ref, results;
      ref = form.elements;
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        el = ref[i];
        if (el.checked && !el.classList.contains('exclude')) {
          results.push(el.value);
        }
      }
      return results;
    })();
    if (patients.length > 0) {
      assign_btn = '<a href="#" data-action="claim" ' + 'data-target="claim_patients" data-ajax-action="json_claim_patients">' + 'Claim</a>';
      can_btn = '<a href="#" data-action="close" data-target="claim_patients"' + '>Cancel</a>';
      claim_msg = '<p class="block">Claim patients shared with colleagues</p>';
      btns = [assign_btn, can_btn];
      new window.NH.NHModal('claim_patients', 'Claim Patients?', claim_msg, btns, 0, self.form);
    } else {
      msg = '<p class="block">Please select patients to claim back</p>';
      btn = ['<a href="#" data-action="close" data-target="invalid_form">' + 'Cancel</a>'];
      new window.NH.NHModal('invalid_form', 'No Patients selected', msg, btn, 0, self.form);
    }
    return true;
  };

  NHMobileShare.prototype.assign_button_click = function(self, event) {
    var body, data_string, el, error_message, form, nurse_ids, nurses, patient_ids, patients, popup, url;
    nurses = event.detail.nurses;
    form = document.getElementById('handover_form');
    popup = document.getElementById('assign_nurse');
    error_message = popup.getElementsByClassName('error')[0];
    body = document.getElementsByTagName('body')[0];
    patients = (function() {
      var i, len, ref, results;
      ref = form.elements;
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        el = ref[i];
        if (el.checked && !el.classList.contains('exclude')) {
          results.push(el.value);
        }
      }
      return results;
    })();
    if (nurses.length < 1 || patients.length < 1) {
      error_message.innerHTML = 'Please select colleague(s) to share with';
    } else {
      error_message.innerHTML = '';
      url = self.urls.json_share_patients();
      data_string = '';
      nurse_ids = 'user_ids=' + nurses;
      patient_ids = 'patient_ids=' + patients;
      data_string = patient_ids + '&' + nurse_ids;
      Promise.when(self.call_resource(url, data_string)).then(function(server_data) {
        var btns, can_btn, cover, data, i, len, pt, pt_el, pts, share_msg, ti;
        data = server_data[0][0];
        if (data['status']) {
          pts = (function() {
            var i, len, ref, ref1, results;
            ref = form.elements;
            results = [];
            for (i = 0, len = ref.length; i < len; i++) {
              el = ref[i];
              if (ref1 = el.value, indexOf.call(patients, ref1) >= 0) {
                results.push(el);
              }
            }
            return results;
          })();
          for (i = 0, len = pts.length; i < len; i++) {
            pt = pts[i];
            pt.checked = false;
            pt_el = pt.parentNode.getElementsByClassName('block')[0];
            pt_el.parentNode.classList.add('shared');
            ti = pt_el.getElementsByClassName('taskInfo')[0];
            if (ti.innerHTML.indexOf('Shared') < 0) {
              ti.innerHTML = 'Shared with: ' + data['shared_with'].join(', ');
            } else {
              ti.innerHTML += ', ' + data['shared_with'].join(', ');
            }
          }
          cover = document.getElementById('cover');
          document.getElementsByTagName('body')[0].removeChild(cover);
          popup.parentNode.removeChild(popup);
          can_btn = '<a href="#" data-action="close" ' + 'data-target="share_success">Cancel</a>';
          share_msg = '<p class="block">Successfully shared patients with ' + data['shared_with'].join(', ') + '</p>';
          btns = [can_btn];
          return new window.NH.NHModal('share_success', 'Patients Shared', share_msg, btns, 0, body);
        } else {
          return error_message.innerHTML = 'Error assigning colleague(s),' + ' please try again';
        }
      });
    }
    return true;
  };

  NHMobileShare.prototype.claim_patients_click = function(self, event) {
    var data_string, el, form, patients, url;
    form = document.getElementById('handover_form');
    patients = (function() {
      var i, len, ref, results;
      ref = form.elements;
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        el = ref[i];
        if (el.checked && !el.classList.contains('exclude')) {
          results.push(el.value);
        }
      }
      return results;
    })();
    data_string = 'patient_ids=' + patients;
    url = self.urls.json_claim_patients();
    Promise.when(self.call_resource(url, data_string)).then(function(server_data) {
      var body, btns, can_btn, claim_msg, cover, data, i, len, popup, pt, pt_el, pts, ti;
      data = server_data[0][0];
      popup = document.getElementById('claim_patients');
      cover = document.getElementById('cover');
      body = document.getElementsByTagName('body')[0];
      body.removeChild(cover);
      popup.parentNode.removeChild(popup);
      if (data['status']) {
        pts = (function() {
          var i, len, ref, ref1, results;
          ref = form.elements;
          results = [];
          for (i = 0, len = ref.length; i < len; i++) {
            el = ref[i];
            if (ref1 = el.value, indexOf.call(patients, ref1) >= 0) {
              results.push(el);
            }
          }
          return results;
        })();
        for (i = 0, len = pts.length; i < len; i++) {
          pt = pts[i];
          pt.checked = false;
          pt_el = pt.parentNode.getElementsByClassName('block')[0];
          pt_el.parentNode.classList.remove('shared');
          ti = pt_el.getElementsByClassName('taskInfo')[0];
          ti.innerHTML = '<br>';
        }
        can_btn = '<a href="#" data-action="close" ' + 'data-target="claim_success">Cancel</a>';
        claim_msg = '<p class="block">Successfully claimed patients</p>';
        btns = [can_btn];
        return new window.NH.NHModal('claim_success', 'Patients Claimed', claim_msg, btns, 0, body);
      } else {
        can_btn = '<a href="#" data-action="close" data-target="claim_error"' + '>Cancel</a>';
        claim_msg = '<p class="block">There was an error claiming back your' + ' patients, please contact your Ward Manager</p>';
        btns = [can_btn];
        return new window.NH.NHModal('claim_error', 'Error claiming patients', claim_msg, btns, 0, body);
      }
    });
    return true;
  };

  NHMobileShare.prototype.select_all_patients = function(self, event) {
    var el, form, i, len, ref;
    form = document.getElementById('handover_form');
    ref = form.elements;
    for (i = 0, len = ref.length; i < len; i++) {
      el = ref[i];
      if (!el.classList.contains('exclude')) {
        el.checked = true;
      }
    }
    return true;
  };

  NHMobileShare.prototype.unselect_all_patients = function(self, event) {
    var el, form, i, len, ref;
    form = document.getElementById('handover_form');
    ref = form.elements;
    for (i = 0, len = ref.length; i < len; i++) {
      el = ref[i];
      if (!el.classList.contains('exclude')) {
        el.checked = false;
      }
    }
    return true;
  };

  return NHMobileShare;

})(NHMobile);


/* istanbul ignore else */

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobileShare = NHMobileShare;
}
