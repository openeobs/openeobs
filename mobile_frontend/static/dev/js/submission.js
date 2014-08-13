/**
 * Created by colin on 30/12/13.
 */
function processObs(obsType){
    var score;
    if(obsType == "NEWS"){
        if($("#obsData_respRate").val() == "" || $("#obsData_o2").val() == "" || $("#obsData_temp").val() == "" || $("#obsData_systolicBP").val() == ""  || $("#obsData_diastolicBP").val() == "" || $("#obsData_pulse").val() == "" || $("#obsData_avpu").val() == "" || $("#obsData_supplementaryO2_o2Flag").val() == ""){
            return false;
        }else{
            if($("#obsData_supplementaryO2_oxygen_administration_flag").val().toString() == "true"){
                if($("#obsData_supplementaryO2_O2Device").val() == ""){
                    return false;
                }else if($("#obsData_supplementaryO2_O2Device").val() == "44"){
                    if(($("#obsData_supplementaryO2_parameters_flow").val() == "" && $("#obsData_supplementaryO2_parameters_concentration").val() == "" ) || $("#obsData_supplementaryO2_parameters_cpapPeep").val() == ""){
                        return false;
                    }
                }else if($("#obsData_supplementaryO2_O2Device").val() == "45"){
                    if(($("#obsData_supplementaryO2_parameters_flow").val() == "" && $("#obsData_supplementaryO2_parameters_concentration").val() == "" ) || ($("#obsData_supplementaryO2_parameters_nivBackupRate").val() == "" || $("#obsData_supplementaryO2_parameters_nivIpap").val() == "" || $("#obsData_supplementaryO2_parameters_nivEpap").val() == "")){
                        return false;
                    }
                }else{
                    if($("#obsData_supplementaryO2_parameters_flow").val() == "" && $("#obsData_supplementaryO2_parameters_concentration").val() == "" ){
                        return false;
                    }
                }
            }



            return score = news(
                parseFloat($("#obsData_respRate").val()),
                parseFloat($("#obsData_o2").val()),
                $("#obsData_supplementaryO2_o2Flag").val().toString(),
                parseFloat($("#obsData_temp").val()),
                parseFloat($("#obsData_systolicBP").val()),
                parseFloat($("#obsData_pulse").val()),
                $("#obsData_avpu").val().toString()
            );
        }
    }
    if(obsType == "BTUHMEWS"){
        if($("#obsData_respiration_rate").val() == "" || $("#obsData_indirect_oxymetry_spo2").val() == "" || $("#obsData_body_temperature").val() == "" || $("#obsData_blood_pressure_systolic").val() == ""  || $("#obsData_diastolicBP").val() == "" || $("#obsData_pulse_rate").val() == "" || $("#obsData_avpu_text").val() == "" || $("#obsData_supplementaryO2_oxygen_administration_flag").val() == ""){
            return false;
        }else{
            if($("#obsData_supplementaryO2_oxygen_administration_flag").val().toString() == "true"){
                if($("#obsData_supplementaryO2_O2Device").val() == ""){
                    return false;
                }else if($("#obsData_supplementaryO2_O2Device").val() == "44"){
                    if(($("#obsData_supplementaryO2_parameters_flow").val() == "" && $("#obsData_supplementaryO2_parameters_concentration").val() == "" ) || $("#obsData_supplementaryO2_parameters_cpapPeep").val() == ""){
                        return false;
                    }
                }else if($("#obsData_supplementaryO2_O2Device").val() == "45"){
                    if(($("#obsData_supplementaryO2_parameters_flow").val() == "" && $("#obsData_supplementaryO2_parameters_concentration").val() == "" ) || ($("#obsData_supplementaryO2_parameters_nivBackupRate").val() == "" || $("#obsData_supplementaryO2_parameters_nivIpap").val() == "" || $("#obsData_supplementaryO2_parameters_nivEpap").val() == "")){
                        return false;
                    }
                }else{
                    if($("#obsData_supplementaryO2_parameters_flow").val() == "" && $("#obsData_supplementaryO2_parameters_concentration").val() == "" ){
                        return false;
                    }
                }
            }

            var talkToServer = jsRoutes.controllers.Observations.calculateEWS();
            var getScore = $.ajax({
               url: talkToServer.url,
               type: talkToServer.type,
               data: $($("#obsForm")[0].elements).not(".exclude").serialize(),
               success: function(data){
                    console.log(data);
                   data.class = data.clinicalRisk.toLowerCase();
                   if((data.score == 3 || data.score == 4) && data.threeInOne == true){
                       data.clinicalRisk = "One observation scored 3 therefore " + data.clinicalRisk + " clinical risk";
                   }
                   score = data;
               },
               error: function(error){
                   console.log("nay");
               }
            })
            getScore.then(function(data){
                console.log("this is being called");
                displayModal("obsConfirm", "Submit NEWS of <span id=\"newsScore\" class=\"newsScore\">" + data.score + "</span> for " + patientName + "?", "<p><strong>Clinical risk: "+data.clinicalRisk+"</strong></p><p>Please confirm you want to submit this score</p><p class=\"obsError error\">Data not sent, please resubmit</p>", [" <a href=\"#\" id=\"obsCancel\" class=\"cancel\">Cancel</a>","<a href=\"#\" id=\"obsSubmit\">Submit</a>"]);
                $("#obsConfirm").addClass("clinicalrisk-"+data.class);
                return score;
            });

            return true;


        }
    }

    if(obsType == "MEWS"){
        console.log($("#obsForm"));
        if($("#obsData_pulse").val() == "" || $("#obsData_pulseType").val() == "" || $("#obsData_respRate").val() == "" || $("#obsData_temp").val() == "" || ($("#obsData_consciousnessToggle").val() == "avpu" && $("#obsData_avpu").val() == "") || ($("#obsData_consciousnessToggle").val() == "gcs" && ($("#obsData_eyes").val() == "" || $("#obsData_verbal").val() == "" || $("#obsData_motor").val() == "")) || $("#obsData_urine").val() == "" || $("#obsData_systolicBP").val == "" || $("#obsData_diastolicBP").val == ""){// || $("#obsData_supplementaryO2_o2Flag").val() == "" || $("#obsData_o2").val() == ""){
            return false;

            }


            var consciousness;
            $("#obsData_gcs").val("");
            if($("#obsData_consciousnessToggle").val() == "gcs"){
                consciousness = parseInt(gcs($("#obsData_eyes").val(), $("#obsData_verbal").val(), $("#obsData_motor").val()).gcsScore);
                $("#obsData_gcs").val(consciousness);
            }else if($("#obsData_consciousnessToggle").val() == "avpu"){
                consciousness = $("#obsData_avpu").val();
            }
            return score = mews(
                parseFloat($("#obsData_pulse").val()),
                parseFloat($("#obsData_respRate").val()),
                parseFloat($("#obsData_temp").val()),
                parseFloat($("#obsData_urine").val()),
                parseFloat($("#obsData_systolicBP").val()),
                consciousness
            );
        //}
    }
    if(obsType == "GCS"){
        if($("#gcsData_eyes").val() == "" || $("#gcsData_verbal").val() == "" || $("#gcsData_motor").val() == ""){
            return false;
        }else{
            return score = gcs(
                $("#gcsData_eyes").val(),
                $("#gcsData_verbal").val(),
                $("#gcsData_motor").val()
            )
        }
    }
    if(obsType == "STOOL"){
        if($("#stoolsData_bowelOpen").val() == "" || $("#stoolsData_nausea").val() == "" || $("#stoolsData_vomiting").val() == "" || $("#stoolsData_quantity").val() == "" || $("#stoolsData_colour").val() == "" || $("#stoolsData_bristolType").val() == "" || $("#stoolsData_offensive").val() == "" || $("#stoolsData_strain").val() == "" || $("#stoolsData_laxatives").val() == "" || $("#stoolsData_samples").val() == "" || $("#stoolsData_rectalExam").val() == ""){
            return false;
        }else{
            return true;
        }
    }

    if(obsType == "BLOODS"){
        if($("#bloodSugarData_bloodSugar").val() == "" || $("#bloodSugarData_diabetic").val() == ""){
            return false;
        }else{
            return true;
        }
    }

    if(obsType == "WEIGHT"){
        if($("#heightWeightData_weight").val() == ""){
            return false;
        }else{
            return true;
        }
    }

    if(obsType == "BLOODP"){
        if($("#BloodProductData_volume").val() == "" || $("#BloodProductData_product").val() == ""){
            return false;
        }else{
            return true;
        }
    }
}