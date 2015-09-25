var NHLib,
  bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

NHLib = (function() {
  NHLib.date_format = '%Y-%m-%d H:M:S';

  function NHLib() {
    this.date_to_dob_string = bind(this.date_to_dob_string, this);
    this.date_to_string = bind(this.date_to_string, this);
    this.version = '0.0.1';
  }

  NHLib.prototype.date_from_string = function(date_string) {
    var date;
    date = new Date(date_string);
    if (isNaN(date.getTime())) {
      date = new Date(date_string.replace(' ', 'T'));
    }
    if (isNaN(date.getTime())) {
      throw new Error("Invalid date format");
    }
    return date;
  };

  NHLib.prototype.date_to_string = function(date) {
    if (isNaN(date.getTime())) {
      throw new Error("Invalid date format");
    }
    return date.getFullYear() + "-" + this.leading_zero(date.getMonth() + 1) + "-" + this.leading_zero(date.getDate()) + " " + this.leading_zero(date.getHours()) + ":" + this.leading_zero(date.getMinutes()) + ":" + this.leading_zero(date.getSeconds());
  };

  NHLib.prototype.date_to_dob_string = function(date) {
    if (isNaN(date.getTime())) {
      throw new Error("Invalid date format");
    }
    return date.getFullYear() + "-" + this.leading_zero(date.getMonth() + 1) + "-" + this.leading_zero(date.getDate());
  };

  NHLib.prototype.get_timestamp = function() {
    return Math.round(new Date().getTime() / 1000);
  };

  NHLib.prototype.leading_zero = function(date_element) {
    return ("0" + date_element).slice(-2);
  };

  return NHLib;

})();

if (!window.NH) {
  window.NH = {};
}

window.NH.NHLib = NHLib;

var NHMobile, Promise,
  slice = [].slice,
  bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty,
  indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

Promise = (function() {
  Promise.when = function() {
    var args, fn, i, len, num_uncompleted, promise, task, task_id, tasks;
    tasks = 1 <= arguments.length ? slice.call(arguments, 0) : [];
    num_uncompleted = tasks.length;
    args = new Array(num_uncompleted);
    promise = new Promise();
    fn = function(task_id) {
      return task.then(function() {
        args[task_id] = Array.prototype.slice.call(arguments);
        num_uncompleted--;
        if (num_uncompleted === 0) {
          return promise.complete.apply(promise, args);
        }
      });
    };
    for (task_id = i = 0, len = tasks.length; i < len; task_id = ++i) {
      task = tasks[task_id];
      fn(task_id);
    }
    return promise;
  };

  function Promise() {
    this.completed = false;
    this.callbacks = [];
  }

  Promise.prototype.complete = function() {
    var callback, i, len, ref, results;
    this.completed = true;
    this.data = arguments;
    ref = this.callbacks;
    results = [];
    for (i = 0, len = ref.length; i < len; i++) {
      callback = ref[i];
      results.push(callback.apply(callback, arguments));
    }
    return results;
  };

  Promise.prototype.then = function(callback) {
    if (this.completed === true) {
      callback.apply(callback, this.data);
      return;
    }
    return this.callbacks.push(callback);
  };

  return Promise;

})();

NHMobile = (function(superClass) {
  extend(NHMobile, superClass);

  NHMobile.prototype.process_request = function(verb, resource, data) {
    var promise, req;
    promise = new Promise();
    req = new XMLHttpRequest();
    req.addEventListener('readystatechange', function() {
      var btn, msg, ref, successResultCodes;
      if (req.readyState === 4) {
        successResultCodes = [200, 304];
        if (ref = req.status, indexOf.call(successResultCodes, ref) >= 0) {
          data = eval('[' + req.responseText + ']');
          return promise.complete(data);
        } else {
          btn = '<a href="#" data-action="close" ' + 'data-target="data_error">Ok</a>';
          msg = '<div class="block">The server returned an error ' + 'while processing the request. Please check your ' + 'input and resubmit</div>';
          new NHModal('data_error', 'Error while processing request', msg, [btn], 0, document.getElementsByTagName('body')[0]);
          return promise.complete(false);
        }
      }
    });
    req.open(verb, resource, true);
    if (data) {
      req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
      req.send(data);
    } else {
      req.send();
    }
    return promise;
  };

  function NHMobile() {
    this.get_patient_info = bind(this.get_patient_info, this);
    this.call_resource = bind(this.call_resource, this);
    var self;
    this.urls = frontend_routes;
    self = this;
    NHMobile.__super__.constructor.call(this);
  }

  NHMobile.prototype.call_resource = function(url_object, data) {
    return this.process_request(url_object.method, url_object.url, data);
  };

  NHMobile.prototype.render_patient_info = function(patient, nameless, self) {
    var patientDOB, patient_info;
    patient_info = '';
    if (!nameless) {
      if (patient.full_name) {
        patient_info += '<dt>Name:</dt><dd>' + patient.full_name + '</dd>';
      }
      if (patient.gender) {
        patient_info += '<dt>Gender:</dt><dd>' + patient.gender + '</dd>';
      }
    }
    if (patient.dob) {
      patientDOB = self.date_from_string(patient.dob);
      patient_info += '<dt>DOB:</dt><dd>' + self.date_to_dob_string(patientDOB) + '</dd>';
    }
    if (patient.location) {
      patient_info += '<dt>Location:</dt><dd>' + patient.location;
    }
    if (patient.parent_location) {
      patient_info += ',' + patient.parent_location + '</dd>';
    } else {
      patient_info += '</dd>';
    }
    if (patient.ews_score) {
      patient_info += '<dt class="twoline">Latest Score:</dt>' + '<dd class="twoline">' + patient.ews_score + '</dd>';
    }
    if (patient.ews_trend) {
      patient_info += '<dt>NEWS Trend:</dt><dd>' + patient.ews_trend + '</dd>';
    }
    if (patient.other_identifier) {
      patient_info += '<dt>Hospital ID:</dt><dd>' + patient.other_identifier + '</dd>';
    }
    if (patient.patient_identifier) {
      patient_info += '<dt>NHS Number:</dt><dd>' + patient.patient_identifier + '</dd>';
    }
    return '<dl>' + patient_info + '</dl>';
  };

  NHMobile.prototype.get_patient_info = function(patient_id, self) {
    var patient_url;
    patient_url = this.urls.json_patient_info(patient_id).url;
    Promise.when(this.process_request('GET', patient_url)).then(function(server_data) {
      var cancel, data, fullscreen, patient_details, patient_name;
      data = server_data[0][0];
      patient_name = '';
      patient_details = '';
      if (data.full_name) {
        patient_name += ' ' + data.full_name;
      }
      if (data.gender) {
        patient_name += '<span class="alignright">' + data.gender + '</span>';
      }
      patient_details = self.render_patient_info(data, true, self) + '<p><a href="' + self.urls['single_patient'](patient_id).url + '" id="patient_obs_fullscreen" class="button patient_obs">' + 'View Patient Observation Data</a></p>';
      cancel = '<a href="#" data-target="patient_info" ' + 'data-action="close">Cancel</a>';
      new NHModal('patient_info', patient_name, patient_details, [cancel], 0, document.getElementsByTagName('body')[0]);
      fullscreen = document.getElementById('patient_obs_fullscreen');
      return fullscreen.addEventListener('click', function(event) {
        if (!event.handled) {
          self.fullscreen_patient_info(event, self);
          return event.handled = true;
        }
      });
    });
    return true;
  };

  NHMobile.prototype.fullscreen_patient_info = function(event, self) {
    var container, options, options_close, page, target_el;
    event.preventDefault();
    if (!event.handled) {
      target_el = event.srcElement ? event.srcElement : event.target;
      container = document.createElement('div');
      container.setAttribute('class', 'full-modal');
      options = document.createElement('p');
      options_close = document.createElement('a');
      options_close.setAttribute('href', '#');
      options_close.setAttribute('id', 'closeFullModal');
      options_close.innerText = 'Close popup';
      options_close.addEventListener('click', function(event) {
        if (!event.handled) {
          self.close_fullscreen_patient_info(event);
          return event.handled = true;
        }
      });
      options.appendChild(options_close);
      container.appendChild(options);
      page = document.createElement('iframe');
      page.setAttribute('src', target_el.getAttribute('href'));
      page.onload = function() {
        var contents, header, iframe, modal, obs, ref, ref1;
        modal = document.getElementsByClassName('full-modal')[0];
        iframe = modal.getElementsByTagName('iframe')[0];
        contents = iframe.contentDocument ? iframe.contentDocument : iframe.contentWindow.document;
        header = contents != null ? (ref = contents.getElementsByClassName('header')) != null ? ref[0] : void 0 : void 0;
        if (header != null) {
          header.parentNode.removeChild(header);
        }
        obs = contents != null ? (ref1 = contents.getElementsByClassName('obs')) != null ? ref1[0] : void 0 : void 0;
        return obs != null ? obs.parentNode.removeChild(obs) : void 0;
      };
      container.appendChild(page);
      document.getElementsByTagName('body')[0].appendChild(container);
      return event.handled = true;
    }
  };

  NHMobile.prototype.close_fullscreen_patient_info = function(event) {
    var body;
    event.preventDefault();
    if (!event.handled) {
      body = document.getElementsByTagName('body')[0];
      body.removeChild(document.getElementsByClassName('full-modal')[0]);
      return event.handled = true;
    }
  };

  return NHMobile;

})(NHLib);

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobile = NHMobile;
}

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
    if (!event.handled) {
      input = event.srcElement ? event.srcElement : event.target;
      dialog = input.parentNode.parentNode;
      if (input.value === '') {
        return;
      }
      url = self.urls.json_patient_barcode(input.value.split(',')[1]);
      url_meth = url.method;
      return Promise.when(self.process_request(url_meth, url.url)).then(function(server_data) {
        var activities_string, activity, content, data, i, len, ref;
        data = server_data[0][0];
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
        dialog.innerHTML = content;
        return event.handled = true;
      });
    }
  };

  return NHMobileBarcode;

})(NHMobile);

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobileBarcode = NHMobileBarcode;
}

var NHMobileForm,
  bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

NHMobileForm = (function(superClass) {
  extend(NHMobileForm, superClass);

  function NHMobileForm() {
    this.cancel_notification = bind(this.cancel_notification, this);
    this.submit_observation = bind(this.submit_observation, this);
    this.display_partial_reasons = bind(this.display_partial_reasons, this);
    this.show_reference = bind(this.show_reference, this);
    this.submit = bind(this.submit, this);
    this.trigger_actions = bind(this.trigger_actions, this);
    this.validate = bind(this.validate, this);
    var ptn_name, ref, self;
    this.form = (ref = document.getElementsByTagName('form')) != null ? ref[0] : void 0;
    this.form_timeout = 240 * 1000;
    ptn_name = document.getElementById('patientName');
    this.patient_name_el = ptn_name.getElementsByTagName('a')[0];
    this.patient_name = function() {
      return this.patient_name_el.text;
    };
    self = this;
    this.setup_event_listeners(self);
    NHMobileForm.__super__.constructor.call(this);
  }

  NHMobileForm.prototype.setup_event_listeners = function(self) {
    var fn, i, input, len, ref;
    ref = self.form.elements;
    fn = function() {
      switch (input.localName) {
        case 'input':
          switch (input.getAttribute('type')) {
            case 'number':
              input.addEventListener('change', self.validate);
              return input.addEventListener('change', self.trigger_actions);
            case 'submit':
              return input.addEventListener('click', self.submit);
            case 'reset':
              return input.addEventListener('click', self.cancel_notification);
            case 'radio':
              return input.addEventListener('click', self.trigger_actions);
            case 'text':
              input.addEventListener('change', self.validate);
              return input.addEventListener('change', self.trigger_actions);
          }
          break;
        case 'select':
          return input.addEventListener('change', self.trigger_actions);
        case 'button':
          return input.addEventListener('click', self.show_reference);
      }
    };
    for (i = 0, len = ref.length; i < len; i++) {
      input = ref[i];
      fn();
    }
    document.addEventListener('form_timeout', function(event) {
      var task_id;
      task_id = self.form.getAttribute('task-id');
      if (task_id) {
        return self.handle_timeout(self, task_id);
      }
    });
    window.timeout_func = function() {
      var timeout;
      timeout = document.createEvent('CustomEvent');
      timeout.initCustomEvent('form_timeout', false, true, {
        'detail': 'form timed out'
      });
      return document.dispatchEvent(timeout);
    };
    window.form_timeout = setTimeout(window.timeout_func, self.form_timeout);
    document.addEventListener('post_score_submit', function(event) {
      if (!event.handled) {
        self.process_post_score_submit(self, event);
        return event.handled = true;
      }
    });
    document.addEventListener('partial_submit', function(event) {
      if (!event.handled) {
        self.process_partial_submit(self, event);
        return event.handled = true;
      }
    });
    return this.patient_name_el.addEventListener('click', function(event) {
      var can_btn, patient_id;
      event.preventDefault();
      input = event.srcElement ? event.srcElement : event.target;
      patient_id = input.getAttribute('patient-id');
      if (patient_id) {
        return self.get_patient_info(patient_id, self);
      } else {
        can_btn = '<a href="#" data-action="close" ' + 'data-target="patient_info_error">Cancel</a>';
        return new window.NH.NHModal('patient_info_error', 'Error getting patient information', '', [can_btn], 0, document.getElementsByTagName('body')[0]);
      }
    });
  };

  NHMobileForm.prototype.validate = function(event) {
    var cond, crit_target, crit_val, criteria, criterias, i, input, input_type, len, max, min, operator, other_input, other_input_value, regex_res, target_input, target_input_value, value;
    event.preventDefault();
    this.reset_form_timeout(this);
    input = event.srcElement ? event.srcElement : event.target;
    input_type = input.getAttribute('type');
    value = input_type === 'number' ? parseFloat(input.value) : input.value;
    this.reset_input_errors(input);
    if (typeof value !== 'undefined' && value !== '') {
      if (input.getAttribute('type') === 'number' && !isNaN(value)) {
        min = parseFloat(input.getAttribute('min'));
        max = parseFloat(input.getAttribute('max'));
        if (input.getAttribute('step') === '1' && value % 1 !== 0) {
          this.add_input_errors(input, 'Must be whole number');
          return;
        }
        if (value < min) {
          this.add_input_errors(input, 'Input too low');
          return;
        }
        if (value > max) {
          this.add_input_errors(input, 'Input too high');
          return;
        }
        if (input.getAttribute('data-validation')) {
          criterias = eval(input.getAttribute('data-validation'));
          for (i = 0, len = criterias.length; i < len; i++) {
            criteria = criterias[i];
            crit_target = criteria['condition']['target'];
            crit_val = criteria['condition']['value'];
            target_input = document.getElementById(crit_target);
            target_input_value = target_input != null ? target_input.value : void 0;
            other_input = document.getElementById(crit_val);
            other_input_value = other_input != null ? other_input.value : void 0;
            operator = criteria['condition']['operator'];
            if ((target_input != null ? target_input.getAttribute('type') : void 0) === 'number') {
              other_input_value = parseFloat(other_input_value);
            }
            cond = target_input_value + ' ' + operator + ' ' + other_input_value;
            if (eval(cond)) {
              this.reset_input_errors(other_input);
              continue;
            }
            if (typeof other_input_value !== 'undefined' && !isNaN(other_input_value) && other_input_value !== '') {
              this.add_input_errors(target_input, criteria['message']['target']);
              this.add_input_errors(other_input, criteria['message']['value']);
              continue;
            } else {
              this.add_input_errors(target_input, criteria['message']['target']);
              this.add_input_errors(other_input, 'Please enter a value');
              continue;
            }
          }
        }
      }
      if (input.getAttribute('type') === 'text') {
        if (input.getAttribute('pattern')) {
          regex_res = input.validity.patternMismatch;
          if (regex_res) {
            this.add_input_errors(input, 'Invalid value');
          }
        }
      }
    }
  };

  NHMobileForm.prototype.trigger_actions = function(event) {
    var action, actions, condition, conditions, el, field, i, input, j, k, l, len, len1, len2, len3, len4, len5, len6, len7, m, mode, n, o, p, ref, ref1, ref2, ref3, ref4, ref5, ref6, ref7, ref8, ref9, value;
    this.reset_form_timeout(this);
    input = event.srcElement ? event.srcElement : event.target;
    value = input.value;
    if (input.getAttribute('type') === 'radio') {
      ref = document.getElementsByName(input.name);
      for (i = 0, len = ref.length; i < len; i++) {
        el = ref[i];
        if (el.value !== value) {
          el.classList.add('exclude');
        } else {
          el.classList.remove('exclude');
        }
      }
    }
    if (value === '') {
      value = 'Default';
    }
    if (input.getAttribute('data-onchange')) {
      actions = eval(input.getAttribute('data-onchange'));
      for (j = 0, len1 = actions.length; j < len1; j++) {
        action = actions[j];
        ref1 = action['condition'];
        for (k = 0, len2 = ref1.length; k < len2; k++) {
          condition = ref1[k];
          if (((ref2 = condition[0]) !== 'True' && ref2 !== 'False') && typeof condition[0] === 'string') {
            condition[0] = 'document.getElementById("' + condition[0] + '").value';
          }
          if (((ref3 = condition[2]) !== 'True' && ref3 !== 'False') && typeof condition[2] === 'string' && condition[2] !== '') {
            condition[2] = 'document.getElementById("' + condition[2] + '").value';
          }
          if ((ref4 = condition[2]) === 'True' || ref4 === 'False' || ref4 === '') {
            condition[2] = "'" + condition[2] + "'";
          }
        }
        mode = ' && ';
        conditions = [];
        ref5 = action['condition'];
        for (l = 0, len3 = ref5.length; l < len3; l++) {
          condition = ref5[l];
          if (typeof condition === 'object') {
            conditions.push(condition.join(' '));
          } else {
            mode = condition;
          }
        }
        conditions = conditions.join(mode);
        if (eval(conditions)) {
          if (action['action'] === 'hide') {
            ref6 = action['fields'];
            for (m = 0, len4 = ref6.length; m < len4; m++) {
              field = ref6[m];
              this.hide_triggered_elements(field);
            }
          }
          if (action['action'] === 'show') {
            ref7 = action['fields'];
            for (n = 0, len5 = ref7.length; n < len5; n++) {
              field = ref7[n];
              this.show_triggered_elements(field);
            }
          }
          if (action['action'] === 'disable') {
            ref8 = action['fields'];
            for (o = 0, len6 = ref8.length; o < len6; o++) {
              field = ref8[o];
              this.disable_triggered_elements(field);
            }
          }
          if (action['action'] === 'enable') {
            ref9 = action['fields'];
            for (p = 0, len7 = ref9.length; p < len7; p++) {
              field = ref9[p];
              this.enable_triggered_elements(field);
            }
          }
        }
      }
    }
  };

  NHMobileForm.prototype.submit = function(event) {
    var action_buttons, ajax_act, btn, button, element, empty_elements, form_elements, i, invalid_elements, j, len, len1, msg;
    event.preventDefault();
    this.reset_form_timeout(this);
    ajax_act = this.form.getAttribute('ajax-action');
    form_elements = (function() {
      var i, len, ref, results;
      ref = this.form.elements;
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        element = ref[i];
        if (!element.classList.contains('exclude')) {
          results.push(element);
        }
      }
      return results;
    }).call(this);
    invalid_elements = (function() {
      var i, len, results;
      results = [];
      for (i = 0, len = form_elements.length; i < len; i++) {
        element = form_elements[i];
        if (element.classList.contains('error')) {
          results.push(element);
        }
      }
      return results;
    })();
    empty_elements = (function() {
      var i, len, results;
      results = [];
      for (i = 0, len = form_elements.length; i < len; i++) {
        element = form_elements[i];
        if (!element.value || element.value === '') {
          results.push(element);
        }
      }
      return results;
    })();
    if (invalid_elements.length < 1 && empty_elements.length < 1) {
      action_buttons = (function() {
        var i, len, ref, ref1, results;
        ref = this.form.elements;
        results = [];
        for (i = 0, len = ref.length; i < len; i++) {
          element = ref[i];
          if ((ref1 = element.getAttribute('type')) === 'submit' || ref1 === 'reset') {
            results.push(element);
          }
        }
        return results;
      }).call(this);
      for (i = 0, len = action_buttons.length; i < len; i++) {
        button = action_buttons[i];
        button.setAttribute('disabled', 'disabled');
      }
      return this.submit_observation(this, form_elements, this.form.getAttribute('ajax-action'), this.form.getAttribute('ajax-args'));
    } else if (empty_elements.length > 0 && ajax_act.indexOf('notification') > 0) {
      msg = '<p>The form contains empty fields, please enter ' + 'data into these fields and resubmit</p>';
      btn = '<a href="#" data-action="close" data-target="invalid_form">' + 'Cancel</a>';
      return new window.NH.NHModal('invalid_form', 'Form contains empty fields', msg, [btn], 0, this.form);
    } else if (invalid_elements.length > 0) {
      msg = '<p>The form contains errors, please correct ' + 'the errors and resubmit</p>';
      btn = '<a href="#" data-action="close" data-target="invalid_form">' + 'Cancel</a>';
      return new window.NH.NHModal('invalid_form', 'Form contains errors', msg, [btn], 0, this.form);
    } else {
      action_buttons = (function() {
        var j, len1, ref, ref1, results;
        ref = this.form.elements;
        results = [];
        for (j = 0, len1 = ref.length; j < len1; j++) {
          element = ref[j];
          if ((ref1 = element.getAttribute('type')) === 'submit' || ref1 === 'reset') {
            results.push(element);
          }
        }
        return results;
      }).call(this);
      for (j = 0, len1 = action_buttons.length; j < len1; j++) {
        button = action_buttons[j];
        button.setAttribute('disabled', 'disabled');
      }
      return this.display_partial_reasons(this);
    }
  };

  NHMobileForm.prototype.show_reference = function(event) {
    var btn, iframe, img, input, ref_title, ref_type, ref_url;
    event.preventDefault();
    this.reset_form_timeout(this);
    input = event.srcElement ? event.srcElement : event.target;
    ref_type = input.getAttribute('data-type');
    ref_url = input.getAttribute('data-url');
    ref_title = input.getAttribute('data-title');
    if (ref_type === 'image') {
      img = '<img src="' + ref_url + '"/>';
      btn = '<a href="#" data-action="close" data-target="popup_image">' + 'Cancel</a>';
      new window.NH.NHModal('popup_image', ref_title, img, [btn], 0, this.form);
    }
    if (ref_type === 'iframe') {
      iframe = '<iframe src="' + ref_url + '"></iframe>';
      btn = '<a href="#" data-action="close" data-target="popup_iframe">' + 'Cancel</a>';
      return new window.NH.NHModal('popup_iframe', ref_title, iframe, [btn], 0, this.form);
    }
  };

  NHMobileForm.prototype.display_partial_reasons = function(self) {
    var form_type;
    form_type = self.form.getAttribute('data-source');
    return Promise.when(this.call_resource(this.urls.json_partial_reasons())).then(function(data) {
      var can_btn, con_btn, i, len, msg, option, option_name, option_val, options, ref, select;
      options = '';
      ref = data[0][0];
      for (i = 0, len = ref.length; i < len; i++) {
        option = ref[i];
        option_val = option[0];
        option_name = option[1];
        options += '<option value="' + option_val + '">' + option_name + '</option>';
      }
      select = '<select name="partial_reason">' + options + '</select>';
      con_btn = form_type === 'task' ? '<a href="#" ' + 'data-target="partial_reasons" data-action="partial_submit" ' + 'data-ajax-action="json_task_form_action">Confirm</a>' : '<a href="#" data-target="partial_reasons" ' + 'data-action="partial_submit" ' + 'data-ajax-action="json_patient_form_action">Confirm</a>';
      can_btn = '<a href="#" data-action="renable" ' + 'data-target="partial_reasons">Cancel</a>';
      msg = '<p>Please state reason for ' + 'submitting partial observation</p>';
      return new window.NH.NHModal('partial_reasons', 'Submit partial observation', msg + select, [can_btn, con_btn], 0, self.form);
    });
  };

  NHMobileForm.prototype.submit_observation = function(self, elements, endpoint, args) {
    var el, serialised_string, url;
    serialised_string = ((function() {
      var i, len, results;
      results = [];
      for (i = 0, len = elements.length; i < len; i++) {
        el = elements[i];
        results.push(el.name + '=' + el.value);
      }
      return results;
    })()).join("&");
    url = this.urls[endpoint].apply(this, args.split(','));
    return Promise.when(this.call_resource(url, serialised_string)).then(function(server_data) {
      var act_btn, action_buttons, body, btn, button, buttons, can_btn, cls, data, element, i, j, len, len1, os, pos, ref, rt_url, st_url, sub_ob, task, task_list, tasks, title, triggered_tasks;
      data = server_data[0][0];
      body = document.getElementsByTagName('body')[0];
      if (data && data.status === 3) {
        can_btn = '<a href="#" data-action="renable" ' + 'data-target="submit_observation">Cancel</a>';
        act_btn = '<a href="#" data-target="submit_observation" ' + 'data-action="submit" data-ajax-action="' + data.modal_vals['next_action'] + '">Submit</a>';
        new window.NH.NHModal('submit_observation', data.modal_vals['title'] + ' for ' + self.patient_name() + '?', data.modal_vals['content'], [can_btn, act_btn], 0, body);
        if ('clinical_risk' in data.score) {
          sub_ob = document.getElementById('submit_observation');
          cls = 'clinicalrisk-' + data.score['clinical_risk'].toLowerCase();
          return sub_ob.classList.add(cls);
        }
      } else if (data && data.status === 1) {
        triggered_tasks = '';
        buttons = ['<a href="' + self.urls['task_list']().url + '" data-action="confirm">Go to My Tasks</a>'];
        if (data.related_tasks.length === 1) {
          triggered_tasks = '<p>' + data.related_tasks[0].summary + '</p>';
          rt_url = self.urls['single_task'](data.related_tasks[0].id).url;
          buttons.push('<a href="' + rt_url + '">Confirm</a>');
        } else if (data.related_tasks.length > 1) {
          tasks = '';
          ref = data.related_tasks;
          for (i = 0, len = ref.length; i < len; i++) {
            task = ref[i];
            st_url = self.urls['single_task'](task.id).url;
            tasks += '<li><a href="' + st_url + '">' + task.summary + '</a></li>';
          }
          triggered_tasks = '<ul class="menu">' + tasks + '</ul>';
        }
        pos = '<p>Observation was submitted</p>';
        os = 'Observation successfully submitted';
        task_list = triggered_tasks ? triggered_tasks : pos;
        title = triggered_tasks ? 'Action required' : os;
        return new window.NH.NHModal('submit_success', title, task_list, buttons, 0, body);
      } else if (data && data.status === 4) {
        btn = '<a href="' + self.urls['task_list']().url + '" data-action="confirm" data-target="cancel_success">' + 'Go to My Tasks</a>';
        return new window.NH.NHModal('cancel_success', 'Task successfully cancelled', '', [btn], 0, self.form);
      } else {
        action_buttons = (function() {
          var j, len1, ref1, ref2, results;
          ref1 = self.form.elements;
          results = [];
          for (j = 0, len1 = ref1.length; j < len1; j++) {
            element = ref1[j];
            if ((ref2 = element.getAttribute('type')) === 'submit' || ref2 === 'reset') {
              results.push(element);
            }
          }
          return results;
        })();
        for (j = 0, len1 = action_buttons.length; j < len1; j++) {
          button = action_buttons[j];
          button.removeAttribute('disabled');
        }
        btn = '<a href="#" data-action="close" ' + 'data-target="submit_error">Cancel</a>';
        return new window.NH.NHModal('submit_error', 'Error submitting observation', 'Server returned an error', [btn], 0, body);
      }
    });
  };

  NHMobileForm.prototype.handle_timeout = function(self, id) {
    var can_id;
    can_id = self.urls['json_cancel_take_task'](id);
    return Promise.when(self.call_resource(can_id)).then(function(server_data) {

      /* Should be checking server data */
      var btn, msg;
      msg = '<p>Please pick the task again from the task list ' + 'if you wish to complete it</p>';
      btn = '<a href="' + self.urls['task_list']().url + '" data-action="confirm">Go to My Tasks</a>';
      return new window.NH.NHModal('form_timeout', 'Task window expired', msg, [btn], 0, document.getElementsByTagName('body')[0]);
    });
  };

  NHMobileForm.prototype.cancel_notification = function(self) {
    var opts;
    opts = this.urls.ajax_task_cancellation_options();
    return Promise.when(this.call_resource(opts)).then(function(data) {
      var can_btn, con_btn, i, len, msg, option, option_name, option_val, options, ref, select;
      options = '';
      ref = data[0][0];
      for (i = 0, len = ref.length; i < len; i++) {
        option = ref[i];
        option_val = option.id;
        option_name = option.name;
        options += '<option value="' + option_val + '">' + option_name + '</option>';
      }
      select = '<select name="reason">' + options + '</select>';
      msg = '<p>Please state reason for cancelling task</p>';
      can_btn = '<a href="#" data-action="close" ' + 'data-target="cancel_reasons">Cancel</a>';
      con_btn = '<a href="#" data-target="cancel_reasons" ' + 'data-action="partial_submit" ' + 'data-ajax-action="cancel_clinical_notification">Confirm</a>';
      return new window.NH.NHModal('cancel_reasons', 'Cancel task', msg + select, [can_btn, con_btn], 0, document.getElementsByTagName('form')[0]);
    });
  };

  NHMobileForm.prototype.reset_form_timeout = function(self) {
    clearTimeout(window.form_timeout);
    return window.form_timeout = setTimeout(window.timeout_func, self.form_timeout);
  };

  NHMobileForm.prototype.reset_input_errors = function(input) {
    var container_el, error_el;
    container_el = input.parentNode.parentNode;
    error_el = container_el.getElementsByClassName('errors')[0];
    container_el.classList.remove('error');
    input.classList.remove('error');
    return error_el.innerHTML = '';
  };

  NHMobileForm.prototype.add_input_errors = function(input, error_string) {
    var container_el, error_el;
    container_el = input.parentNode.parentNode;
    error_el = container_el.getElementsByClassName('errors')[0];
    container_el.classList.add('error');
    input.classList.add('error');
    return error_el.innerHTML = '<label for="' + input.name + '" class="error">' + error_string + '</label>';
  };

  NHMobileForm.prototype.hide_triggered_elements = function(field) {
    var el, inp;
    el = document.getElementById('parent_' + field);
    el.style.display = 'none';
    inp = document.getElementById(field);
    return inp.classList.add('exclude');
  };

  NHMobileForm.prototype.show_triggered_elements = function(field) {
    var el, inp;
    el = document.getElementById('parent_' + field);
    el.style.display = 'block';
    inp = document.getElementById(field);
    return inp.classList.remove('exclude');
  };

  NHMobileForm.prototype.disable_triggered_elements = function(field) {
    var inp;
    inp = document.getElementById(field);
    inp.classList.add('exclude');
    return inp.disabled = true;
  };

  NHMobileForm.prototype.enable_triggered_elements = function(field) {
    var inp;
    inp = document.getElementById(field);
    inp.classList.remove('exclude');
    return inp.disabled = false;
  };

  NHMobileForm.prototype.process_partial_submit = function(self, event) {
    var cancel_reason, cover, dialog_id, element, form_elements, reason, reason_to_use;
    form_elements = (function() {
      var i, len, ref, results;
      ref = self.form.elements;
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        element = ref[i];
        if (!element.classList.contains('exclude')) {
          results.push(element);
        }
      }
      return results;
    })();
    reason_to_use = false;
    reason = document.getElementsByName('partial_reason')[0];
    cancel_reason = document.getElementsByName('reason')[0];
    if (reason) {
      reason_to_use = reason;
    }
    if (cancel_reason) {
      reason_to_use = cancel_reason;
    }
    if (reason_to_use) {
      form_elements.push(reason_to_use);
      self.submit_observation(self, form_elements, event.detail.action, self.form.getAttribute('ajax-args'));
      dialog_id = document.getElementById(event.detail.target);
      cover = document.getElementById('cover');
      document.getElementsByTagName('body')[0].removeChild(cover);
      return dialog_id.parentNode.removeChild(dialog_id);
    }
  };

  NHMobileForm.prototype.process_post_score_submit = function(self, event) {
    var element, endpoint, form, form_elements, ref;
    form = (ref = document.getElementsByTagName('form')) != null ? ref[0] : void 0;
    form_elements = (function() {
      var i, len, ref1, results;
      ref1 = form.elements;
      results = [];
      for (i = 0, len = ref1.length; i < len; i++) {
        element = ref1[i];
        if (!element.classList.contains('exclude')) {
          results.push(element);
        }
      }
      return results;
    })();
    endpoint = event.detail.endpoint;
    return self.submit_observation(self, form_elements, endpoint, self.form.getAttribute('ajax-args'));
  };

  return NHMobileForm;

})(NHMobile);

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobileForm = NHMobileForm;
}

var NHMobilePatient,
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

NHMobilePatient = (function(superClass) {
  extend(NHMobilePatient, superClass);

  function NHMobilePatient() {
    var data_id, i, len, obs, obs_menu, self, tab, table_view, tabs, tabs_el;
    self = this;
    NHMobilePatient.__super__.constructor.call(this);
    obs_menu = document.getElementById('obsMenu');
    obs_menu.style.display = 'none';
    table_view = document.getElementById('table-content');
    table_view.style.display = 'none';
    obs = document.getElementsByClassName('obs');
    if (obs && obs.length > 0) {
      obs[0].addEventListener('click', this.show_obs_menu);
    }
    tabs_el = document.getElementsByClassName('tabs');
    tabs = tabs_el[0].getElementsByTagName('a');
    for (i = 0, len = tabs.length; i < len; i++) {
      tab = tabs[i];
      tab.addEventListener('click', this.handle_tabs);
    }
    data_id = document.getElementById('graph-content').getAttribute('data-id');
    Promise.when(this.call_resource(this.urls['ajax_get_patient_obs'](data_id))).then(function(server_data) {
      return self.draw_graph(self, server_data);
    });
  }

  NHMobilePatient.prototype.handle_tabs = function(event) {
    var i, len, tab, tab_target, tabs, target_el;
    event.preventDefault();
    if (!event.handled) {
      tabs = document.getElementsByClassName('tabs')[0].getElementsByTagName('a');
      for (i = 0, len = tabs.length; i < len; i++) {
        tab = tabs[i];
        tab.classList.remove('selected');
      }
      document.getElementById('graph-content').style.display = 'none';
      document.getElementById('table-content').style.display = 'none';
      target_el = event.srcElement ? event.srcElement : event.target;
      target_el.classList.add('selected');
      tab_target = target_el.getAttribute('href').replace('#', '');
      document.getElementById(tab_target).style.display = 'block';
      return event.handled = true;
    }
  };

  NHMobilePatient.prototype.show_obs_menu = function(event) {
    var body, menu, obs_menu;
    event.preventDefault();
    obs_menu = document.getElementById('obsMenu');
    body = document.getElementsByTagName('body')[0];
    menu = '<ul class="menu">' + obs_menu.innerHTML + '</ul>';
    return new NHModal('obs_menu', 'Pick an observation for ', menu, ['<a href="#" data-action="close" data-target="obs_menu">Cancel</a>'], 0, body);
  };

  NHMobilePatient.prototype.draw_graph = function(self, server_data) {
    var bp_graph, c, chart, context, controls, element_for_chart, f, focus, fr, graph_content, graph_tabs, i, len, ob, obs, oxy_graph, pulse_graph, resp_rate_graph, score_graph, svg, tabular_obs, temp_graph;
    element_for_chart = 'chart';
    obs = server_data[0][0].obs.reverse();
    if (obs.length > 0) {
      svg = new window.NH.NHGraphLib('#' + element_for_chart);
      resp_rate_graph = new window.NH.NHGraph();
      resp_rate_graph.options.keys = ['respiration_rate'];
      resp_rate_graph.options.label = 'RR';
      resp_rate_graph.options.measurement = '/min';
      resp_rate_graph.axes.y.min = 0;
      resp_rate_graph.axes.y.max = 40;
      resp_rate_graph.options.normal.min = 12;
      resp_rate_graph.options.normal.max = 20;
      resp_rate_graph.style.dimensions.height = 250;
      resp_rate_graph.style.data_style = 'linear';
      resp_rate_graph.style.label_width = 60;
      resp_rate_graph.drawables.background.data = [
        {
          "class": "red",
          s: 0,
          e: 9
        }, {
          "class": "green",
          s: 9,
          e: 12
        }, {
          "class": "amber",
          s: 21,
          e: 25
        }, {
          "class": "red",
          s: 25,
          e: 60
        }
      ];
      oxy_graph = new window.NH.NHGraph();
      oxy_graph.options.keys = ['indirect_oxymetry_spo2'];
      oxy_graph.options.label = 'Spo2';
      oxy_graph.options.measurement = '%';
      oxy_graph.axes.y.min = 70;
      oxy_graph.axes.y.max = 100;
      oxy_graph.options.normal.min = 96;
      oxy_graph.options.normal.max = 100;
      oxy_graph.style.dimensions.height = 200;
      oxy_graph.style.axis.x.hide = true;
      oxy_graph.style.data_style = 'linear';
      oxy_graph.style.label_width = 60;
      oxy_graph.drawables.background.data = [
        {
          "class": "red",
          s: 0,
          e: 92
        }, {
          "class": "amber",
          s: 92,
          e: 94
        }, {
          "class": "green",
          s: 94,
          e: 96
        }
      ];
      temp_graph = new window.NH.NHGraph();
      temp_graph.options.keys = ['body_temperature'];
      temp_graph.options.label = 'Temp';
      temp_graph.options.measurement = '°C';
      temp_graph.axes.y.min = 25;
      temp_graph.axes.y.max = 45;
      temp_graph.options.normal.min = 36.1;
      temp_graph.options.normal.max = 38.1;
      temp_graph.style.dimensions.height = 200;
      temp_graph.style.axis.x.hide = true;
      temp_graph.style.data_style = 'linear';
      temp_graph.style.label_width = 60;
      temp_graph.drawables.background.data = [
        {
          "class": "red",
          s: 0,
          e: 35
        }, {
          "class": "amber",
          s: 35,
          e: 35.1
        }, {
          "class": "green",
          s: 35.1,
          e: 36.0
        }, {
          "class": "green",
          s: 38.1,
          e: 39.1
        }, {
          "class": "amber",
          s: 39.1,
          e: 50
        }
      ];
      pulse_graph = new window.NH.NHGraph();
      pulse_graph.options.keys = ['pulse_rate'];
      pulse_graph.options.label = 'HR';
      pulse_graph.options.measurement = '/min';
      pulse_graph.axes.y.min = 25;
      pulse_graph.axes.y.max = 200;
      pulse_graph.options.normal.min = 50;
      pulse_graph.options.normal.max = 91;
      pulse_graph.style.dimensions.height = 200;
      pulse_graph.style.axis.x.hide = true;
      pulse_graph.style.data_style = 'linear';
      pulse_graph.style.label_width = 60;
      pulse_graph.drawables.background.data = [
        {
          "class": "red",
          s: 0,
          e: 40
        }, {
          "class": "amber",
          s: 40,
          e: 41
        }, {
          "class": "green",
          s: 41,
          e: 50
        }, {
          "class": "green",
          s: 91,
          e: 111
        }, {
          "class": "amber",
          s: 111,
          e: 131
        }, {
          "class": "red",
          s: 131,
          e: 200
        }
      ];
      bp_graph = new window.NH.NHGraph();
      bp_graph.options.keys = ['blood_pressure_systolic', 'blood_pressure_diastolic'];
      bp_graph.options.label = 'BP';
      bp_graph.options.measurement = 'mmHg';
      bp_graph.axes.y.min = 30;
      bp_graph.axes.y.max = 260;
      bp_graph.options.normal.min = 150;
      bp_graph.options.normal.max = 151;
      bp_graph.style.dimensions.height = 200;
      bp_graph.style.axis.x.hide = true;
      bp_graph.style.data_style = 'range';
      bp_graph.style.label_width = 60;
      bp_graph.drawables.background.data = [
        {
          "class": "red",
          s: 0,
          e: 91
        }, {
          "class": "amber",
          s: 91,
          e: 101
        }, {
          "class": "green",
          s: 101,
          e: 111
        }, {
          "class": "red",
          s: 220,
          e: 260
        }
      ];
      score_graph = new window.NH.NHGraph();
      score_graph.options.keys = ['score'];
      score_graph.style.dimensions.height = 200;
      score_graph.style.data_style = 'stepped';
      score_graph.axes.y.min = 0;
      score_graph.axes.y.max = 22;
      score_graph.drawables.background.data = [
        {
          "class": "green",
          s: 1,
          e: 4
        }, {
          "class": "amber",
          s: 4,
          e: 6
        }, {
          "class": "red",
          s: 6,
          e: 22
        }
      ];
      score_graph.style.label_width = 60;
      tabular_obs = new window.NH.NHTable();
      tabular_obs.keys = [
        {
          key: 'avpu_text',
          title: 'AVPU'
        }, {
          key: 'oxygen_administration_device',
          title: 'On Supplemental O2'
        }, {
          key: 'inspired_oxygen',
          title: 'Inspired Oxygen'
        }
      ];
      tabular_obs.title = 'Tabular values';
      focus = new window.NH.NHFocus();
      context = new window.NH.NHContext();
      focus.graphs.push(resp_rate_graph);
      focus.graphs.push(oxy_graph);
      focus.graphs.push(temp_graph);
      focus.graphs.push(pulse_graph);
      focus.graphs.push(bp_graph);
      focus.tables.push(tabular_obs);
      focus.title = 'Individual values';
      focus.style.padding.right = 0;
      context.graph = score_graph;
      context.title = 'NEWS Score';
      svg.focus = focus;
      svg.context = context;
      svg.options.controls.date.start = document.getElementById('start_date');
      svg.options.controls.date.end = document.getElementById('end_date');
      svg.options.controls.time.start = document.getElementById('start_time');
      svg.options.controls.time.end = document.getElementById('end_time');
      svg.options.controls.rangify = document.getElementById('rangify');
      svg.table.element = '#table';
      svg.table.keys = [
        {
          title: 'NEWS Score',
          keys: ['score_display']
        }, {
          title: 'Respiration Rate',
          keys: ['respiration_rate']
        }, {
          title: 'O2 Saturation',
          keys: ['indirect_oxymetry_spo2']
        }, {
          title: 'Body Temperature',
          keys: ['body_temperature']
        }, {
          title: 'Blood Pressure Systolic',
          keys: ['blood_pressure_systolic']
        }, {
          title: 'Blood Pressure Diastolic',
          keys: ['blood_pressure_diastolic']
        }, {
          title: 'Pulse Rate',
          keys: ['pulse_rate']
        }, {
          title: 'AVPU',
          keys: ['avpu_text']
        }, {
          title: 'Patient on Supplemental O2',
          keys: ['oxygen_administration_flag']
        }, {
          title: 'Inspired Oxygen',
          keys: [
            {
              title: 'Flow Rate',
              keys: ['flow_rate']
            }, {
              title: 'Concentration',
              keys: ['concentration']
            }, {
              title: 'Device',
              keys: ['device_id']
            }, {
              title: 'CPAP PEEP',
              keys: ['cpap_peep']
            }, {
              title: 'NIV iPAP',
              keys: ['niv_ipap']
            }, {
              title: 'NIV ePAP',
              keys: ['niv_epap']
            }, {
              title: 'NIV Backup Rate',
              keys: ['niv_backup']
            }
          ]
        }
      ];
      for (i = 0, len = obs.length; i < len; i++) {
        ob = obs[i];
        ob.oxygen_administration_device = 'No';
        if (ob.oxygen_administration_flag) {
          ob.oxygen_administration_device = 'Yes';
        }
        fr = ob.flow_rate && ob.flow_rate > -1;
        c = ob.concentration && ob.concentration > -1;
        f = ob.oxygen_administration_flag;
        if (fr || c || f) {
          ob.inspired_oxygen = "";
          if (ob.device_id) {
            ob.inspired_oxygen += "<strong>Device:</strong> " + ob.device_id[1] + "<br>";
          }
          if (fr) {
            ob.inspired_oxygen += "<strong>Flow:</strong> " + ob.flow_rate + "l/hr<br>";
          }
          if (c) {
            ob.inspired_oxygen += "<strong>Concentration:</strong> " + ob.concentration + "%<br>";
          }
          if (ob.cpap_peep && ob.cpap_peep > -1) {
            ob.inspired_oxygen += "<strong>CPAP PEEP:</strong> " + ob.cpap_peep + "<br>";
          } else if (ob.niv_backup && ob.niv_backup > -1) {
            ob.inspired_oxygen += "<strong>NIV Backup Rate:</strong> " + ob.niv_backup + "<br>";
            ob.inspired_oxygen += "<strong>NIV EPAP:</strong> " + ob.niv_epap + "<br>";
            ob.inspired_oxygen += "<strong>NIV IPAP</strong>: " + ob.niv_ipap + "<br>";
          }
          if (ob.indirect_oxymetry_spo2) {
            ob.indirect_oxymetry_spo2_label = ob.indirect_oxymetry_spo2 + "%";
          }
        }
      }
      svg.data.raw = obs;
      svg.init();
      return svg.draw();
    } else {
      graph_content = document.getElementById('graph-content');
      controls = document.getElementById('controls');
      chart = document.getElementById(element_for_chart);
      graph_tabs = graph_content.parentNode.getElementsByClassName('tabs');
      controls.style.display = 'none';
      chart.innerHTML = '<h2>No observation data available for patient</h2>';
      return graph_tabs[0].style.display = 'none';
    }
  };

  return NHMobilePatient;

})(NHMobile);

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobilePatient = NHMobilePatient;
}

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
      msg = '<p>Please select patients to hand' + ' to another staff member</p>';
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
      claim_msg = '<p>Claim patients shared with colleagues</p>';
      btns = [assign_btn, can_btn];
      new window.NH.NHModal('claim_patients', 'Claim Patients?', claim_msg, btns, 0, self.form);
    } else {
      msg = '<p>Please select patients to claim back</p>';
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
          share_msg = '<p>Successfully shared patients with ' + data['shared_with'].join(', ') + '</p>';
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
        claim_msg = '<p>Successfully claimed patients</p>';
        btns = [can_btn];
        return new window.NH.NHModal('claim_success', 'Patients Claimed', claim_msg, btns, 0, body);
      } else {
        can_btn = '<a href="#" data-action="close" data-target="claim_error"' + '>Cancel</a>';
        claim_msg = '<p>There was an error claiming back your' + ' patients, please contact your Ward Manager</p>';
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

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobileShare = NHMobileShare;
}

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
        return new window.NH.NHModal('invite_success', 'Successfully accepted patients', '<p>Now following ' + data['count'] + ' patients from ' + data['user'] + '</p>', btns, 0, body);
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
        return new window.NH.NHModal('invite_error', 'Error accepting patients', '<p>There was an error accepting the invite to follow,' + 'Please try again</p>', btns, 0, body);
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
        return new window.NH.NHModal('reject_success', 'Successfully rejected patients', '<p>The invitation to follow ' + data['user'] + '\'s ' + 'patients was rejected</p>', btns, 0, body);
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
        return new window.NH.NHModal('reject_error', 'Error rejecting patients', '<p>There was an error rejecting the invite to follow,' + ' Please try again</p>', btns, 0, body);
      }
    });
  };

  return NHMobileShareInvite;

})(NHMobile);

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobileShareInvite = NHMobileShareInvite;
}

var NHModal;

NHModal = (function() {
  function NHModal(id1, title1, content1, options1, popupTime, el1) {
    var body, cover, dialog, self;
    this.id = id1;
    this.title = title1;
    this.content = content1;
    this.options = options1;
    this.popupTime = popupTime;
    this.el = el1;
    self = this;
    dialog = this.create_dialog(self, this.id, this.title, this.content, this.options);
    body = document.getElementsByTagName('body')[0];
    cover = document.createElement('div');
    cover.setAttribute('class', 'cover');
    cover.setAttribute('id', 'cover');
    cover.setAttribute('data-action', 'close');
    if (this.id === 'submit_observation') {
      cover.setAttribute('data-action', 'renable');
    }
    cover.setAttribute('data-target', this.id);
    cover.style.height = body.clientHeight + 'px';
    cover.addEventListener('click', self.handle_button_events);
    body.appendChild(cover);
    this.el.appendChild(dialog);
    this.calculate_dimensions(dialog, dialog.getElementsByClassName('dialogContent')[0], this.el);
  }

  NHModal.prototype.create_dialog = function(self, popup_id, popup_title, popup_content, popup_options) {
    var container, content, dialog_content, dialog_div, dialog_header, dialog_options, header, options;
    dialog_div = function(id) {
      var div;
      div = document.createElement('div');
      div.setAttribute('class', 'dialog');
      div.setAttribute('id', id);
      return div;
    };
    dialog_header = function(title) {
      var header;
      header = document.createElement('h2');
      header.innerHTML = title;
      return header;
    };
    dialog_content = function(message) {
      var content;
      content = document.createElement('div');
      content.setAttribute('class', 'dialogContent');
      content.innerHTML = message;
      return content;
    };
    dialog_options = function(self, buttons) {
      var button, fn, i, len, option_list;
      option_list = document.createElement('ul');
      switch (buttons.length) {
        case 1:
          option_list.setAttribute('class', 'options one-col');
          break;
        case 2:
          option_list.setAttribute('class', 'options two-col');
          break;
        case 3:
          option_list.setAttribute('class', 'options three-col');
      }
      fn = function(self) {
        var option_button, ref;
        option_button = document.createElement('li');
        option_button.innerHTML = button;
        if ((ref = option_button.getElementsByTagName('a')) != null) {
          ref[0].addEventListener('click', self.handle_button_events);
        }
        return option_list.appendChild(option_button);
      };
      for (i = 0, len = buttons.length; i < len; i++) {
        button = buttons[i];
        fn(self);
      }
      return option_list;
    };
    container = dialog_div(popup_id);
    header = dialog_header(popup_title);
    content = dialog_content(popup_content);
    options = dialog_options(self, popup_options);
    container.appendChild(header);
    container.appendChild(content);
    container.appendChild(options);
    return container;
  };

  NHModal.prototype.calculate_dimensions = function(dialog, dialog_content, el) {
    var available_space, margins, max_height, top_offset;
    margins = {
      top: 80,
      bottom: 300,
      right: 0,
      left: 0
    };
    available_space = function(dialog, el) {
      var dh, dhh, dialog_height, dopt, dopth, elh;
      dh = dialog.getElementsByTagName('h2');
      dhh = parseInt(document.defaultView.getComputedStyle(dh != null ? dh[0] : void 0, '').getPropertyValue('height').replace('px', ''));
      dopt = dialog.getElementsByClassName('options');
      dopth = parseInt(document.defaultView.getComputedStyle(dopt != null ? dopt[0] : void 0, '').getPropertyValue('height').replace('px', ''));
      elh = parseInt(document.defaultView.getComputedStyle(el, '').getPropertyValue('height').replace('px', ''));
      dialog_height = (dhh + dopth) + (margins.top + margins.bottom);
      if (elh > window.innerHeight) {
        return window.innerHeight - dialog_height;
      }
    };
    max_height = available_space(dialog, el);
    top_offset = el.offsetTop + margins.top;
    dialog.style.top = top_offset + 'px';
    dialog.style.display = 'inline-block';
    if (max_height) {
      dialog_content.style.maxHeight = max_height + 'px';
    }
  };

  NHModal.prototype.handle_button_events = function(event) {
    var accept_detail, accept_event, action_buttons, assign_detail, assign_event, button, claim_event, cover, data_action, data_target, dialog, dialog_form, dialog_id, el, element, form, forms, i, j, len, len1, nurses, reject_detail, reject_event, submit_detail, submit_event, target_el;
    event.preventDefault();
    if (!event.handled) {
      target_el = event.srcElement ? event.srcElement : event.target;
      data_target = target_el.getAttribute('data-target');
      data_action = target_el.getAttribute('data-ajax-action');
      switch (target_el.getAttribute('data-action')) {
        case 'close':
          dialog_id = document.getElementById(data_target);
          cover = document.getElementById('cover');
          document.getElementsByTagName('body')[0].removeChild(cover);
          dialog_id.parentNode.removeChild(dialog_id);
          break;
        case 'renable':
          forms = document.getElementsByTagName('form');
          for (i = 0, len = forms.length; i < len; i++) {
            form = forms[i];
            action_buttons = (function() {
              var j, len1, ref, ref1, results;
              ref = form.elements;
              results = [];
              for (j = 0, len1 = ref.length; j < len1; j++) {
                element = ref[j];
                if ((ref1 = element.getAttribute('type')) === 'submit' || ref1 === 'reset') {
                  results.push(element);
                }
              }
              return results;
            })();
            for (j = 0, len1 = action_buttons.length; j < len1; j++) {
              button = action_buttons[j];
              button.removeAttribute('disabled');
            }
          }
          dialog_id = document.getElementById(data_target);
          cover = document.getElementById('cover');
          document.getElementsByTagName('body')[0].removeChild(cover);
          dialog_id.parentNode.removeChild(dialog_id);
          break;
        case 'submit':
          submit_event = document.createEvent('CustomEvent');
          submit_detail = {
            'endpoint': target_el.getAttribute('data-ajax-action')
          };
          submit_event.initCustomEvent('post_score_submit', true, false, submit_detail);
          document.dispatchEvent(submit_event);
          dialog_id = document.getElementById(data_target);
          cover = document.getElementById('cover');
          document.getElementsByTagName('body')[0].removeChild(cover);
          dialog_id.parentNode.removeChild(dialog_id);
          break;
        case 'partial_submit':
          if (!event.handled) {
            submit_event = document.createEvent('CustomEvent');
            submit_detail = {
              'action': data_action,
              'target': data_target
            };
            submit_event.initCustomEvent('partial_submit', false, true, submit_detail);
            document.dispatchEvent(submit_event);
            event.handled = true;
          }
          break;
        case 'assign':
          dialog = document.getElementById(data_target);
          dialog_form = dialog.getElementsByTagName('form')[0];
          nurses = (function() {
            var k, len2, ref, results;
            ref = dialog_form.elements;
            results = [];
            for (k = 0, len2 = ref.length; k < len2; k++) {
              el = ref[k];
              if (el.checked) {
                results.push(el.value);
              }
            }
            return results;
          })();
          assign_event = document.createEvent('CustomEvent');
          assign_detail = {
            'action': data_action,
            'target': data_target,
            'nurses': nurses
          };
          assign_event.initCustomEvent('assign_nurse', false, true, assign_detail);
          document.dispatchEvent(assign_event);
          break;
        case 'claim':
          claim_event = document.createEvent('CustomEvent');
          claim_event.initCustomEvent('claim_patients', false, true, false);
          document.dispatchEvent(claim_event);
          break;
        case 'accept':
          accept_event = document.createEvent('CustomEvent');
          accept_detail = {
            'invite_id': target_el.getAttribute('data-invite-id')
          };
          accept_event.initCustomEvent('accept_invite', false, true, accept_detail);
          document.dispatchEvent(accept_event);
          break;
        case 'reject':
          reject_event = document.createEvent('CustomEvent');
          reject_detail = {
            'invite_id': target_el.getAttribute('data-invite-id')
          };
          reject_event.initCustomEvent('reject_invite', false, true, reject_detail);
          document.dispatchEvent(reject_event);
      }
      event.handled = true;
    }
  };

  return NHModal;

})();

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHModal = NHModal;
}
