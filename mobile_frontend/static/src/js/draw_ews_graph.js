var route = frontend_routes.ajax_get_patient_obs(graph_lib.svg.patientId).ajax({
    dataType: "json",
    success: function(e) {
        console.log(e);
        var a = graph_lib.svg, t = graph_lib.context, n = graph_lib.focus;
        a.chartType = e.obsType;
        var r = e.obs.reverse();
        if (r.length < 1 && console.log("no data"), a.ticks = Math.floor(a.width / 100), 
        t.earliestDate = a.startParse(r[0].date_started), t.now = a.startParse(r[r.length - 1].date_started), 
        a.isMob) if ($(window).width() > $(window).height()) {
            var s = new Date(t.now);
            s.setDate(s.getDate() - a.dateRange.landscape), t.earliestDate = s;
        } else {
            var s = new Date(t.now);
            s.setDate(s.getDate() - a.dateRange.portrait), t.earliestDate = s;
        }
        t.scoreRange = [ {
            "class": "green",
            s: 0,
            e: 4
        }, {
            "class": "amber",
            s: 4,
            e: 6
        }, {
            "class": "red",
            s: 6,
            e: 20
        } ];
        var i = !1;
        r.forEach(function(e) {
            e.date_started = a.startParse(e.date_started), e.indirect_oxymetry_spo2 && (e.indirect_oxymetry_spo2_label = e.indirect_oxymetry_spo2 + "%"), 
            e.oxygen_administration_flag && (i = !0, e.inspired_oxygen = "", "undefined" != typeof e.flow_rate && (e.inspired_oxygen += "Flow: " + e.flow_rate + "l/hr<br>"), 
            "undefined" != typeof e.concentration && (e.inspired_oxygen += "Concentration: " + e.concentration + "%<br>"), 
            e.cpap_peep && (e.inspired_oxygen += "CPAP PEEP: " + e.cpap_peep + "<br>"), e.niv_backup && (e.inspired_oxygen += "NIV Backup Rate: " + e.niv_backup + "<br>"), 
            e.niv_ipap && (e.inspired_oxygen += "NIV IPAP: " + e.niv_ipap + "<br>"), e.niv_epap && (e.inspired_oxygen += "NIV EPAP: " + e.niv_epap + "<br>"));
        }), a.data = r, n.graphs.push({
            key: "respiration_rate",
            label: "RR",
            measurement: "/min",
            max: 60,
            min: 0,
            normMax: 20,
            normMin: 12
        }), n.graphs.push({
            key: "indirect_oxymetry_spo2",
            label: "Spo2",
            measurement: "%",
            max: 100,
            min: 70,
            normMax: 100,
            normMin: 96
        }), n.graphs.push({
            key: "body_temperature",
            label: "Temp",
            measurement: "°C",
            max: 50,
            min: 15,
            normMax: 37.1,
            normMin: 35
        }), n.graphs.push({
            key: "pulse_rate",
            label: "HR",
            measurement: "/min",
            max: 200,
            min: 30,
            normMax: 100,
            normMin: 50
        }), n.graphs.push({
            key: "blood_pressure",
            label: "BP",
            measurement: "mmHg",
            max: 260,
            min: 30,
            normMax: 150,
            normMin: 50
        }), n.tables.push({
            key: "avpu_text",
            label: "AVPU"
        }), n.tables.push({
            key: "indirect_oxymetry_spo2_label",
            label: "Oxygen saturation"
        }), i && n.tables.push({
            key: "inspired_oxygen",
            label: "Inspired oxygen"
        }), a.data = r, graph_lib.initGraph(20), graph_lib.initTable();
    },
    error: function(e) {
        console.log(e);
    }
});

$(document).ready(function() {
    $("#table-content").hide(), $("#obsMenu").hide(), $("#obsButton").click(function(e) {
        e.preventDefault();
        var a = '<ul class="menu">', t = $("#obsMenu").html(), n = $("h3.name strong").first().text().trim();
        a += t, a += "</ul>", displayModal("obsPick", "Pick an observation for " + n, a, [ '<a href="#" id="obsCancel" class="cancel">Cancel</a>' ], 0);
    }), $(".tabs li a").click(function(e) {
        e.preventDefault();
        var a = $(this).attr("href");
        $("#graph-content").hide(), $("#table-content").hide(), $(a).show(), $(".tabs li a").removeClass("selected"), 
        $(this).addClass("selected");
    });
});
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