/**
 * Created by colin on 30/12/13.
 */
/**
 * User: max@tactix4.com
 * Date: 11/1/13
 * Time: 10:52 AM
 */

var timeIdle = 0;
var idleTime = 2400;
var timing = true;
var taskId;
var EWSlabel = "NEWS";
var oxmin, oxmax;
var patientName;

$(document).ready(function () {
    // define variables that will be used throughout the observation form
    var patientId = $("#obsForm").attr("patient-id"),  obsType = $("#obsForm").attr("data-type"), obsSource = $("#obsForm").attr("data-source");
        taskId = $("#obsForm").attr("task-id");
        oxmin = $("#obsForm").attr("data-min");
        oxmax = $("#obsForm").attr("data-max");
        patientName = $("#patientName a").text().trim();

    $(".header").css({"box-shadow": "none", "border-bottom": "1px solid #eeeeee"});

    //reset the form on page load
    if(obsType != "medical_team" && obsType != "ObsFreq"){
        $("#obsForm")[0].reset();
    }

    var submitDisabled = false;

    // if it's a task observation then log that it's taken, if the user comes back to page without the system remove this it forces a reload to make sure that the task is still theirs to take
    if(obsSource == "task"){

        if(taskId != null && taskId != undefined && taskId != ""){
            frontend_routes.json_take_task(taskId).ajax({
                cache: false,
                success: function(data){
                    console.log(data);
                    if(data.status.toString() === "true"){

                    }else{
                        displayModal("getTaskIssue", "Task unavailable", "<p>This task is unavailable. This may be due to the task being taken by another user or that it has been completed.</p>",["<a href="+frontend_routes.task_list().url+ " class=\"action\">Go to Task list</a>"]);

                    }
                },
                error: function(err){
                    console.log(err);
                    displayModal("getTaskError", "Error checking if task available", "<p>There was error checking if this task is available. Someone may have taken it or the task is already been completed.</p>",["<a href="+frontend_routes.task_list().url+ " class=\"action\">Go to Task list</a>"]);
                }
            });
        }
    }else{
        timing = false;
    }


    // if the user presses the patients name do an ajax call to grab and display their details
    $("#patientName a").click(function(e){
        e.preventDefault();
        timeIdle = 0;
        var patientName = "", patientGender = "", patientDetails = "";
        frontend_routes.json_patient_info(patientId).ajax({
            success: function(data){
                console.log(data);
                if(data.full_name){
                    patientName += " " + data.full_name;
                }
                if(data.gender){
                    patientGender = data.gender;
                }
                if(data.dob){
                    var patientDOB = new Date(data.dob);
                    patientDOB = ("0"+patientDOB.getDate()).slice(-2) + "/" + ("0"+(patientDOB.getMonth()+1)).slice(-2) + "/" + patientDOB.getFullYear();
                    patientDetails += "<dt>DOB:</dt><dd>"+patientDOB+"</dd>";
                }
                if(data.location != ""){
                    patientDetails += "<dt>Location:</dt><dd>"+data.location+"</dd>";
                }

                EWSlabel = "NEWS";

                if(data.ews_score){
                    patientDetails += "<dt class='twoline'>Latest " + EWSlabel +  " Score</dt><dd class='twoline'>"+data.ews_score+"</dd>";
                }
                if(data.other_identifier){
                    patientDetails += "<dt>Hospital ID</dt><dd>" + data.other_identifier + "</dd>"
                }
                if(data.patient_identifier){
                    patientDetails += "<dt>NHS Number</dt><dd>" + data.patient_identifier + "</dd>"
                }
                displayModal("patientInfo", patientName+"<span class=\"alignright\">" + patientGender +"</span>", "<dl>" + patientDetails + "</dl><p><a href='#' id='loadObs'>View Patient Observation Data</a></p>",["<a href=\"#\" class=\"cancel\">Cancel</a>"]);
            },error: function(err){
                displayModal("patientInfo", "Error getting patient details", "<p>Sorry there seems to have been an error</p>", ["<a href=\"#\" class=\"cancel\">Cancel</a>"]);
            }
        });
    });

    // There's a four minute timer until the task it checked back, changing the input will reset the timer
    $("input").on("change", function() {
        $("#startTimestamp").val($.now());
        timeIdle = 0;
    });

    $("input").on("keyup", function(){
       $(this).valid();
    });

    $("input").on("focus", function(){
       timeIdle = 0;
    });

    $("select").on("change", function() {
        $("#startTimestamp").val($.now());
        timeIdle = 0;
    });

    $("select").on("focus", function(){
        timeIdle = 0;
    });

    $("#startTimestamp").val($.now());

    //setup validation
    var validator;
    if(obsType != "medical_team" && obsType != "ObsFreq"){

        console.log('adding custom methods');


        jQuery.validator.addMethod("pimpedNumber", function(value, element){
            if(/^[-+]?\d+(\.\d+)?$/.test( value )){
                return true;
            }else{
                element.value = "";
                return true;
            }
        }, "Invalid character found in field");

        jQuery.validator.addMethod("lessThan", function (value, element, param) {
                var $max = $(param);
                if (this.settings.onfocusout) {
                    $max.off(".validate-lessThan").on("blur.validate-lessThan", function () {
                        $(element).valid();
                    });
                }
                if(element.value != "" && $max.val() != "") {
                    return parseInt(value) < parseInt($max.val());
                }else{
                    return true;
                }
            }, "Diastolic must be less than systolic");

        jQuery.validator.addMethod("greaterThan", function (value, element, param) {
            var $max = $(param);
            if (this.settings.onfocusout) {
                $max.off(".validate-greaterThan").on("blur.validate-greaterThan", function () {
                    $(element).valid();
                });
            }
            if(element.value != "" && $max.val() != "") {
                return parseInt(value) > parseInt($max.val());
            }else{
                return true;
            }
        }, "Systolic must be greater than diastolic");


        jQuery.validator.addMethod("mewsO2", function(value, element){
            if(element.value <= 94 && element.value !== ""){
                $(element).parent().parent().addClass("warning");
                $(element).parent().siblings(".input-body").children(".help").text("O2 less than 95%, action required");
                return true;
            }else{
                $(element).parent().siblings(".input-body").children(".help").text("");
                $(element).parent().parent().removeClass("warning");
                return true;
            }
        }, "O2 less than 95%, action required");

        jQuery.validator.addMethod("pimpedDigits", function(value, element){
           if(/^[-+]?\d+$/.test(value)){
               return true;
           }else{
               if(/^[-+]?\d+\.(\d+)?$/.test( value )){
                   return false;
               }else{
                   element.value = "";
                   return true;
               }
           }
        }, "Invalid character found in field");


        validator = $("#obsForm").validate({
            success: function(element){
                resetErrors(element.attr("for"), "empty");
            },
            errorPlacement: function (error, element) {
                $("#"+element.attr("id")).parent().parent().addClass("error");
                $("#"+element.attr("id")).parent().parent().find(".input-body .errors").append(error);
            }
        });

        addValidationRules(obsType);
    }

    $('.content').on("click", "#confirmSubmit", function(e){
        e.preventDefault();
      timeIdle = 0;
        var r = frontend_routes.confirm_clinical_notification(taskId);
        $.ajax({
            url: r.url,
            type: r.type,
            success: function(data){
                console.log(data);
                if(data.status == 1){
                    if(data.related_tasks){
                        if(data.related_tasks.length == 1){
                            dismissModal("obsConfirm", "hide");
                            displayModal("obsConfirm", "Action required", "<p>" + data.related_tasks[0].summary + "</p>", ["<a href=\""+frontend_routes.task_list().url+ "\" class=\"action\">Go to My Tasks</a>", "<a href=\""+frontend_routes.single_task(data.related_tasks[0].id).url+"\" class=\"confirm\">Confirm</a>"], 500);
                        }else if(data.related_tasks.length > 1){
                            var taskList = "";
                            for(var a = 0; a < data.related_tasks.length; a++){
                                taskList += "<li><a href=\""+frontend_route.single_task(data.related_tasks[a].id).url+ "\">"+ data.related_tasks[a].summary + "</a></li>";
                            }
                            dismissModal("obsConfirm", "hide");
                            displayModal("obsConfirm", "Action required", "<ul class=\"menu\">" + taskList + "</ul>", ["<a href=\""+frontend_routes.task_list().url+ "\">Go to My Tasks</a>"], 500);
                        }else{
                            dismissModal("obsConfirm", "hide");
                            displayModal("obsConfirm", "Successfully submitted", "<p>The confirmation has been successfully submitted.</p>", ["<a href=\""+frontend_routes.task_list().url+ "\" class=\"action\">Go to My Tasks</a>"], 500);
                        }
                    }else{
                        dismissModal("obsConfirm", "hide");
                        displayModal("obsConfirm", "Successfully submitted", "<p>The confirmation has been successfully submitted.</p>", ["<a href=\""+frontend_routes.task_list().url+ "\" class=\"action\">Go to My Tasks</a>"], 500);
                    }
            }},
            error: function(err){
                console.log("re-enabling submit");
                submitDisabled = false;
                console.log(err)
                console.log(err.responseText);
                $(".obsConfirm .error").css("display", "block");
                var errResp = $.parseJSON(err.responseText);
                if(errResp.errors){
                    showErrors(errResp.errors);
                }
            }
        });
        return true;
    });


    $('.content').on("click", "#obsFreqSubmit", function(e){
        e.preventDefault();
        timeIdle = 0;
        var formData = $($("#obsForm")[0].elements).not(".exclude").serialize();
        var r = jsRoutes.controllers.Observations.submitObsChange(taskId);
        $.ajax({
            url: r.url,
            type: r.type,
            data: formData,
            success: function(data){
                console.log(data);
                if(data.status == 1){
                    if(data.relatedTasks){
                        if(data.relatedTasks.length == 1){
                            dismissModal("obsConfirm", "hide");
                            displayModal("obsConfirm", "Action required", "<p>" + data.relatedTasks[0].reason + "</p>", ["<a href=\""+jsRoutes.controllers.Tasks.listTasks().url+ "\" class=\"action\">Go to My Tasks</a>", "<a href=\""+jsRoutes.controllers.Tasks.performTask(data.relatedTasks[0].taskId).url+"\" class=\"confirm\">Confirm</a>"], 500);
                        }else if(data.relatedTasks.length > 1){
                            var taskList = "";
                            for(var a = 0; a < data.relatedTasks.length; a++){
                                taskList += "<li><a href=\""+jsRoutes.controllers.Tasks.performTask(data.relatedTasks[a].taskId).url+"\">"+ data.relatedTasks[a].reason + "</a></li>";
                            }
                            dismissModal("obsConfirm", "hide");
                            displayModal("obsConfirm", "Action required", "<ul class=\"menu\">" + taskList + "</ul>", ["<a href=\""+jsRoutes.controllers.Tasks.listTasks().url+ "\">Go to My Tasks</a>"], 500);
                        }else{
                            dismissModal("obsConfirm", "hide");
                            displayModal("obsConfirm", "Successfully submitted", "<p>The observation frequency has been successfully submitted.</p>", ["<a href=\""+jsRoutes.controllers.Tasks.listTasks().url+ "\" class=\"action\">Go to My Tasks</a>"], 500);
                        }
                    }else{
                        dismissModal("obsConfirm", "hide");
                        displayModal("obsConfirm", "Successfully submitted", "<p>The  observation frequency has been successfully submitted.</p>", ["<a href=\""+jsRoutes.controllers.Tasks.listTasks().url+ "\" class=\"action\">Go to My Tasks</a>"], 500);
                    }
                }},
            error: function(err){
                console.log("re-enabling submit");
                submitDisabled = false;
                console.log(err)
                console.log(err.responseText);
                $(".obsConfirm .error").css("display", "block");
                var errResp = $.parseJSON(err.responseText);
                if(errResp.errors){
                    showErrors(errResp.errors);
                }
            }
        });
        return true;
    });


    // on submitting the obs do an ajax call and display any messages from the server
    $('.content').on("click", "#obsSubmit", function(e){
        e.preventDefault();
        timeIdle = 0;
        resetErrors("empty");
        var formData = $($("#obsForm")[0].elements).not(".exclude").serialize();
        console.log(formData);
        var r;
        if(obsSource == "patient"){
            console.log("obsource is patient");
            r = jsRoutes.controllers.Observations.submitObsForPatient(obsType);
        }else{
            console.log("obsource is task");
            r = frontend_routes.json_task_form_action(taskId);
        }
        if(!submitDisabled){
            console.log("disabling submit");
            submitDisabled = true;
            $.ajax({
                url: r.url,
                type: r.type,
                data: formData,
                success: function(data){
                    console.log(data);
                    if(data.status == 1){
                        if(data.related_tasks){
                            if(data.related_tasks.length == 1){
                                dismissModal("obsConfirm", "hide");
                                displayModal("obsConfirm", "Action required", "<p>" + data.related_tasks[0].summary + "</p>", ["<a href=\""+frontend_routes.task_list().url+ "\" class=\"action\">Go to My Tasks</a>", "<a href=\""+frontend_routes.single_task(data.related_tasks[0].id).url+"\" class=\"confirm\">Proceed</a>"], 500);
                            }else if(data.related_tasks.length > 1){
                                var taskList = "";
                                for(var a = 0; a < data.related_tasks.length; a++){
                                    taskList += "<li><a href=\""+frontend_routes.single_task(data.related_tasks[a].id).url+"\">"+ data.related_tasks[a].summary + "</a></li>";
                                }
                                dismissModal("obsConfirm", "hide");
                                displayModal("obsConfirm", "Action required", "<ul class=\"menu\">" + taskList + "</ul>", ["<a href=\""+frontend_routes.task_list().url+ "\">Go to My Tasks</a>"], 500);
                            }else{
                                dismissModal("obsConfirm", "hide");
                                displayModal("obsConfirm", "Successfully submitted", "<p>The observations have been successfully submitted.</p>", ["<a href=\""+frontend_routes.task_list().url+ "\" class=\"action\">Go to My Tasks</a>"], 500);
                            }
                        }else{
                            dismissModal("obsConfirm", "hide");
                            displayModal("obsConfirm", "Successfully submitted", "<p>The observations have been successfully submitted.</p>", ["<a href=\""+frontend_routes.task_list().url+ "\" class=\"action\">Go to My Tasks</a>"], 500);
                        }
                    }else if(data.responseText){
                        console.log("re-enabling submit");
                        submitDisabled = false;
                        var errResp = $.parseJSON(data.responseText);
                        if(errResp.errors){
                            showErrors(errResp.errors);
                        }
                        $("#obsConfirm .error").css("display", "block");
                    }else{
                        $("#obsConfirm .error").css("display", "block");
                    }
                },
                error: function(err){
                    console.log("re-enabling submit");
                    submitDisabled = false;
                    console.log(err)
                    console.log(err.responseText);
                    $(".obsConfirm .error").css("display", "block");
                    var errResp = $.parseJSON(err.responseText);
                    if(errResp.errors){
                        showErrors(errResp.errors);
                    }
                }
            });
        }else{

        }
        return true;
    });

    // if the user tries to submit a partial observation then they get a popup asking them the reason, this submits the reason and passes any messages back
    $('form').on("click", ".confirmPartial", function(e){
        e.preventDefault();
        timeIdle = 0;
        resetErrors("empty");
        var formData = $($("#obsForm")[0].elements).not(".exclude").serialize();
        console.log(formData);
        var r;
        if(obsSource == "patient"){
            console.log("partial obs for patient");
            r = jsRoutes.controllers.Observations.submitObsForPatient(obsType);
        }else{
            console.log("partial obs for task");
            r = frontend_routes.json_task_form_action(taskId);
        }
        if(!submitDisabled){
            console.log("disabling submit");
            submitDisabled = true;
            $.ajax({
                url: r.url,
                type: r.type,
                data: formData,
                success: function(data){
                    console.log(data);
                    if(data.status == 1 || data.status == 2){
                        if(data.status == 1){
                            dismissModal("obsPartial", "hide");
                            displayModal("obsConfirm", "Successfully submitted", "<p>The partial observation have been successfully submitted. Please be aware that this task is still active until all observations have been taken. Only the last complete NEWS score will be displayed..</p>", ["<a href=\""+frontend_routes.task_list().url+ "\" class=\"action\">Go to My Tasks</a>"], 500);
                        }else{
                            dismissModal("obsPartial", "hide");
                            displayModal("obsConfirm", "Action required", "<p>" + data.message + "</p>", ["<a href=\""+frontend_routes.task_list().url+ "\" class=\"action\">Go to My Tasks</a>", "<a href=\""+frontend_routes.single_task(data.id).url+"\" class=\"confirm\">Proceed</a>"], 500);
                        }
                    }else if(data.responseText){
                        console.log("re-enabling submit");
                        submitDisbled = false;
                        var errResp = $.parseJSON(data.responseText);
                        if(errResp.errors){
                            showErrors(errResp.errors);
                        }
                        dismissModal("obsPartial", "hide");
                    }else{
                        $(".obsConfirm .error").css("display", "block");
                    }
                },
                error: function(err){
                    console.log("re-enabling submit");
                    submitDisbled = false;
                    console.log(err)
                    console.log(err.responseText);
                    $(".obsConfirm .error").css("display", "block");
                    var errResp = $.parseJSON(err.responseText);
                    if(errResp.errors){
                        showErrors(errResp.errors);
                    }
                }
            });
        }
    });

    $('.content').on("click", "#loadObs", function(e) {
        e.preventDefault();
        timeIdle = 0;
        $('body').append("<div class='full-modal'><p><a href='#' id='closeFullModal'>Close Popup</a></p><iframe src='"+frontend_routes.single_patient(patientId).url+"'></iframe></div>");
        $('.full-modal iframe').load(function(){
            $(this).show();
            $('.full-modal iframe').contents().find('.header').hide();
            $('.full-modal iframe').contents().find('.patientInfo').hide();
            $('.full-modal iframe').contents().find('.content').css('margin-top', '-3em');
        });
    });

    $('body').on("click", "#closeFullModal", function(e) {
        e.preventDefault();
        timeIdle = 0;
        $('.full-modal').remove();
    });



    $('#obsForm').on("click", ".confirmCancel", function(e){
        e.preventDefault();
        timeIdle = 0;
        resetErrors("empty");
        var formData = $($("#obsForm .cancelValues")).not(".exclude").serialize();
        console.log(formData);
        var r = frontend_routes.cancel_clinical_notification(taskId);
        if(!submitDisabled){
            console.log("disabling submit");
            submitDisabled = true;
            $.ajax({
                url: r.url,
                type: r.type,
                data: formData,
                success: function(data){
                console.log(data);
                if(data.status == 1 || data.status == 2){
                    if(data.status == 1){
                        dismissModal("taskCancel", "hide");
                        displayModal("obsConfirm", "Successfully submitted", "<p>Action successfully cancelled</p>", ["<a href=\""+frontend_routes.task_list().url+"\" class=\"action\">Go to My Tasks</a>"], 500);
                        }else{
                        dismissModal("taskCancel", "hide");
                        displayModal("obsConfirm", "Action required", "<p>" + data.message + "</p>", ["<a href=\""+frontend_routes.task_list().url+"\" class=\"action\">Go to My Tasks</a>", "<a href=\""+frontend_routes.single_task(data.taskId).url+"\" class=\"confirm\">Proceed</a>"], 500);
                }
                }else if(data.responseText){
                    console.log("re-enabling submit");
                    submitDisbled = false;
                    var errResp = $.parseJSON(data.responseText);
                    if(errResp.errors){
                        showErrors(errResp.errors);
                    }
                    dismissModal("taskCancel", "hide");
                }else{
                    $(".obsConfirm .error").css("display", "block");
                }
            },
            error: function(err){
                console.log("re-enabling submit");
                submitDisbled = false;
                console.log(err)
                console.log(err.responseText);
                $(".obsConfirm .error").css("display", "block");
                var errResp = $.parseJSON(err.responseText);
                if(errResp.errors){
                    showErrors(errResp.errors);
                }
            }
        });
    }
});

    // if the user goes to submit obs, validate them, see if all required values are included and process a score, then either ask them to confirm if they want to submit partial obs or confirm proper obs
    $('#submitButton').click(function (e) {
        e.preventDefault();
        timeIdle = 0;
        if (validator.form()) {
            //get news score
            var obsResult = processObs(obsType);
            console.log(obsResult);
            $(".obsError").css("display", "none");
            if(obsResult){
                if(obsType == "NEWS"){
                    displayModal("obsConfirm", "Submit NEWS of <span id=\"newsScore\" class=\"newsScore\">" + obsResult.score + "</span> for " + patientName + "?", "<p>Please confirm you want to submit this score</p><p class=\"obsError error\">Input error, please correct and resubmit</p>", [" <a href=\"#\" id=\"obsCancel\" class=\"cancel\">Cancel</a>","<a href=\"#\" id=\"obsSubmit\">Submit</a>"]);
                }else if(obsType == "MEWS"){
                    displayModal("obsConfirm", "Submit MEWS of <span id=\"newsScore\" class=\"newsScore\">" + obsResult.score + "</span> for " + patientName + "?", "<p>Please confirm you want to submit this score</p><p class=\"obsError error\">Input error, please correct and resubmit</p>", [" <a href=\"#\" id=\"obsCancel\" class=\"cancel\">Cancel</a>","<a href=\"#\" id=\"obsSubmit\">Submit</a>"]);
               }else if(obsType == "BTUHMEWS"){
//                    displayModal("obsConfirm", "Submit NEWS of <span id=\"newsScore\" class=\"newsScore\">" + obsResult.score + "</span> for " + patientName + "?", "<p>Please confirm you want to submit this score</p><p class=\"obsError error\">Data not sent, please resubmit</p>", [" <a href=\"#\" id=\"obsCancel\" class=\"cancel\">Cancel</a>","<a href=\"#\" id=\"obsSubmit\">Submit</a>"]);
                }else if(obsType == "GCS"){
                    displayModal("obsConfirm", "Submit GCS of <span id=\"obsScore\" class=\"" + obsResult.colour + "\">" + obsResult.gcsScore + "</span> for " + patientName + "?", "<p>Please confirm you want to submit this score</p><p class=\"obsError error\">Input error, please correct and resubmit</p>", [" <a href=\"#\" id=\"obsCancel\" class=\"cancel\">Cancel</a>","<a href=\"#\" id=\"obsSubmit\">Submit</a>"]);
                }else if(obsType == "STOOL"){
                    displayModal("obsConfirm", "Submit Stool observation for " + patientName + "?", "<p>Please confirm you want to submit this observation</p><p class=\"obsError error\">Input error, please correct and resubmit</p>", ["<a href=\"#\" id=\"obsCancel\" class=\"cancel\">Cancel</a>","<a href=\"#\" id=\"obsSubmit\">Submit</a>"], 0);
                }else if(obsType == "BLOODS"){
                    displayModal("obsConfirm", "Submit Blood Sugar observation for " + patientName + "?", "<p>Please confirm you want to submit this observation</p><p class=\"obsError error\">Input error, please correct and resubmit</p>", ["<a href=\"#\" id=\"obsCancel\" class=\"cancel\">Cancel</a>","<a href=\"#\" id=\"obsSubmit\">Submit</a>"], 0);
                }else if(obsType == "WEIGHT"){
                    displayModal("obsConfirm", "Submit Height and Weight observation for " + patientName + "?", "<p>Please confirm you want to submit this observation</p><p class=\"obsError error\">Input error, please correct and resubmit</p>", ["<a href=\"#\" id=\"obsCancel\" class=\"cancel\">Cancel</a>","<a href=\"#\" id=\"obsSubmit\">Submit</a>"], 0);
                }else if(obsType == "BLOODP"){
                    displayModal("obsConfirm", "Submit Blood Product observation for " + patientName + "?", "<p>Please confirm you want to submit this observation</p><p class=\"obsError error\">Input error, please correct and resubmit</p>", ["<a href=\"#\" id=\"obsCancel\" class=\"cancel\">Cancel</a>","<a href=\"#\" id=\"obsSubmit\">Submit</a>"], 0);
                }
            }else{
                if(obsType == "ews"){
                    displayPartialObsDialog();
                }else{
                    displayModal("obsConfirm", "Mandatory observation values not entered", "<p>Please enter all information and submit observation again</p>", ["<a href=\"#\" id=\"obsCancel\" class=\"cancel\">OK</a>"], 0);
                }
            }
        }else{
            console.log(validator.errors());
            displayModal("obsConfirm", "Form validation errors", "<p>The observation your are trying to submit has input errors. Please correct them and resubmit.</p>", [" <a href=\"#\" id=\"obsCancel\" class=\"cancel\">Cancel</a>"]);
        }
    });


    $('#cancelSubmit').click(function (e) {
        e.preventDefault();
        timeIdle = 0;
        displayTaskCancellationOptions();
    })

    // on the stool observation a bristol stool chart popup is available
    $('#bristolPopup').click(function (e) {
        e.preventDefault();
        timeIdle = 0;
        var bristolImage =  new Image();
        bristolImage.src="/assets/img/Bristol_stool_chart.png";
        displayModal("bristol", "Bristol Stool Chart", bristolImage, ["<a href=\"#\" class=\"cancel\">Cancel</a>"], 0);
    });

    // On MEWS if consciousness selector changed then show the correct one
    $("#obsData_consciousnessToggle").change(function(e){
        var value =  $("#obsData_consciousnessToggle").val();
        if(value == "avpu"){
            $("#parent_obsData_avpu").removeClass("valHide");
            $("#parent_obsData_eyes").addClass("valHide");
            $("#parent_obsData_verbal").addClass("valHide");
            $("#parent_obsData_motor").addClass("valHide");
        }else if(value == "gcs"){
            $("#parent_obsData_avpu").addClass("valHide");
            $("#parent_obsData_eyes").removeClass("valHide");
            $("#parent_obsData_verbal").removeClass("valHide");
            $("#parent_obsData_motor").removeClass("valHide");
        }else{
            $("#parent_obsData_avpu").addClass("valHide");
            $("#parent_obsData_eyes").addClass("valHide");
            $("#parent_obsData_verbal").addClass("valHide");
            $("#parent_obsData_motor").addClass("valHide");
        }
    });

    $("#oxygen_administration_flag").change(function(e){
       var value = $("#oxygen_administration_flag").val();
       if(value == "True"){
           $("#parent_device_id").removeClass("valHide");
           $("#device_id").removeClass("exclude");
           var value = $("#device_id").val();
           if(value <= 43){
               ToggleBaseSupO2("show");
               ToggleCPAPSupO2("hide");
               ToggleNIVSupO2("hide");
           }else if(value == 44){
               ToggleBaseSupO2("show");
               ToggleCPAPSupO2("show");
               ToggleNIVSupO2("hide");
           }else if(value == 45){
               ToggleBaseSupO2("show");
               ToggleCPAPSupO2("hide");
               ToggleNIVSupO2("show");
           }else if(value > 45){
               ToggleBaseSupO2("show");
               ToggleCPAPSupO2("hide");
               ToggleNIVSupO2("hide");
           }
       }else{
           $("#parent_device_id").addClass("valHide");
           $("#device_id").addClass("exclude");
           ToggleBaseSupO2("hide");
           ToggleCPAPSupO2("hide");
           ToggleNIVSupO2("hide");
       }
    });

    $("#device_id").change(function(e){
       var value = $("#device_id").val();
       if(value <= 43){
           ToggleBaseSupO2("show");
           ToggleCPAPSupO2("hide");
           ToggleNIVSupO2("hide");
       }else if(value == 44){
           ToggleBaseSupO2("show");
           ToggleCPAPSupO2("show");
           ToggleNIVSupO2("hide");
       }else if(value == 45){
           ToggleBaseSupO2("show");
           ToggleCPAPSupO2("hide");
           ToggleNIVSupO2("show");
       } else if (value > 45) {
           ToggleBaseSupO2("show");
           ToggleCPAPSupO2("hide");
           ToggleNIVSupO2("hide");
       }
    });
});

function ToggleBaseSupO2(whichWay){
    if(whichWay == "show"){
        $("#parent_flow_rate").removeClass("valHide");
        $("#flow_rate").removeClass("exclude");
        $("#parent_concentration").removeClass("valHide");
        $("#concentration").removeClass("exclude");
    }else{
        $("#parent_flow_rate").addClass("valHide");
        $("#flow_rate").addClass("exclude");
        $("#parent_concentration").addClass("valHide");
        $("#concentration").addClass("exclude");
    }
}

function ToggleCPAPSupO2(whichWay){
    if(whichWay == "show"){
        $("#parent_cpap_peep").removeClass("valHide");
        $("#cpap_peep").removeClass("exclude");
    }else{
        $("#parent_cpap_peep").addClass("valHide");
        $("#cpap_peep").addClass("exclude");
    }
}

function ToggleNIVSupO2(whichWay){
    if(whichWay == "show"){
        $("#parent_niv_backup").removeClass("valHide");
        $("#niv_backup").removeClass("exclude");
        $("#parent_niv_ipap").removeClass("valHide");
        $("#niv_ipap").removeClass("exclude");
        $("#parent_niv_epap").removeClass("valHide");
        $("#niv_epap").removeClass("exclude");
    }else{
        $("#parent_niv_backup").addClass("valHide");
        $("#niv_backup").addClass("exclude");
        $("#parent_niv_ipap").addClass("valHide");
        $("#niv_ipap").addClass("exclude");
        $("#parent_niv_epap").addClass("valHide");
        $("#niv_epap").addClass("exclude");
    }
}


function displayTaskCancellationOptions(){
    console.log("this is being called");
    timeIdle = 0;
    var j = frontend_routes.ajax_task_cancellation_options();
    $.ajax({
        url: j.url,
        type: j.type,
        success: function(data){
        console.log(data);
        var cont = "<p>Please state reason for cancelling action.</p>";
        var sel = "<select name=\"reason\" class=\"cancelValues\">";
        for(i = 0; i < data.length; i++){
            console.log(data[i]);
            sel += "<option value=\"" + data[i].id + "\">" + data[i].name + "</option>";
        }
        sel += "</select>";
        displayModal("taskCancel", "Reason for cancelling action", cont + sel, ["<a href=\"#\" class=\"cancel\">Cancel</a>", "<a href=\"#\" class=\"confirmCancel selected\">Confirm</a>"], 500, "#obsForm");
    },
    error: function(err){
        console.log(err);
        var errResp = $.parseJSON(err.responseText);
        if(errResp.errors){
            showErrors(errResp.errors);
        }
    }
});
return;
}



// if partial obs has been detected then do a modal with reasons via ajax
function displayPartialObsDialog(){
    timeIdle = 0;
    var j = frontend_routes.json_partial_reasons();
    $.ajax({
        url: j.url,
        type: j.type,
        success: function(data){

            var cont = "<p>Please state reason for submitting partial observation.</p>";
            var sel = "<select name=\"partial_reason\">";
            for(i = 0; i < data.length; i++){
                sel += "<option value=\"" + data[i][0] + "\">" + data[i][1] + "</option>";
            }
            sel += "</select>";
            displayModal("obsPartial", "Submit partial observation", cont + sel, ["<a href=\"#\" class=\"cancel\">Cancel</a>", "<a href=\"#\" class=\"confirmPartial selected\">Confirm</a>"], 500, "form");
        },
        error: function(err){
            var errResp = $.parseJSON(err.responseText);
            if(errResp.errors){
                showErrors(errResp.errors);
            }
        }
    });
    return;
}



window.setInterval(function(){
    if(timing){
        if(timeIdle == idleTime){
            var taskCancelled = "";
            var j = frontend_routes.json_cancel_take_task(taskId);
            $.ajax({
                url: j.url,
                type: j.type,
                success: function(data){
                    if(data.status.toString() === "true"){
                        taskCancelled = "task has been checked back into the system";
                    }else{
                        taskCancelled = "task has <strong>not</strong> been checked into the system: <em>" + data.reason + "</em>";
                    }

                },
                error: function(err){
                    taskCancelled = "task has <strong>not</strong> been checked back into the system";
                }
            });
            displayModal("obsSentBack", "Data entry window expired", "<p>No data entry for 4 minutes, no data submitted.</p>", ["<a href="+frontend_routes.task_list().url+ " class=\"action\">Back to task list</a>"], 0);
            timing = false;
        }else{
            timeIdle++;
            //console.log(timeIdle);
        }
    }
}, 1000);