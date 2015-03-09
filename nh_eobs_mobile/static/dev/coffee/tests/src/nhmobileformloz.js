var NHMobileFormLoz,
  bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty,
  indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

NHMobileFormLoz = (function(superClass) {
  extend(NHMobileFormLoz, superClass);

  function NHMobileFormLoz() {
    this.submit_observation = bind(this.submit_observation, this);
    var self;
    NHMobileFormLoz.__super__.constructor.call(this);
    this.patient_name_el = document.getElementsByClassName('news-name')[0];
    this.patient_name = function() {
      return this.patient_name_el.textContent;
    };
    self = this;
  }

  NHMobileFormLoz.prototype.submit_observation = function(self, elements, endpoint, args) {
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
      var btn_str, buttons, cancel, cancel_button, cls, data, i, len, ob_s, obs_sub, ref, sub, sub_ob, task, task_button, task_list, task_url, tasks, title, triggered_tasks;
      data = server_data[0][0];
      if (data && data.status === 3) {
        sub = '<a href="#" data-target="submit_observation" ' + 'data-action="submit" data-ajax-action="' + data.modal_vals['next_action'] + '">Submit</a>';
        cancel = '<a href="#" data-action="close" ' + 'data-target="submit_observation">Cancel</a>';
        new window.NH.NHModal('submit_observation', data.modal_vals['title'] + ' for ' + self.patient_name() + '?', data.modal_vals['content'], [cancel, sub], 0, self.form);
        if (indexOf.call(data.score, 'clinical_risk') >= 0) {
          sub_ob = document.getElementById('submit_observation');
          cls = 'clinicalrisk-' + data.score['clinical_risk'].toLowerCase();
          return sub_ob.classList.add(cls);
        }
      } else if (data && data.status === 1) {
        triggered_tasks = '';
        task_url = self.urls['task_list']().url;
        btn_str = '<a href="' + task_url + '" data-action="confirm">' + 'Go to My Tasks</a>';
        buttons = [btn_str];
        if (data.related_tasks.length === 1) {
          triggered_tasks = '<p>' + data.related_tasks[0].summary + '</p>';
          task_url = self.urls['single_task'](data.related_tasks[0].id).url;
          buttons.push('<a href="' + task_url + '">Confirm</a>');
        } else if (data.related_tasks.length > 1) {
          tasks = '';
          ref = data.related_tasks;
          for (i = 0, len = ref.length; i < len; i++) {
            task = ref[i];
            task_url = self.urls['single_task'](task.id).url;
            tasks += '<li><a href="' + task_url + '">' + task.summary + '</a></li>';
          }
          triggered_tasks = '<ul class="menu">' + tasks + '</ul>';
        }
        obs_sub = '<p>Observation was submitted</p>';
        task_list = triggered_tasks ? triggered_tasks : obs_sub;
        ob_s = 'Observation successfully submitted';
        title = triggered_tasks ? 'Action required' : ob_s;
        return new window.NH.NHModal('submit_success', title, task_list, buttons, 0, document.getElementsByTagName('body')[0]);
      } else if (data && data.status === 4) {
        task_button = '<a href="' + self.urls['task_list']().url + '" data-action="confirm" data-target="cancel_success">' + 'Go to My Tasks</a>';
        return new window.NH.NHModal('cancel_success', 'Task successfully cancelled', '', [task_button], 0, self.form);
      } else {
        cancel_button = '<a href="#" data-action="close" ' + 'data-target="submit_error">Cancel</a>';
        return new window.NH.NHModal('submit_error', 'Error submitting observation', 'Server returned an error', [cancel_button], 0, self.form);
      }
    });
  };

  NHMobileFormLoz.prototype.reset_input_errors = function(input) {
    var container_el, error_el;
    container_el = input.parentNode;
    error_el = container_el.getElementsByClassName('errors')[0];
    container_el.classList.remove('error');
    input.classList.remove('error');
    if (error_el) {
      return container_el.removeChild(error_el);
    }
  };

  NHMobileFormLoz.prototype.add_input_errors = function(input, error_string) {
    var container_el, error_el;
    container_el = input.parentNode;
    error_el = document.createElement('div');
    error_el.setAttribute('class', 'errors');
    container_el.classList.add('error');
    input.classList.add('error');
    error_el.innerHTML = '<label for="' + input.name + '" class="error">' + error_string + '</label>';
    return container_el.appendChild(error_el);
  };

  NHMobileFormLoz.prototype.hide_triggered_elements = function(field) {
    var el, inp;
    el = document.getElementById('parent_' + field);
    el.style.display = 'none';
    inp = document.getElementById(field);
    return inp.classList.add('exclude');
  };

  NHMobileFormLoz.prototype.show_triggered_elements = function(field) {
    var el, inp;
    el = document.getElementById('parent_' + field);
    el.style.display = 'inline-block';
    inp = document.getElementById(field);
    return inp.classList.remove('exclude');
  };

  return NHMobileFormLoz;

})(NHMobileForm);

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobileFormLoz = NHMobileFormLoz;
}
