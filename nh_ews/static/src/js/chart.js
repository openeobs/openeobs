function processOxygenAdministrationDevice(ob){
    ob.oxygen_administration_device = "No";
        if (ob.oxygen_administration_flag) {
            ob.oxygen_administration_device = "Yes";
        }
    return ob;
}

function processInspiredOxygen(ob){
    var fr = ob.flow_rate && ob.flow_rate > -1;
    var c = ob.concentration && ob.concentration > -1;
    var f = ob.oxygen_administration_flag;

    if (fr || c || f) {
        ob.inspired_oxygen = "";
    }
    if (ob.device_id) {
        ob.inspired_oxygen += "<strong>Device:</strong> " +
            ob.device_id[1] + "<br>";
    }
    if (fr) {
        ob.inspired_oxygen += "<strong>Flow:</strong> " +
            ob.flow_rate + "l/hr<br>";
    }
    if (c) {
        ob.inspired_oxygen += "<strong>Concentration:</strong> " +
            ob.concentration + "%<br>";
    }
    if (ob.cpap_peep && ob.cpap_peep > -1) {
        ob.inspired_oxygen += "<strong>CPAP PEEP:</strong> " +
            ob.cpap_peep + "<br>";
    } else if (ob.niv_backup && ob.niv_backup > -1) {
        ob.inspired_oxygen += "<strong>NIV Backup Rate:</strong> " +
            ob.niv_backup + "<br>";
        ob.inspired_oxygen += "<strong>NIV EPAP:</strong> " +
            ob.niv_epap + "<br>";
        ob.inspired_oxygen += "<strong>NIV IPAP</strong>: " +
            ob.niv_ipap + "<br>";
    }
    return ob;
}

function processSpo2(ob){
    if (ob.indirect_oxymetry_spo2) {
        ob.indirect_oxymetry_spo2_label = ob.indirect_oxymetry_spo2 + "%";
    }
    return ob;
}

function convertValue(value, valueToChange, substituteValue){
    return value === valueToChange ? substituteValue : value;
}

function processEwsData(obs){
    for (var i = 0; i < obs.length; i++) {
        var ob = obs[i];
        if (ob.is_partial) {
            ob.score = false;
        }
        ob = processOxygenAdministrationDevice(ob);
        ob = processInspiredOxygen(ob);
        ob = processSpo2(ob);
        ob["table_respiration_rate"] = convertValue(ob["respiration_rate"], null, "");
        ob["table_indirect_oxymetry_spo2"] = convertValue(ob["indirect_oxymetry_spo2"], null, "");
        ob["table_body_temperature"] = convertValue(ob["body_temperature"], null, "");
        ob["table_blood_pressure_systolic"] = convertValue(ob["blood_pressure_systolic"], null, "");
        ob["table_blood_pressure_diastolic"] = convertValue(ob["blood_pressure_diastolic"], null, "");
        ob["table_pulse_rate"] = convertValue(ob["pulse_rate"], null, "");
        ob["table_avpu"] = convertValue(ob["avpu"], null, "");
    }
    return obs;
}

function drawEwsChart(settings, serverData) {
    var obs = serverData;
    var svg = new window.NH.NHGraphLib("#" + settings.chart_element);
    var respRateGraph = new window.NH.NHGraph();
    respRateGraph.options.keys = ["respiration_rate"];
    respRateGraph.options.label = "RR";
    respRateGraph.options.measurement = "/min";
    respRateGraph.axes.y.min = 0;
    respRateGraph.axes.y.max = 40;
    respRateGraph.options.normal.min = 12;
    respRateGraph.options.normal.max = 20;
    respRateGraph.style.dimensions.height = 250;
    respRateGraph.style.data_style = "linear";
    respRateGraph.style.label_width = 60;
    respRateGraph.drawables.background.data = [
        {"class": "red", s: 0, e: 9},
        {"class": "green", s: 9, e: 12},
        {"class": "amber", s: 21, e: 25},
        {"class": "red", s: 25, e: 60}
    ];

    var oxyGraph = new window.NH.NHGraph();
    oxyGraph.options.keys = ["indirect_oxymetry_spo2"];
    oxyGraph.options.label = "Spo2";
    oxyGraph.options.measurement = "%";
    oxyGraph.axes.y.min = 70;
    oxyGraph.axes.y.max = 100;
    oxyGraph.options.normal.min = 96;
    oxyGraph.options.normal.max = 100;
    oxyGraph.style.dimensions.height = 200;
    oxyGraph.style.axis.x.hide = true;
    oxyGraph.style.data_style = "linear";
    oxyGraph.style.label_width = 60;
    oxyGraph.drawables.background.data = [
        {"class": "red", s: 0, e: 92},
        {"class": "amber", s: 92, e: 94},
        {"class": "green", s: 94, e: 96}
    ];

    var tempGraph = new window.NH.NHGraph();
    tempGraph.options.keys = ["body_temperature"];
    tempGraph.options.label = "Temp";
    tempGraph.options.measurement = "°C";
    tempGraph.axes.y.min = 25;
    tempGraph.axes.y.max = 45;
    tempGraph.options.normal.min = 36.1;
    tempGraph.options.normal.max = 38.1;
    tempGraph.style.dimensions.height = 200;
    tempGraph.style.axis.x.hide = true;
    tempGraph.style.data_style = "linear";
    tempGraph.style.label_width = 60;
    tempGraph.drawables.background.data = [
        {"class": "red", s: 0, e: 35},
        {"class": "amber", s: 35, e: 35.1},
        {"class": "green", s: 35.1, e: 36.0},
        {"class": "green", s: 38.1, e: 39.1},
        {"class": "amber", s: 39.1, e: 50}
    ];

    var pulseGraph = new window.NH.NHGraph();
    pulseGraph.options.keys = ["pulse_rate"];
    pulseGraph.options.label = "HR";
    pulseGraph.options.measurement = "/min";
    pulseGraph.axes.y.min = 25;
    pulseGraph.axes.y.max = 200;
    pulseGraph.options.normal.min = 50;
    pulseGraph.options.normal.max = 91;
    pulseGraph.style.dimensions.height = 200;
    pulseGraph.style.axis.x.hide = true;
    pulseGraph.style.data_style = "linear";
    pulseGraph.style.label_width = 60;
    pulseGraph.drawables.background.data = [
        {"class": "red", s: 0, e: 40},
        {"class": "amber", s: 40, e: 41},
        {"class": "green", s: 41, e: 50},
        {"class": "green", s: 91, e: 111},
        {"class": "amber", s: 111, e: 131},
        {"class": "red", s: 131, e: 200}
    ];

    var bpGraph = new window.NH.NHGraph();
    bpGraph.options.keys = [
        "blood_pressure_systolic",
        "blood_pressure_diastolic"
    ];
    bpGraph.options.label = "BP";
    bpGraph.options.measurement = "mmHg";
    bpGraph.axes.y.min = 30;
    bpGraph.axes.y.max = 260;
    bpGraph.options.normal.min = 150;
    bpGraph.options.normal.max = 151;
    bpGraph.style.dimensions.height = 200;
    bpGraph.style.axis.x.hide = true;
    bpGraph.style.data_style = "range";
    bpGraph.style.label_width = 60;
    bpGraph.drawables.background.data = [
        {"class": "red", s: 0, e: 91},
        {"class": "amber", s: 91, e: 101},
        {"class": "green", s: 101, e: 111},
        {"class": "red", s: 220, e: 260}
    ];

    var scoreGraph = new window.NH.NHGraph();
    scoreGraph.options.keys = ["score"];
    scoreGraph.options.plot_partial = true;
    scoreGraph.style.dimensions.height = 200;
    scoreGraph.style.data_style = "stepped";
    scoreGraph.axes.y.min = 0;
    scoreGraph.axes.y.max = 22;
    scoreGraph.drawables.background.data = [
        {"class": "green", s: 1, e: 4},
        {"class": "amber", s: 4, e: 6},
        {"class": "red", s: 6, e: 22}
    ];
    scoreGraph.style.label_width = 60;


    var tabularObs = new window.NH.NHTable();
    tabularObs.keys = [
        {key: "avpu_text", title: "AVPU"},
        {key: "oxygen_administration_device", title: "On Supplemental O2"},
        {key: "inspired_oxygen", title: "Inspired Oxygen"}
    ];
    tabularObs.title = "Tabular values";
    focus = new window.NH.NHFocus();
    context = new window.NH.NHContext();
    focus.graphs.push(respRateGraph);
    focus.graphs.push(oxyGraph);
    focus.graphs.push(tempGraph);
    focus.graphs.push(pulseGraph);
    focus.graphs.push(bpGraph);
    focus.tables.push(tabularObs);
    focus.title = "Individual values";
    focus.style.padding.right = 0;
    context.graph = scoreGraph;
    context.title = "NEWS Score";
    svg.focus = focus;
    svg.context = context;
    svg.options.controls.date.start = document.getElementById("start_date");
    svg.options.controls.date.end = document.getElementById("end_date");
    svg.options.controls.time.start = document.getElementById("start_time");
    svg.options.controls.time.end = document.getElementById("end_time");
    svg.options.controls.rangify = document.getElementById("rangify");
    svg.options.refused = settings.refused;
    svg.options.partial_type = settings.partial_type;
    svg.data.raw = processEwsData(obs);
    svg.init();
    svg.draw();
}

function drawEwsTable(settings, serverData){
    var obs = serverData.reverse();
    var tableEl = new window.NH.NHGraphLib("#table");
    tableEl.table = {
        element: "#table",
        keys: [
            {
                title: "NEWS Score",
                keys: ["score_display"]
            },
            {
                title: "Respiration Rate",
                keys: ["table_respiration_rate"]
            },
            {
                title: "O2 Saturation",
                keys: ["table_indirect_oxymetry_spo2"]
            },
            {
                title: "Body Temperature",
                keys: ["table_body_temperature"]
            },
            {
                title: "Blood Pressure Systolic",
                keys: ["table_blood_pressure_systolic"]
            },
            {
                title: "Blood Pressure Diastolic",
                keys: ["table_blood_pressure_diastolic"]
            },
            {
                title: "Pulse Rate",
                keys: ["table_pulse_rate"]
            },
            {
                title: "AVPU",
                keys: ["table_avpu_text"]
            },
            {
                title: "Patient on Supplemental O2",
                keys: ["oxygen_administration_flag"]
            },
            {
                title: "Inspired Oxygen",
                keys: [
                    {
                        title: "Flow Rate",
                        keys: ["flow_rate"]
                    },
                    {
                        title: "Concentration",
                        keys: ["concentration"]
                    },
                    {
                        title: "Device",
                        keys: ["device_id"]
                    },
                    {
                        title: "CPAP PEEP",
                        keys: ["cpap_peep"]
                    },
                    {
                        title: "NIV iPAP",
                        keys: ["niv_ipap"]
                    },
                    {
                        title: "NIV ePAP",
                        keys: ["niv_epap"]
                    },
                    {
                        title: "NIV Backup Rate",
                        keys: ["niv_backup"]
                    }
                ]
            }
        ]
    };
    tableEl.data.raw = processEwsData(obs);
    tableEl.draw();
}