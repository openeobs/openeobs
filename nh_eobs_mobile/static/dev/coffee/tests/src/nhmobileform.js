
/* istanbul ignore next */
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
    this.forms = document.getElementsByTagName('form');
    this.form = (ref = this.forms) != null ? ref[0] : void 0;
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
    var fn, form, i, input, j, len, len1, ref, ref1, resetButton, submitButton;
    ref = self.forms;
    for (i = 0, len = ref.length; i < len; i++) {
      form = ref[i];
      ref1 = form.elements;
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
      for (j = 0, len1 = ref1.length; j < len1; j++) {
        input = ref1[j];
        fn();
      }
    }
    submitButton = document.querySelector('input[type="submit"]');
    if (submitButton != null) {
      submitButton.addEventListener('click', function(e) {
        var change_event, el, element, elements, errored_els, form_elements, forms, inp, k, l, len2, len3, len4, len5, m, n, ref2;
        forms = document.getElementsByTagName('form');
        elements = [];
        for (k = 0, len2 = forms.length; k < len2; k++) {
          form = forms[k];
          ref2 = form.elements;
          for (l = 0, len3 = ref2.length; l < len3; l++) {
            element = ref2[l];
            elements.push(element);
          }
        }
        errored_els = (function() {
          var len4, m, results;
          results = [];
          for (m = 0, len4 = elements.length; m < len4; m++) {
            el = elements[m];
            if (el.classList.contains('error')) {
              results.push(el);
            }
          }
          return results;
        })();
        for (m = 0, len4 = errored_els.length; m < len4; m++) {
          inp = errored_els[m];
          self.reset_input_errors(inp);
        }
        form_elements = (function() {
          var len5, n, results;
          results = [];
          for (n = 0, len5 = elements.length; n < len5; n++) {
            element = elements[n];
            if (!element.classList.contains('exclude')) {
              results.push(element);
            }
          }
          return results;
        })();
        for (n = 0, len5 = form_elements.length; n < len5; n++) {
          el = form_elements[n];
          change_event = document.createEvent('CustomEvent');
          change_event.initCustomEvent('change', false, true, false);
          el.dispatchEvent(change_event);
        }
        return self.handle_event(e, self.submit, true);
      });
    }
    resetButton = document.querySelector('input[type="reset"]');
    if (resetButton != null) {
      resetButton.addEventListener('click', function(e) {
        return self.handle_event(e, self.cancel_notification, true);
      });
    }
    document.addEventListener('form_timeout', function(event) {
      var task_id;
      task_id = self.form.getAttribute('task-id');

      /* istanbul ignore else */
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

          /* istanbul ignore else */
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
    var body_el, btn, el, element, empty_mandatory, form, form_elements, i, invalid_elements, j, len, len1, msg, ref, ref1;
    this.reset_form_timeout(this);
    body_el = document.getElementsByTagName('body')[0];
    form_elements = [];
    ref = this.forms;
    for (i = 0, len = ref.length; i < len; i++) {
      form = ref[i];
      ref1 = form.elements;
      for (j = 0, len1 = ref1.length; j < len1; j++) {
        element = ref1[j];
        if (!element.classList.contains('exclude')) {
          form_elements.push(element);
        }
      }
    }
    invalid_elements = (function() {
      var k, len2, results;
      results = [];
      for (k = 0, len2 = form_elements.length; k < len2; k++) {
        element = form_elements[k];
        if (element.classList.contains('error')) {
          results.push(element);
        }
      }
      return results;
    })();
    empty_mandatory = (function() {
      var k, len2, results;
      results = [];
      for (k = 0, len2 = form_elements.length; k < len2; k++) {
        el = form_elements[k];
        if (!el.value && (el.getAttribute('data-required').toLowerCase() === 'true') || el.value === '' && (el.getAttribute('data-required').toLowerCase() === 'true')) {
          results.push(el);
        }
      }
      return results;
    })();
    if (empty_mandatory.length > 0) {
      msg = '<p>The form contains empty fields, please enter ' + 'data into these fields and resubmit</p>';
      btn = '<a href="#" data-action="close" data-target="invalid_form">' + 'Cancel</a>';
      return new window.NH.NHModal('invalid_form', 'Form contains empty fields', msg, [btn], 0, body_el);
    } else if (invalid_elements.length > 0) {
      msg = '<p>The form contains errors, please correct ' + 'the errors and resubmit</p>';
      btn = '<a href="#" data-action="close" data-target="invalid_form">' + 'Cancel</a>';
      return new window.NH.NHModal('invalid_form', 'Form contains errors', msg, [btn], 0, body_el);
    } else {
      return this.submit_forms();
    }
  };

  NHMobileForm.prototype.submit_forms = function() {
    var ajaxAct, ajaxArgs, ajaxPartialAct, el, element, emptyElements, form, formElements, forms, i, j, len, len1, ref, results;
    forms = document.getElementsByTagName('form');
    results = [];
    for (i = 0, len = forms.length; i < len; i++) {
      form = forms[i];
      formElements = [];
      ref = form.elements;
      for (j = 0, len1 = ref.length; j < len1; j++) {
        element = ref[j];
        if (!element.classList.contains('exclude')) {
          formElements.push(element);
        }
      }
      ajaxAct = form.getAttribute('ajax-action');
      ajaxPartialAct = form.getAttribute('ajax-partial-action');
      ajaxArgs = form.getAttribute('ajax-args');
      emptyElements = (function() {
        var k, len2, results1;
        results1 = [];
        for (k = 0, len2 = formElements.length; k < len2; k++) {
          el = formElements[k];
          if (!el.value && (el.getAttribute('data-necessary').toLowerCase() === 'true') || el.value === '' && (el.getAttribute('data-necessary').toLowerCase() === 'true')) {
            results1.push(el);
          }
        }
        return results1;
      })();
      this.disable_action_buttons();
      if (emptyElements.length > 0) {
        if (ajaxPartialAct === 'score') {
          results.push(this.submit_observation(form, formElements, ajaxAct, ajaxArgs, true));
        } else {
          results.push(this.display_partial_reasons(form));
        }
      } else {
        results.push(this.submit_observation(form, formElements, ajaxAct, ajaxArgs));
      }
    }
    return results;
  };

  NHMobileForm.prototype.disable_action_buttons = function() {
    var action_buttons, button, i, len, results;
    action_buttons = document.querySelectorAll('input[type="submit"], input[type="reset"]');
    results = [];
    for (i = 0, len = action_buttons.length; i < len; i++) {
      button = action_buttons[i];
      results.push(button.setAttribute('disabled', 'disabled'));
    }
    return results;
  };

  NHMobileForm.prototype.enableActionButtons = function() {
    var action_buttons, button, i, len, results;
    action_buttons = document.querySelectorAll('input[type="submit"], input[type="reset"]');
    results = [];
    for (i = 0, len = action_buttons.length; i < len; i++) {
      button = action_buttons[i];
      results.push(button.removeAttribute('disabled'));
    }
    return results;
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

  NHMobileForm.prototype.display_partial_reasons = function(form) {
    var form_type, observation, partials_url;
    form_type = form.getAttribute('data-source');
    observation = form.getAttribute('data-type');
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
      return new window.NH.NHModal('partial_reasons', server_data.title, msg + select, [can_btn, con_btn], 0, form);
    });
  };

  NHMobileForm.prototype.submit_observation = function(form, elements, endpoint, args, partial) {
    var el, formValues, i, key, len, self, serialised_string, type, url, value;
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
    self = this;
    return Promise.when(this.call_resource(url, serialised_string)).then(function(raw_data) {
      var act_btn, body, btn, buttons, can_btn, cls, data, data_action, j, k, len1, len2, os, pos, ref, ref1, rt_url, server_data, st_url, sub_ob, task, task_list, tasks, triggered_tasks;
      server_data = raw_data[0];
      data = server_data.data;
      body = document.getElementsByTagName('body')[0];
      if (server_data.status === 'success' && data.status === 3) {
        data_action = !partial ? 'submit' : 'display_partial_reasons';
        can_btn = '<a href="#" data-action="renable" ' + 'data-target="submit_observation">Cancel</a>';
        act_btn = '<a href="#" data-target="submit_observation" ' + 'data-action="' + data_action + '" data-ajax-action="' + data.next_action + '">Submit</a>';
        new window.NH.NHModal('submit_observation', server_data.title + ' for ' + self.patient_name() + '?', server_data.desc, [can_btn, act_btn], 0, form);
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
        return new window.NH.NHModal('cancel_success', server_data.title, task_list, buttons, 0, body);
      } else {
        self.enableActionButtons();
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
    var cancel_reason, cover, dialog_id, element, form, form_elements, reason, reason_to_use;
    form = event.detail.parent_node;
    form_elements = (function() {
      var i, len, ref, results;
      ref = form.elements;
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
      self.submit_observation(self.form, form_elements, event.detail.action, self.form.getAttribute('ajax-args'));
      dialog_id = document.getElementById(event.detail.target);
      cover = document.getElementById('cover');
      document.getElementsByTagName('body')[0].removeChild(cover);
      return dialog_id.parentNode.removeChild(dialog_id);
    }
  };

  NHMobileForm.prototype.process_post_score_submit = function(event, self) {
    var element, endpoint, form, form_elements;
    form = event.detail.parent_node;
    form_elements = (function() {
      var i, len, ref, results;
      ref = form.elements;
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        element = ref[i];
        if (!element.classList.contains('exclude')) {
          results.push(element);
        }
      }
      return results;
    })();
    endpoint = event.detail.endpoint;
    return self.submit_observation(form, form_elements, endpoint, form.getAttribute('ajax-args'));
  };

  NHMobileForm.prototype.handle_display_partial_reasons = function(event) {
    var form;
    if (!event.handled) {
      form = event.detail.parent_node;
      this.display_partial_reasons(form);
      return event.handled = true;
    }
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


/* istanbul ignore if */

if (!window.NH) {
  window.NH = {};
}


/* istanbul ignore else */

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobileForm = NHMobileForm;
}
