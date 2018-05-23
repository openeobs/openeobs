# NHMobilePatient contains utilities for working with
# the nh_eobs_mobile patient view, namely getting data
#  and passing it to graph lib
### istanbul ignore next ###
class NHMobilePatient extends NHMobile

  String.prototype.capitalize = () ->
    @.charAt(0).toUpperCase() + @.slice(1)

  constructor: (refused = false, partialType = "dot") ->
    self = @
    super()
    # find the obs menu on page
    self.setUpObsMenu(self)
    self.setUpTableView()
    self.setUpChartSelect(self)
    self.setUpTabs(self)
    dataId = document.getElementById("graph-content").getAttribute("data-id")
    self.refused = refused
    self.partial_type = partialType
    self.chart_element = "chart"
    self.table_element = "table-content"

    Promise.when(
      @call_resource(@.urls["ajax_get_patient_obs"]("ews", dataId)))
      .then (rawData) ->
        serverData = rawData[0]
        data = serverData.data
        obsData = data.obs
        self.drawGraph(self, obsData, "ews")

  setUpObsMenu: (self) ->
    obsMenu = document.getElementById("obsMenu")
    if obsMenu
      obsMenu.style.display = "none"
    obs = document.getElementById("take-observation")
    ### istanbul ignore else ###
    if obs
      obs.addEventListener("click", (e) ->
        self.handle_event(e, self.showObsMenu, true)
      )

  setUpTableView: () ->
    table_view = document.getElementById("table-content")
    table_view.style.display = "none"

  setUpChartSelect: (self) ->
    chartSelect = document.getElementById("chart_select")
    if chartSelect
      chartSelect.addEventListener("change", (event) ->
        self.handle_event(event, self.changeChart, false, [self])
      )

  setUpTabs: (self) ->
    tabs_el = document.getElementsByClassName("tabs")
    tabs = tabs_el[0].getElementsByTagName("a")
    for tab in tabs
      tab.addEventListener("click", (e) ->
        self.handle_event(e, self.handleTabs, true)
      )

  handleTabs: (event) ->
#    event.preventDefault()
#    if not event.handled
    tabs = document.getElementsByClassName("tabs")[0]
    .getElementsByTagName("a")
    for tab in tabs
      tab.classList.remove("selected")
    document.getElementById("graph-content").style.display = "none"
    document.getElementById("table-content").style.display = "none"
#    targetEl = if event.srcElement then event.srcElement else event.target
    targetEl = event.src_el
    targetEl.classList.add("selected")
    tabTarget = targetEl.getAttribute("href").replace("#", "")
    document.getElementById(tabTarget).style.display = "block"
#      event.handled = true

  changeChart: (event, self) ->
    chart = document.getElementById(self.chart_element)
    table = document.getElementById(self.table_element)
    chart.innerHTML = ""
    table.innerHTML = ""
    newDataModel = event.src_el.value
    dataId = document.getElementById("graph-content").getAttribute("data-id")
    Promise.when(
      self.call_resource(
        self.urls["ajax_get_patient_obs"](newDataModel, dataId)
      )
    ).then (rawData) ->
      serverData = rawData[0]
      data = serverData.data
      obsData = data.obs
      self.drawGraph(self, obsData, newDataModel)

  showObsMenu: (event) ->
#    event.preventDefault()
    obsMenu = document.getElementById("obsMenu")
    body = document.getElementsByTagName("body")[0]
    menu = "<ul class=\"menu\">" + obsMenu.innerHTML + "</ul>"
    pats = document.querySelectorAll("a.patientInfo h3.name strong")
    pat = ""
    if pats.length > 0
      pat = pats[0].textContent
    new NHModal("obs_menu",
      "Pick an observation for " + pat, menu,
      ["<a href=\"#\" data-action=\"close\" "+
        "data-target=\"obs_menu\">Cancel</a>"], 0, body)

  drawGraph: (self, serverData, dataModel) ->
    graphContent = document.getElementById("graph-content")
    controls = document.getElementById("controls")
    chartEl = document.getElementById(self.chart_element)
    tableEl = document.getElementById(self.table_element)
    graphTabs = graphContent.parentNode.getElementsByClassName("tabs")[0]
    activeTab =
      graphTabs.getElementsByClassName("selected")[0].getAttribute('href')
    chartFuncName = "draw" + dataModel.capitalize() + "Chart"
    tableFuncName = "draw" + dataModel.capitalize() + "Table"
    if serverData.length > 0
      visualisation_els = [controls, graphTabs, chartEl, graphContent, tableEl]
      for el in visualisation_els
        el.style.display = "block"
      chartFunc = window[chartFuncName]
      tableFunc = window[tableFuncName]
      validChart = (typeof chartFunc is "function")
      validTable = (typeof tableFunc is "function")
      if validChart
        chartFunc(self, serverData)
      if validTable
        tableFunc(self, serverData)
      if not validChart or not validTable
        graphTabs.style.display = "none"
      else
        graphTabs.style.display = "block"
        if activeTab is "#graph-content"
          tableEl.style.display = "none"
        else
          graphContent.style.display = "none"
    else
      controls.style.display = "none"
      graphContent.style.display = "block"
      chartEl.innerHTML = '<h2 class="placeholder">' +
        'No observation data available for patient' + '</h2>'
      graphTabs.style.display = "none"


### istanbul ignore if ###
if !window.NH
  window.NH = {}
### istanbul ignore else ###
window?.NH.NHMobilePatient = NHMobilePatient