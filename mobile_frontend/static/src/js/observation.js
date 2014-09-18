function gcs(r, e, n) {
    var a = 0, c = "green";
    return "C" == r ? a += 1 : r >= 1 && 4 >= r && (a += parseInt(r)), "T" == e ? a += 1 : e >= 1 && 5 >= e && (a += parseInt(e)), 
    n >= 1 && 6 >= n && (a += parseInt(n)), 9 > a ? c = "red" : a >= 9 && 12 >= a ? c = "amber" : a >= 13 && (c = "green"), 
    {
        colour: c,
        gcsScore: a
    };
}
function displayModal(e, o, i, n, t, a) {
    t = "undefined" != typeof t ? t : 0, a = "undefined" != typeof a ? a : ".content", 
    console.log("id:" + e + " title:" + o + " content:" + i + " options:" + n + " popupTime:" + t + " el:" + a), 
    $(".content").prepend('<div class="cover" id="obsCover" style="height:' + $(".content").height() + 'px"></div>');
    var l = $('<div class="dialog" id="' + e + '"></div>');
    l.append("<h2>" + o + "</h2>");
    var s = $('<div class="dialogContent"></div>');
    "object" != typeof i && (s.append(i), l.append(s));
    var c;
    switch (n.length) {
      case 1:
        c = "one";
        break;

      case 2:
        c = "two";
        break;

      case 3:
        c = "three";
        break;

      case 4:
        c = "four";
        break;

      default:
        c = "one";
    }
    for (var d = $('<ul class="options ' + c + '-col"></ul>'), p = 0; p < n.length; p++) d.append("<li>" + n[p] + "</li>");
    "object" != typeof i && l.append(d), l.css("display", "inline-block").fadeIn(t), 
    $(a).append(l), $("body").css("overflow", "hidden"), "object" == typeof i ? (console.log("content is object"), 
    i.onload = function() {
        s.append(this), l.append(s), l.append(d), calculateModalSize(l, s);
    }) : calculateModalSize(l, s);
}

function calculateModalSize(e, o) {
    var i = 40, n = $(".header").height(), t = e.children("h2").height(), a = e.children(".options").children("li").first().height(), l = $("#patientName").height(), s = $(window).height() - ($(".header").height() - l - 2 * i), c = s - (t + a) - 2 * i;
    console && console.log("available space is: " + $(window).height() + " - " + ($(".header").height() - 2 * i) + " so entire popup is " + s + ", options is " + a + " and header is " + t + " so menu can be" + c), 
    e.css("top", n + l + i), e.css("max-height", s), o.css("max-height", c);
}

function dismissModal(e, o) {
    if ("delete" == o) $("#" + e).remove(); else if ("hide" == o) $("#" + e).css("display", "none"); else {
        if ("all" != o) return !1;
        $(".dialog").remove();
    }
    $(".cover").remove(), $("body").css("overflow", "auto");
}

$(".content").on("click", ".dialog .cancel", function(e) {
    e.preventDefault(), dismissModal("", "all");
}), $(".content").on("click", ".cover", function(e) {
    e.preventDefault(), dismissModal("", "all");
});
function addValidationRules(e) {
    "ews" == e && ($("#body_temperature").rules("add", {
        min: 27.1,
        max: 44.9,
        pimpedNumber: !0,
        messages: {
            min: "Temperature too low (degrees Celsius)",
            max: "Temperature too high (degrees Celsius)",
            pimpedNumber: "Value must be a number"
        }
    }), $("#respiration_rate").rules("add", {
        min: 1,
        max: 59,
        pimpedDigits: !0,
        messages: {
            min: "Respiratory rate too low",
            max: "Respiratory rate too high",
            pimpedDigits: "Value must be a whole number"
        }
    }), $("#indirect_oxymetry_spo2").rules("add", {
        min: 51,
        max: 100,
        pimpedDigits: !0,
        messages: {
            min: "O2 saturation too low",
            max: "O2 saturation too high",
            pimpedDigits: "Value must be a whole number"
        }
    }), $("#pulse_rate").rules("add", {
        min: 1,
        max: 250,
        pimpedDigits: !0,
        messages: {
            min: "Heart rate too low",
            max: "Heart rate too high",
            pimpedDigits: "Value must be a whole number"
        }
    }), $("#blood_pressure_diastolic").rules("add", {
        min: 1,
        max: 280,
        pimpedDigits: !0,
        lessThan: "#blood_pressure_systolic",
        messages: {
            min: "Diastolic BP too low",
            max: "Diastolic BP too high",
            pimpedDigits: "Value must be a whole number",
            lessThan: "Diastolic must be less than systolic"
        }
    }), $("#blood_pressure_systolic").rules("add", {
        min: 1,
        max: 300,
        pimpedDigits: !0,
        greaterThan: "#blood_pressure_diastolic",
        messages: {
            min: "Systolic BP too low",
            max: "Systolic BP too high",
            pimpedDigits: "Value must be a whole number",
            greaterThan: "Systolic must be greater than diastolic"
        }
    }), $("#device_id").rules("add", {
        required: !1
    }), $("#flow_rate").rules("add", {
        pimpedNumber: !0,
        required: !1,
        min: 0,
        messages: {
            pimpedNumber: "Value must be a number",
            min: "Value too low"
        }
    }), $("#concentration").rules("add", {
        required: !1,
        min: 0,
        messages: {
            min: "Value too low"
        }
    }), $("#cpap_peep").rules("add", {
        required: !1,
        min: 0,
        messages: {
            min: "Value too low"
        }
    }), $("#niv_backup").rules("add", {
        required: !1,
        min: 0,
        messages: {
            min: "Value too low"
        }
    }), $("#niv_ipap").rules("add", {
        required: !1,
        min: 0,
        messages: {
            min: "Value too low"
        }
    }), $("#niv_epap").rules("add", {
        required: !1,
        min: 0,
        messages: {
            min: "Value too low"
        }
    })), "GCS" == e && ($("#gcsData_eyes").rules("add", {
        required: !1
    }), $("#gcsData_verbal").rules("add", {
        required: !1
    }), $("#gcsData_motor").rules("add", {
        required: !1
    })), "STOOL" == e && ($("#stoolsData_bowelOpen").rules("add", {
        required: !1
    }), $("#stoolsData_nausea").rules("add", {
        required: !1
    }), $("#stoolsData_vomiting").rules("add", {
        required: !1
    }), $("#stoolsData_quantity").rules("add", {
        required: !1
    }), $("#stoolsData_colour").rules("add", {
        required: !1
    }), $("#stoolsData_bristolType").rules("add", {
        required: !1
    }), $("#stoolsData_offensive").rules("add", {
        required: !1
    }), $("#stoolsData_strain").rules("add", {
        required: !1
    }), $("#stoolsData_laxatives").rules("add", {
        required: !1
    }), $("#stoolsData_samples").rules("add", {
        required: !1
    }), $("#stoolsData_rectalExam").rules("add", {
        required: !1
    })), "BLOODS" == e && $("#bloodSugarData_bloodSugar").rules("add", {
        min: 1,
        max: 99.9,
        pimpedNumber: !0,
        messages: {
            min: "Blood sugar too low",
            max: "Blood sugar too high",
            pimpedNumber: "Value must be a number"
        }
    }), "WEIGHT" == e && ($("#heightWeightData_height").rules("add", {
        pimpedNumber: !0,
        required: !1,
        messages: {
            pimpedNumber: "Value must be a number"
        }
    }), $("#heightWeightData_weight").rules("add", {
        pimpedNumber: !0,
        messages: {
            pimpedNumber: "Value must be a number"
        }
    })), "BLOODP" == e && $("#BloodProductData_volume").rules("add", {
        pimpedNumber: !0,
        messages: {
            pimpedNumber: "Value must be a number"
        }
    });
}

function resetErrors(e, a) {
    if ("delete" == a) $("#" + e).parent().parent(".obsField").removeClass("error"), 
    $("#" + e).parent().siblings(".input-body").children(".errors").children("label.error").remove(); else {
        if ("empty" != a) return !1;
        $("#" + e).parent().parent(".obsField").removeClass("error"), $("#" + e).parent().parent().find(".errors").text("");
    }
}

function showErrors(e) {
    $.each(e, function(e, a) {
        var r = e.replace(/\./g, "_");
        $("#" + r).parent().parent().addClass("error"), $("#" + r).parent().parent().find(".input-body .errors").text(a);
    });
}
function ToggleBaseSupO2(e) {
    "show" == e ? ($("#parent_flow_rate").removeClass("valHide"), $("#flow_rate").removeClass("exclude"), 
    $("#parent_concentration").removeClass("valHide"), $("#concentration").removeClass("exclude")) : ($("#parent_flow_rate").addClass("valHide"), 
    $("#flow_rate").addClass("exclude"), $("#parent_concentration").addClass("valHide"), 
    $("#concentration").addClass("exclude"));
}

function ToggleCPAPSupO2(e) {
    "show" == e ? ($("#parent_cpap_peep").removeClass("valHide"), $("#cpap_peep").removeClass("exclude")) : ($("#parent_cpap_peep").addClass("valHide"), 
    $("#cpap_peep").addClass("exclude"));
}

function ToggleNIVSupO2(e) {
    "show" == e ? ($("#parent_niv_backup").removeClass("valHide"), $("#niv_backup").removeClass("exclude"), 
    $("#parent_niv_ipap").removeClass("valHide"), $("#niv_ipap").removeClass("exclude"), 
    $("#parent_niv_epap").removeClass("valHide"), $("#niv_epap").removeClass("exclude")) : ($("#parent_niv_backup").addClass("valHide"), 
    $("#niv_backup").addClass("exclude"), $("#parent_niv_ipap").addClass("valHide"), 
    $("#niv_ipap").addClass("exclude"), $("#parent_niv_epap").addClass("valHide"), $("#niv_epap").addClass("exclude"));
}

function displayTaskCancellationOptions() {
    console.log("this is being called"), timeIdle = 0;
    var e = frontend_routes.ajax_task_cancellation_options();
    $.ajax({
        url: e.url,
        type: e.type,
        success: function(e) {
            console.log(e);
            var s = "<p>Please state reason for cancelling action.</p>", a = '<select name="reason" class="cancelValues">';
            for (i = 0; i < e.length; i++) console.log(e[i]), a += '<option value="' + e[i].id + '">' + e[i].name + "</option>";
            a += "</select>", displayModal("taskCancel", "Reason for cancelling action", s + a, [ '<a href="#" class="cancel">Cancel</a>', '<a href="#" class="confirmCancel selected">Confirm</a>' ], 500, "#obsForm");
        },
        error: function(e) {
            console.log(e);
            var s = $.parseJSON(e.responseText);
            s.errors && showErrors(s.errors);
        }
    });
}

function displayPartialObsDialog() {
    timeIdle = 0;
    var e = frontend_routes.json_partial_reasons();
    $.ajax({
        url: e.url,
        type: e.type,
        success: function(e) {
            var s = "<p>Please state reason for submitting partial observation.</p>", a = '<select name="partial_reason">';
            for (i = 0; i < e.length; i++) a += '<option value="' + e[i][0] + '">' + e[i][1] + "</option>";
            a += "</select>", displayModal("obsPartial", "Submit partial observation", s + a, [ '<a href="#" class="cancel">Cancel</a>', '<a href="#" class="confirmPartial selected">Confirm</a>' ], 500, "form");
        },
        error: function(e) {
            var s = $.parseJSON(e.responseText);
            s.errors && showErrors(s.errors);
        }
    });
}

var timeIdle = 0, idleTime = 2400, timing = !0, taskId, EWSlabel = "NEWS", oxmin, oxmax, patientName;

$(document).ready(function() {
    var e = $("#obsForm").attr("patient-id"), s = $("#obsForm").attr("data-type"), a = $("#obsForm").attr("data-source");
    taskId = $("#obsForm").attr("task-id"), oxmin = $("#obsForm").attr("data-min"), 
    oxmax = $("#obsForm").attr("data-max"), patientName = $("#patientName a").text().trim(), 
    $(".header").css({
        "box-shadow": "none",
        "border-bottom": "1px solid #eeeeee"
    }), "medical_team" != s && "frequency" != s && $("#obsForm")[0].reset();
    var o = !1;
    "task" == a ? null != taskId && void 0 != taskId && "" != taskId && frontend_routes.json_take_task(taskId).ajax({
        cache: !1,
        success: function(e) {
            console.log(e), "true" === e.status.toString() || displayModal("getTaskIssue", "Task unavailable", "<p>This task is unavailable. This may be due to the task being taken by another user or that it has been completed.</p>", [ "<a href=" + frontend_routes.task_list().url + ' class="action">Go to Task list</a>' ]);
        },
        error: function(e) {
            console.log(e), displayModal("getTaskError", "Error checking if task available", "<p>There was error checking if this task is available. Someone may have taken it or the task is already been completed.</p>", [ "<a href=" + frontend_routes.task_list().url + ' class="action">Go to Task list</a>' ]);
        }
    }) : timing = !1, $("#patientName a").click(function(s) {
        s.preventDefault(), timeIdle = 0;
        var a = "", o = "", t = "";
        frontend_routes.json_patient_info(e).ajax({
            success: function(e) {
                if (console.log(e), e.full_name && (a += " " + e.full_name), e.gender && (o = e.gender), 
                e.dob) {
                    var s = new Date(e.dob);
                    s = ("0" + s.getDate()).slice(-2) + "/" + ("0" + (s.getMonth() + 1)).slice(-2) + "/" + s.getFullYear(), 
                    t += "<dt>DOB:</dt><dd>" + s + "</dd>";
                }
                "" != e.location && (t += "<dt>Location:</dt><dd>" + e.location + "</dd>"), EWSlabel = "NEWS", 
                e.ews_score && (t += "<dt class='twoline'>Latest " + EWSlabel + " Score</dt><dd class='twoline'>" + e.ews_score + "</dd>"), 
                e.other_identifier && (t += "<dt>Hospital ID</dt><dd>" + e.other_identifier + "</dd>"), 
                e.patient_identifier && (t += "<dt>NHS Number</dt><dd>" + e.patient_identifier + "</dd>"), 
                displayModal("patientInfo", a + '<span class="alignright">' + o + "</span>", "<dl>" + t + "</dl><p><a href='#' id='loadObs'>View Patient Observation Data</a></p>", [ '<a href="#" class="cancel">Cancel</a>' ]);
            },
            error: function() {
                displayModal("patientInfo", "Error getting patient details", "<p>Sorry there seems to have been an error</p>", [ '<a href="#" class="cancel">Cancel</a>' ]);
            }
        });
    }), $("input").on("change", function() {
        timeIdle = 0;
    }), $("input").on("keyup", function() {
        $(this).valid();
    }), $("input").on("focus", function() {
        timeIdle = 0;
    }), $("select").on("change", function() {
        timeIdle = 0;
    }), $("select").on("focus", function() {
        timeIdle = 0;
    });
    var t;
    "medical_team" != s && "frequency" != s && (console.log("adding custom methods"), 
    jQuery.validator.addMethod("pimpedNumber", function(e, s) {
        return /^[-+]?\d+(\.\d+)?$/.test(e) ? !0 : (s.value = "", !0);
    }, "Invalid character found in field"), jQuery.validator.addMethod("lessThan", function(e, s, a) {
        var o = $(a);
        return this.settings.onfocusout && o.off(".validate-lessThan").on("blur.validate-lessThan", function() {
            $(s).valid();
        }), "" != s.value && "" != o.val() ? parseInt(e) < parseInt(o.val()) : !0;
    }, "Diastolic must be less than systolic"), jQuery.validator.addMethod("greaterThan", function(e, s, a) {
        var o = $(a);
        return this.settings.onfocusout && o.off(".validate-greaterThan").on("blur.validate-greaterThan", function() {
            $(s).valid();
        }), "" != s.value && "" != o.val() ? parseInt(e) > parseInt(o.val()) : !0;
    }, "Systolic must be greater than diastolic"), jQuery.validator.addMethod("mewsO2", function(e, s) {
        return s.value <= 94 && "" !== s.value ? ($(s).parent().parent().addClass("warning"), 
        $(s).parent().siblings(".input-body").children(".help").text("O2 less than 95%, action required"), 
        !0) : ($(s).parent().siblings(".input-body").children(".help").text(""), $(s).parent().parent().removeClass("warning"), 
        !0);
    }, "O2 less than 95%, action required"), jQuery.validator.addMethod("pimpedDigits", function(e, s) {
        return /^[-+]?\d+$/.test(e) ? !0 : /^[-+]?\d+\.(\d+)?$/.test(e) ? !1 : (s.value = "", 
        !0);
    }, "Invalid character found in field"), t = $("#obsForm").validate({
        success: function(e) {
            resetErrors(e.attr("for"), "empty");
        },
        errorPlacement: function(e, s) {
            $("#" + s.attr("id")).parent().parent().addClass("error"), $("#" + s.attr("id")).parent().parent().find(".input-body .errors").append(e);
        }
    }), addValidationRules(s)), $(".content").on("click", "#confirmSubmit", function(e) {
        e.preventDefault(), timeIdle = 0;
        var s = frontend_routes.confirm_clinical_notification(taskId);
        return $.ajax({
            url: s.url,
            type: s.type,
            success: function(e) {
                if (console.log(e), 1 == e.status) if (e.related_tasks) if (1 == e.related_tasks.length) dismissModal("obsConfirm", "hide"), 
                displayModal("obsConfirm", "Action required", "<p>" + e.related_tasks[0].summary + "</p>", [ '<a href="' + frontend_routes.task_list().url + '" class="action">Go to My Tasks</a>', '<a href="' + frontend_routes.single_task(e.related_tasks[0].id).url + '" class="confirm">Confirm</a>' ], 500); else if (e.related_tasks.length > 1) {
                    for (var s = "", a = 0; a < e.related_tasks.length; a++) s += '<li><a href="' + frontend_route.single_task(e.related_tasks[a].id).url + '">' + e.related_tasks[a].summary + "</a></li>";
                    dismissModal("obsConfirm", "hide"), displayModal("obsConfirm", "Action required", '<ul class="menu">' + s + "</ul>", [ '<a href="' + frontend_routes.task_list().url + '">Go to My Tasks</a>' ], 500);
                } else dismissModal("obsConfirm", "hide"), displayModal("obsConfirm", "Successfully submitted", "<p>The confirmation has been successfully submitted.</p>", [ '<a href="' + frontend_routes.task_list().url + '" class="action">Go to My Tasks</a>' ], 500); else dismissModal("obsConfirm", "hide"), 
                displayModal("obsConfirm", "Successfully submitted", "<p>The confirmation has been successfully submitted.</p>", [ '<a href="' + frontend_routes.task_list().url + '" class="action">Go to My Tasks</a>' ], 500);
            },
            error: function(e) {
                console.log("re-enabling submit"), o = !1, console.log(e), console.log(e.responseText), 
                $(".obsConfirm .error").css("display", "block");
                var s = $.parseJSON(e.responseText);
                s.errors && showErrors(s.errors);
            }
        }), !0;
    }), $(".content").on("click", "#obsFreqSubmit", function(e) {
        e.preventDefault(), timeIdle = 0;
        var s = $($("#obsForm")[0].elements).not(".exclude").serialize(), a = frontend_routes.confirm_review_frequency(taskId);
        return $.ajax({
            url: a.url,
            type: a.type,
            data: s,
            success: function(e) {
                if (console.log(e), 1 == e.status) if (e.related_tasks) if (1 == e.related_tasks.length) dismissModal("obsConfirm", "hide"), 
                displayModal("obsConfirm", "Action required", "<p>" + e.related_tasks[0].summary + "</p>", [ '<a href="' + frontend_routes.task_list().url + '" class="action">Go to My Tasks</a>', '<a href="' + frontend_routes.single_task(e.relatedTasks[0].id).url + '" class="confirm">Confirm</a>' ], 500); else if (e.related_tasks.length > 1) {
                    for (var s = "", a = 0; a < e.related_tasks.length; a++) s += '<li><a href="' + frontend_routes.single_task(e.relatedTasks[a].id).url + '">' + e.related_tasks[a].summary + "</a></li>";
                    dismissModal("obsConfirm", "hide"), displayModal("obsConfirm", "Action required", '<ul class="menu">' + s + "</ul>", [ '<a href="' + frontend_routes.task_list().url + '">Go to My Tasks</a>' ], 500);
                } else dismissModal("obsConfirm", "hide"), displayModal("obsConfirm", "Successfully submitted", "<p>The observation frequency has been successfully submitted.</p>", [ '<a href="' + frontend_routes.task_list().url + '" class="action">Go to My Tasks</a>' ], 500); else dismissModal("obsConfirm", "hide"), 
                displayModal("obsConfirm", "Successfully submitted", "<p>The  observation frequency has been successfully submitted.</p>", [ '<a href="' + frontend_routes.task_list().url + '" class="action">Go to My Tasks</a>' ], 500);
            },
            error: function(e) {
                console.log("re-enabling submit"), o = !1, console.log(e), console.log(e.responseText), 
                $(".obsConfirm .error").css("display", "block");
                var s = $.parseJSON(e.responseText);
                s.errors && showErrors(s.errors);
            }
        }), !0;
    }), $(".content").on("click", "#obsSubmit", function(e) {
        e.preventDefault(), timeIdle = 0, resetErrors("empty");
        var t = $($("#obsForm")[0].elements).not(".exclude").serialize();
        console.log(t);
        var r;
        return "patient" == a ? (console.log("obsource is patient"), r = jsRoutes.controllers.Observations.submitObsForPatient(s)) : (console.log("obsource is task"), 
        r = frontend_routes.json_task_form_action(taskId)), o || (console.log("disabling submit"), 
        o = !0, $.ajax({
            url: r.url,
            type: r.type,
            data: t,
            success: function(e) {
                if (console.log(e), 1 == e.status) if (e.related_tasks) if (1 == e.related_tasks.length) dismissModal("obsConfirm", "hide"), 
                displayModal("obsConfirm", "Action required", "<p>" + e.related_tasks[0].summary + "</p>", [ '<a href="' + frontend_routes.task_list().url + '" class="action">Go to My Tasks</a>', '<a href="' + frontend_routes.single_task(e.related_tasks[0].id).url + '" class="confirm">Proceed</a>' ], 500); else if (e.related_tasks.length > 1) {
                    for (var s = "", a = 0; a < e.related_tasks.length; a++) s += '<li><a href="' + frontend_routes.single_task(e.related_tasks[a].id).url + '">' + e.related_tasks[a].summary + "</a></li>";
                    dismissModal("obsConfirm", "hide"), displayModal("obsConfirm", "Action required", '<ul class="menu">' + s + "</ul>", [ '<a href="' + frontend_routes.task_list().url + '">Go to My Tasks</a>' ], 500);
                } else dismissModal("obsConfirm", "hide"), displayModal("obsConfirm", "Successfully submitted", "<p>The observations have been successfully submitted.</p>", [ '<a href="' + frontend_routes.task_list().url + '" class="action">Go to My Tasks</a>' ], 500); else dismissModal("obsConfirm", "hide"), 
                displayModal("obsConfirm", "Successfully submitted", "<p>The observations have been successfully submitted.</p>", [ '<a href="' + frontend_routes.task_list().url + '" class="action">Go to My Tasks</a>' ], 500); else if (e.responseText) {
                    console.log("re-enabling submit"), o = !1;
                    var t = $.parseJSON(e.responseText);
                    t.errors && showErrors(t.errors), $("#obsConfirm .error").css("display", "block");
                } else $("#obsConfirm .error").css("display", "block");
            },
            error: function(e) {
                console.log("re-enabling submit"), o = !1, console.log(e), console.log(e.responseText), 
                $(".obsConfirm .error").css("display", "block");
                var s = $.parseJSON(e.responseText);
                s.errors && showErrors(s.errors);
            }
        })), !0;
    }), $("form").on("click", ".confirmPartial", function(e) {
        e.preventDefault(), timeIdle = 0, resetErrors("empty");
        var t = $($("#obsForm")[0].elements).not(".exclude").serialize();
        console.log(t);
        var r;
        "patient" == a ? (console.log("partial obs for patient"), r = jsRoutes.controllers.Observations.submitObsForPatient(s)) : (console.log("partial obs for task"), 
        r = frontend_routes.json_task_form_action(taskId)), o || (console.log("disabling submit"), 
        o = !0, $.ajax({
            url: r.url,
            type: r.type,
            data: t,
            success: function(e) {
                if (console.log(e), 1 == e.status || 2 == e.status) 1 == e.status ? (dismissModal("obsPartial", "hide"), 
                displayModal("obsConfirm", "Successfully submitted", "<p>The partial observation have been successfully submitted. Please be aware that this task is still active until all observations have been taken. Only the last complete NEWS score will be displayed..</p>", [ '<a href="' + frontend_routes.task_list().url + '" class="action">Go to My Tasks</a>' ], 500)) : (dismissModal("obsPartial", "hide"), 
                displayModal("obsConfirm", "Action required", "<p>" + e.message + "</p>", [ '<a href="' + frontend_routes.task_list().url + '" class="action">Go to My Tasks</a>', '<a href="' + frontend_routes.single_task(e.id).url + '" class="confirm">Proceed</a>' ], 500)); else if (e.responseText) {
                    console.log("re-enabling submit"), submitDisbled = !1;
                    var s = $.parseJSON(e.responseText);
                    s.errors && showErrors(s.errors), dismissModal("obsPartial", "hide");
                } else $(".obsConfirm .error").css("display", "block");
            },
            error: function(e) {
                console.log("re-enabling submit"), submitDisbled = !1, console.log(e), console.log(e.responseText), 
                $(".obsConfirm .error").css("display", "block");
                var s = $.parseJSON(e.responseText);
                s.errors && showErrors(s.errors);
            }
        }));
    }), $(".content").on("click", "#loadObs", function(s) {
        s.preventDefault(), timeIdle = 0, $("body").append("<div class='full-modal'><p><a href='#' id='closeFullModal'>Close Popup</a></p><iframe src='" + frontend_routes.single_patient(e).url + "'></iframe></div>"), 
        $(".full-modal iframe").load(function() {
            $(this).show(), $(".full-modal iframe").contents().find(".header").hide(), $(".full-modal iframe").contents().find(".patientInfo").hide(), 
            $(".full-modal iframe").contents().find(".content").css("margin-top", "-3em");
        });
    }), $("body").on("click", "#closeFullModal", function(e) {
        e.preventDefault(), timeIdle = 0, $(".full-modal").remove();
    }), $("#obsForm").on("click", ".confirmCancel", function(e) {
        e.preventDefault(), timeIdle = 0, resetErrors("empty");
        var s = $($("#obsForm .cancelValues")).not(".exclude").serialize();
        console.log(s);
        var a = frontend_routes.cancel_clinical_notification(taskId);
        o || (console.log("disabling submit"), o = !0, $.ajax({
            url: a.url,
            type: a.type,
            data: s,
            success: function(e) {
                if (console.log(e), 1 == e.status || 2 == e.status) 1 == e.status ? (dismissModal("taskCancel", "hide"), 
                displayModal("obsConfirm", "Successfully submitted", "<p>Action successfully cancelled</p>", [ '<a href="' + frontend_routes.task_list().url + '" class="action">Go to My Tasks</a>' ], 500)) : (dismissModal("taskCancel", "hide"), 
                displayModal("obsConfirm", "Action required", "<p>" + e.message + "</p>", [ '<a href="' + frontend_routes.task_list().url + '" class="action">Go to My Tasks</a>', '<a href="' + frontend_routes.single_task(e.taskId).url + '" class="confirm">Proceed</a>' ], 500)); else if (e.responseText) {
                    console.log("re-enabling submit"), submitDisbled = !1;
                    var s = $.parseJSON(e.responseText);
                    s.errors && showErrors(s.errors), dismissModal("taskCancel", "hide");
                } else $(".obsConfirm .error").css("display", "block");
            },
            error: function(e) {
                console.log("re-enabling submit"), submitDisbled = !1, console.log(e), console.log(e.responseText), 
                $(".obsConfirm .error").css("display", "block");
                var s = $.parseJSON(e.responseText);
                s.errors && showErrors(s.errors);
            }
        }));
    }), $("#submitButton").click(function(e) {
        if (e.preventDefault(), timeIdle = 0, t.form()) {
            var a = processObs(s);
            console.log(a), $(".obsError").css("display", "none"), a ? "NEWS" == s ? displayModal("obsConfirm", 'Submit NEWS of <span id="newsScore" class="newsScore">' + a.score + "</span> for " + patientName + "?", '<p>Please confirm you want to submit this score</p><p class="obsError error">Input error, please correct and resubmit</p>', [ ' <a href="#" id="obsCancel" class="cancel">Cancel</a>', '<a href="#" id="obsSubmit">Submit</a>' ]) : "MEWS" == s ? displayModal("obsConfirm", 'Submit MEWS of <span id="newsScore" class="newsScore">' + a.score + "</span> for " + patientName + "?", '<p>Please confirm you want to submit this score</p><p class="obsError error">Input error, please correct and resubmit</p>', [ ' <a href="#" id="obsCancel" class="cancel">Cancel</a>', '<a href="#" id="obsSubmit">Submit</a>' ]) : "BTUHMEWS" == s || ("GCS" == s ? displayModal("obsConfirm", 'Submit GCS of <span id="obsScore" class="' + a.colour + '">' + a.gcsScore + "</span> for " + patientName + "?", '<p>Please confirm you want to submit this score</p><p class="obsError error">Input error, please correct and resubmit</p>', [ ' <a href="#" id="obsCancel" class="cancel">Cancel</a>', '<a href="#" id="obsSubmit">Submit</a>' ]) : "STOOL" == s ? displayModal("obsConfirm", "Submit Stool observation for " + patientName + "?", '<p>Please confirm you want to submit this observation</p><p class="obsError error">Input error, please correct and resubmit</p>', [ '<a href="#" id="obsCancel" class="cancel">Cancel</a>', '<a href="#" id="obsSubmit">Submit</a>' ], 0) : "BLOODS" == s ? displayModal("obsConfirm", "Submit Blood Sugar observation for " + patientName + "?", '<p>Please confirm you want to submit this observation</p><p class="obsError error">Input error, please correct and resubmit</p>', [ '<a href="#" id="obsCancel" class="cancel">Cancel</a>', '<a href="#" id="obsSubmit">Submit</a>' ], 0) : "WEIGHT" == s ? displayModal("obsConfirm", "Submit Height and Weight observation for " + patientName + "?", '<p>Please confirm you want to submit this observation</p><p class="obsError error">Input error, please correct and resubmit</p>', [ '<a href="#" id="obsCancel" class="cancel">Cancel</a>', '<a href="#" id="obsSubmit">Submit</a>' ], 0) : "BLOODP" == s && displayModal("obsConfirm", "Submit Blood Product observation for " + patientName + "?", '<p>Please confirm you want to submit this observation</p><p class="obsError error">Input error, please correct and resubmit</p>', [ '<a href="#" id="obsCancel" class="cancel">Cancel</a>', '<a href="#" id="obsSubmit">Submit</a>' ], 0)) : "ews" == s ? displayPartialObsDialog() : displayModal("obsConfirm", "Mandatory observation values not entered", "<p>Please enter all information and submit observation again</p>", [ '<a href="#" id="obsCancel" class="cancel">OK</a>' ], 0);
        } else console.log(t.errors()), displayModal("obsConfirm", "Form validation errors", "<p>The observation your are trying to submit has input errors. Please correct them and resubmit.</p>", [ ' <a href="#" id="obsCancel" class="cancel">Cancel</a>' ]);
    }), $("#cancelSubmit").click(function(e) {
        e.preventDefault(), timeIdle = 0, displayTaskCancellationOptions();
    }), $("#bristolPopup").click(function(e) {
        e.preventDefault(), timeIdle = 0;
        var s = new Image();
        s.src = "/assets/img/Bristol_stool_chart.png", displayModal("bristol", "Bristol Stool Chart", s, [ '<a href="#" class="cancel">Cancel</a>' ], 0);
    }), $("#obsData_consciousnessToggle").change(function() {
        var e = $("#obsData_consciousnessToggle").val();
        "avpu" == e ? ($("#parent_obsData_avpu").removeClass("valHide"), $("#parent_obsData_eyes").addClass("valHide"), 
        $("#parent_obsData_verbal").addClass("valHide"), $("#parent_obsData_motor").addClass("valHide")) : "gcs" == e ? ($("#parent_obsData_avpu").addClass("valHide"), 
        $("#parent_obsData_eyes").removeClass("valHide"), $("#parent_obsData_verbal").removeClass("valHide"), 
        $("#parent_obsData_motor").removeClass("valHide")) : ($("#parent_obsData_avpu").addClass("valHide"), 
        $("#parent_obsData_eyes").addClass("valHide"), $("#parent_obsData_verbal").addClass("valHide"), 
        $("#parent_obsData_motor").addClass("valHide"));
    }), $("#oxygen_administration_flag").change(function() {
        var e = $("#oxygen_administration_flag").val();
        if ("True" == e) {
            $("#parent_device_id").removeClass("valHide"), $("#device_id").removeClass("exclude");
            var e = $("#device_id").val();
            43 >= e ? (ToggleBaseSupO2("show"), ToggleCPAPSupO2("hide"), ToggleNIVSupO2("hide")) : 44 == e ? (ToggleBaseSupO2("show"), 
            ToggleCPAPSupO2("show"), ToggleNIVSupO2("hide")) : 45 == e ? (ToggleBaseSupO2("show"), 
            ToggleCPAPSupO2("hide"), ToggleNIVSupO2("show")) : e > 45 && (ToggleBaseSupO2("show"), 
            ToggleCPAPSupO2("hide"), ToggleNIVSupO2("hide"));
        } else $("#parent_device_id").addClass("valHide"), $("#device_id").addClass("exclude"), 
        ToggleBaseSupO2("hide"), ToggleCPAPSupO2("hide"), ToggleNIVSupO2("hide");
    }), $("#device_id").change(function() {
        var e = $("#device_id").val();
        43 >= e ? (ToggleBaseSupO2("show"), ToggleCPAPSupO2("hide"), ToggleNIVSupO2("hide")) : 44 == e ? (ToggleBaseSupO2("show"), 
        ToggleCPAPSupO2("show"), ToggleNIVSupO2("hide")) : 45 == e ? (ToggleBaseSupO2("show"), 
        ToggleCPAPSupO2("hide"), ToggleNIVSupO2("show")) : e > 45 && (ToggleBaseSupO2("show"), 
        ToggleCPAPSupO2("hide"), ToggleNIVSupO2("hide"));
    });
}), window.setInterval(function() {
    if (timing) if (timeIdle == idleTime) {
        var e = "", s = frontend_routes.json_cancel_take_task(taskId);
        $.ajax({
            url: s.url,
            type: s.type,
            success: function(s) {
                e = "true" === s.status.toString() ? "task has been checked back into the system" : "task has <strong>not</strong> been checked into the system: <em>" + s.reason + "</em>";
            },
            error: function() {
                e = "task has <strong>not</strong> been checked back into the system";
            }
        }), displayModal("obsSentBack", "Data entry window expired", "<p>No data entry for 4 minutes, no data submitted.</p>", [ "<a href=" + frontend_routes.task_list().url + ' class="action">Back to task list</a>' ], 0), 
        timing = !1;
    } else timeIdle++;
}, 1e3);
function processObs(a) {
    var o;
    if ("ews" == a) {
        if ("" == $("#respiration_rate").val() || "" == $("#indirect_oxymetry_spo2").val() || "" == $("#body_temperature").val() || "" == $("#blood_pressure_systolic").val() || "" == $("#blood_pressure_diastolic").val() || "" == $("#pulse_rate").val() || "" == $("#avpu_text").val() || "" == $("#oxygen_administration_flag").val()) return !1;
        if ("True" == $("#oxygen_administration_flag").val().toString()) {
            if ("" == $("#device_id").val()) return !1;
            if ("44" == $("device_id").val()) {
                if ("" == $("#flow_rate").val() && "" == $("#concentration").val() || "" == $("#cpap_peep").val()) return !1;
            } else if ("45" == $("#device_id").val()) {
                if ("" == $("#flow_rate").val() && "" == $("#concentration").val() || "" == $("#niv_backup").val() || "" == $("#niv_ipap").val() || "" == $("#niv_epap").val()) return !1;
            } else if ("" == $("#flow_rate").val() && "" == $("#concentration").val()) return !1;
        }
        var l = frontend_routes.ews_score(), e = $.ajax({
            url: l.url,
            type: l.type,
            data: $($("#obsForm")[0].elements).not(".exclude").serialize(),
            success: function(a) {
                console.log(a), a.class = a.clinical_risk.toLowerCase(), 3 != a.score && 4 != a.score || 1 != a.three_in_one || (a.clinical_risk = "One observation scored 3 therefore " + a.clinical_risk + " clinical risk"), 
                o = a;
            },
            error: function() {
                console.log("nay");
            }
        });
        return e.then(function(a) {
            return console.log("this is being called"), displayModal("obsConfirm", 'Submit NEWS of <span id="newsScore" class="newsScore">' + a.score + "</span> for " + patientName + "?", "<p><strong>Clinical risk: " + a.clinical_risk + '</strong></p><p>Please confirm you want to submit this score</p><p class="obsError error">Data not sent, please resubmit</p>', [ ' <a href="#" id="obsCancel" class="cancel">Cancel</a>', '<a href="#" id="obsSubmit">Submit</a>' ]), 
            $("#obsConfirm").addClass("clinicalrisk-" + a.class), o;
        }), !0;
    }
    return "GCS" == a ? "" == $("#gcsData_eyes").val() || "" == $("#gcsData_verbal").val() || "" == $("#gcsData_motor").val() ? !1 : o = gcs($("#gcsData_eyes").val(), $("#gcsData_verbal").val(), $("#gcsData_motor").val()) : "STOOL" == a ? "" == $("#stoolsData_bowelOpen").val() || "" == $("#stoolsData_nausea").val() || "" == $("#stoolsData_vomiting").val() || "" == $("#stoolsData_quantity").val() || "" == $("#stoolsData_colour").val() || "" == $("#stoolsData_bristolType").val() || "" == $("#stoolsData_offensive").val() || "" == $("#stoolsData_strain").val() || "" == $("#stoolsData_laxatives").val() || "" == $("#stoolsData_samples").val() || "" == $("#stoolsData_rectalExam").val() ? !1 : !0 : "BLOODS" == a ? "" == $("#bloodSugarData_bloodSugar").val() || "" == $("#bloodSugarData_diabetic").val() ? !1 : !0 : "WEIGHT" == a ? "" == $("#heightWeightData_weight").val() ? !1 : !0 : "BLOODP" == a ? "" == $("#BloodProductData_volume").val() || "" == $("#BloodProductData_product").val() ? !1 : !0 : void 0;
}