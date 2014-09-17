function initGraph(t) {
    "undefined" == typeof t && (t = 20), svg.width = $(svg.el).width() - svg.margins.left - svg.margins.right, 
    svg.infoAreaRight = svg.width / 18, focus.height = (focus.graphs.length + 1) * focus.chartHeight, 
    svg.height = context.height + focus.height + context.margins.bottom + context.margins.top + focus.margins.bottom + focus.margins.top, 
    svg.obj.context = d3.select("#contextChart").append("svg").attr("width", svg.width + svg.margins.left + svg.margins.right).attr("height", context.height + context.margins.bottom + context.margins.top).append("g").attr("transform", "translate(0," + context.margins.top + ")"), 
    svg.obj.focus = d3.select("#focusChart").append("svg").attr("width", svg.width + svg.margins.left + svg.margins.right).attr("height", focus.height + focus.margins.bottom + focus.margins.top).append("g").attr("transform", "translate(0," + focus.margins.top / 3 + ")"), 
    context.yScale = d3.scale.linear().domain([ 0, t ]).range([ context.height, 0 ]), 
    context.yAxis = d3.svg.axis().scale(context.yScale).orient("left");
    var e = new Date(context.earliestDate), s = new Date(context.now), a = (s - e) / 1e3 / 60 / 60;
    if (a >= 2 ? (e.setHours(e.getHours() - 1), e.setMinutes(0), e.setSeconds(0), s.setHours(s.getHours() + 1), 
    s.setMinutes(0), s.setSeconds(0)) : (e.setMinutes(e.getMinutes() - 6), s.setMinutes(s.getMinutes() + 6)), 
    context.now = s, context.xScale = d3.time.scale().domain([ e, s ]).range([ svg.margins.left / 4, svg.width - (svg.infoAreaRight + svg.margins.right / 4) ]), 
    context.xAxis = d3.svg.axis().scale(context.xScale).orient("top"), svg.isMob) {
        $(window).width() > $(window).height() ? (e = new Date(context.now), e.setDate(e.getDate() - svg.dateRange.landscape)) : (e = new Date(context.now), 
        e.setDate(e.getDate() - svg.dateRange.portrait));
        var n = new Date(e), i = new Date(s), o = n.getFullYear() + "-" + ("0" + (n.getMonth() + 1)).slice(-2) + "-" + ("0" + n.getDate()).slice(-2), g = ("0" + n.getHours()).slice(-2) + ":" + ("0" + n.getMinutes()).slice(-2) + ":00", r = i.getFullYear() + "-" + ("0" + (i.getMonth() + 1)).slice(-2) + "-" + ("0" + i.getDate()).slice(-2), l = ("0" + i.getHours()).slice(-2) + ":" + ("0" + i.getMinutes()).slice(-2) + ":00";
        $("#contextStartD").val(o), $("#contextStartT").val(g), $("#contextEndD").val(r), 
        $("#contextEndT").val(l), $(".chartDates").show();
    }
    focus.xScale = d3.time.scale().domain([ e, s ]).range([ svg.margins.left / 4, svg.width - (svg.infoAreaRight + svg.margins.right / 4) ]), 
    focus.xAxis = d3.svg.axis().scale(focus.xScale).orient("top"), svg.isMob && (context.xAxis.ticks(5), 
    focus.xAxis.ticks(5)), drawChart(), drawGraph();
}

var svg = {
    margins: {
        top: 20,
        bottom: 20,
        left: 20,
        right: 47
    },
    el: "#contextChart",
    obj: new Array(),
    width: null,
    height: 0,
    infoAreaRight: null,
    labelGap: 10,
    popup: null,
    startParse: d3.time.format("%Y-%m-%d %H:%M:%S").parse,
    patientId: $(".name").attr("data-id"),
    transitionDuration: 1e3,
    chartType: null,
    isMob: $(window).width() <= 600,
    datesChanged: !1,
    dateRange: {
        portrait: 1,
        landscape: 5
    },
    data: null,
    windowWidthDelta: $(window).width(),
    ticks: 10
}, context = {
    height: 100,
    margins: {
        top: 30,
        bottom: 40
    },
    xAxis: null,
    yAxis: null,
    xScale: null,
    area: null,
    yScale: null,
    brush: null,
    scoreRange: [ {
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
        e: 17.9
    } ],
    earliestDate: new Date(),
    now: new Date()
}, focus = {
    chartHeight: 100,
    margins: {
        top: 60,
        bottom: 20
    },
    height: null,
    xAxis: null,
    graphs: new Array(),
    tables: new Array(),
    areas: new Array(),
    xScale: null,
    yScale: null,
    yAxis: null,
    chartPadding: 20
};
function insertLinebreaks(e) {
    var t = d3.select(this), s = 10, n = [ "Sun", "Mon", "Tues", "Wed", "Thu", "Fri", "Sat" ], r = n[e.getDay()] + " " + e.getDate() + "/" + ("0" + (e.getMonth() + 1)).slice(-2) + " " + ("0" + e.getHours()).slice(-2) + ":" + ("0" + e.getMinutes()).slice(-2), a = r.split(" ");
    t.text("");
    for (var i = 0; i < a.length; i++) {
        var o = t.append("tspan").text(a[i]);
        i > 0 && o.attr("x", 0).attr("dy", "15");
    }
    t.attr("y", "-" + (a.length * s + s));
}

function lineGen(e) {
    return e.join("L");
}

function handleResize() {
    $("#chart").width() - (svg.margins.right + svg.margins.left);
    if (svg.isMob && !svg.datesChanged) {
        var e, t;
        e = new Date(context.now), t = new Date(context.now), t.setDate($(window).width() > $(window).height() ? e.getDate() - svg.dateRange.landscape : e.getDate() - svg.dateRange.portrait);
        var s = t.getFullYear() + "-" + ("0" + (t.getMonth() + 1)).slice(-2) + "-" + ("0" + t.getDate()).slice(-2), n = ("0" + t.getHours()).slice(-2) + ":" + ("0" + t.getMinutes()).slice(-2) + ":00", r = e.getFullYear() + "-" + ("0" + (e.getMonth() + 1)).slice(-2) + "-" + ("0" + e.getDate()).slice(-2), a = ("0" + e.getHours()).slice(-2) + ":" + ("0" + e.getMinutes()).slice(-2) + ":00";
        $("#contextStartD").val(s), $("#contextStartT").val(n), $("#contextEndD").val(r), 
        $("#contextEndT").val(a), focus.xScale.domain([ t, e ]);
    }
    resizeGraphs();
}

function process_obs_name(e) {
    switch (e) {
      case "avpu_text":
        return "AVPU";

      case "pulse_rate":
        return "Pulse Rate";

      case "indirect_oxymetry_spo2":
        return "Indirect Oxymetry spO2";

      case "oxygen_administration_flag":
        return "Oxygen Administration Flag";

      case "respiration_rate":
        return "Respiration Rate";

      case "body_temperature":
        return "Body Temperature";

      case "blood_pressure_systolic":
        return "Blood Pressure Systolic";

      case "blood_pressure_diastolic":
        return "Blood Pressure Diastolic";

      case "score":
        return "NEWS Score";

      case "inspired_oxygen":
        return "Inspired Oxygen Parameters";
    }
}

$(window).resize(function() {
    $(window).width() != svg.windowWidthDelta && (setTimeout(function() {
        handleResize();
    }, 1e3), svg.windowWidthDelta = $(window).width());
});
function drawChart() {
    context.obj = svg.obj.context.append("g").attr("transform", "translate(" + svg.margins.left + "," + context.margins.top + ")"), 
    context.obj.selectAll("rect.scoreRange").data(context.scoreRange).enter().append("rect").attr({
        "class": function(t) {
            return t.class;
        },
        x: context.xScale(context.xScale.domain()[0]),
        y: function(t) {
            return context.yScale(t.e) - 1;
        },
        width: svg.width - (svg.infoAreaRight + svg.margins.right / 3),
        height: function(t) {
            return context.yScale(t.s) - (context.yScale(t.e) - 1);
        }
    }), context.obj.selectAll("line.verticalGrid").data(context.xScale.ticks()).enter().append("line").attr({
        "class": "verticalGrid",
        x1: function(t) {
            return context.xScale(t);
        },
        x2: function(t) {
            return context.xScale(t);
        },
        y1: 0,
        y2: context.height,
        "shape-rendering": "cripsEdges",
        stroke: "rgba(0,0,0,0.1)",
        "stroke-width": "1px"
    }), context.obj.selectAll("line.horizontalGrid").data([ 0, 3, 6, 9, 12, 15, 18 ]).enter().append("line").attr({
        "class": "horizontalGrid",
        x1: context.xScale(context.xScale.domain()[0]),
        x2: context.xScale(context.xScale.domain()[1]),
        y1: function(t) {
            return context.yScale(t);
        },
        y2: function(t) {
            return context.yScale(t);
        },
        "shape-rendering": "cripsEdges",
        stroke: "rgba(0,0,0,0.1)",
        "stroke-width": "1px"
    }), context.obj.append("g").attr("class", "x axis").call(context.xAxis), context.obj.append("g").attr({
        "class": "y axis",
        transform: "translate(5,0)"
    }).call(context.yAxis), context.brush = d3.svg.brush().x(context.xScale).on("brush", brushed), 
    context.obj.append("g").attr("class", "x brush").call(context.brush).selectAll("rect").attr("y", -6).attr("height", context.height + 7).style({
        fill: "#333",
        opacity: "0.5"
    }), context.area = d3.svg.line().interpolate("step-after").defined(function(t) {
        return t.score > -1 ? t : void 0;
    }).x(function(t) {
        return context.xScale(t.date_started);
    }).y(function(t) {
        return context.yScale(t.score);
    }), context.obj.append("path").datum(svg.data).attr("d", context.area).style({
        stroke: "#555555",
        "stroke-width": "1",
        fill: "none"
    }).attr("class", "contextPath"), context.obj.selectAll("circle.contextPoint").data(svg.data.filter(function(t) {
        return t.score > -1 ? t : void 0;
    })).enter().append("circle").attr("cx", function(t) {
        return context.xScale(t.date_started);
    }).attr("cy", function(t) {
        return context.yScale(t.score);
    }).attr("r", 3).attr("class", "contextPoint").on("mouseover", function(t) {
        return contextMouseOver(t.score);
    }).on("mouseout", contextMouseOut), context.obj.selectAll("circle.emptyContextPoint").data(svg.data.filter(function(t) {
        return console.log(typeof t.score), void 0 == t.score ? t : void 0;
    })).enter().append("circle").attr("cx", function(t) {
        return context.xScale(t.date_started);
    }).attr("cy", function() {
        return context.yScale(context.yScale.domain()[1] / 2);
    }).attr("r", 3).attr("class", "emptyContextPoint").on("mouseover", function() {
        return contextMouseOver("Partial observation");
    }).on("mouseout", contextMouseOut), svg.popup = d3.select("body").append("div").attr("class", "contextPopup").style("opacity", 1e-6), 
    context.obj.selectAll(".x.axis g text").each(insertLinebreaks), focus.obj = svg.obj.focus.append("g").attr("transform", "translate(" + svg.margins.left + "," + focus.margins.top + ")"), 
    focus.obj.append("defs").append("clipPath").attr("id", "clip").append("rect").attr("width", svg.width - svg.infoAreaRight).attr("height", focus.height - focus.margins.bottom).attr("y", -20), 
    focus.obj.append("g").attr("class", "x axis").attr("transform", "translate(0,-20)").call(focus.xAxis), 
    focus.obj.selectAll(".x.axis g text").each(insertLinebreaks);
}

function drawGraph() {
    for (var t = 0; t < focus.graphs.length; t++) {
        var e = focus.graphs[t];
        e.offset = t * focus.chartHeight + focus.chartPadding * (t - 1), e.yScale = d3.scale.linear().domain([ e.min, e.max ]).range([ focus.chartHeight + e.offset, e.offset ]), 
        e.diffNorm = e.yScale(e.normMin) - e.yScale(e.normMax), focus.obj.append("line").attr("x1", 5).attr("x2", svg.width - svg.infoAreaRight - 11).attr("y1", focus.chartHeight + e.offset).attr("y2", focus.chartHeight + e.offset).style("stroke", "black").style("opacity", 1).style("stroke-width", 2).attr("class", "line line-" + e.label), 
        "BP" != e.label ? focus.obj.append("rect").attr("x", 5).attr("y", e.yScale(e.normMax)).attr("width", svg.width - svg.infoAreaRight - 16).attr("height", e.diffNorm).style("fill", "#CCCCCC").style("opacity", .75).attr("class", "norm norm-" + e.label) : focus.obj.append("line").attr("x1", 5).attr("x2", svg.width - svg.infoAreaRight - 11).attr("y1", e.yScale(100)).attr("y2", e.yScale(100)).style("stroke", "black").style("opacity", 1).style("stroke-width", 1).attr("class", "line line-" + e.label), 
        focus.obj.append("text").text(e.normMin).attr("x", -5).attr("y", e.yScale(e.normMin)).attr("font-family", "sans-serif").attr("font-size", "10px").attr("font-weight", "normal").attr("text-anchor", "middle").attr("dominant-baseline", "hanging"), 
        focus.obj.append("text").text(e.normMax).attr("x", -5).attr("y", e.yScale(e.normMax)).attr("font-family", "sans-serif").attr("font-size", "10px").attr("font-weight", "normal").attr("text-anchor", "middle");
        var a = e.diffNorm - 10;
        a > 0 && (a = 0);
        var n = d3.svg.axis().scale(e.yScale).orient("left").ticks(10), o = focus.obj.append("g").call(n);
        n = e.yScale.ticks(), o.remove(), focus.obj.selectAll("line.verticalGrid.focus" + e.label).data(focus.xScale.ticks()).enter().append("line").attr({
            "class": "verticalGrid focus" + e.label,
            x1: function(t) {
                return focus.xScale(t);
            },
            x2: function(t) {
                return focus.xScale(t);
            },
            y1: e.yScale.range()[0],
            y2: e.yScale.range()[1],
            "shape-rendering": "crispEdges",
            stroke: "rgba(0,0,0,0.1)",
            "stroke-width": "1px"
        }), focus.obj.selectAll("line.horizontalGrid.focus" + e.label).data(n).enter().append("line").attr({
            "class": "horizontalGrid focus" + e.label,
            x1: 5,
            x2: svg.width - svg.infoAreaRight - 11,
            y1: function(t) {
                return e.yScale(t);
            },
            y2: function(t) {
                return e.yScale(t);
            },
            "shape-rendering": "crispEdges",
            stroke: "rgba(0,0,0,0.1)",
            "stroke-width": "1px"
        }), "BP" == e.label ? (focus.obj.selectAll("." + e.label + "up-arrows").data(svg.data.filter(function(t) {
            return t.blood_pressure_systolic ? t : void 0;
        })).enter().append("path").attr({
            d: d3.svg.symbol().size(function() {
                return 45;
            }).type(function() {
                return "triangle-up";
            }),
            transform: function(t) {
                return "translate(" + context.xScale(t.date_started) + "," + (e.yScale(t.blood_pressure_systolic) + 3) + ")";
            },
            "class": "data_symbols " + e.label + "up-arrows"
        }).style("display", function(t) {
            return null === t.blood_pressure_systolic ? "none" : null;
        }).on("mouseover", function(t) {
            return contextMouseOver("s:" + t.blood_pressure_systolic + " d:" + t.blood_pressure_diastolic);
        }).on("mouseout", contextMouseOut), focus.obj.selectAll("." + e.label + "down-arrows").data(svg.data.filter(function(t) {
            return t.blood_pressure_diastolic ? t : void 0;
        })).enter().append("path").attr({
            d: d3.svg.symbol().size(function() {
                return 45;
            }).type(function() {
                return "triangle-down";
            }),
            transform: function(t) {
                return "translate(" + context.xScale(t.date_started) + "," + (e.yScale(t.blood_pressure_diastolic) - 3) + ")";
            },
            "class": "data_symbols " + e.label + "down-arrows"
        }).style("display", function(t) {
            return null === t.blood_pressure_diastolic ? "none" : null;
        }).on("mouseover", function(t) {
            return contextMouseOver("s:" + t.blood_pressure_systolic + " d:" + t.blood_pressure_diastolic);
        }).on("mouseout", contextMouseOut), focus.obj.selectAll("#" + e.label).data(svg.data.filter(function(t) {
            return t.blood_pressure_diastolic && t.blood_pressure_systolic ? t : void 0;
        })).enter().append("rect").attr({
            width: 2,
            height: function(t) {
                return e.yScale(t.blood_pressure_diastolic) - e.yScale(t.blood_pressure_systolic);
            },
            x: function(t) {
                return focus.xScale(t.date_started) - 1;
            },
            y: function(t) {
                return e.yScale(t.blood_pressure_systolic);
            },
            "clip-path": "url(#clip)",
            "class": "data_lines data-" + e.label
        }).style("display", function(t) {
            return null === t.blood_pressure_systolic || null === t.blood_pressure_diastolic ? "none" : null;
        }).style({
            stroke: "rgba(0,0,0,0)",
            "stroke-width": "3"
        }).on("mouseover", function(t) {
            return contextMouseOver("s:" + t.blood_pressure_systolic + " d:" + t.blood_pressure_diastolic);
        }).on("mouseout", contextMouseOut), focus.obj.append("text").text(e.label).attr("y", e.yScale(e.normMax) + a).attr("x", svg.width - svg.infoAreaRight).attr({
            "font-family": "sans-serif",
            "font-size": "12px",
            "font-weight": "bold",
            fill: "#BBBBBB",
            "text-anchor": "start",
            "class": "info infoname-" + e.label
        }), focus.obj.append("text").text(function() {
            return svg.data[svg.data.length - 1].blood_pressure_systolic ? svg.data[svg.data.length - 1].blood_pressure_systolic : "";
        }).attr("y", e.yScale(e.normMin) - 20).attr("x", svg.width - svg.infoAreaRight).attr({
            "font-family": "sans-serif",
            "font-size": "12px",
            "font-weight": "bold",
            "text-anchor": "start",
            "class": "info infovalue1-" + e.label
        }), focus.obj.append("text").text(function() {
            return svg.data[svg.data.length - 1].blood_pressure_diastolic ? svg.data[svg.data.length - 1].blood_pressure_diastolic : "";
        }).attr("y", e.yScale(e.normMin) - 10).attr("x", svg.width - svg.infoAreaRight).attr({
            "font-family": "sans-serif",
            "font-size": "12px",
            "font-weight": "bold",
            "text-anchor": "start",
            "class": "info infovalue2-" + e.label
        }), focus.obj.append("text").text(function() {
            return e.measurement;
        }).attr("y", e.yScale(e.normMin) - 10).attr("x", svg.width - svg.infoAreaRight + 2 * svg.labelGap).attr({
            "font-family": "sans-serif",
            "font-size": "9px",
            "font-weight": "bold",
            "text-anchor": "start",
            "class": "info infovalue3-" + e.label
        })) : (e.area = d3.svg.line().interpolate("linear").defined(function(t) {
            return t[e.key] ? t : void 0;
        }).x(function(t) {
            return focus.xScale(t.date_started);
        }).y(function(t) {
            return e.yScale(t[e.key]);
        }), focus.obj.append("path").datum(svg.data.filter(function(t) {
            return t[e.key] ? t : void 0;
        })).attr("d", e.area).style({
            stroke: "#888888",
            "stroke-width": "1",
            fill: "none"
        }).attr("class", "focusPath").attr("id", "path-" + e.key).attr("clip-path", "url(#clip)"), 
        focus.obj.selectAll("#" + e.label).data(svg.data.filter(function(t) {
            return t[e.key] ? t : void 0;
        })).enter().append("circle").attr("cx", function(t) {
            return focus.xScale(t.date_started);
        }).attr("cy", function(t) {
            return e.yScale(t[e.key]);
        }).attr("r", 3).attr("class", "data_points data-" + e.label).style("display", function(t) {
            return t[e.key] ? null : "none";
        }).attr("clip-path", "url(#clip)").on("mouseover", function(t) {
            return contextMouseOver(t[e.label]);
        }).on("mouseout", contextMouseOut), focus.obj.append("text").text(e.label).attr("y", e.yScale(e.normMax) + a).attr("x", svg.width - svg.infoAreaRight).attr({
            "font-family": "sans-serif",
            "font-size": "12px",
            "font-weight": "bold",
            fill: "#BBBBBB",
            "text-anchor": "start",
            "class": "info infoname-" + e.label
        }), focus.obj.append("text").text(function() {
            return svg.data[svg.data.length - 1][e.key] ? svg.data[svg.data.length - 1][e.key] + e.measurement : "";
        }).attr("y", e.yScale(e.normMin) - a).attr("x", svg.width - svg.infoAreaRight).attr({
            "font-family": "sans-serif",
            "font-size": "12px",
            "font-weight": "bold",
            "text-anchor": "start",
            "class": "info infovalue-" + e.label
        }));
    }
}

function drawTabularObs() {
    var t = d3.select("#table-content").append("div").attr("style", "padding-top: 1em"), e = t.selectAll(".card").data(svg.data.reverse()).enter().append("div").attr("class", "card"), a = (e.append("h3").text(function(t) {
        return ("0" + t.date_started.getHours()).slice(-2) + ":" + ("0" + t.date_started.getMinutes()).slice(-2) + " " + ("0" + t.date_started.getDate()).slice(-2) + "/" + ("0" + (t.date_started.getMonth() + 1)).slice(-2) + "/" + t.date_started.getFullYear();
    }), e.append("table")), n = a.selectAll("tr").data(function(t) {
        return $.map(t, function(t, e) {
            if ("indirect_oxymetry_spo2_label" !== e) {
                var a = process_obs_name(e);
                if ("undefined" != typeof a) return {
                    key: a,
                    value: t
                };
            }
        });
    }).enter();
    n.append("tr").html(function(t) {
        return "object" != typeof t.value ? "<td>" + t.key + "</td><td>" + t.value + "</td>" : "Oxygen Administration Flag" == t.key ? 1 == t.value.onO2 ? "<td>" + t.key + "</td><td> true </td>" : "<td>" + t.key + "</td><td> false </td>" : void 0;
    });
}

function redrawFocus(t) {
    focus.obj.selectAll(".data_points").transition().duration(svg.transitionDuration).attr("cx", function(t) {
        return focus.xScale(t.date_started);
    }), svg.transitionDuration = t ? 1e3 : 0;
    for (var e = 0; e < focus.graphs.length; e++) {
        var a = focus.graphs[e];
        a.area = d3.svg.line().interpolate("linear").x(function(t) {
            return focus.xScale(t.date_started);
        }).y(function(t) {
            return a.yScale(t[a.key]);
        }), focus.obj.select("#path-" + a.key).transition().duration(svg.transitionDuration).attr("d", a.area), 
        focus.obj.selectAll("line.verticalGrid.focus" + a.label).remove().data(focus.xScale.ticks()).enter().append("line").attr({
            "class": "verticalGrid focus" + a.label,
            x1: function(t) {
                return focus.xScale(t);
            },
            x2: function(t) {
                return focus.xScale(t);
            },
            y1: a.yScale.range()[0],
            y2: a.yScale.range()[1],
            "shape-rendering": "crispEdges",
            stroke: "rgba(0,0,0,0.1)",
            "stroke-width": "1px"
        });
    }
    focus.obj.select(".x.axis").call(focus.xAxis), focus.obj.selectAll(".data_points").transition().duration(svg.transitionDuration).attr("cx", function(t) {
        return focus.xScale(t.date_started);
    }), focus.obj.selectAll(".data_symbols").remove(), focus.obj.selectAll(".BPup-arrows").data(svg.data.filter(function(t) {
        return t.blood_pressure_systolic && t.date_started >= focus.xScale.domain()[0] && t.date_started <= focus.xScale.domain()[1] ? (console.log(t), 
        t) : void 0;
    })).enter().append("path").attr({
        d: d3.svg.symbol().size(function() {
            return console.log("calling size"), 45;
        }).type(function() {
            return console.log("calling type"), "triangle-up";
        }),
        transform: function(t) {
            return console.log("calling transform"), "translate(" + (focus.xScale(t.date_started) + 1) + "," + (focus.graphs[focus.graphs.length - 1].yScale(t.blood_pressure_systolic) + 3) + ")";
        },
        "class": "data_symbols BPup-arrows"
    }).style("display", function(t) {
        return null === t.blood_pressure_systolic ? "none" : null;
    }).on("mouseover", function(t) {
        return contextMouseOver("s:" + t.blood_pressure_systolic + " d:" + t.blood_pressure_diastolic);
    }).on("mouseout", contextMouseOut), focus.obj.selectAll(".BPdown-arrows").data(svg.data.filter(function(t) {
        return t.blood_pressure_diastolic && t.date_started >= focus.xScale.domain()[0] && t.date_started <= focus.xScale.domain()[1] ? t : void 0;
    })).enter().append("path").attr({
        d: d3.svg.symbol().size(function() {
            return 45;
        }).type(function() {
            return "triangle-down";
        }),
        transform: function(t) {
            return "translate(" + (focus.xScale(t.date_started) + 1) + "," + (focus.graphs[focus.graphs.length - 1].yScale(t.blood_pressure_diastolic) - 3) + ")";
        },
        "class": "data_symbols BPdown-arrows"
    }).style("display", function(t) {
        return null === t.blood_pressure_diastolic ? "none" : null;
    }).on("mouseover", function(t) {
        return contextMouseOver("s:" + t.blood_pressure_systolic + " d:" + t.blood_pressure_diastolic);
    }).on("mouseout", contextMouseOut), focus.obj.selectAll(".data_lines").transition().duration(svg.transitionDuration).attr("x", function(t) {
        return focus.xScale(t.date_started);
    }), focus.obj.select(".x.axis").call(focus.xAxis), focus.obj.selectAll(".horizontalGrid").transition().duration(svg.transitionDuration).attr("x2", focus.xScale(focus.xScale.domain()[1])), 
    initTable(), focus.obj.selectAll(".x.axis g text").each(insertLinebreaks);
}

function resizeGraphs() {
    {
        var t = $(svg.el);
        t.width() > t.height() ? "landscape" : "portrait";
    }
    w = t.width() - svg.margins.left - svg.margins.right, svg.width = w + svg.margins.left + svg.margins.right, 
    svg.obj = d3.select("svg").transition().duration(svg.transitionDuration).attr("width", svg.width), 
    context.xScale.range([ svg.margins.left / 4, w - (svg.infoAreaRight + svg.margins.right / 4) ]), 
    context.xAxis.scale(context.xScale), context.obj.selectAll(".x.axis").call(context.xAxis), 
    context.area.x(function(t) {
        return context.xScale(t.date_started);
    }).y(function(t) {
        return context.yScale(t.score);
    }), context.obj.selectAll(".contextPath").transition().duration(svg.transitionDuration).attr("d", context.area), 
    context.obj.selectAll(".contextPoint").transition().duration(svg.transitionDuration).attr("cx", function(t) {
        return context.xScale(t.date_started);
    }), context.obj.selectAll(".x.axis g text").each(insertLinebreaks), context.obj.selectAll(".horizontalGrid").transition().duration(svg.transitionDuration).attr("x2", w - svg.infoAreaRight - 10), 
    context.obj.selectAll(".green").transition().duration(svg.transitionDuration).attr("width", w - (svg.infoAreaRight + svg.margins.right / 3)), 
    context.obj.selectAll(".amber").transition().duration(svg.transitionDuration).attr("width", w - (svg.infoAreaRight + svg.margins.right / 3)), 
    context.obj.selectAll(".red").transition().duration(svg.transitionDuration).attr("width", w - (svg.infoAreaRight + svg.margins.right / 3)), 
    context.obj.selectAll(".verticalGrid").remove().data(context.xScale.ticks()).enter().append("line").attr({
        "class": "verticalGrid",
        x1: function(t) {
            return context.xScale(t);
        },
        x2: function(t) {
            return context.xScale(t);
        },
        y1: 0,
        y2: context.height,
        "shape-rendering": "crispEdges",
        stroke: "rgba(0,0,0,0.1)",
        "stroke-width": "1px"
    }), svg.isMob || context.brush.x(context.xScale), focus.obj.select("#clip").transition().duration(svg.transitionDuration).attr("width", w - (svg.infoAreaRight + svg.margins.right / 4)), 
    focus.obj.select("#clip").transition().duration(svg.transitionDuration).select("rect").attr("width", w - (svg.infoAreaRight + svg.margins.right / 4)), 
    focus.xScale.range([ svg.margins.left / 4, w - (svg.infoAreaRight + svg.margins.right / 4) ]), 
    focus.xAxis.scale(focus.xScale), d3.select("#focusChart").select("svg").transition().duration(svg.transitionDuration).attr("width", w + svg.infoAreaRight + svg.margins.right), 
    focus.obj.selectAll(".line").transition().duration(svg.transitionDuration).attr("x2", w - (svg.infoAreaRight + svg.margins.right / 4)), 
    focus.obj.selectAll(".norm").transition().duration(svg.transitionDuration).attr("width", w - (svg.infoAreaRight + svg.margins.right / 3)), 
    focus.obj.selectAll(".info").transition().duration(svg.transitionDuration).attr("x", w - (svg.infoAreaRight + svg.margins.right / 4) + svg.labelGap), 
    focus.obj.selectAll(".infovalue3-BP").transition().duration(svg.transitionDuration).attr("x", w - (svg.infoAreaRight + svg.margins.right / 4) + 3 * svg.labelGap), 
    redrawFocus(!1);
}

function initTable() {
    var t = [ "Type" ];
    d3.select("#chartTable").selectAll("tr").remove();
    for (var e = new Date(focus.xScale.domain()[0]), a = new Date(focus.xScale.domain()[1]), n = 0; n < svg.data.length; n++) svg.data[n].date_started >= e && svg.data[n].date_started <= a && t.push(svg.data[n].date_started);
    dataTableTr = d3.select("#chartTable").append("tr"), dataTableTr.selectAll("th").data(t).enter().append("th").html(function(t) {
        return "Type" == t ? t : ("0" + t.getDate()).slice(-2) + "/" + ("0" + (t.getMonth() + 1)).slice(-2) + "<br>" + ("0" + t.getHours()).slice(-2) + ":" + ("0" + t.getMinutes()).slice(-2);
    }).style("width", 90 / t.length + "%"), drawTable();
}

function drawTable() {
    for (var t = 0; t < focus.tables.length; t++) {
        for (var e = focus.tables[t], a = [ e.label ], n = new Date(focus.xScale.domain()[0]), o = new Date(focus.xScale.domain()[1]), r = 0; r < svg.data.length; r++) svg.data[r].date_started >= n && svg.data[r].date_started <= o && a.push(svg.data[r][e.key]);
        var s = d3.select("#chartTable").append("tr");
        s.selectAll("td." + e.label).data(a).enter().append("td").html(function(t) {
            return t;
        }).attr("class", e.label);
    }
}
function contextMouseOver(t) {
    var e = {
        top: 0,
        left: 3,
        right: 0,
        bottom: 40
    };
    svg.popup.style("left", d3.event.pageX + e.left + "px").style("top", d3.event.pageY - e.bottom + "px").text(t), 
    svg.popup.transition().duration(500).style("opacity", 1);
}

function contextMouseOut() {
    svg.popup.transition().duration(500).style("opacity", 1e-6);
}

function contextChange() {
    if ("" != $("#contextStartT").val() && "" != $("#contextEndD").val() && "" != $("#contextEndT").val() && "" != $("#contextStartD").val()) {
        svg.datesChanged = !0;
        var t = $("#contextStartT").val(), e = $("#contextStartD").val(), o = $("#contextEndT").val(), n = $("#contextEndD").val(), s = e + "T" + t, a = n + "T" + o, c = new Date(s), l = new Date(a);
        focus.xScale.domain([ c, l ]), focus.obj.select(".x.axis").call(focus.xAxis), redrawFocus(!1), 
        initTable(), focus.obj.selectAll(".x.axis g text").each(insertLinebreaks);
    }
}

function brushed() {
    if (focus.xScale.domain(context.brush.empty() ? context.xScale.domain() : context.brush.extent()), 
    context.brush.empty()) $("#focusTitle").html("Individual values"); else {
        var t = context.brush.extent()[0], e = context.brush.extent()[1], o = ("0" + t.getHours()).slice(-2) + ":" + ("0" + t.getMinutes()).slice(-2) + " " + ("0" + t.getDate()).slice(-2) + "/" + ("0" + t.getMonth()).slice(-2), n = ("0" + e.getHours()).slice(-2) + ":" + ("0" + e.getMinutes()).slice(-2) + " " + ("0" + e.getDate()).slice(-2) + "/" + ("0" + e.getMonth()).slice(-2);
        $("#focusTitle").html("Individual values for " + o + " - " + n);
    }
    redrawFocus(!1);
}
var route = frontend_routes.ajax_get_patient_obs(svg.patientId).ajax({
    dataType: "json",
    success: function(e) {
        console.log(e), svg.chartType = e.obsType;
        var t = e.obs.reverse();
        if (t.length < 1 && console.log("no data"), svg.ticks = Math.floor(svg.width / 100), 
        context.earliestDate = svg.startParse(t[0].date_started), context.now = svg.startParse(t[t.length - 1].date_started), 
        svg.isMob) if ($(window).width() > $(window).height()) {
            var a = new Date(context.now);
            a.setDate(a.getDate() - svg.dateRange.landscape), context.earliestDate = a;
        } else {
            var a = new Date(context.now);
            a.setDate(a.getDate() - svg.dateRange.portrait), context.earliestDate = a;
        }
        context.scoreRange = [ {
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
        var n = !1;
        svg.data = t, t.forEach(function(e) {
            e.date_started = svg.startParse(e.date_started), e.indirect_oxymetry_spo2 && (e.indirect_oxymetry_spo2_label = e.indirect_oxymetry_spo2 + "%"), 
            e.oxygen_administration_flag && (n = !0, e.inspired_oxygen = "", "undefined" != typeof e.flow_rate && (e.inspired_oxygen += "Flow: " + e.flow_rate + "l/hr<br>"), 
            "undefined" != typeof e.concentration && (e.inspired_oxygen += "Concentration: " + e.concentration + "%<br>"), 
            e.cpap_peep && (e.inspired_oxygen += "CPAP PEEP: " + e.cpap_peep + "<br>"), e.niv_backup && (e.inspired_oxygen += "NIV Backup Rate: " + e.niv_backup + "<br>"), 
            e.niv_ipap && (e.inspired_oxygen += "NIV IPAP: " + e.niv_ipap + "<br>"), e.niv_epap && (e.inspired_oxygen += "NIV EPAP: " + e.niv_epap + "<br>"));
        }), svg.data = t, focus.graphs.push({
            key: "respiration_rate",
            label: "RR",
            measurement: "/min",
            max: 60,
            min: 0,
            normMax: 20,
            normMin: 12
        }), focus.graphs.push({
            key: "indirect_oxymetry_spo2",
            label: "Spo2",
            measurement: "%",
            max: 100,
            min: 70,
            normMax: 100,
            normMin: 96
        }), focus.graphs.push({
            key: "body_temperature",
            label: "Temp",
            measurement: "°C",
            max: 50,
            min: 15,
            normMax: 37.1,
            normMin: 35
        }), focus.graphs.push({
            key: "pulse_rate",
            label: "HR",
            measurement: "/min",
            max: 200,
            min: 30,
            normMax: 100,
            normMin: 50
        }), focus.graphs.push({
            key: "blood_pressure",
            label: "BP",
            measurement: "mmHg",
            max: 260,
            min: 30,
            normMax: 150,
            normMin: 50
        }), focus.tables.push({
            key: "avpu_text",
            label: "AVPU"
        }), focus.tables.push({
            key: "indirect_oxymetry_spo2_label",
            label: "Oxygen saturation"
        }), n && focus.tables.push({
            key: "inspired_oxygen",
            label: "Inspired oxygen"
        }), initGraph(20), initTable(), drawTabularObs("#table-content");
    },
    error: function(e) {
        console.log(e);
    }
});

$(document).ready(function() {
    $("#table-content").hide(), $(".tabs li a").click(function(e) {
        e.preventDefault();
        var t = $(this).attr("href");
        $("#graph-content").hide(), $("#table-content").hide(), $(t).show(), $(".tabs li a").removeClass("selected"), 
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