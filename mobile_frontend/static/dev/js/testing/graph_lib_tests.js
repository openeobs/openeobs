/**
 * Created by colin on 14/02/14.
 */
// AJAX call to get the data
$.ajax({
    url: "graph_lib_demo_data.json",
    dataType: "json",
    success: function (obsData) { // on success process it
        console.log(obsData);
        // set the chart type

        var svg = graph_lib.svg, context = graph_lib.context, focus = graph_lib.focus;

        svg.chartType = obsData.obsType;

        // setup data object so can read obs easier
        var data = obsData.obs.reverse();

        if(obsData.obs.length < 1){
            console.log("no data");
        }

        svg.ticks = Math.floor(svg.width / 100);

        // set the first and last date
        context.earliestDate = svg.startParse(data[0].obsStart);
        context.now = svg.startParse(data[data.length-1].obsStart);

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

        // if charttype is news then process news data
        if(svg.chartType == "t4skr.observation.news"){

            // set the score ranges for news
            context.scoreRange = [
                {class: "green", s:0, e:5},
                {class: "amber", s:5, e:7},
                {class: "red", s:7, e:18}
            ];

            // go through the data and clean it
            data.forEach(function(d) {
                //add this to table later
                d.obs.score = news(d.obs.respiration_rate, d.obs.indirect_oxymetry_spo2, d.obs.oxygen_administration_flag, d.obs.body_temperature, d.obs.blood_pressure_systolic, d.obs.pulse_rate, d.obs.avpu_text).newsScore;
                d.obsStart = svg.startParse(d.obsStart);
            });

            // setup data to be stored in svg object
            svg.data = data;

            // setup graph object so can plot graph
            focus.graphs.push({key: "respiration_rate", label: "RR", measurement: "/min", max: 60, min: 0, normMax: 20, normMin: 12});
            focus.graphs.push({key: "indirect_oxymetry_spo2", label: "Spo2", measurement: "%", max: 100, min: 70, normMax: 100, normMin: 96});
            focus.graphs.push({key: "body_temperature", label: "Temp", measurement: "°C", max: 50, min: 15, normMax: 37.1, normMin: 35});
            focus.graphs.push({key: "pulse_rate", label:"HR", measurement:"/min", max:200, min: 30, normMax:100, normMin:50});
            focus.graphs.push({key: "blood_pressure", label: "BP", measurement:"mmHg", max: 260, min: 30, normMax:150, normMin:50});
            $(".table-wrapper").remove();
            graph_lib.initGraph(18);
        }else if(svg.chartType == "t4skr.observation.mews"){ // process mews obs

            // set up the score range for the data
            context.scoreRange = [
                {class: "green", s:0, e:4},
                {class: "amber", s:4, e:6},
                {class: "red", s:6, e:17.7}
            ];

            // got through the data and clean it
            data.forEach(function(d) {
                d.obs.score = mews(d.obs.pulse_rate, d.obs.respiration_rate, d.obs.body_temperature, d.obs.urine_output, d.obs.blood_pressure_systolic, d.obs.consciousness).mewsScore;
                d.obsStart = svg.startParse(d.obsStart);
                if(d.obs.urine_output){
                    switch(d.obs.urine_output){
                        case "1":
                            d.obs.urine_output = "3";
                            break;
                        case "2":
                            d.obs.urine_output = "2";
                            break;
                        case "3":
                            d.obs.urine_output = "0";
                            break;
                    }
                }
                if(d.obs.indirect_oxymetry_spo2){
                    d.obs.indirect_oxymetry_spo2 = d.obs.indirect_oxymetry_spo2 + "%";
                }
            });

            // setup data to be stored in svg object
            svg.data = data;

            // setup graph object so can plot graph
            focus.graphs.push({key: "respiration_rate", label: "RR", measurement: "/min", max: 60, min: 0, normMax: 20, normMin: 12});
            focus.graphs.push({key: "body_temperature", label: "Temp", measurement: "°C", max: 50, min: 15, normMax: 37.1, normMin: 35});
            focus.graphs.push({key: "pulse_rate", label:"HR", measurement:"/min", max:200, min: 30, normMax:100, normMin:50});
            focus.graphs.push({key: "blood_pressure", label: "BP", measurement:"mmHg", max: 260, min: 30, normMax:150, normMin:50});
            focus.tables.push({key: "consciousness", label:"Consciousness"});
            focus.tables.push({key: "urine_output", label:"Urine output"});
            focus.tables.push({key: "indirect_oxymetry_spo2", label:"Oxygen saturation"});
            graph_lib.initGraph(18);
            graph_lib.initTable();
        }
    },
    error: function (err) {
        console.log(err)
    }
});



