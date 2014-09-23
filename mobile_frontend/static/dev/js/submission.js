/**
 * Created by colin on 30/12/13.
 */
function processObs(obsType){
    var score;
    if(obsType == "ews"){
        if($("#respiration_rate").val() == "" || $("#indirect_oxymetry_spo2").val() == "" || $("#body_temperature").val() == "" || $("#blood_pressure_systolic").val() == ""  || $("#blood_pressure_diastolic").val() == "" || $("#pulse_rate").val() == "" || $("#avpu_text").val() == "" || $("#oxygen_administration_flag").val() == ""){
            return false;
        }else{
            if($("#oxygen_administration_flag").val().toString() == "True"){
                if($("#device_id").val() == ""){
                    return false;
                }else if($("device_id").val() == "44"){
                    if(($("#flow_rate").val() == "" && $("#concentration").val() == "" ) || $("#cpap_peep").val() == ""){
                        return false;
                    }
                }else if($("#device_id").val() == "45"){
                    if(($("#flow_rate").val() == "" && $("#concentration").val() == "" ) || ($("#niv_backup").val() == "" || $("#niv_ipap").val() == "" || $("#niv_epap").val() == "")){
                        return false;
                    }
                }else{
                    if($("#flow_rate").val() == "" && $("#concentration").val() == "" ){
                        return false;
                    }
                }
            }

            var talkToServer = frontend_routes.ews_score();
            var getScore = $.ajax({
               url: talkToServer.url,
               type: talkToServer.type,
               data: $($("#obsForm")[0].elements).not(".exclude").serialize(),
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

    if(obsType == "gcs"){
        if($("#eyes").val() == "" || $("#verbal").val() == "" || $("#motor").val() == ""){
            return false;
        }else{
            return score = gcs(
                $("#eyes").val(),
                $("#verbal").val(),
                $("#motor").val()
            )
        }
    }
    if(obsType == "stools"){
        if($("#bowel_open").val() == "" || $("#nausea").val() == "" || $("#vomiting").val() == "" || $("#quantity").val() == "" || $("#colour").val() == "" || $("#bristol_type").val() == "" || $("#offensive").val() == "" || $("#strain").val() == "" || $("#laxatives").val() == "" || $("#samples").val() == "" || $("#rectal_exam").val() == ""){
            return false;
        }else{
            return true;
        }
    }

    if(obsType == "blood_sugar"){
        if($("#blood_sugar").val() == ""){
            return false;
        }else{
            return true;
        }
    }

    if(obsType == "weight"){
        if($("#weight").val() == ""){
            return false;
        }else{
            return true;
        }
    }

    if(obsType == "height"){
        if($("#height").val() == ""){
            return false;
        }else{
            return true;
        }
    }

    if(obsType == "blood_product"){
        if($("#vol").val() == "" || $("#product").val() == ""){
            return false;
        }else{
            return true;
        }
    }
}