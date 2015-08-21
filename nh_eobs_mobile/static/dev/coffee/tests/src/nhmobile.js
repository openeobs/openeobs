
/* istanbul ignore next */
var NHMobile, Promise,
  indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; },
  slice = [].slice,
  bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

if (!(indexOf.call(document.documentElement, 'classList') >= 0) && Object.defineProperty && typeof HTMLElement !== 'undefined') {
  Object.defineProperty(HTMLElement.prototype, 'classList', {
    get: function() {
      var ret, self;
      self = this;
      function update(fn) {
        return function(value) {
          var classes = self.className.split(/\s+/);
          var index = classes.indexOf(value);

          fn(classes, index, value);
          self.className = classes.join(" ");
        }
      };
      ret = {
        add: update(function(classes, index, value) {
          ~index || classes.push(value);
        }),
        remove: update(function(classes, index) {
          ~index && classes.splice(index, 1);
        }),
        toggle: update(function(classes, index, value) {
          if (~index) {
            classes.splice(index, 1);
          } else {
            classes.push(value);
          }
        }),
        contains: function(value) {
          return !!~self.className.split(/\s+/).indexOf(value);
        },
        item: function(i) {
          return self.className.split(/\s+/)[i] || null;
        }
      };
      Object.defineProperty(ret, 'length', {
        get: function() {
          return self.className.split(/\s+/).length;
        }
      });
      return ret;
    }
  });
}

Promise = (function() {
  Promise.when = function() {
    var args, fn, j, len, num_uncompleted, promise, task, task_id, tasks;
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
    for (task_id = j = 0, len = tasks.length; j < len; task_id = ++j) {
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
    var callback, j, len, ref, results;
    this.completed = true;
    this.data = arguments;
    ref = this.callbacks;
    results = [];
    for (j = 0, len = ref.length; j < len; j++) {
      callback = ref[j];
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
          console.log('data: ', data);
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

  NHMobile.prototype.get_patient_info = function(patient_id, self) {
    var patient_url;
    patient_url = this.urls.json_patient_info(patient_id).url;
    Promise.when(this.process_request('GET', patient_url)).then(function(server_data) {
      var cancel, data, fullscreen, patientDOB, patient_details, patient_name;
      data = server_data[0][0];
      patient_name = '';
      patient_details = '';
      if (data.full_name) {
        patient_name += ' ' + data.full_name;
      }
      if (data.gender) {
        patient_name += '<span class="alignright">' + data.gender + '</span>';
      }
      if (data.dob) {
        patientDOB = self.date_from_string(data.dob);
        patient_details += '<dt>DOB:</dt><dd>' + self.date_to_dob_string(patientDOB) + '</dd>';
      }
      if (data.location) {
        patient_details += '<dt>Location:</dt><dd>' + data.location;
      }
      if (data.parent_location) {
        patient_details += ',' + data.parent_location + '</dd>';
      } else {
        patient_details += '</dd>';
      }
      if (data.ews_score) {
        patient_details += '<dt class="twoline">Latest Score:</dt>' + '<dd class="twoline">' + data.ews_score + '</dd>';
      }
      if (data.other_identifier) {
        patient_details += '<dt>Hospital ID:</dt><dd>' + data.other_identifier + '</dd>';
      }
      if (data.patient_identifier) {
        patient_details += '<dt>NHS Number:</dt><dd>' + data.patient_identifier + '</dd>';
      }
      patient_details = '<dl>' + patient_details + '</dl><p><a href="' + self.urls['single_patient'](patient_id).url + '" id="patient_obs_fullscreen" class="button patient_obs">' + 'View Patient Observation Data</a></p>';
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
      container.appendChild(page);
      document.getElementsByTagName('body')[0].appendChild(container);
      return event.handled = true;
    }
  };

  return NHMobile;

})(NHLib);


/* istanbul ignore else */

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobile = NHMobile;
}
