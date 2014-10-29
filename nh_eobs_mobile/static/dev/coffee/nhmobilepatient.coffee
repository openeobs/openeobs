# NHMobilePatient contains utilities for working with the nh_eobs_mobile patient view, namely getting data and passing it to graph lib
class NHMobilePatient extends NHMobile

  constructor: () ->
    self = @
    super()
    # find the obs menu on page
    obs_menu = document.getElementById('obsMenu')
    obs_menu.addEventListener('click', @.show_obs_menu)
    obs_menu.style.display = 'none'
    table_view = document.getElementById('table-content')
    table_view.style.display = 'none'

    tabs = document.getElementsByClassName('tabs')[0].getElementsByTagName('a')
    for tab in tabs
      tab.addEventListener('click', @.handle_tabs)

    Promise.when(@call_resource(@.urls['ajax_get_patient_obs'](document.getElementById('graph-content').getAttribute('data-id')))).then (server_data) ->
      a = graph_lib.svg
      t = graph_lib.context
      n = graph_lib.focus
      e = server_data[0][0]
      a.chartType = e.obsType
      r = e.obs.reverse()
      console.log(r)
#      if r.length < 1
#        console.log('no data')
#      a.ticks = Math.floor(a.width / 100)
#      t.earliestDate = a.startParse(r[0].date_started)
#      t.now = a.startParse(r[r.length-1].date_started)
#      if window.clientWidth() > window.clientHeight()
#        a.isMob
#        s = new Date(t.now)
#        s.setDate(s.getDate() - a.dateRange.landscape)
#        t.earliestDate = s
#      else
#        s = new Date(t.now)
#        s.setDate(s.getDate() - a.dateRange.portrait)
#        t.earliestDate = s
#
#        t.scoreRange = [{"class": "green",s: 0,e: 4}, {"class": "amber",s: 4,e: 6}, {"class": "red",s: 6,e: 21}];
#        i = !1;
#        r.forEach(function(e) {
#          e.date_started = a.startParse(e.date_started)
#          e.body_temperature = e.body_temperature.toFixed(1)
#          e.indirect_oxymetry_spo2 && (e.indirect_oxymetry_spo2_label = e.indirect_oxymetry_spo2 + "%")
#          e.oxygen_administration_flag && (i = !0, e.inspired_oxygen = "", "undefined" != typeof e.flow_rate && (e.inspired_oxygen += "Flow: " + e.flow_rate + "l/hr<br>")
#          "undefined" != typeof e.concentration && (e.inspired_oxygen += "Concentration: " + e.concentration + "%<br>")
#          e.cpap_peep && (e.inspired_oxygen += "CPAP PEEP: " + e.cpap_peep + "<br>"), e.niv_backup && (e.inspired_oxygen += "NIV Backup Rate: " + e.niv_backup + "<br>")
#          e.niv_ipap && (e.inspired_oxygen += "NIV IPAP: " + e.niv_ipap + "<br>"), e.niv_epap && (e.inspired_oxygen += "NIV EPAP: " + e.niv_epap + "<br>"))
#        })
#        a.data = r, n.graphs.push({
#      key: "respiration_rate",
#      label: "RR",
#      measurement: "/min",
#      max: 60,
#      min: 0,
#      normMax: 20,
#      normMin: 12
#    }), n.graphs.push({
#      key: "indirect_oxymetry_spo2",
#      label: "Spo2",
#      measurement: "%",
#      max: 100,
#      min: 70,
#      normMax: 100,
#      normMin: 96
#    }), n.graphs.push({
#      key: "body_temperature",
#      label: "Temp",
#      measurement: "Â°C",
#      max: 50,
#      min: 15,
#      normMax: 37.1,
#      normMin: 35
#    }), n.graphs.push({
#      key: "pulse_rate",
#      label: "HR",
#      measurement: "/min",
#      max: 200,
#      min: 30,
#      normMax: 100,
#      normMin: 50
#    }), n.graphs.push({
#      key: "blood_pressure",
#      label: "BP",
#      measurement: "mmHg",
#      max: 260,
#      min: 30,
#      normMax: 150,
#      normMin: 50
#    }), n.tables.push({
#      key: "avpu_text",
#      label: "AVPU"
#    }), n.tables.push({
#      key: "indirect_oxymetry_spo2_label",
#      label: "Oxygen saturation"
#    }), i && n.tables.push({
#      key: "inspired_oxygen",
#      label: "Inspired oxygen"
#    }), a.data = r, graph_lib.initGraph(20), graph_lib.initTable(), graph_lib.drawTabularObs("#table-content");




if !window.NH
  window.NH = {}
window?.NH.NHMobilePatient = NHMobilePatient