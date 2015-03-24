var NHMobileShare,
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

NHMobileShare = (function(superClass) {
  extend(NHMobileShare, superClass);

  function NHMobileShare(share_button1, claim_button1) {
    var self;
    this.share_button = share_button1;
    this.claim_button = claim_button1;
    self = this;
    this.form = document.getElementById('handover_form');
    this.share_button.addEventListener('click', function(event) {
      var nurse_id, share_button;
      share_button = event.srcElement ? event.srcElement : event.target;
      nurse_id = share_button.getAttribute('data-nurse');
      return self.share_button_click(self, nurse_id);
    });
    this.claim_button.addEventListener('click', function(event) {
      var claim_button, nurse_id;
      claim_button = event.srcElement ? event.srcElement : event.target;
      nurse_id = claim_button.getAttribute('data-nurse');
      return self.claim_button_click(self, nurse_id);
    });
    NHMobileShare.__super__.constructor.call(this);
  }

  NHMobileShare.prototype.share_button_click = function(self, current_nurse_id) {
    var btn, el, msg, patients, url, urlmeth;
    patients = (function() {
      var i, len, ref, results;
      ref = this.form.elements;
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        el = ref[i];
        if (el.checked && !el.classList.contains('exclude')) {
          results.push(el.value);
        }
      }
      return results;
    }).call(this);
    if (patients.length > 0) {
      url = self.urls.json_nurse_list(current_nurse_id);
      urlmeth = url.method;
      return Promise.when(self.process_request(urlmeth, url.url)).then(function(server_data) {
        var assign_btn, btns, can_btn, data, i, len, nurse, nurse_list;
        data = server_data[0];
        nurse_list = '<form id="nurse_list"><ul>';
        for (i = 0, len = data.length; i < len; i++) {
          nurse = data[i];
          nurse_list += '<li><input type="checkbox" name="nurse_select_' + nurse['id'] + '" value="' + nurse['id'] + '"/>' + nurse['display_name'] + ' (' + nurse['current_allocation'] + ')</li>';
        }
        nurse_list += '</ul></form>';
        assign_btn = '<a href="#" data-action="assign" ' + 'data-target="assign_nurse" data-ajax-action="json_assign_nurse">' + 'Assign</a>';
        can_btn = '<a href="#" data-action="close" data-target="assign_nurse"' + '>Cancel</a>';
        btns = [assign_btn, can_btn];
        return new window.NH.NHModal('assign_nurse', 'Assign patient to colleague', nurse_list, btns, 0, self.form);
      });
    } else {
      msg = '<p class="block">Please select patients to hand' + ' to another staff member</p>';
      btn = '<a href="#" data-action="close" data-target="invalid_form">' + 'Cancel</a>';
      return new window.NH.NHModal('invalid_form', 'No Patients selected', msg, [btn], 0, self.form);
    }
  };

  NHMobileShare.prototype.claim_button_click = function(self, current_nurse_id) {
    return true;
  };

  return NHMobileShare;

})(NHMobile);

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobileShare = NHMobileShare;
}
