# NHMobilePatient contains utilities for working with
# the nh_eobs_mobile patient view, namely getting data
#  and passing it to graph lib
### istanbul ignore next ###
class NHMobilePatient extends NHMobile

  constructor: (refused = false, partial_type = 'dot') ->
    self = @
    super()
    # find the obs menu on page
    obs_menu = document.getElementById('obsMenu')
    if obs_menu
      obs_menu.style.display = 'none'
    table_view = document.getElementById('table-content')
    table_view.style.display = 'none'

    obs = document.getElementsByClassName('obs')
    ### istanbul ignore else ###
    if obs and obs.length > 0
      obs[0].addEventListener('click', (e) ->
        self.handle_event(e, self.show_obs_menu, true)
      )

    chart_select = document.getElementById('chart_select')
    if chart_select
      chart_select.addEventListener('change', (event) ->
        self.handle_event(event, self.change_chart, false, [self])
      )

    tabs_el = document.getElementsByClassName('tabs')
    tabs = tabs_el[0].getElementsByTagName('a')
    for tab in tabs
      tab.addEventListener('click', (e) ->
        self.handle_event(e, self.handle_tabs, true)
      )

    data_id = document.getElementById('graph-content').getAttribute('data-id')

    self.refused = refused
    self.partial_type = partial_type
    self.chart_element = 'chart'
    self.table_element = 'table-content'

    Promise.when(
      @call_resource(@.urls['ajax_get_patient_obs']('ews', data_id)))
      .then (raw_data) ->
        server_data = raw_data[0]
        data = server_data.data
        obs_data = data.obs
        self.draw_graph(self, obs_data, 'ews')

  handle_tabs: (event) ->
#    event.preventDefault()
#    if not event.handled
    tabs = document.getElementsByClassName('tabs')[0]
    .getElementsByTagName('a')
    for tab in tabs
      tab.classList.remove('selected')
    document.getElementById('graph-content').style.display = 'none'
    document.getElementById('table-content').style.display = 'none'
#    target_el = if event.srcElement then event.srcElement else event.target
    target_el = event.src_el
    target_el.classList.add('selected')
    tab_target = target_el.getAttribute('href').replace('#', '')
    document.getElementById(tab_target).style.display = 'block'
#      event.handled = true

  change_chart: (event, self) ->
    chart = document.getElementById(self.chart_element)
    table = document.getElementById(self.table_element)
    chart.innerHTML = ''
    table.innerHTML = ''
    new_data_model = event.src_el.value
    data_id = document.getElementById('graph-content').getAttribute('data-id')
    Promise.when(
      self.call_resource(
        self.urls['ajax_get_patient_obs'](new_data_model, data_id)
      )
    ).then (raw_data) ->
      server_data = raw_data[0]
      data = server_data.data
      obs_data = data.obs
      self.draw_graph(self, obs_data, new_data_model)

  show_obs_menu: (event) ->
#    event.preventDefault()
    obs_menu = document.getElementById('obsMenu')
    body = document.getElementsByTagName('body')[0]
    menu = '<ul class="menu">' + obs_menu.innerHTML + '</ul>'
    pats = document.querySelectorAll('a.patientInfo h3.name strong')
    pat = ''
    if pats.length > 0
      pat = pats[0].textContent
    new NHModal('obs_menu',
      'Pick an observation for ' + pat, menu,
      ['<a href="#" data-action="close" data-target="obs_menu">Cancel</a>'],
      0, body)

  draw_graph: (self, server_data, data_model) ->
    graph_content = document.getElementById('graph-content')
    controls = document.getElementById('controls')
    chart_el = document.getElementById(self.chart_element)
    graph_tabs = graph_content.parentNode.getElementsByClassName('tabs')[0]
    chart_func_name = 'draw_' + data_model + '_chart'
    table_func_name = 'draw_' + data_model + '_table'
    if server_data.length > 0
      controls.style.display = 'block'
      graph_tabs.style.display = 'block'
      chart_func = window[chart_func_name]
      table_func = window[table_func_name]
      valid_chart = (typeof chart_func is 'function')
      valid_table = (typeof table_func is 'function')
      if not valid_chart or not valid_table
        graph_tabs.style.display = 'none'
      else
        graph_tabs.style.display = 'block'
      if valid_chart
        chart_func(self, server_data)
      if valid_table
        table_func(self, server_data)
    else
      controls.style.display = 'none'
      chart_el.innerHTML = '<h2>No observation data available for patient</h2>'
      graph_tabs.style.display = 'none'

### istanbul ignore if ###
if !window.NH
  window.NH = {}
### istanbul ignore else ###
window?.NH.NHMobilePatient = NHMobilePatient