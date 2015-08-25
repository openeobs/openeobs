
/* istanbul ignore next */
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

        /* istanbul ignore else */
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

        /* istanbul ignore if */
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

      /* istanbul ignore else */
      if (patient.full_name) {
        patient_info += '<dt>Name:</dt><dd>' + patient.full_name + '</dd>';
      }

      /* istanbul ignore else */
      if (patient.gender) {
        patient_info += '<dt>Gender:</dt><dd>' + patient.gender + '</dd>';
      }
    }

    /* istanbul ignore else */
    if (patient.dob) {
      patientDOB = self.date_from_string(patient.dob);
      patient_info += '<dt>DOB:</dt><dd>' + self.date_to_dob_string(patientDOB) + '</dd>';
    }

    /* istanbul ignore else */
    if (patient.location) {
      patient_info += '<dt>Location:</dt><dd>' + patient.location;
    }
    if (patient.parent_location) {
      patient_info += ',' + patient.parent_location + '</dd>';
    } else {
      patient_info += '</dd>';
    }

    /* istanbul ignore else */
    if (patient.ews_score) {
      patient_info += '<dt class="twoline">Latest Score:</dt>' + '<dd class="twoline">' + patient.ews_score + '</dd>';
    }

    /* istanbul ignore else */
    if (patient.ews_trend) {
      patient_info += '<dt>NEWS Trend:</dt><dd>' + patient.ews_trend + '</dd>';
    }

    /* istanbul ignore else */
    if (patient.other_identifier) {
      patient_info += '<dt>Hospital ID:</dt><dd>' + patient.other_identifier + '</dd>';
    }

    /* istanbul ignore else */
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

      /* istanbul ignore else */
      if (data.full_name) {
        patient_name += ' ' + data.full_name;
      }

      /* istanbul ignore else */
      if (data.gender) {
        patient_name += '<span class="alignright">' + data.gender + '</span>';
      }
      patient_details = self.render_patient_info(data, true, self) + '<p><a href="' + self.urls['single_patient'](patient_id).url + '" id="patient_obs_fullscreen" class="button patient_obs">' + 'View Patient Observation Data</a></p>';
      cancel = '<a href="#" data-target="patient_info" ' + 'data-action="close">Cancel</a>';
      new NHModal('patient_info', patient_name, patient_details, [cancel], 0, document.getElementsByTagName('body')[0]);
      fullscreen = document.getElementById('patient_obs_fullscreen');
      return fullscreen.addEventListener('click', self.fullscreen_patient_info);
    });
    return true;
  };

  NHMobile.prototype.fullscreen_patient_info = function(event) {
    var container, options, options_close, page;
    event.preventDefault();

    /* istanbul ignore else */
    if (!event.handled) {
      container = document.createElement('div');
      container.setAttribute('class', 'full-modal');
      options = document.createElement('p');
      options_close = document.createElement('a');
      options_close.setAttribute('href', '#');
      options_close.setAttribute('id', 'closeFullModal');
      options_close.innerText = 'Close popup';
      options_close.addEventListener('click', function(event) {
        var body;
        if (!event.handled) {
          body = document.getElementsByTagName('body')[0];
          body.removeChild(document.getElementsByClassName('full-modal')[0]);
          return event.handled = true;
        }
      });
      options.appendChild(options_close);
      container.appendChild(options);
      page = document.createElement('iframe');
      page.setAttribute('src', event.srcElement.getAttribute('href'));

      /* istanbul ignore next */
      page.onload = function() {
        var contents, header, iframe, modal, obs;
        modal = document.getElementsByClassName('full-modal')[0];
        iframe = modal.getElementsByTagName('iframe')[0];
        contents = iframe.contentDocument ? iframe.contentDocument : iframe.contentWindow.document;
        header = contents.getElementsByClassName('header')[0];
        header.parentNode.removeChild(header);
        obs = contents.getElementsByClassName('obs')[0];
        return obs.parentNode.removeChild(obs);
      };
      container.appendChild(page);
      document.getElementsByTagName('body')[0].appendChild(container);
      return event.handled = true;
    }
  };

  return NHMobile;

})(NHLib);


/* istanbul ignore if */

if (!window.NH) {
  window.NH = {};
}


/* istanbul ignore else */

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobile = NHMobile;
}
