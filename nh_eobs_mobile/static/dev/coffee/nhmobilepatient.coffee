# NHMobilePatient contains utilities for working with the nh_eobs_mobile patient view, namely getting data and passing it to graph lib
class NHMobilePatient extends NHMobile

  constructor: () ->
    self = @
    super()
    # find the obs menu on page
    obs_menu = document.getElementById('obsMenu')
    obs_menu.style.display = 'none'
    table_view = document.getElementById('table-content')
    table_view.style.display = 'none'

    document.getElementsByClassName('obs')[0].addEventListener('click', @.show_obs_menu)

    tabs = document.getElementsByClassName('tabs')[0].getElementsByTagName('a')
    for tab in tabs
      tab.addEventListener('click', @.handle_tabs)

    Promise.when(@call_resource(@.urls['ajax_get_patient_obs'](document.getElementById('graph-content').getAttribute('data-id')))).then (server_data) ->
      self.draw_graph(self, server_data)

  handle_tabs: (event) =>
    event.preventDefault()
    tabs = document.getElementsByClassName('tabs')[0].getElementsByTagName('a')
    for tab in tabs
      tab.classList.remove('selected')
    document.getElementById('graph-content').style.display = 'none'
    document.getElementById('table-content').style.display = 'none'
    event.srcElement.classList.add('selected')
    $(event.srcElement.getAttribute('href')).show()

  show_obs_menu: (event) =>
    event.preventDefault()
    obs_menu = document.getElementById('obsMenu')
    new window.NH.NHModal('obs_menu', 'Pick an observation for ', '<ul class="menu">'+obs_menu.innerHTML+'</ul>', ['<a href="#" data-action="close" data-target="obs_menu">Cancel</a>'], 0, document.getElementsByTagName('body')[0])


  draw_graph: (self, server_data) =>
    obs = server_data[0][0].obs.reverse()
    svg = new window.NH.NHGraphLib('#graph-content')
    resp_rate_graph = new window.NH.NHGraph()
    resp_rate_graph.options.keys = ['respiration_rate']
    resp_rate_graph.options.label = 'RR'
    resp_rate_graph.options.measurement = '/min'
    resp_rate_graph.axes.y.min = 0
    resp_rate_graph.axes.y.max = 60
    resp_rate_graph.options.normal.min = 12
    resp_rate_graph.options.normal.max = 20
    resp_rate_graph.style.dimensions.height = 250
    resp_rate_graph.style.data_style = 'linear'
    resp_rate_graph.style.label_width = 50

    oxy_graph = new window.NH.NHGraph()
    oxy_graph.options.keys = ['indirect_oxymetry_spo2']
    oxy_graph.options.label = 'Spo2'
    oxy_graph.options.measurement = '%'
    oxy_graph.axes.y.min = 70
    oxy_graph.axes.y.max = 100
    oxy_graph.options.normal.min = 96
    oxy_graph.options.normal.max = 100
    oxy_graph.style.dimensions.height = 200
    oxy_graph.style.axis.x.hide = true
    oxy_graph.style.data_style = 'linear'
    oxy_graph.style.label_width = 50

    temp_graph = new window.NH.NHGraph()
    temp_graph.options.keys = ['body_temperature']
    temp_graph.options.label = 'Temp'
    temp_graph.options.measurement = '°C'
    temp_graph.axes.y.min = 15
    temp_graph.axes.y.max = 50
    temp_graph.options.normal.min = 35
    temp_graph.options.normal.max = 37.1
    temp_graph.style.dimensions.height = 200
    temp_graph.style.axis.x.hide = true
    temp_graph.style.data_style = 'linear'
    temp_graph.style.label_width = 50

    pulse_graph = new window.NH.NHGraph()
    pulse_graph.options.keys = ['pulse_rate']
    pulse_graph.options.label = 'HR'
    pulse_graph.options.measurement = '/min'
    pulse_graph.axes.y.min = 30
    pulse_graph.axes.y.max = 200
    pulse_graph.options.normal.min = 50
    pulse_graph.options.normal.max = 100
    pulse_graph.style.dimensions.height = 200
    pulse_graph.style.axis.x.hide = true
    pulse_graph.style.data_style = 'linear'
    pulse_graph.style.label_width = 50

    bp_graph = new window.NH.NHGraph();
    bp_graph.options.keys = ['blood_pressure_systolic', 'blood_pressure_diastolic']
    bp_graph.options.label = 'BP'
    bp_graph.options.measurement = 'mmHg';
    bp_graph.axes.y.min = 30;
    bp_graph.axes.y.max = 260;
    bp_graph.options.normal.min = 150;
    bp_graph.options.normal.max = 151;
    bp_graph.style.dimensions.height = 200;
    bp_graph.style.axis.x.hide = true;
    bp_graph.style.data_style = 'range';
    bp_graph.style.label_width = 50;

    score_graph = new window.NH.NHGraph();
    score_graph.options.keys = ['score'];
    score_graph.style.dimensions.height = 200;
    score_graph.style.data_style = 'stepped';
    score_graph.axes.y.min = 0;
    score_graph.axes.y.max = 22;
    score_graph.drawables.background.data =  [
      {"class": "green",s: 1, e: 4},
      {"class": "amber",s: 4,e: 6},
      {"class": "red",s: 6,e: 22}
    ]
    score_graph.style.label_width = 50;


    tabular_obs = new window.NH.NHTable()
    tabular_obs.keys = ['avpu_text', 'oxygen_administration_flag']
    tabular_obs.title = 'Tabular values'
    focus = new window.NH.NHFocus()
    context = new window.NH.NHContext()
    focus.graphs.push(resp_rate_graph)
    focus.graphs.push(oxy_graph)
    focus.graphs.push(temp_graph)
    focus.graphs.push(pulse_graph)
    focus.graphs.push(bp_graph)
    focus.tables.push(tabular_obs)
    focus.title = 'Individual values'
    focus.style.padding.right = 0
    context.graph = score_graph
    context.title = 'NEWS Score'
    svg.focus = focus
    svg.context = context
    #svg.options.controls.date.start = document.getElementById('date_start');
    #svg.options.controls.date.end = document.getElementById('date_end');
    #svg.options.controls.time.start = document.getElementById('time_start');
    #svg.options.controls.time.end = document.getElementById('time_end');
    #svg.options.controls.rangify = document.getElementById('range_derange');

    svg.data.raw = obs
    svg.init()
    svg.draw()

#      svg = graph_lib.svg
#      context = graph_lib.context
#      focus = graph_lib.focus
#      data = server_data[0][0]
#      svg.chartType = data.obsType
#      obs = data.obs.reverse()
#      console.log(obs)
#
#      if obs.length < 1
#        console.log('no data')
#
#      svg.ticks = Math.floor(svg.width/100)
#
#      context.earliestDate = svg.startParse(obs[0].date_started)
#      context.now = svg.startParse(obs[obs.length-1].date_started)
#      context.height = 200;
#      focus.chartHeight= 200;
#
#      if svg.isMob
#        if $(window).width() > $(window).height()
#          cED = new Date(context.now)
#          cED.setDate(cED.getDate() - svg.dateRange.landscape)
#          context.earliestDate = cED
#        else
#          cED = new Date(context.now)
#          cED.setDate(cED.getDate() - svg.dateRange.portrait)
#          context.earliestDate = cED
#
#
#      context.scoreRange = [
#        {class: "green", s:0, e:4},
#        {class: "amber", s:4, e:6},
#        {class: "red", s:6, e:21}
#      ]
#
#      min = null
#      max = null
#
#      plotO2 = false
#
#      for d in obs
#        d.date_started = svg.startParse(d.date_started)
#        d.body_temperature = d.body_temperature.toFixed(1)
#        if d.indirect_oxymetry_spo2
#          d.indirect_oxymetry_spo2_label = d.indirect_oxymetry_spo2 + '%'
#        if d.oxygen_administration_flag
#          plotO2 = true
#          d.inspired_oxygen = ''
#          if d.flow_rate
#            d.inspired_oxygen += 'Flow: ' + d.flow_rate + 'l/hr<br>'
#          if d.concentration
#            d.inspired_oxygen += 'Concentration: ' + d.concentration + '%<br>'
#          if d.cpap_peep
#            d.inspired_oxygen += 'CPAP PEEP: ' + d.cpap_peep + '<br>'
#          if d.niv_backup
#            d.inspired_oxygen += 'NIV Backup Rate: ' + d.niv_backup + '<br>'
#          if d.niv_ipap
#            d.inspired_oxygen += 'NIV IPAP: ' + d.niv_ipap + '<br>'
#          if d.niv_epap
#            d.inspired_oxygen += 'NIV EPAP: ' + d.niv_epap + '<br>'
#
#      focus.graphs.push({key: "respiration_rate", label: "RR", measurement: "/min", max: 60, min: 0, normMax: 20, normMin: 12})
#      focus.graphs.push({key: "indirect_oxymetry_spo2", label: "Spo2", measurement: "%", max: 100, min: 70, normMax: 100, normMin: 96})
#      focus.graphs.push({key: "body_temperature", label: "Temp", measurement: "°C", max: 50, min: 15, normMax: 37.1, normMin: 35})
#      focus.graphs.push({key: "pulse_rate", label:"HR", measurement:"/min", max:200, min: 30, normMax:100, normMin:50})
#      focus.graphs.push({key: "blood_pressure", label: "BP", measurement:"mmHg", max: 260, min: 30, normMax:150, normMin:50})
#      focus.tables.push({key: "avpu_text", label:"AVPU"})
#      focus.tables.push({key: "indirect_oxymetry_spo2_label", label:"Oxygen saturation"})
#      if plotO2
#        focus.tables.push({key:"inspired_oxygen", label:"Inspired oxygen"})
#
#
#      svg.data = obs
#      graph_lib.initGraph(21)
#      graph_lib.initTable()
#      graph_lib.drawTabularObs('#table-content')






if !window.NH
  window.NH = {}
window?.NH.NHMobilePatient = NHMobilePatient