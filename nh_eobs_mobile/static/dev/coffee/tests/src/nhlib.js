
/* istanbul ignore next */
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

    /* istanbul ignore else */
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


/* istanbul ignore else */

if (!window.NH) {
  window.NH = {};
}

window.NH.NHLib = NHLib;
