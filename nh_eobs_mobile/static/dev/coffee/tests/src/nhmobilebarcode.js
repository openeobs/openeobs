var NHMobileBarcode,
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

NHMobileBarcode = (function(superClass) {
  extend(NHMobileBarcode, superClass);

  function NHMobileBarcode(trigger_button) {
    var self;
    this.trigger_button = trigger_button;
    self = this;
    this.trigger_button.addEventListener('click', function(event) {
      return self.trigger_button_click(self);
    });
    NHMobileBarcode.__super__.constructor.call(this);
  }

  NHMobileBarcode.prototype.trigger_button_click = function(self) {
    var cancel, input;
    input = '<div class="block"><textarea ' + 'name="barcode_scan" class="barcode_scan"></textarea></div>';
    cancel = '<a href="#" data-target="patient_barcode" ' + 'data-action="close">Cancel</a>';
    new NHModal('patient_barcode', 'Scan patient wristband', input, [cancel], 0, document.getElementsByTagName('body')[0]);
    self.input = document.getElementsByClassName('barcode_scan')[0];
    self.input.addEventListener('keydown', function(event) {
      if (event.keyCode === 13 || event.keyCode === 0 || event.keyCode === 116) {
        event.preventDefault();
        return setTimeout(function() {
          return self.barcode_scanned(self, event);
        }, 1000);
      }
    });
    self.input.addEventListener('keypress', function(event) {
      if (event.keyCode === 13 || event.keyCode === 0 || event.keyCode === 116) {
        event.preventDefault();
        return self.barcode_scanned(self, event);
      }
    });
    return self.input.focus();
  };

  NHMobileBarcode.prototype.barcode_scanned = function(self, event) {
    var dialog, input, url, url_meth;
    event.preventDefault();
    input = event.srcElement ? event.srcElement : event.target;
    dialog = input.parentNode.parentNode;
    if (input.value === '') {
      return;
    }
    url = self.urls.json_patient_barcode(input.value.split(',')[1]);
    url_meth = url.method;
    return Promise.when(self.process_request(url_meth, url.url)).then(function(server_data) {
      var activities_string, activity, activties_string, content, data, i, len, patientDOB, patient_details, ref;
      data = server_data[0][0];
      patient_details = '';
      if (data.full_name) {
        patient_details += "<dt>Name:</dt><dd>" + data.full_name + "</dd>";
      }
      if (data.gender) {
        patient_details += '<dt>Gender:</dt><dd>' + data.gender + '</dd>';
      }
      if (data.dob) {
        patientDOB = self.date_from_string(data.dob);
        patient_details += "<dt>DOB:</dt><dd>" + self.date_to_dob_string(patientDOB) + "</dd>";
      }
      if (data.location) {
        patient_details += "<dt>Location:</dt><dd>" + data.location;
      }
      if (data.parent_location) {
        patient_details += ',' + data.parent_location + '</dd>';
      } else {
        patient_details += '</dd>';
      }
      if (data.ews_score) {
        patient_details += '<dt class="twoline">Latest Score:</dt>' + '<dd class="twoline">' + data.ews_score + '</dd>';
      }
      if (data.ews_trend) {
        patient_details += '<dt>NEWS Trend:</dt><dd>' + data.ews_trend + '</dd>';
      }
      if (data.other_identifier) {
        patient_details += "<dt>Hospital ID:</dt><dd>" + data.other_identifier + "</dd>";
      }
      if (data.patient_identifier) {
        patient_details += "<dt>NHS Number:</dt><dd>" + data.patient_identifier + "</dd>";
      }
      activties_string = "";
      if (data.activities.length > 0) {
        activities_string = '<ul class="menu">';
        ref = data.activities;
        for (i = 0, len = ref.length; i < len; i++) {
          activity = ref[i];
          activities_string += '<li class="rightContent"><a href="' + self.urls.single_task(activity.id).url + '">' + activity.display_name + '<span class="aside">' + activity.time + '</span></a></li>';
        }
        activities_string += '</ul>';
      }
      content = '<dl>' + patient_details + '</dl><h3>Tasks</h3>' + activities_string;
      return dialog.innerHTML = content;
    });
  };

  return NHMobileBarcode;

})(NHMobile);

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobileBarcode = NHMobileBarcode;
}
