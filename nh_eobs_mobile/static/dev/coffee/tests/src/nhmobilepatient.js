
/* istanbul ignore next */
var NHMobilePatient,
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

NHMobilePatient = (function(superClass) {
  extend(NHMobilePatient, superClass);

  function NHMobilePatient(refused, partial_type) {
    var chart_select, data_id, i, len, obs, obs_menu, self, tab, table_view, tabs, tabs_el;
    if (refused == null) {
      refused = false;
    }
    if (partial_type == null) {
      partial_type = 'dot';
    }
    self = this;
    NHMobilePatient.__super__.constructor.call(this);
    obs_menu = document.getElementById('obsMenu');
    if (obs_menu) {
      obs_menu.style.display = 'none';
    }
    table_view = document.getElementById('table-content');
    table_view.style.display = 'none';
    obs = document.getElementsByClassName('obs');

    /* istanbul ignore else */
    if (obs && obs.length > 0) {
      obs[0].addEventListener('click', function(e) {
        return self.handle_event(e, self.show_obs_menu, true);
      });
    }
    chart_select = document.getElementById('chart_select');
    if (chart_select) {
      chart_select.addEventListener('change', function(event) {
        return self.handle_event(event, self.change_chart, false, [self]);
      });
    }
    tabs_el = document.getElementsByClassName('tabs');
    tabs = tabs_el[0].getElementsByTagName('a');
    for (i = 0, len = tabs.length; i < len; i++) {
      tab = tabs[i];
      tab.addEventListener('click', function(e) {
        return self.handle_event(e, self.handle_tabs, true);
      });
    }
    data_id = document.getElementById('graph-content').getAttribute('data-id');
    self.refused = refused;
    self.partial_type = partial_type;
    self.chart_element = 'chart';
    Promise.when(this.call_resource(this.urls['ajax_get_patient_obs']('ews', data_id))).then(function(raw_data) {
      var data, obs_data, server_data;
      server_data = raw_data[0];
      data = server_data.data;
      obs_data = data.obs;
      return self.draw_graph(self, obs_data, 'ews');
    });
  }

  NHMobilePatient.prototype.handle_tabs = function(event) {
    var i, len, tab, tab_target, tabs, target_el;
    tabs = document.getElementsByClassName('tabs')[0].getElementsByTagName('a');
    for (i = 0, len = tabs.length; i < len; i++) {
      tab = tabs[i];
      tab.classList.remove('selected');
    }
    document.getElementById('graph-content').style.display = 'none';
    document.getElementById('table-content').style.display = 'none';
    target_el = event.src_el;
    target_el.classList.add('selected');
    tab_target = target_el.getAttribute('href').replace('#', '');
    return document.getElementById(tab_target).style.display = 'block';
  };

  NHMobilePatient.prototype.change_chart = function(event, self) {
    var chart, data_id, new_data_model;
    chart = document.getElementById(self.chart_element);
    chart.innerHTML = '';
    new_data_model = event.src_el.value;
    data_id = document.getElementById('graph-content').getAttribute('data-id');
    return Promise.when(self.call_resource(self.urls['ajax_get_patient_obs'](new_data_model, data_id))).then(function(raw_data) {
      var data, obs_data, server_data;
      server_data = raw_data[0];
      data = server_data.data;
      obs_data = data.obs;
      return self.draw_graph(self, obs_data, new_data_model);
    });
  };

  NHMobilePatient.prototype.show_obs_menu = function(event) {
    var body, menu, obs_menu, pat, pats;
    obs_menu = document.getElementById('obsMenu');
    body = document.getElementsByTagName('body')[0];
    menu = '<ul class="menu">' + obs_menu.innerHTML + '</ul>';
    pats = document.querySelectorAll('a.patientInfo h3.name strong');
    pat = '';
    if (pats.length > 0) {
      pat = pats[0].textContent;
    }
    return new NHModal('obs_menu', 'Pick an observation for ' + pat, menu, ['<a href="#" data-action="close" data-target="obs_menu">Cancel</a>'], 0, body);
  };

  NHMobilePatient.prototype.draw_graph = function(self, server_data, data_model) {
    var chart, chart_func, controls, draw_func_name, graph_content, graph_tabs;
    draw_func_name = 'draw_' + data_model + '_chart';
    if (server_data.length > 0) {
      chart_func = window[draw_func_name];
      if (typeof chart_func === 'function') {
        return chart_func(self, server_data);
      } else {
        return console.log('issue drawing chart');
      }
    } else {
      graph_content = document.getElementById('graph-content');
      controls = document.getElementById('controls');
      chart = document.getElementById(self.chart_element);
      graph_tabs = graph_content.parentNode.getElementsByClassName('tabs');
      controls.style.display = 'none';
      chart.innerHTML = '<h2>No observation data available for patient</h2>';
      return graph_tabs[0].style.display = 'none';
    }
  };

  return NHMobilePatient;

})(NHMobile);


/* istanbul ignore if */

if (!window.NH) {
  window.NH = {};
}


/* istanbul ignore else */

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHMobilePatient = NHMobilePatient;
}
