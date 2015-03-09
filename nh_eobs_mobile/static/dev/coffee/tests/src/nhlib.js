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
    return date;
  };

  NHLib.prototype.date_to_string = function(date) {
    return date.getFullYear() + "-" + this.leading_zero(date.getMonth() + 1) + "-" + this.leading_zero(date.getDate()) + " " + this.leading_zero(date.getHours()) + ":" + this.leading_zero(date.getMinutes()) + ":" + this.leading_zero(date.getSeconds());
  };

  NHLib.prototype.date_to_dob_string = function(date) {
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
