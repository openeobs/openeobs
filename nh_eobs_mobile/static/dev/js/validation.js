/**
 * Created by colin on 30/12/13.
 */
function addValidationRules(obsType) {
    if(obsType == "ews"){
        $("#body_temperature").rules("add", {
            min: 27.1,
            max: 44.9,
            pimpedNumber: true,
            messages:{
                min: "Temperature too low (degrees Celsius)",
                max: "Temperature too high (degrees Celsius)",
                pimpedNumber: "Value must be a number"
            }
        });
        $("#respiration_rate").rules("add", {
            min: 1,
            max: 59,
            pimpedDigits: true,
            messages:{
                min: "Respiratory rate too low",
                max: "Respiratory rate too high" ,
                pimpedDigits: "Value must be a whole number"
            }
        });
        $("#indirect_oxymetry_spo2").rules("add", {
            min: 51,
            max: 100,
            pimpedDigits: true,
            messages:{
                min: "O2 saturation too low",
                max: "O2 saturation too high",
                pimpedDigits: "Value must be a whole number"
            }
        });
        $("#pulse_rate").rules("add", {
            min: 1,
            max: 250,
            pimpedDigits: true,
            messages: {
                min: "Heart rate too low",
                max: "Heart rate too high",
                pimpedDigits: "Value must be a whole number"
            }
        });
        $("#blood_pressure_diastolic").rules("add", {
            min: 1,
            max: 280,
            pimpedDigits: true,
            lessThan: '#blood_pressure_systolic',
            messages:{
                min: "Diastolic BP too low",
                max: "Diastolic BP too high",
                pimpedDigits: "Value must be a whole number",
                lessThan: "Diastolic must be less than systolic"
            }
        });
        $("#blood_pressure_systolic").rules("add", {
            min: 1,
            max: 300,
            pimpedDigits: true,
            greaterThan: '#blood_pressure_diastolic',
            messages:{
                min: "Systolic BP too low",
                max: "Systolic BP too high",
                pimpedDigits: "Value must be a whole number",
                greaterThan: "Systolic must be greater than diastolic"
            }
        });

        $("#device_id").rules("add", {
            required: false
        });
        $("#flow_rate").rules("add", {
            pimpedNumber: true,
            required: false,
            min: 0,
            messages:{
                pimpedNumber: "Value must be a number",
                min: "Value too low"
            }
        });
        $("#concentration").rules("add", {
            required: false,
            min: 0,
            messages:{
                min: "Value too low"
            }
        });
        $("#cpap_peep").rules("add", {
            required: false,
            min: 0,
            messages:{
                min: "Value too low"
            }
        });
        $("#niv_backup").rules("add", {
            required: false,
            min: 0,
            messages:{
                min: "Value too low"
            }
        });
        $("#niv_ipap").rules("add", {
            required: false,
            min: 0,
            messages:{
                min: "Value too low"
            }
        });
        $("#niv_epap").rules("add", {
            required: false,
            min: 0,
            messages:{
                min: "Value too low"
            }
        });
    }

    if(obsType == "gcs"){
        $("#eyes").rules("add", {
            required: false
        });
        $("#verbal").rules("add", {
            required: false
        });
        $("#motor").rules("add", {
            required: false
        });
    }

    if(obsType == "stools"){
        $("#bowel_open").rules("add",{
            required: false
        });
        $("#nausea").rules("add",{
            required: false
        });
        $("#vomiting").rules("add",{
            required: false
        });
        $("#quantity").rules("add",{
            required: false
        });
        $("#colour").rules("add",{
            required: false
        });
        $("#bristol_type").rules("add",{
            required: false
        });
        $("#offensive").rules("add", {
            required: false
        });
        $("#strain").rules("add",{
            required: false
        });
        $("#laxatives").rules("add", {
            required: false
        });
        $("#samples").rules("add", {
            required: false
        });
        $("#rectal_exam").rules("add", {
            required: false
        });
    }

    if(obsType == "blood_sugar"){
        $("#blood_sugar").rules("add", {
            min: 1.0,
            max: 99.9,
            pimpedNumber: true,
            messages:{
                min: "Blood sugar too low",
                max: "Blood sugar too high",
                pimpedNumber: "Value must be a number"
            }
        });
    }

    if(obsType == "height") {
        $("#height").rules("add", {
            pimpedNumber: true,
            required: false,
            messages: {
                pimpedNumber: "Value must be a number"
            }
        });
    }
    if(obsType == "weight"){
        $("#weight").rules("add", {
            pimpedNumber: true,
            messages:{
                pimpedNumber: "Value must be a number"
            }
        });
    }

    if(obsType == "blood_product"){
        $("#vol").rules("add", {
            pimpedNumber: true,
            messages:{
                pimpedNumber: "Value must be a number"
            }
        })
    }

    if(obsType == "pbp"){
        $("#systolic_sitting").rules("add", {
            min: 1,
            max: 300,
            pimpedDigits: true,
            required: false,
            greaterThan: '#diastolic_sitting',
            messages:{
                min: "Systolic BP too low",
                max: "Systolic BP too high",
                pimpedDigits: "Value must be a whole number",
                greaterThan: "Systolic must be greater than diastolic"
            }
        });
        $("#diastolic_sitting").rules("add", {
            min: 1,
            max: 280,
            pimpedDigits: true,
            required: false,
            lessThan: '#systolic_sitting',
            messages:{
                min: "Diastolic BP too low",
                max: "Diastolic BP too high",
                pimpedDigits: "Value must be a whole number",
                lessThan: "Diastolic must be less than systolic"
            }
        });

        $("#systolic_standing").rules("add", {
            min: 1,
            max: 300,
            pimpedDigits: true,
            required: false,
            greaterThan: '#diastolic_standing',
            messages:{
                min: "Systolic BP too low",
                max: "Systolic BP too high",
                pimpedDigits: "Value must be a whole number",
                greaterThan: "Systolic must be greater than diastolic"
            }
        });
        $("#diastolic_standing").rules("add", {
            min: 1,
            max: 280,
            pimpedDigits: true,
            required: false,
            lessThan: '#systolic_standing',
            messages:{
                min: "Diastolic BP too low",
                max: "Diastolic BP too high",
                pimpedDigits: "Value must be a whole number",
                lessThan: "Diastolic must be less than systolic"
            }
        });
    }
}

function resetErrors(el, mode){
    // if delete the actually remove the element
    if(mode == "delete"){
        $("#"+el).parent().parent(".obsField").removeClass("error");
        $("#"+el).parent().siblings(".input-body").children(".errors").children("label.error").remove();

        //$(".obsField").removeClass("error");
        //$(".obsField label.error").remove();

        // if empty then just empty the error text
    }else if(mode == "empty"){
        $("#"+el).parent().parent(".obsField").removeClass("error");
        $("#"+el).parent().parent().find(".errors").text("");
    }else{
        return false;
    }
}

function showErrors(errors){
    $.each(errors, function(k,v){
        var id = k.replace(/\./g, "_");$("#"+id).parent().parent().addClass("error");$("#"+id).parent().parent().find(".input-body .errors").text(v);
    });
}