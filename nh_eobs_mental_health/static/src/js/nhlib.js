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

  NHLib.prototype.handle_event = function(raw_e, func, pref_dev, raw_args) {
    var arg, args, i, len;
    if (!raw_e.handled) {
      raw_e.src_el = raw_e.srcElement ? raw_e.srcElement : raw_e.target;
      if (pref_dev) {
        raw_e.preventDefault();
      }
      args = [raw_e];
      if (typeof raw_args !== 'undefined') {
        if (!Array.isArray(raw_args)) {
          raw_args = [raw_args];
        }
        for (i = 0, len = raw_args.length; i < len; i++) {
          arg = raw_args[i];
          args.push(arg);
        }
      }
      func.apply(func, args);
      return raw_e.handled = true;
    }
  };

  return NHLib;

})();

if (!window.NH) {
  window.NH = {};
}

window.NH.NHLib = NHLib;

var NHMobile, NHMobileData, Promise,
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

NHMobileData = (function() {
  function NHMobileData(raw_data) {
    var self;
    this.status = raw_data.status;
    this.title = raw_data.title;
    this.desc = raw_data.description;
    this.data = raw_data.data;
    self = this;
  }

  return NHMobileData;

})();

NHMobile = (function(superClass) {
  extend(NHMobile, superClass);

  NHMobile.prototype.process_request = function(verb, resource, data) {
    var promise, req;
    promise = new Promise();
    req = new XMLHttpRequest();
    req.addEventListener('readystatechange', function() {
      var btn, mob_data, msg, ref, successResultCodes;
      if (req.readyState === 4) {
        successResultCodes = [200, 304];
        if (ref = req.status, indexOf.call(successResultCodes, ref) >= 0) {
          data = JSON.parse(req.responseText);
          mob_data = new NHMobileData(data);
          return promise.complete(mob_data);
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
    Promise.when(this.process_request('GET', patient_url)).then(function(raw_data) {
      var cancel, data, fullscreen, patient_details, patient_name, server_data;
      server_data = raw_data[0];
      data = server_data.data;
      patient_name = server_data.title;
      patient_details = '';
      if (data.gender) {
        patient_name += '<span class="alignright">' + data.gender + '</span>';
      }
      patient_details = self.render_patient_info(data, true, self) + '<p><a href="' + self.urls['single_patient'](patient_id).url + '" id="patient_obs_fullscreen" class="button big full-width do-it">' + 'View Patient Observation Data</a></p>';
      cancel = '<a href="#" data-target="patient_info" ' + 'data-action="close">Cancel</a>';
      new NHModal('patient_info', patient_name, patient_details, [cancel], 0, document.getElementsByTagName('body')[0]);
      fullscreen = document.getElementById('patient_obs_fullscreen');
      return fullscreen.addEventListener('click', function(event) {
        return self.handle_event(event, self.fullscreen_patient_info, true, self);
      });
    });
    return true;
  };

  NHMobile.prototype.fullscreen_patient_info = function(event, self) {
    var container, options, options_close, page, target_el;
    target_el = event.src_el;
    container = document.createElement('div');
    container.setAttribute('class', 'full-modal');
    options = document.createElement('p');
    options_close = document.createElement('a');
    options_close.setAttribute('href', '#');
    options_close.setAttribute('id', 'closeFullModal');
    options_close.innerText = 'Close popup';
    options_close.addEventListener('click', function(event) {
      return self.handle_event(event, self.close_fullscreen_patient_info, true);
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
    return document.getElementsByTagName('body')[0].appendChild(container);
  };

  NHMobile.prototype.close_fullscreen_patient_info = function(event) {
    var body;
    body = document.getElementsByTagName('body')[0];
    return body.removeChild(document.getElementsByClassName('full-modal')[0]);
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
      if (event.keyCode === 13 || event.keyCode === 0 || event.keyCode === 116) {
        event.preventDefault();
        return setTimeout(function() {
          return self.handle_event(event, self.barcode_scanned, true, self);
        }, 1000);
      }
    });
    self.input.addEventListener('keypress', function(event) {
      if (event.keyCode === 13 || event.keyCode === 0 || event.keyCode === 116) {
        return self.handle_event(event, self.barcode_scanned, true, self);
      }
    });
    return self.input.focus();
  };

  NHMobileBarcode.prototype.barcode_scanned = function(event, self) {
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

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobileBarcode = NHMobileBarcode;
}

var NHMobileForm,
  bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty,
  indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

NHMobileForm = (function(superClass) {
  extend(NHMobileForm, superClass);

  function NHMobileForm() {
    this.cancel_notification = bind(this.cancel_notification, this);
    this.submit_observation = bind(this.submit_observation, this);
    this.display_partial_reasons = bind(this.display_partial_reasons, this);
    this.show_reference = bind(this.show_reference, this);
    this.submit = bind(this.submit, this);
    this.trigger_actions = bind(this.trigger_actions, this);
    this.validate_number_input = bind(this.validate_number_input, this);
    this.validate = bind(this.validate, this);
    var ptn_name, ref, self;
    this.form = (ref = document.getElementsByTagName('form')) != null ? ref[0] : void 0;
    this.form_timeout = 600 * 1000;
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
              return input.addEventListener('change', function(e) {
                self.handle_event(e, self.validate, true);
                e.handled = false;
                return self.handle_event(e, self.trigger_actions, true);
              });
            case 'submit':
              return input.addEventListener('click', function(e) {
                var change_event, el, element, errored_els, form, form_elements, inp, j, k, len1, len2, ref1;
                form = (ref1 = document.getElementsByTagName('form')) != null ? ref1[0] : void 0;
                errored_els = (function() {
                  var j, len1, ref2, results;
                  ref2 = form.elements;
                  results = [];
                  for (j = 0, len1 = ref2.length; j < len1; j++) {
                    el = ref2[j];
                    if (el.classList.contains('error')) {
                      results.push(el);
                    }
                  }
                  return results;
                })();
                for (j = 0, len1 = errored_els.length; j < len1; j++) {
                  inp = errored_els[j];
                  self.reset_input_errors(inp);
                }
                form_elements = (function() {
                  var k, len2, ref2, results;
                  ref2 = form.elements;
                  results = [];
                  for (k = 0, len2 = ref2.length; k < len2; k++) {
                    element = ref2[k];
                    if (!element.classList.contains('exclude')) {
                      results.push(element);
                    }
                  }
                  return results;
                })();
                for (k = 0, len2 = form_elements.length; k < len2; k++) {
                  el = form_elements[k];
                  change_event = document.createEvent('CustomEvent');
                  change_event.initCustomEvent('change', false, true, false);
                  el.dispatchEvent(change_event);
                }
                return self.handle_event(e, self.submit, true);
              });
            case 'reset':
              return input.addEventListener('click', function(e) {
                return self.handle_event(e, self.cancel_notification, true);
              });
            case 'radio':
              return input.addEventListener('click', function(e) {
                return self.handle_event(e, self.trigger_actions, true);
              });
            case 'checkbox':
              input.addEventListener('click', function(e) {
                self.handle_event(e, self.validate, false);
                e.handled = false;
                return self.handle_event(e, self.trigger_actions, false);
              });
              return input.addEventListener('change', function(e) {
                self.handle_event(e, self.validate, false);
                e.handled = false;
                return self.handle_event(e, self.trigger_actions, false);
              });
            case 'text':
              return input.addEventListener('change', function(e) {
                self.handle_event(e, self.validate, true);
                e.handled = false;
                return self.handle_event(e, self.trigger_actions, true);
              });
          }
          break;
        case 'select':
          return input.addEventListener('change', function(e) {
            self.handle_event(e, self.validate, true);
            e.handled = false;
            return self.handle_event(e, self.trigger_actions, true);
          });
        case 'button':
          return input.addEventListener('click', function(e) {
            return self.handle_event(e, self.show_reference, true);
          });
        case 'textarea':
          return input.addEventListener('change', function(e) {
            self.handle_event(e, self.validate, true);
            e.handled = false;
            return self.handle_event(e, self.trigger_actions, true);
          });
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
      return self.handle_event(event, self.process_post_score_submit, true, self);
    });
    document.addEventListener('partial_submit', function(event) {
      return self.handle_event(event, self.process_partial_submit, true, self);
    });
    document.addEventListener('display_partial_reasons', self.handle_display_partial_reasons.bind(self));
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
    var cond, crit_target, crit_val, criteria, criterias, i, input, input_type, len, operator, other_input, other_input_value, regex_res, target_input, target_input_value, value;
    this.reset_form_timeout(this);
    input = event.src_el;
    input_type = input.getAttribute('type');
    value = input_type === 'number' ? parseFloat(input.value) : input.value;
    this.reset_input_errors(input);
    if (typeof value !== 'undefined' && value !== '') {
      if (input_type === 'number') {
        this.validate_number_input(input);
        if (input.getAttribute('data-validation') && !isNaN(value)) {
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
            } else if (typeof other_input_value !== 'undefined' && !isNaN(other_input_value) && other_input_value !== '') {
              this.add_input_errors(target_input, criteria['message']['target']);
              this.add_input_errors(other_input, criteria['message']['value']);
            } else {
              this.add_input_errors(target_input, criteria['message']['target']);
              this.add_input_errors(other_input, 'Please enter a value');
            }
          }
          this.validate_number_input(other_input);
          this.validate_number_input(target_input);
        }
      }
      if (input_type === 'text') {
        if (input.getAttribute('pattern')) {
          regex_res = input.validity.patternMismatch;
          if (regex_res) {
            this.add_input_errors(input, 'Invalid value');
          }
        }
      }
    } else {
      if (input.getAttribute('data-required').toLowerCase() === 'true') {
        this.add_input_errors(input, 'Missing value');
      }
    }
  };

  NHMobileForm.prototype.validate_number_input = function(input) {
    var max, min, value;
    min = parseFloat(input.getAttribute('min'));
    max = parseFloat(input.getAttribute('max'));
    value = parseFloat(input.value);
    if (typeof value !== 'undefined' && value !== '' && !isNaN(value)) {
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
      }
    } else {
      if (input.getAttribute('data-required').toLowerCase() === 'true') {
        return this.add_input_errors(input, 'Missing value');
      }
    }
  };

  NHMobileForm.prototype.trigger_actions = function(event) {
    var action, actionToTrigger, actions, condition, conditions, el, field, fieldsToAffect, i, input, j, k, l, len, len1, len10, len2, len3, len4, len5, len6, len7, len8, len9, m, mode, n, o, p, q, r, ref, ref1, ref2, ref3, s, type, value;
    this.reset_form_timeout(this);
    input = event.src_el;
    value = input.value;
    type = input.getAttribute('type');
    if (type === 'radio') {
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
    if (type === 'checkbox') {
      ref1 = document.getElementsByName(input.name);
      for (j = 0, len1 = ref1.length; j < len1; j++) {
        el = ref1[j];
        if (!el.checked) {
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
      for (k = 0, len2 = actions.length; k < len2; k++) {
        action = actions[k];
        type = action['type'];
        ref2 = action['condition'];
        for (l = 0, len3 = ref2.length; l < len3; l++) {
          condition = ref2[l];
          condition[0] = 'document.getElementById("' + condition[0] + '").value';
          condition[2] = (function() {
            switch (false) {
              case type !== 'value':
                return "'" + condition[2] + "'";
              case type !== 'field':
                return 'document.getElementById("' + condition[2] + '").value';
              default:
                return "'" + condition[2] + "'";
            }
          })();
        }
        mode = ' && ';
        conditions = [];
        ref3 = action['condition'];
        for (m = 0, len4 = ref3.length; m < len4; m++) {
          condition = ref3[m];
          if (typeof condition === 'object') {
            conditions.push(condition.join(' '));
          } else {
            mode = condition;
          }
        }
        conditions = conditions.join(mode);
        if (eval(conditions)) {
          actionToTrigger = action['action'];
          fieldsToAffect = action['fields'];
          if (actionToTrigger === 'hide') {
            for (n = 0, len5 = fieldsToAffect.length; n < len5; n++) {
              field = fieldsToAffect[n];
              this.hide_triggered_elements(field);
            }
          }
          if (actionToTrigger === 'show') {
            for (o = 0, len6 = fieldsToAffect.length; o < len6; o++) {
              field = fieldsToAffect[o];
              this.show_triggered_elements(field);
            }
          }
          if (actionToTrigger === 'disable') {
            for (p = 0, len7 = fieldsToAffect.length; p < len7; p++) {
              field = fieldsToAffect[p];
              this.disable_triggered_elements(field);
            }
          }
          if (actionToTrigger === 'enable') {
            for (q = 0, len8 = fieldsToAffect.length; q < len8; q++) {
              field = fieldsToAffect[q];
              this.enable_triggered_elements(field);
            }
          }
          if (actionToTrigger === 'require') {
            for (r = 0, len9 = fieldsToAffect.length; r < len9; r++) {
              field = fieldsToAffect[r];
              this.require_triggered_elements(field);
            }
          }
          if (actionToTrigger === 'unrequire') {
            for (s = 0, len10 = fieldsToAffect.length; s < len10; s++) {
              field = fieldsToAffect[s];
              this.unrequire_triggered_elements(field);
            }
          }
        }
      }
    }
  };

  NHMobileForm.prototype.submit = function(event) {
    var action_buttons, ajax_act, ajax_args, ajax_partial_act, btn, button, el, element, empty_elements, empty_mandatory, form_elements, i, invalid_elements, j, len, len1, msg;
    this.reset_form_timeout(this);
    ajax_act = this.form.getAttribute('ajax-action');
    ajax_partial_act = this.form.getAttribute('ajax-partial-action');
    ajax_args = this.form.getAttribute('ajax-args');
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
        el = form_elements[i];
        if (!el.value && (el.getAttribute('data-necessary').toLowerCase() === 'true') || el.value === '' && (el.getAttribute('data-necessary').toLowerCase() === 'true')) {
          results.push(el);
        }
      }
      return results;
    })();
    empty_mandatory = (function() {
      var i, len, results;
      results = [];
      for (i = 0, len = form_elements.length; i < len; i++) {
        el = form_elements[i];
        if (!el.value && (el.getAttribute('data-required').toLowerCase() === 'true') || el.value === '' && (el.getAttribute('data-required').toLowerCase() === 'true')) {
          results.push(el);
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
      return this.submit_observation(this, form_elements, ajax_act, ajax_args);
    } else if (empty_mandatory.length > 0 || empty_elements.length > 0 && ajax_act.indexOf('notification') > 0) {
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
      if (ajax_partial_act === 'score') {
        return this.submit_observation(this, form_elements, ajax_act, ajax_args, true);
      } else {
        return this.display_partial_reasons(this);
      }
    }
  };

  NHMobileForm.prototype.show_reference = function(event) {
    var btn, iframe, img, input, ref_title, ref_type, ref_url;
    this.reset_form_timeout(this);
    input = event.src_el;
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
    var form_type, observation, partials_url;
    form_type = self.form.getAttribute('data-source');
    observation = self.form.getAttribute('data-type');
    partials_url = this.urls.json_partial_reasons(observation);
    return Promise.when(this.call_resource(partials_url)).then(function(rdata) {
      var can_btn, con_btn, data, i, len, msg, option, option_name, option_val, options, select, server_data;
      server_data = rdata[0];
      data = server_data.data;
      options = '';
      for (i = 0, len = data.length; i < len; i++) {
        option = data[i];
        option_val = option[0];
        option_name = option[1];
        options += '<option value="' + option_val + '">' + option_name + '</option>';
      }
      select = '<select name="partial_reason">' + options + '</select>';
      con_btn = form_type === 'task' ? '<a href="#" ' + 'data-target="partial_reasons" data-action="partial_submit" ' + 'data-ajax-action="json_task_form_action">Confirm</a>' : '<a href="#" data-target="partial_reasons" ' + 'data-action="partial_submit" ' + 'data-ajax-action="json_patient_form_action">Confirm</a>';
      can_btn = '<a href="#" data-action="renable" ' + 'data-target="partial_reasons">Cancel</a>';
      msg = '<p>' + server_data.desc + '</p>';
      return new window.NH.NHModal('partial_reasons', server_data.title, msg + select, [can_btn, con_btn], 0, self.form);
    });
  };

  NHMobileForm.prototype.submit_observation = function(self, elements, endpoint, args, partial) {
    var el, formValues, i, key, len, serialised_string, type, url, value;
    if (partial == null) {
      partial = false;
    }
    formValues = {};
    for (i = 0, len = elements.length; i < len; i++) {
      el = elements[i];
      type = el.getAttribute('type');
      if (!formValues.hasOwnProperty(el.name)) {
        if (type === 'checkbox') {
          formValues[el.name] = [el.value];
        } else {
          formValues[el.name] = el.value;
        }
      } else {
        if (type === 'checkbox') {
          formValues[el.name].push(el.value);
        }
      }
    }
    serialised_string = ((function() {
      var results;
      results = [];
      for (key in formValues) {
        value = formValues[key];
        results.push(key + '=' + encodeURIComponent(value));
      }
      return results;
    })()).join("&");
    url = this.urls[endpoint].apply(this, args.split(','));
    return Promise.when(this.call_resource(url, serialised_string)).then(function(raw_data) {
      var act_btn, action_buttons, body, btn, button, buttons, can_btn, cls, data, data_action, element, j, k, l, len1, len2, len3, os, pos, ref, ref1, rt_url, server_data, st_url, sub_ob, task, task_list, tasks, triggered_tasks;
      server_data = raw_data[0];
      data = server_data.data;
      body = document.getElementsByTagName('body')[0];
      if (server_data.status === 'success' && data.status === 3) {
        data_action = !partial ? 'submit' : 'display_partial_reasons';
        can_btn = '<a href="#" data-action="renable" ' + 'data-target="submit_observation">Cancel</a>';
        act_btn = '<a href="#" data-target="submit_observation" ' + 'data-action="' + data_action + '" data-ajax-action="' + data.next_action + '">Submit</a>';
        new window.NH.NHModal('submit_observation', server_data.title + ' for ' + self.patient_name() + '?', server_data.desc, [can_btn, act_btn], 0, body);
        if ('clinical_risk' in data.score) {
          sub_ob = document.getElementById('submit_observation');
          cls = 'clinicalrisk-' + data.score.clinical_risk.toLowerCase();
          return sub_ob.classList.add(cls);
        }
      } else if (server_data.status === 'success' && data.status === 1) {
        triggered_tasks = '';
        buttons = ['<a href="' + self.urls['task_list']().url + '" data-action="confirm">Go to My Tasks</a>'];
        if (data.related_tasks.length === 1) {
          triggered_tasks = '<p>' + data.related_tasks[0].summary + '</p>';
          rt_url = self.urls['single_task'](data.related_tasks[0].id).url;
          buttons.push('<a href="' + rt_url + '">Confirm</a>');
        } else if (data.related_tasks.length > 1) {
          tasks = '';
          ref = data.related_tasks;
          for (j = 0, len1 = ref.length; j < len1; j++) {
            task = ref[j];
            st_url = self.urls['single_task'](task.id).url;
            tasks += '<li><a href="' + st_url + '">' + task.summary + '</a></li>';
          }
          triggered_tasks = '<ul class="menu">' + tasks + '</ul>';
        }
        pos = '<p>' + server_data.desc + '</p>';
        os = 'Observation successfully submitted';
        task_list = triggered_tasks ? triggered_tasks : pos;
        return new window.NH.NHModal('submit_success', server_data.title, task_list, buttons, 0, body);
      } else if (server_data.status === 'success' && data.status === 4) {
        triggered_tasks = '';
        buttons = ['<a href="' + self.urls['task_list']().url + '" data-action="confirm" data-target="cancel_success">' + 'Go to My Tasks</a>'];
        if (data.related_tasks.length === 1) {
          triggered_tasks = '<p>' + data.related_tasks[0].summary + '</p>';
          rt_url = self.urls['single_task'](data.related_tasks[0].id).url;
          buttons.push('<a href="' + rt_url + '">Confirm</a>');
        } else if (data.related_tasks.length > 1) {
          tasks = '';
          ref1 = data.related_tasks;
          for (k = 0, len2 = ref1.length; k < len2; k++) {
            task = ref1[k];
            st_url = self.urls['single_task'](task.id).url;
            tasks += '<li><a href="' + st_url + '">' + task.summary + '</a></li>';
          }
          triggered_tasks = '<ul class="menu">' + tasks + '</ul>';
        }
        pos = '<p>' + server_data.desc + '</p>';
        task_list = triggered_tasks ? triggered_tasks : pos;
        return new window.NH.NHModal('cancel_success', server_data.title, task_list, buttons, 0, self.form);
      } else {
        action_buttons = (function() {
          var l, len3, ref2, ref3, results;
          ref2 = self.form.elements;
          results = [];
          for (l = 0, len3 = ref2.length; l < len3; l++) {
            element = ref2[l];
            if ((ref3 = element.getAttribute('type')) === 'submit' || ref3 === 'reset') {
              results.push(element);
            }
          }
          return results;
        })();
        for (l = 0, len3 = action_buttons.length; l < len3; l++) {
          button = action_buttons[l];
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
    return Promise.when(this.call_resource(opts)).then(function(raw_data) {
      var can_btn, con_btn, data, i, len, msg, option, option_name, option_val, options, select, server_data;
      server_data = raw_data[0];
      data = server_data.data;
      options = '';
      for (i = 0, len = data.length; i < len; i++) {
        option = data[i];
        option_val = option.id;
        option_name = option.name;
        options += '<option value="' + option_val + '">' + option_name + '</option>';
      }
      select = '<select name="reason">' + options + '</select>';
      msg = '<p>' + server_data.desc + '</p>';
      can_btn = '<a href="#" data-action="close" ' + 'data-target="cancel_reasons">Cancel</a>';
      con_btn = '<a href="#" data-target="cancel_reasons" ' + 'data-action="partial_submit" ' + 'data-ajax-action="cancel_clinical_notification">Confirm</a>';
      return new window.NH.NHModal('cancel_reasons', server_data.title, msg + select, [can_btn, con_btn], 0, document.getElementsByTagName('form')[0]);
    });
  };

  NHMobileForm.prototype.reset_form_timeout = function(self) {
    clearTimeout(window.form_timeout);
    return window.form_timeout = setTimeout(window.timeout_func, self.form_timeout);
  };

  NHMobileForm.prototype.reset_input_errors = function(input) {
    var container_el, error_el;
    container_el = this.findParentWithClass(input, 'block');
    error_el = container_el.getElementsByClassName('errors')[0];
    container_el.classList.remove('error');
    input.classList.remove('error');
    return error_el.innerHTML = '';
  };

  NHMobileForm.prototype.add_input_errors = function(input, error_string) {
    var container_el, error_el;
    container_el = this.findParentWithClass(input, 'block');
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
    inp.classList.add('exclude');
    return inp.setAttribute('data-necessary', 'false');
  };

  NHMobileForm.prototype.show_triggered_elements = function(field) {
    var el, inp;
    el = document.getElementById('parent_' + field);
    el.style.display = 'block';
    inp = document.getElementById(field);
    inp.classList.remove('exclude');
    return inp.setAttribute('data-necessary', 'true');
  };

  NHMobileForm.prototype.disable_triggered_elements = function(field) {
    var inp;
    inp = document.getElementById(field);
    inp.classList.add('exclude');
    inp.setAttribute('data-necessary', 'false');
    return inp.disabled = true;
  };

  NHMobileForm.prototype.enable_triggered_elements = function(field) {
    var inp;
    inp = document.getElementById(field);
    inp.classList.remove('exclude');
    inp.setAttribute('data-necessary', 'true');
    return inp.disabled = false;
  };

  NHMobileForm.prototype.require_triggered_elements = function(field) {
    var inp;
    inp = document.getElementById(field);
    inp.classList.remove('exclude');
    return inp.setAttribute('data-required', 'true');
  };

  NHMobileForm.prototype.unrequire_triggered_elements = function(field) {
    var inp;
    inp = document.getElementById(field);
    inp.classList.add('exclude');
    return inp.setAttribute('data-required', 'false');
  };

  NHMobileForm.prototype.process_partial_submit = function(event, self) {
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

  NHMobileForm.prototype.process_post_score_submit = function(event, self) {
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

  NHMobileForm.prototype.handle_display_partial_reasons = function(event) {
    return this.display_partial_reasons(this);
  };

  NHMobileForm.prototype.findParentWithClass = function(el, className) {
    while (el.parentNode) {
      el = el.parentNode;
      if (el && indexOf.call(el.classList, className) >= 0) {
        return el;
      }
    }
    return null;
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

  String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
  };

  function NHMobilePatient(refused, partialType) {
    var dataId, self;
    if (refused == null) {
      refused = false;
    }
    if (partialType == null) {
      partialType = "dot";
    }
    self = this;
    NHMobilePatient.__super__.constructor.call(this);
    self.setUpObsMenu(self);
    self.setUpTableView();
    self.setUpChartSelect(self);
    self.setUpTabs(self);
    dataId = document.getElementById("graph-content").getAttribute("data-id");
    self.refused = refused;
    self.partial_type = partialType;
    self.chart_element = "chart";
    self.table_element = "table-content";
    Promise.when(this.call_resource(this.urls["ajax_get_patient_obs"]("ews", dataId))).then(function(rawData) {
      var data, obsData, serverData;
      serverData = rawData[0];
      data = serverData.data;
      obsData = data.obs;
      return self.drawGraph(self, obsData, "ews");
    });
  }

  NHMobilePatient.prototype.setUpObsMenu = function(self) {
    var obs, obsMenu;
    obsMenu = document.getElementById("obsMenu");
    if (obsMenu) {
      obsMenu.style.display = "none";
    }
    obs = document.getElementById("take-observation");
    if (obs) {
      return obs.addEventListener("click", function(e) {
        return self.handle_event(e, self.showObsMenu, true);
      });
    }
  };

  NHMobilePatient.prototype.setUpTableView = function() {
    var table_view;
    table_view = document.getElementById("table-content");
    return table_view.style.display = "none";
  };

  NHMobilePatient.prototype.setUpChartSelect = function(self) {
    var chartSelect;
    chartSelect = document.getElementById("chart_select");
    if (chartSelect) {
      return chartSelect.addEventListener("change", function(event) {
        return self.handle_event(event, self.changeChart, false, [self]);
      });
    }
  };

  NHMobilePatient.prototype.setUpTabs = function(self) {
    var i, len, results, tab, tabs, tabs_el;
    tabs_el = document.getElementsByClassName("tabs");
    tabs = tabs_el[0].getElementsByTagName("a");
    results = [];
    for (i = 0, len = tabs.length; i < len; i++) {
      tab = tabs[i];
      results.push(tab.addEventListener("click", function(e) {
        return self.handle_event(e, self.handleTabs, true);
      }));
    }
    return results;
  };

  NHMobilePatient.prototype.handleTabs = function(event) {
    var i, len, tab, tabTarget, tabs, targetEl;
    tabs = document.getElementsByClassName("tabs")[0].getElementsByTagName("a");
    for (i = 0, len = tabs.length; i < len; i++) {
      tab = tabs[i];
      tab.classList.remove("selected");
    }
    document.getElementById("graph-content").style.display = "none";
    document.getElementById("table-content").style.display = "none";
    targetEl = event.src_el;
    targetEl.classList.add("selected");
    tabTarget = targetEl.getAttribute("href").replace("#", "");
    return document.getElementById(tabTarget).style.display = "block";
  };

  NHMobilePatient.prototype.changeChart = function(event, self) {
    var chart, dataId, newDataModel, table;
    chart = document.getElementById(self.chart_element);
    table = document.getElementById(self.table_element);
    chart.innerHTML = "";
    table.innerHTML = "";
    newDataModel = event.src_el.value;
    dataId = document.getElementById("graph-content").getAttribute("data-id");
    return Promise.when(self.call_resource(self.urls["ajax_get_patient_obs"](newDataModel, dataId))).then(function(rawData) {
      var data, obsData, serverData;
      serverData = rawData[0];
      data = serverData.data;
      obsData = data.obs;
      return self.drawGraph(self, obsData, newDataModel);
    });
  };

  NHMobilePatient.prototype.showObsMenu = function(event) {
    var body, menu, obsMenu, pat, pats;
    obsMenu = document.getElementById("obsMenu");
    body = document.getElementsByTagName("body")[0];
    menu = "<ul class=\"menu\">" + obsMenu.innerHTML + "</ul>";
    pats = document.querySelectorAll("a.patientInfo h3.name strong");
    pat = "";
    if (pats.length > 0) {
      pat = pats[0].textContent;
    }
    return new NHModal("obs_menu", "Pick an observation for " + pat, menu, ["<a href=\"#\" data-action=\"close\" " + "data-target=\"obs_menu\">Cancel</a>"], 0, body);
  };

  NHMobilePatient.prototype.redrawGraphAreaWithData = function(self, serverData, dataModel) {
    var activeTab, chartEl, chartFunc, chartFuncName, controls, el, graphContent, graphTabs, i, len, tableEl, tableFunc, tableFuncName, validChart, validTable, visualisation_els;
    graphContent = document.getElementById("graph-content");
    controls = document.getElementById("controls");
    chartEl = document.getElementById(self.chart_element);
    tableEl = document.getElementById(self.table_element);
    graphTabs = graphContent.parentNode.getElementsByClassName("tabs")[0];
    activeTab = graphTabs.getElementsByClassName("selected")[0].getAttribute('href');
    chartFuncName = "draw" + dataModel.capitalize() + "Chart";
    tableFuncName = "draw" + dataModel.capitalize() + "Table";
    visualisation_els = [controls, graphTabs, chartEl, graphContent, tableEl];
    for (i = 0, len = visualisation_els.length; i < len; i++) {
      el = visualisation_els[i];
      el.style.display = "block";
    }
    chartFunc = window[chartFuncName];
    tableFunc = window[tableFuncName];
    validChart = typeof chartFunc === "function";
    validTable = typeof tableFunc === "function";
    if (validChart) {
      chartFunc(self, serverData);
    }
    if (validTable) {
      tableFunc(self, serverData);
    }
    if (!validChart || !validTable) {
      graphTabs.style.display = "none";
    } else {
      graphTabs.style.display = "block";
      if (activeTab === "#graph-content") {
        tableEl.style.display = "none";
      } else {
        graphContent.style.display = "none";
      }
    }
    if (!validChart && validTable) {
      return controls.style.display = 'none';
    }
  };

  NHMobilePatient.prototype.redrawGraphAreaWithNoDataPlaceholder = function(self) {
    var chartEl, controls, graphContent, graphTabs;
    graphContent = document.getElementById("graph-content");
    controls = document.getElementById("controls");
    chartEl = document.getElementById(self.chart_element);
    graphTabs = graphContent.parentNode.getElementsByClassName("tabs")[0];
    controls.style.display = "none";
    graphContent.style.display = "block";
    chartEl.innerHTML = '<h2 class="placeholder">' + 'No observation data available for patient' + '</h2>';
    return graphTabs.style.display = "none";
  };

  NHMobilePatient.prototype.drawGraph = function(self, serverData, dataModel) {
    if (serverData.length > 0) {
      return self.redrawGraphAreaWithData(self, serverData, dataModel);
    } else {
      return self.redrawGraphAreaWithNoDataPlaceholder(self);
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

  function NHMobileShare(share_button, claim_button, all_button) {
    var self;
    this.share_button = share_button;
    this.claim_button = claim_button;
    this.all_button = all_button;
    self = this;
    this.form = document.getElementById('handover_form');
    this.share_button.addEventListener('click', function(event) {
      return self.handle_event(event, self.share_button_click, true, self);
    });
    this.claim_button.addEventListener('click', function(event) {
      return self.handle_event(event, self.claim_button_click, true, self);
    });
    this.all_button.addEventListener('click', function(event) {
      var button, button_mode;
      button = event.srcElement ? event.srcElement : event.target;
      button_mode = button.getAttribute('mode');
      if (button_mode === 'select') {
        self.handle_event(event, self.select_all_patients, true, self);
        button.textContent = 'Unselect all';
        return button.setAttribute('mode', 'unselect');
      } else {
        self.handle_event(event, self.unselect_all_patients, true, self);
        button.textContent = 'Select all';
        return button.setAttribute('mode', 'select');
      }
    });
    document.addEventListener('assign_nurse', function(event) {
      return self.handle_event(event, self.assign_button_click, true, self);
    });
    document.addEventListener('claim_patients', function(event) {
      return self.handle_event(event, self.claim_patients_click, true, self);
    });
    NHMobileShare.__super__.constructor.call(this);
  }

  NHMobileShare.prototype.share_button_click = function(event, self) {
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
      return Promise.when(self.process_request(urlmeth, url.url)).then(function(raw_data) {
        var assign_btn, btns, can_btn, data, i, len, nurse, nurse_list, ref, server_data;
        server_data = raw_data[0];
        data = server_data.data;
        nurse_list = '<form id="nurse_list"><ul class="sharelist">';
        ref = data.colleagues;
        for (i = 0, len = ref.length; i < len; i++) {
          nurse = ref[i];
          nurse_list += '<li><input type="checkbox" name="nurse_select_' + nurse.id + '" class="patient_share_nurse" value="' + nurse.id + '"/><label for="nurse_select_' + nurse.id + '">' + nurse.name + ' (' + nurse.patients + ')</label></li>';
        }
        nurse_list += '</ul><p class="error"></p></form>';
        assign_btn = '<a href="#" data-action="assign" ' + 'data-target="assign_nurse" data-ajax-action="json_assign_nurse">' + 'Assign</a>';
        can_btn = '<a href="#" data-action="close" data-target="assign_nurse"' + '>Cancel</a>';
        btns = [assign_btn, can_btn];
        return new window.NH.NHModal('assign_nurse', server_data.title, nurse_list, btns, 0, self.form);
      });
    } else {
      msg = '<p>Please select patients to hand' + ' to another staff member</p>';
      btn = ['<a href="#" data-action="close" data-target="invalid_form">' + 'Cancel</a>'];
      return new window.NH.NHModal('invalid_form', 'No Patients selected', msg, btn, 0, self.form);
    }
  };

  NHMobileShare.prototype.claim_button_click = function(event, self) {
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

  NHMobileShare.prototype.assign_button_click = function(event, self) {
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
      Promise.when(self.call_resource(url, data_string)).then(function(raw_data) {
        var btns, can_btn, cover, data, i, len, pt, pt_el, pts, server_data, share_msg, ti;
        server_data = raw_data[0];
        data = server_data.data;
        if (server_data.status === 'success') {
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
              ti.innerHTML = 'Shared with: ' + data.shared_with.join(', ');
            } else {
              ti.innerHTML += ', ' + data.shared_with.join(', ');
            }
          }
          cover = document.getElementById('cover');
          document.getElementsByTagName('body')[0].removeChild(cover);
          popup.parentNode.removeChild(popup);
          can_btn = '<a href="#" data-action="close" ' + 'data-target="share_success">Close</a>';
          share_msg = '<p>' + server_data.desc + data.shared_with.join(', ') + '</p>';
          btns = [can_btn];
          return new window.NH.NHModal('share_success', server_data.title, share_msg, btns, 0, body);
        } else {
          return error_message.innerHTML = 'Error assigning colleague(s),' + ' please try again';
        }
      });
    }
    return true;
  };

  NHMobileShare.prototype.claim_patients_click = function(event, self) {
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
    Promise.when(self.call_resource(url, data_string)).then(function(raw_data) {
      var body, btns, can_btn, claim_msg, cover, data, i, len, popup, pt, pt_el, pts, server_data, ti;
      server_data = raw_data[0];
      data = server_data.data;
      popup = document.getElementById('claim_patients');
      cover = document.getElementById('cover');
      body = document.getElementsByTagName('body')[0];
      body.removeChild(cover);
      popup.parentNode.removeChild(popup);
      if (server_data.status === 'success') {
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
        can_btn = '<a href="#" data-action="close" ' + 'data-target="claim_success">Close</a>';
        claim_msg = '<p>' + server_data.desc + '</p>';
        btns = [can_btn];
        return new window.NH.NHModal('claim_success', server_data.title, claim_msg, btns, 0, body);
      } else {
        can_btn = '<a href="#" data-action="close" data-target="claim_error"' + '>Close</a>';
        claim_msg = '<p>There was an error claiming back your' + ' patients, please contact your Shift Coordinator</p>';
        btns = [can_btn];
        return new window.NH.NHModal('claim_error', 'Error claiming patients', claim_msg, btns, 0, body);
      }
    });
    return true;
  };

  NHMobileShare.prototype.select_all_patients = function(event, self) {
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

  NHMobileShare.prototype.unselect_all_patients = function(event, self) {
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
        var activity_id, args, btn;
        btn = event.srcElement ? event.srcElement : event.target;
        activity_id = btn.getAttribute('data-invite-id');
        args = [self, activity_id];
        return self.handle_event(event, self.handle_invite_click, true, args);
      });
    }
    document.addEventListener('accept_invite', function(event) {
      var activity_id, args;
      activity_id = event.detail.invite_id;
      args = [self, activity_id];
      return self.handle_event(event, self.handle_accept_button_click, true, args);
    });
    document.addEventListener('reject_invite', function(event) {
      var activity_id, args;
      activity_id = event.detail.invite_id;
      args = [self, activity_id];
      return self.handle_event(event, self.handle_reject_button_click, true, args);
    });
    NHMobileShareInvite.__super__.constructor.call(this);
  }

  NHMobileShareInvite.prototype.handle_invite_click = function(event, self, activity_id) {
    var url, urlmeth;
    url = self.urls.json_invite_patients(activity_id);
    urlmeth = url.method;
    Promise.when(self.process_request(urlmeth, url.url)).then(function(raw_data) {
      var acpt_btn, body, btns, can_btn, cls_btn, data, j, len, pt, pt_list, pt_obj, server_data;
      server_data = raw_data[0];
      data = server_data.data;
      pt_list = '<ul class="tasklist">';
      for (j = 0, len = data.length; j < len; j++) {
        pt = data[j];
        pt_obj = '<li class="block"><a>' + '<div class="task-meta">' + '<div class="task-right">' + '<p class="aside">' + pt.next_ews_time + '</p></div>' + '<div class="task-left">' + '<strong>' + pt.full_name + '</strong>' + '(' + pt.ews_score + ' <i class="icon-' + pt.ews_trend + '-arrow"></i> )' + '<br><em>' + pt.location + ', ' + pt.parent_location + '</em>' + '</div>' + '</div>' + '</a></li>';
        pt_list += pt_obj;
      }
      pt_list += '</ul>';
      cls_btn = '<a href="#" data-action="close" data-target="accept_invite"' + '>Close</a>';
      can_btn = '<a href="#" data-action="reject" data-target="accept_invite"' + 'data-ajax-action="json_reject_invite" ' + 'data-invite-id="' + activity_id + '">Reject</a>';
      acpt_btn = '<a href="#" data-action="accept" data-target="accept_invite"' + 'data-ajax-action="json_accept_invite" ' + 'data-invite-id="' + activity_id + '">Accept</a>';
      btns = [cls_btn, can_btn, acpt_btn];
      body = document.getElementsByTagName('body')[0];
      return new window.NH.NHModal('accept_invite', server_data.title, pt_list, btns, 0, body);
    });
    return true;
  };

  NHMobileShareInvite.prototype.handle_accept_button_click = function(event, self, activity_id) {
    var body, url, urlmeth;
    url = self.urls.json_accept_patients(activity_id);
    urlmeth = url.method;
    body = document.getElementsByTagName('body')[0];
    return Promise.when(self.process_request(urlmeth, url.url)).then(function(raw_data) {
      var btns, cover, covers, data, i, invite, invite_modal, invites, j, k, len, len1, server_data;
      server_data = raw_data[0];
      data = server_data.data;
      if (server_data.status === 'success') {
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
        btns = ['<a href="#" data-action="close" data-target="invite_success"' + '>Close</a>'];
        covers = document.getElementsByClassName('cover');
        for (j = 0, len = covers.length; j < len; j++) {
          cover = covers[j];
          if (cover != null) {
            cover.parentNode.removeChild(cover);
          }
        }
        invite_modal = document.getElementById('accept_invite');
        invite_modal.parentNode.removeChild(invite_modal);
        return new window.NH.NHModal('invite_success', server_data.title, '<p>' + server_data.desc + '</p>', btns, 0, body);
      } else {
        btns = ['<a href="#" data-action="close" data-target="invite_error"' + '>Close</a>'];
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

  NHMobileShareInvite.prototype.handle_reject_button_click = function(event, self, activity_id) {
    var body, url, urlmeth;
    url = self.urls.json_reject_patients(activity_id);
    urlmeth = url.method;
    body = document.getElementsByTagName('body')[0];
    return Promise.when(self.process_request(urlmeth, url.url)).then(function(raw_data) {
      var btns, cover, covers, data, i, invite, invite_modal, invites, j, k, len, len1, server_data;
      server_data = raw_data[0];
      data = server_data.data;
      if (server_data.status === 'success') {
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
        btns = ['<a href="#" data-action="close" data-target="reject_success"' + '>Close</a>'];
        covers = document.getElementsByClassName('cover');
        for (j = 0, len = covers.length; j < len; j++) {
          cover = covers[j];
          if (cover != null) {
            cover.parentNode.removeChild(cover);
          }
        }
        invite_modal = document.getElementById('accept_invite');
        invite_modal.parentNode.removeChild(invite_modal);
        return new window.NH.NHModal('reject_success', server_data.title, '<p>' + server_data.desc + '</p>', btns, 0, body);
      } else {
        btns = ['<a href="#" data-action="close" data-target="reject_success"' + '>Close</a>'];
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

var NHModal,
  bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

NHModal = (function(superClass) {
  extend(NHModal, superClass);

  function NHModal(id1, title1, content1, options1, popupTime, el1) {
    var body, cover, dialog, self;
    this.id = id1;
    this.title = title1;
    this.content = content1;
    this.options = options1;
    this.popupTime = popupTime;
    this.el = el1;
    this.handle_button_events = bind(this.handle_button_events, this);
    this.close_modal = bind(this.close_modal, this);
    self = this;
    dialog = this.create_dialog(self, this.id, this.title, this.content, this.options);
    body = document.getElementsByTagName('body')[0];
    cover = document.createElement('div');
    cover.setAttribute('class', 'cover');
    cover.setAttribute('id', 'cover');
    cover.setAttribute('data-action', 'close');
    if (this.id === 'submit_observation' || this.id === 'partial_reasons') {
      cover.setAttribute('data-action', 'renable');
    }
    if (this.id === 'rapid_tranq_check') {
      cover.setAttribute('data-action', 'close_reload');
    }
    cover.setAttribute('data-target', this.id);
    cover.addEventListener('click', function(e) {
      return self.handle_event(e, self.handle_button_events, false);
    });
    this.lock_scrolling();
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
        var a_button, option_button, ref;
        option_button = document.createElement('li');
        option_button.innerHTML = button;
        a_button = (ref = option_button.getElementsByTagName('a')) != null ? ref[0] : void 0;
        a_button.addEventListener('click', function(e) {
          return self.handle_event(e, self.handle_button_events, false);
        });
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
    available_space = function(dialog, el, dialog_content) {
      var dc_height, dh, dhh, dialog_height, dialog_total, dopt, dopth, elh;
      dh = dialog.getElementsByTagName('h2');
      dhh = parseInt(document.defaultView.getComputedStyle(dh != null ? dh[0] : void 0, '').getPropertyValue('height').replace('px', ''));
      dopt = dialog.getElementsByClassName('options');
      dopth = parseInt(document.defaultView.getComputedStyle(dopt != null ? dopt[0] : void 0, '').getPropertyValue('height').replace('px', ''));
      elh = parseInt(document.defaultView.getComputedStyle(el, '').getPropertyValue('height').replace('px', ''));
      dialog_height = (dhh + dopth) + (margins.top + margins.bottom);
      dc_height = parseInt(document.defaultView.getComputedStyle(dialog_content, '').getPropertyValue('height').replace('px', ''));
      dialog_total = dialog_height + dc_height;
      if (elh > window.innerHeight) {
        return window.innerHeight - dialog_height;
      }
      if (dialog_total > window.innerHeight) {
        return window.innerHeight - dialog_height;
      }
    };
    max_height = available_space(dialog, el, dialog_content);
    top_offset = el.offsetTop + margins.top;
    dialog.style.top = top_offset + 'px';
    dialog.style.display = 'inline-block';
    if (max_height) {
      dialog_content.style.maxHeight = max_height + 'px';
    }
  };

  NHModal.prototype.close_modal = function(modal_id) {
    var cover, dialog_id, self;
    self = this;
    dialog_id = document.getElementById(modal_id);
    if (typeof dialog_id !== 'undefined' && dialog_id) {
      cover = document.querySelectorAll('#cover[data-target="' + modal_id + '"]')[0];
      document.getElementsByTagName('body')[0].removeChild(cover);
      dialog_id.parentNode.removeChild(dialog_id);
      return self.unlock_scrolling();
    }
  };

  NHModal.prototype.reloadPage = function() {
    return location.reload();
  };

  NHModal.prototype.handle_button_events = function(event) {
    var accept_detail, accept_event, action_buttons, assign_detail, assign_event, button, claim_event, confirmEvent, data_action, data_target, dialog, dialog_form, el, element, form, forms, i, j, len, len1, nurses, reject_detail, reject_event, submit_detail, submit_event, target_el;
    target_el = event.src_el;
    data_target = target_el.getAttribute('data-target');
    data_action = target_el.getAttribute('data-ajax-action');
    switch (target_el.getAttribute('data-action')) {
      case 'close':
        event.preventDefault();
        return this.close_modal(data_target);
      case 'close_reload':
        event.preventDefault();
        return this.reloadPage();
      case 'renable':
        event.preventDefault();
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
        return this.close_modal(data_target);
      case 'confirm_submit':
        event.preventDefault();
        confirmEvent = document.createEvent("CustomEvent");
        confirmEvent.initCustomEvent("confirm_change", false, true, false);
        document.dispatchEvent(confirmEvent);
        return this.close_modal(data_target);
      case 'submit':
        event.preventDefault();
        submit_event = document.createEvent('CustomEvent');
        submit_detail = {
          'endpoint': target_el.getAttribute('data-ajax-action')
        };
        submit_event.initCustomEvent('post_score_submit', true, false, submit_detail);
        document.dispatchEvent(submit_event);
        return this.close_modal(data_target);
      case 'partial_submit':
        event.preventDefault();
        submit_event = document.createEvent('CustomEvent');
        submit_detail = {
          'action': data_action,
          'target': data_target
        };
        submit_event.initCustomEvent('partial_submit', false, true, submit_detail);
        return document.dispatchEvent(submit_event);
      case 'display_partial_reasons':
        event.preventDefault();
        this.close_modal(data_target);
        submit_event = document.createEvent('CustomEvent');
        submit_detail = {
          'action': data_action,
          'target': data_target
        };
        submit_event.initCustomEvent('display_partial_reasons', false, true, submit_detail);
        return document.dispatchEvent(submit_event);
      case 'assign':
        event.preventDefault();
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
        return document.dispatchEvent(assign_event);
      case 'claim':
        event.preventDefault();
        claim_event = document.createEvent('CustomEvent');
        claim_event.initCustomEvent('claim_patients', false, true, false);
        return document.dispatchEvent(claim_event);
      case 'accept':
        event.preventDefault();
        accept_event = document.createEvent('CustomEvent');
        accept_detail = {
          'invite_id': target_el.getAttribute('data-invite-id')
        };
        accept_event.initCustomEvent('accept_invite', false, true, accept_detail);
        return document.dispatchEvent(accept_event);
      case 'reject':
        event.preventDefault();
        reject_event = document.createEvent('CustomEvent');
        reject_detail = {
          'invite_id': target_el.getAttribute('data-invite-id')
        };
        reject_event.initCustomEvent('reject_invite', false, true, reject_detail);
        return document.dispatchEvent(reject_event);
    }
  };

  NHModal.prototype.lock_scrolling = function() {
    var body;
    body = document.getElementsByTagName('body')[0];
    return body.classList.add('no-scroll');
  };

  NHModal.prototype.unlock_scrolling = function() {
    var body, dialogs;
    body = document.getElementsByTagName('body')[0];
    dialogs = document.getElementsByClassName('dialog');
    if (dialogs.length < 1) {
      return body.classList.remove('no-scroll');
    }
  };

  return NHModal;

})(NHLib);

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHModal = NHModal;
}

var NHMobilePatientMentalHealth,
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

NHMobilePatientMentalHealth = (function(superClass) {
  extend(NHMobilePatientMentalHealth, superClass);

  function NHMobilePatientMentalHealth() {
    var partialType, rapidTranqButton, refused, self;
    NHMobilePatientMentalHealth.__super__.constructor.call(this, refused = true, partialType = "character");
    self = this;
    rapidTranqButton = document.getElementById('toggle-rapid-tranq');
    rapidTranqButton.addEventListener("click", function(e) {
      return self.handle_event(e, self.checkRapidTranqStatus, true, [self]);
    });
    document.addEventListener("confirm_change", function(e) {
      return self.handle_event(e, self.submitRapidTranqChange, true, [self]);
    });
  }

  NHMobilePatientMentalHealth.prototype.getEndpoint = function(self) {
    var dataId, intendedState, intendedStateString, rapidTranqButton, url;
    rapidTranqButton = document.getElementById('toggle-rapid-tranq');
    intendedState = rapidTranqButton.getAttribute('data-state-to-set');
    intendedStateString = '?check=' + intendedState.toString();
    dataId = document.getElementById("graph-content").getAttribute("data-id");
    url = self.urls.rapid_tranq(dataId);
    url.url += intendedStateString;
    return {
      url: url,
      data: intendedStateString
    };
  };

  NHMobilePatientMentalHealth.prototype.checkRapidTranqStatus = function(event, self) {
    var endpoint;
    endpoint = self.getEndpoint(self);
    return Promise.when(self.process_request('GET', endpoint.url.url, endpoint.data)).then(function(serverResult) {
      var body, buttons, result;
      body = document.getElementsByTagName("body")[0];
      result = serverResult[0];
      buttons = [];
      if (result.status === "fail") {
        buttons = ["<a href=\"#\" data-action=\"close_reload\" " + "data-target=\"rapid_tranq_check\">Reload</a>"];
      } else {
        buttons = ["<a href=\"#\" data-action=\"close\" " + "data-target=\"rapid_tranq_check\">Cancel</a>", "<a href=\"#\" data-action=\"confirm_submit\" " + "data-target=\"rapid_tranq_check\">Confirm</a>"];
      }
      return new NHModal('rapid_tranq_check', result.title, '<p>' + result.desc + '</p>', buttons, 0, body);
    });
  };

  NHMobilePatientMentalHealth.prototype.submitRapidTranqChange = function(event, self) {
    var endpoint;
    if (!event.handled) {
      endpoint = self.getEndpoint(self);
      return Promise.when(self.process_request('POST', endpoint.url.url, endpoint.data)).then(function(serverResult) {
        var body, newStatus, rapidTranqButton, result;
        result = serverResult[0];
        body = document.getElementsByTagName("body")[0];
        newStatus = result.data.rapid_tranq;
        rapidTranqButton = document.getElementById('toggle-rapid-tranq');
        rapidTranqButton.setAttribute('data-state-to-set', !newStatus);
        if (newStatus === true) {
          rapidTranqButton.innerText = 'Stop Rapid Tranquilisation';
          rapidTranqButton.classList.remove('dont-do-it');
          return rapidTranqButton.classList.add('white-on-black');
        } else {
          rapidTranqButton.innerText = 'Start Rapid Tranquilisation';
          rapidTranqButton.classList.add('dont-do-it');
          return rapidTranqButton.classList.remove('white-on-black');
        }
      });
    }
  };

  return NHMobilePatientMentalHealth;

})(NHMobilePatient);

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobilePatient = NHMobilePatientMentalHealth;
}
