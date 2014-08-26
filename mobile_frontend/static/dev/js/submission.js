/**
 * Created by colin on 30/12/13.
 */
function processObs(obsType){
    var score;
    if(obsType == "ews"){
        if($("#respiration_rate").val() == "" || $("#indirect_oxymetry_spo2").val() == "" || $("#body_temperature").val() == "" || $("#blood_pressure_systolic").val() == ""  || $("#blood_pressure_diastolic").val() == "" || $("#pulse_rate").val() == "" || $("#avpu_text").val() == "" || $("#oxygen_administration_flag").val() == ""){
            return false;
        }else{
            if($("#oxygen_administration_flag").val().toString() == "true"){
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

            var talkToServer = frontend_routes.ews_score();
            var getScore = $.ajax({
               url: talkToServer.url,
               type: talkToServer.type,
               data: jQuery("#obsForm").not(".exclude").serialize(),
               success: function(data){
                    console.log(data);
                   data.class = data.clinical_risk.toLowerCase();
                   if((data.score == 3 || data.score == 4) && data.three_in_one == true){
                       data.clinical_risk = "One observation scored 3 therefore " + data.clinical_risk + " clinical risk";
                   }
                   score = data;
               },
               error: function(error){
                   console.log("nay");
               }
            })
            getScore.then(function(data){
                console.log("this is being called");
                displayModal("obsConfirm", "Submit NEWS of <span id=\"newsScore\" class=\"newsScore\">" + data.score + "</span> for " + patientName + "?", "<p><strong>Clinical risk: "+data.clinical_risk+"</strong></p><p>Please confirm you want to submit this score</p><p class=\"obsError error\">Data not sent, please resubmit</p>", [" <a href=\"#\" id=\"obsCancel\" class=\"cancel\">Cancel</a>","<a href=\"#\" id=\"obsSubmit\">Submit</a>"]);
                $("#obsConfirm").addClass("clinicalrisk-"+data.class);
                return score;
            });

            return true;


        }
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