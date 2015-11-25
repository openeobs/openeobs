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
    ref = this.form.elements;
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
      timeout = new CustomEvent('form_timeout', {
        'detail': 'form timed out'
      });
      return document.dispatchEvent(timeout);
    };
    window.form_timeout = setTimeout(window.timeout_func, this.form_timeout);
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
    var cond, crit_target, crit_val, criteria, criterias, i, input, len, max, min, operator, other_input, other_input_value, results, target_input, target_input_value, value;
    event.preventDefault();
    this.reset_form_timeout(this);
    input = event.srcElement ? event.srcElement : event.target;
    this.reset_input_errors(input);
    value = parseFloat(input.value);
    min = parseFloat(input.getAttribute('min'));
    max = parseFloat(input.getAttribute('max'));
    if (typeof value !== 'undefined' && !isNaN(value) && value !== '') {
      if (input.getAttribute('type') === 'number') {
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
          results = [];
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
          return results;
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
    var action_buttons, btn, button, element, empty_elements, form_elements, i, invalid_elements, j, len, len1, msg;
    event.preventDefault();
    this.reset_form_timeout(this);
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
        if (!element.value) {
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
    } else if (invalid_elements.length > 0) {
      msg = '<p class="block">The form contains errors, please correct ' + 'the errors and resubmit</p>';
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
      msg = '<p class="block">Please state reason for ' + 'submitting partial observation</p>';
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
      var btn, msg;
      msg = '<p class="block">Please pick the task again from the task list ' + 'if you wish to complete it</p>';
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
    var element, endpoint, form_elements;
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
