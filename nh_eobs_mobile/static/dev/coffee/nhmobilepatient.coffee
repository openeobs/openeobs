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
    new window.NH.NHModal('obs_menu', 'Pick an observation for ', '<ul>'+obs_menu.innerHTML+'</ul>', ['<a href="#" data-action="close" data-target="obs_menu">Cancel</a>'], 0, document.getElementsByTagName('body')[0])


  draw_graph: (self, server_data) =>
      svg = graph_lib.svg
      context = graph_lib.context
      focus = graph_lib.focus
      data = server_data[0][0]
      svg.chartType = data.obsType
      obs = data.obs.reverse()
      console.log(obs)

      if obs.length < 1
        console.log('no data')

      svg.ticks = Math.floor(svg.width/100)

      context.earliestDate = svg.startParse(obs[0].date_started)
      context.now = svg.startParse(obs[obs.length-1].date_started)
      context.height = 200;
      focus.chartHeight= 200;

      if svg.isMob
        if $(window).width() > $(window).height()
          cED = new Date(context.now)
          cED.setDate(cED.getDate() - svg.dateRange.landscape)
          context.earliestDate = cED
        else
          cED = new Date(context.now)
          cED.setDate(cED.getDate() - svg.dateRange.portrait)
          context.earliestDate = cED


      context.scoreRange = [
        {class: "green", s:0, e:4},
        {class: "amber", s:4, e:6},
        {class: "red", s:6, e:21}
      ]

      min = null
      max = null

      plotO2 = false

      for d in obs
        d.date_started = svg.startParse(d.date_started)
        d.body_temperature = d.body_temperature.toFixed(1)
        if d.indirect_oxymetry_spo2
          d.indirect_oxymetry_spo2_label = d.indirect_oxymetry_spo2 + '%'
        if d.oxygen_administration_flag
          plotO2 = true
          d.inspired_oxygen = ''
          if d.flow_rate
            d.inspired_oxygen += 'Flow: ' + d.flow_rate + 'l/hr<br>'
          if d.concentration
            d.inspired_oxygen += 'Concentration: ' + d.concentration + '%<br>'
          if d.cpap_peep
            d.inspired_oxygen += 'CPAP PEEP: ' + d.cpap_peep + '<br>'
          if d.niv_backup
            d.inspired_oxygen += 'NIV Backup Rate: ' + d.niv_backup + '<br>'
          if d.niv_ipap
            d.inspired_oxygen += 'NIV IPAP: ' + d.niv_ipap + '<br>'
          if d.niv_epap
            d.inspired_oxygen += 'NIV EPAP: ' + d.niv_epap + '<br>'

      focus.graphs.push({key: "respiration_rate", label: "RR", measurement: "/min", max: 60, min: 0, normMax: 20, normMin: 12})
      focus.graphs.push({key: "indirect_oxymetry_spo2", label: "Spo2", measurement: "%", max: 100, min: 70, normMax: 100, normMin: 96})
      focus.graphs.push({key: "body_temperature", label: "Temp", measurement: "°C", max: 50, min: 15, normMax: 37.1, normMin: 35})
      focus.graphs.push({key: "pulse_rate", label:"HR", measurement:"/min", max:200, min: 30, normMax:100, normMin:50})
      focus.graphs.push({key: "blood_pressure", label: "BP", measurement:"mmHg", max: 260, min: 30, normMax:150, normMin:50})
      focus.tables.push({key: "avpu_text", label:"AVPU"})
      focus.tables.push({key: "indirect_oxymetry_spo2_label", label:"Oxygen saturation"})
      if plotO2
        focus.tables.push({key:"inspired_oxygen", label:"Inspired oxygen"})


      svg.data = obs
      graph_lib.initGraph(21)
      graph_lib.initTable()
      graph_lib.drawTabularObs('#table-content')






if !window.NH
  window.NH = {}
window?.NH.NHMobilePatient = NHMobilePatient