
/* istanbul ignore next */
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
      return self.handle_event(event, self.trigger_button_click, true, self);
    });
    NHMobileBarcode.__super__.constructor.call(this);
  }

  NHMobileBarcode.prototype.trigger_button_click = function(event, self) {
    var cancel, input;
    input = '<div class="block"><textarea ' + 'name="barcode_scan" class="barcode_scan"></textarea></div>';
    cancel = '<a href="#" data-target="patient_barcode" ' + 'data-action="close">Cancel</a>';
    new NHModal('patient_barcode', 'Scan patient wristband', input, [cancel], 0, document.getElementsByTagName('body')[0]);
    self.input = document.getElementsByClassName('barcode_scan')[0];
    self.input.addEventListener('keydown', function(event) {

      /* istanbul ignore else */
      if (event.keyCode === 13 || event.keyCode === 0 || event.keyCode === 116) {
        event.preventDefault();
        return setTimeout(function() {
          return self.handle_event(event, self.barcode_scanned, true, self);
        }, 1000);
      }
    });
    self.input.addEventListener('keypress', function(event) {

      /* istanbul ignore else */
      if (event.keyCode === 13 || event.keyCode === 0 || event.keyCode === 116) {
        return self.handle_event(event, self.barcode_scanned, true, self);
      }
    });
    return self.input.focus();
  };

  NHMobileBarcode.prototype.barcode_scanned = function(event, self) {

    /* istanbul ignore else */
    var dialog, input, url, url_meth;
    input = event.src_el;
    dialog = input.parentNode.parentNode;
    if (input.value === '') {
      return;
    }
    url = self.urls.json_patient_barcode(input.value.split(',')[1]);
    url_meth = url.method;
    return Promise.when(self.process_request(url_meth, url.url)).then(function(raw_data) {
      var activities_string, activity, content, data, i, len, ref, server_data;
      server_data = raw_data[0];
      data = server_data.data;
      activities_string = "";
      if (data.activities.length > 0) {
        activities_string = '<ul class="menu">';
        ref = data.activities;
        for (i = 0, len = ref.length; i < len; i++) {
          activity = ref[i];
          activities_string += '<li class="rightContent"><a href="' + self.urls.single_task(activity.id).url + '">' + activity.display_name + '<span class="aside">' + activity.time + '</span></a></li>';
        }
        activities_string += '</ul>';
      }
      content = self.render_patient_info(data, false, self) + '<h3>Tasks</h3>' + activities_string;
      return dialog.innerHTML = content;
    });
  };

  return NHMobileBarcode;

})(NHMobile);


/* istanbul ignore if */

if (!window.NH) {
  window.NH = {};
}


/* istanbul ignore else */

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobileBarcode = NHMobileBarcode;
}
