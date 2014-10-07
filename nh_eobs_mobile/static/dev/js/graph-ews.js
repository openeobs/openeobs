// AJAX call to get the data


var route = frontend_routes.ajax_get_patient_obs(graph_lib.svg.patientId).ajax({
    dataType: "json",
    success: function (obsData) { // on success process it
        console.log(obsData);
        var svg = graph_lib.svg, context = graph_lib.context, focus = graph_lib.focus;
        // set the chart type
        svg.chartType = obsData.obsType;

        // setup data object so can read obs easier
        var data = obsData.obs.reverse();

        if(data.length < 1){
             console.log("no data");
        }

        svg.ticks = Math.floor(svg.width / 100);

        // set the first and last date
        context.earliestDate = svg.startParse(data[0].date_started);
        context.now = svg.startParse(data[data.length-1].date_started);

        // if the device is a mobile then show 1 or 5 days worth of data
        if(svg.isMob){
            if($(window).width() > $(window).height()){
                var cED = new Date(context.now);
                cED.setDate(cED.getDate() - svg.dateRange.landscape);
                context.earliestDate = cED;
            }else{
                var cED = new Date(context.now);
                cED.setDate(cED.getDate() - svg.dateRange.portrait);
                context.earliestDate = cED;
            }

        }
        // set up the score range for the data
        context.scoreRange = [
            {class: "green", s:0, e:4},
            {class: "amber", s:4, e:6},
            {class: "red", s:6, e:20}
        ];

        var min = null;
        var max = null;

        var plotO2 = false;



        // got through the data and clean it
        data.forEach(function(d) {

            d.date_started = svg.startParse(d.date_started);
            d.body_temperature = d.body_temperature.toFixed(1);
            if(d.indirect_oxymetry_spo2){
                d.indirect_oxymetry_spo2_label = d.indirect_oxymetry_spo2 + "%";
            }
            if(d.oxygen_administration_flag){
                plotO2 = true;
                d.inspired_oxygen = "";
                if(typeof(d.flow_rate) != "undefined") {
                    d.inspired_oxygen += "Flow: " + d.flow_rate + "l/hr<br>";
                }
                if(typeof(d.concentration) != "undefined") {
                    d.inspired_oxygen += "Concentration: " + d.concentration + "%<br>";
                }
                if(d.cpap_peep){ d.inspired_oxygen += "CPAP PEEP: " + d.cpap_peep + "<br>";}
                if(d.niv_backup){ d.inspired_oxygen += "NIV Backup Rate: " + d.niv_backup + "<br>";}
                if(d.niv_ipap){d.inspired_oxygen += "NIV IPAP: " + d.niv_ipap + "<br>";}
                if(d.niv_epap){ d.inspired_oxygen += "NIV EPAP: " + d.niv_epap + "<br>";}
            }
        });

        // setup data to be stored in svg object
        svg.data = data;

        // setup graph object so can plot graph
        // setup graph object so can plot graph
        focus.graphs.push({key: "respiration_rate", label: "RR", measurement: "/min", max: 60, min: 0, normMax: 20, normMin: 12});
        focus.graphs.push({key: "indirect_oxymetry_spo2", label: "Spo2", measurement: "%", max: 100, min: 70, normMax: 100, normMin: 96});
        focus.graphs.push({key: "body_temperature", label: "Temp", measurement: "°C", max: 50, min: 15, normMax: 37.1, normMin: 35});
        focus.graphs.push({key: "pulse_rate", label:"HR", measurement:"/min", max:200, min: 30, normMax:100, normMin:50});
        focus.graphs.push({key: "blood_pressure", label: "BP", measurement:"mmHg", max: 260, min: 30, normMax:150, normMin:50});
        focus.tables.push({key: "avpu_text", label:"AVPU"});
        focus.tables.push({key: "indirect_oxymetry_spo2_label", label:"Oxygen saturation"});
        if(plotO2){
            focus.tables.push({key:"inspired_oxygen", label:"Inspired oxygen"});
        }

        // setup data to be stored in svg object
        svg.data = data;

        graph_lib.initGraph(20);
        graph_lib.initTable();
        graph_lib.drawTabularObs('#table-content');
    },
    error: function (err) {
        console.log(err)
    }
});


$(document).ready(function(){
    $('#table-content').hide();
    $('#obsMenu').hide();
    $("#obsButton").click(function(e){
        e.preventDefault();
        var content = "<ul class=\"menu\">";
        var obs_options = $('#obsMenu').html();
        var patientName = $('h3.name strong').first().text().trim();
        content += obs_options;
//        content += "<li class='rightContent'><a href='/mobile/patients/takeMewsObs/71'>NEWS <span class='aside'>overdue: 169.57&nbsp;hours</span></a></li>";content += "<li><a href='/mobile/patients/takeGcsObs/71'>GCS</a></li>";content += "<li><a href='/mobile/patients/takeBloodProductObs/71'>Blood Product</a></li>";content += "<li><a href='/mobile/patients/takeHeightWeightObs/71'>Height and Weight</a></li>";content += "<li><a href='/mobile/patients/takeBloodSugarObs/71'>Blood Sugar</a></li>";content += "<li><a href='/mobile/patients/takeStoolsObs/71'>Stools</a></li>";
        content += "</ul>";
        displayModal("obsPick", "Pick an observation for " + patientName, content, ["<a href=\"#\" id=\"obsCancel\" class=\"cancel\">Cancel</a>"],0)
    });
    $(".tabs li a").click(function(e){
        e.preventDefault();
        var toShow = $(this).attr('href');
        $('#graph-content').hide();
        $('#table-content').hide();
        $(toShow).show();
        $('.tabs li a').removeClass('selected');
        $(this).addClass('selected');
    });
});




