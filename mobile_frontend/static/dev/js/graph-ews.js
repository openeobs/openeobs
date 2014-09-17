// AJAX call to get the data
var route = frontend_routes.ajax_get_patient_obs(svg.patientId).ajax({
    dataType: "json",
    success: function (obsData) { // on success process it
        console.log(obsData);
        // set the chart type
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



            // set up the score range for the data
            context.scoreRange = [
                {class: "green", s:0, e:4},
                {class: "amber", s:4, e:6},
                {class: "red", s:6, e:20}
            ];
            
            var o2 = jsRoutes.controllers.Patients.getPatientO2Target(svg.patientId).ajax({
				dataType: "json",
				success: function (o2Data) { // on success process it
                    var min = null;
                    var max = null;
                    if(o2Data.status == 1){
                        min = o2Data.min;
                        max = o2Data.max;
                    }

                    var plotO2 = false;

					// setup data to be stored in svg object
					svg.data = data;

	            // got through the data and clean it
		            data.forEach(function(d) {

                        d.obsStart = svg.startParse(d.obsStart);
		                if(d.obs.indirect_oxymetry_spo2){
		                    d.obs.indirect_oxymetry_spo2_label = d.obs.indirect_oxymetry_spo2 + "%";
		                }
                        if(Object.keys(d.obs.oxygen_administration_flag.parameters).length != 0){
                            plotO2 = true;
                            d.obs.inspired_oxygen = "";
                            if(typeof(d.obs.oxygen_administration_flag.parameters.flow) != "undefined") {
                                d.obs.inspired_oxygen += "Flow: " + d.obs.oxygen_administration_flag.parameters.flow + "l/hr<br>";
                            }
                            if(typeof(d.obs.oxygen_administration_flag.parameters.concentration) != "undefined") {
                                d.obs.inspired_oxygen += "Concentration: " + d.obs.oxygen_administration_flag.parameters.concentration + "%<br>";
                            }
                            if(d.obs.oxygen_administration_flag.parameters.cpapPeep){ d.obs.inspired_oxygen += "CPAP PEEP: " + d.obs.oxygen_administration_flag.parameters.cpapPeep + "<br>";}
                            if(d.obs.oxygen_administration_flag.parameters.nivBackupRate){ d.obs.inspired_oxygen += "NIV Backup Rate: " + d.obs.oxygen_administration_flag.parameters.nivBackupRate + "<br>";}
                            if(d.obs.oxygen_administration_flag.parameters.nivIpap){ d.obs.inspired_oxygen += "NIV IPAP: " + d.obs.oxygen_administration_flag.parameters.nivIpap + "<br>";}
                            if(d.obs.oxygen_administration_flag.parameters.nivEpap){ d.obs.inspired_oxygen += "NIV EPAP: " + d.obs.oxygen_administration_flag.parameters.nivEpap + "<br>";}
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
	            initGraph(20);
	            initTable();
                drawTabularObs('#table-content');
	        },
	        error: function (err) {
			    console.log(err)
		    }
	    });
    },
    error: function (err) {
        console.log(err)
    }
});



