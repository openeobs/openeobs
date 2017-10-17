
/* istanbul ignore next */
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


/* istanbul ignore if */

if (!window.NH) {
  window.NH = {};
}


/* istanbul ignore else */

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobilePatient = NHMobilePatientMentalHealth;
}
