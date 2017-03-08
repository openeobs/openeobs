
/* istanbul ignore next */
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
    obs = document.getElementsByClassName("obs");

    /* istanbul ignore else */
    if (obs && obs.length > 0) {
      return obs[0].addEventListener("click", function(e) {
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

  NHMobilePatient.prototype.drawGraph = function(self, serverData, dataModel) {
    var activeTab, chartEl, chartFunc, chartFuncName, controls, el, graphContent, graphTabs, i, len, tableEl, tableFunc, tableFuncName, validChart, validTable, visualisation_els;
    graphContent = document.getElementById("graph-content");
    controls = document.getElementById("controls");
    chartEl = document.getElementById(self.chart_element);
    tableEl = document.getElementById(self.table_element);
    graphTabs = graphContent.parentNode.getElementsByClassName("tabs")[0];
    activeTab = graphTabs.getElementsByClassName("selected")[0].getAttribute('href');
    chartFuncName = "draw" + dataModel.capitalize() + "Chart";
    tableFuncName = "draw" + dataModel.capitalize() + "Table";
    if (serverData.length > 0) {
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
        return graphTabs.style.display = "none";
      } else {
        graphTabs.style.display = "block";
        if (activeTab === "#graph-content") {
          return tableEl.style.display = "none";
        } else {
          return graphContent.style.display = "none";
        }
      }
    } else {
      controls.style.display = "none";
      graphContent.style.display = "block";
      chartEl.innerHTML = "<h2>No observation data available for patient</h2>";
      return graphTabs.style.display = "none";
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
