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
    datesChanged: false,
    dateRange: {
        portrait: 1,
        landscape: 5
    },
    data: null,
    windowWidthDelta: $(window).width(),
    ticks: 10
};

var context = {
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
        s: 1,
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
};

var focus = {
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

function initGraph(maxScore) {
    if (typeof maxScore === "undefined") {
        maxScore = 10;
    }
    svg.width = $(svg.el).width() - svg.margins.left - svg.margins.right - 8;
    svg.infoAreaRight = svg.width / 18;
    focus.height = (focus.graphs.length + 1) * focus.chartHeight;
    svg.height = context.height + focus.height + context.margins.bottom + context.margins.top + focus.margins.bottom + focus.margins.top;
    svg.obj.context = d3.select("#contextChart").append("svg").attr("width", svg.width).attr("height", context.height + context.margins.bottom + context.margins.top).append("g").attr("transform", "translate(" + 0 + "," + context.margins.top + ")");
    svg.obj.focus = d3.select("#focusChart").append("svg").attr("width", svg.width).attr("height", focus.height + focus.margins.bottom + focus.margins.top).append("g").attr("transform", "translate(" + 0 + "," + focus.margins.top / 3 + ")");
    context.yScale = d3.scale.linear().domain([ 0, maxScore ]).range([ context.height, 0 ]);
    context.yAxis = d3.svg.axis().scale(context.yScale).orient("left");
    var earliestDate = new Date(context.earliestDate);
    var now = new Date(context.now);
    var dateDiffHours = (now - earliestDate) / 1e3 / 60 / 60;
    if (dateDiffHours >= 2) {
        earliestDate.setHours(earliestDate.getHours() - 1);
        earliestDate.setMinutes(0);
        earliestDate.setSeconds(0);
        now.setHours(now.getHours() + 1);
        now.setMinutes(0);
        now.setSeconds(0);
    } else {
        earliestDate.setMinutes(earliestDate.getMinutes() - 6);
        now.setMinutes(now.getMinutes() + 6);
    }
    context.now = now;
    if (svg.isMob) {
        if ($(window).width() > $(window).height()) {
            earliestDate = new Date(context.now);
            earliestDate.setDate(earliestDate.getDate() - svg.dateRange.landscape);
        } else {
            earliestDate = new Date(context.now);
            earliestDate.setDate(earliestDate.getDate() - svg.dateRange.portrait);
        }
        var cED = new Date(earliestDate);
        var cN = new Date(now);
        var lD = cED.getFullYear() + "-" + ("0" + (cED.getMonth() + 1)).slice(-2) + "-" + ("0" + cED.getDate()).slice(-2);
        var lT = ("0" + cED.getHours()).slice(-2) + ":" + ("0" + cED.getMinutes()).slice(-2) + ":" + "00";
        var eD = cN.getFullYear() + "-" + ("0" + (cN.getMonth() + 1)).slice(-2) + "-" + ("0" + cN.getDate()).slice(-2);
        var eT = ("0" + cN.getHours()).slice(-2) + ":" + ("0" + cN.getMinutes()).slice(-2) + ":" + "00";
        $("#contextStartD").val(lD);
        $("#contextStartT").val(lT);
        $("#contextEndD").val(eD);
        $("#contextEndT").val(eT);
        $(".chartDates").show();
    }
    context.xScale = d3.time.scale().domain([ earliestDate, now ]).range([ svg.margins.left / 4, svg.width - (svg.infoAreaRight + svg.margins.right / 4) ]);
    context.xAxis = d3.svg.axis().scale(context.xScale).orient("top");
    focus.xScale = d3.time.scale().domain([ earliestDate, now ]).range([ svg.margins.left / 4, svg.width - (svg.infoAreaRight + svg.margins.right / 4) ]);
    focus.xAxis = d3.svg.axis().scale(focus.xScale).orient("top");
    if (svg.isMob) {
        context.xAxis.ticks(5);
        focus.xAxis.ticks(5);
    }
    drawChart();
    drawGraph();
}

function insertLinebreaks(d) {
    var el = d3.select(this);
    var textHeight = 10;
    var days = [ "Sun", "Mon", "Tues", "Wed", "Thu", "Fri", "Sat" ];
    var dateString = days[d.getDay()] + " " + d.getDate() + "/" + ("0" + (d.getMonth() + 1)).slice(-2) + " " + ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2);
    var words = dateString.split(" ");
    el.text("");
    for (var i = 0; i < words.length; i++) {
        var tspan = el.append("tspan").text(words[i]);
        if (i > 0) tspan.attr("x", 0).attr("dy", "15");
    }
    el.attr("y", "-" + (words.length * textHeight + textHeight));
}

function lineGen(points) {
    return points.join("L");
}

function handleResize() {
    var wid = $("#chart").width() - (svg.margins.right + svg.margins.left);
    if (svg.isMob && !svg.datesChanged) {
        var now, earliestDate;
        now = new Date(context.now);
        earliestDate = new Date(context.now);
        if ($(window).width() > $(window).height()) {
            earliestDate.setDate(now.getDate() - svg.dateRange.landscape);
        } else {
            earliestDate.setDate(now.getDate() - svg.dateRange.portrait);
        }
        var lD = earliestDate.getFullYear() + "-" + ("0" + (earliestDate.getMonth() + 1)).slice(-2) + "-" + ("0" + earliestDate.getDate()).slice(-2);
        var lT = ("0" + earliestDate.getHours()).slice(-2) + ":" + ("0" + earliestDate.getMinutes()).slice(-2) + ":" + "00";
        var eD = now.getFullYear() + "-" + ("0" + (now.getMonth() + 1)).slice(-2) + "-" + ("0" + now.getDate()).slice(-2);
        var eT = ("0" + now.getHours()).slice(-2) + ":" + ("0" + now.getMinutes()).slice(-2) + ":" + "00";
        $("#contextStartD").val(lD);
        $("#contextStartT").val(lT);
        $("#contextEndD").val(eD);
        $("#contextEndT").val(eT);
        focus.xScale.domain([ earliestDate, now ]);
    }
    resizeGraphs();
}

$(window).resize(function() {
    if ($(window).width() != svg.windowWidthDelta) {
        setTimeout(function() {
            handleResize();
        }, 1e3);
        svg.windowWidthDelta = $(window).width();
    }
});

function contextMouseOver(text) {
    var popupMargins = {
        top: 0,
        left: 3,
        right: 0,
        bottom: 40
    };
    svg.popup.style("left", d3.event.pageX + popupMargins.left + "px").style("top", d3.event.pageY - popupMargins.bottom + "px").text(text);
    svg.popup.transition().duration(500).style("opacity", 1);
}

function contextMouseOut(el) {
    svg.popup.transition().duration(500).style("opacity", 1e-6);
}

function contextChange() {
    if ($("#contextStartT").val() != "" && $("#contextEndD").val() != "" && $("#contextEndT").val() != "" && $("#contextStartD").val() != "") {
        svg.datesChanged = true;
        var cST = $("#contextStartT").val();
        var cSD = $("#contextStartD").val();
        var cET = $("#contextEndT").val();
        var cED = $("#contextEndD").val();
        var cS = cSD + "T" + cST;
        var cE = cED + "T" + cET;
        var newStart = new Date(cS);
        var newEnd = new Date(cE);
        focus.xScale.domain([ newStart, newEnd ]);
        focus.obj.select(".x.axis").call(focus.xAxis);
        redrawFocus(false);
        initTable();
        focus.obj.selectAll(".x.axis g text").each(insertLinebreaks);
    }
}

function brushed() {
    focus.xScale.domain(context.brush.empty() ? context.xScale.domain() : context.brush.extent());
    if (!context.brush.empty()) {
        var stD = context.brush.extent()[0];
        var enD = context.brush.extent()[1];
        var stdT = ("0" + stD.getHours()).slice(-2) + ":" + ("0" + stD.getMinutes()).slice(-2) + " " + ("0" + stD.getDate()).slice(-2) + "/" + ("0" + stD.getMonth()).slice(-2);
        var enT = ("0" + enD.getHours()).slice(-2) + ":" + ("0" + enD.getMinutes()).slice(-2) + " " + ("0" + enD.getDate()).slice(-2) + "/" + ("0" + enD.getMonth()).slice(-2);
        $("#focusTitle").html("Individual values for " + stdT + " - " + enT);
    } else {
        $("#focusTitle").html("Individual values");
    }
    redrawFocus(false);
}

function drawChart() {
    context.obj = svg.obj.context.append("g").attr("transform", "translate(" + svg.margins.left + "," + context.margins.top + ")");
    context.obj.selectAll("rect.scoreRange").data(context.scoreRange).enter().append("rect").attr({
        "class": function(d) {
            return d.class;
        },
        x: context.xScale(context.xScale.domain()[0]),
        y: function(d) {
            return context.yScale(d.e);
        },
        width: svg.width - (svg.infoAreaRight + svg.margins.right / 3),
        height: function(d) {
            return context.yScale(d.s) - context.yScale(d.e);
        }
    });
    context.obj.selectAll("line.verticalGrid").data(context.xScale.ticks()).enter().append("line").attr({
        "class": "verticalGrid",
        x1: function(d) {
            return context.xScale(d);
        },
        x2: function(d) {
            return context.xScale(d);
        },
        y1: 0,
        y2: context.height,
        "shape-rendering": "cripsEdges",
        stroke: "rgba(0,0,0,0.1)",
        "stroke-width": "1px"
    });
    context.obj.selectAll("line.horizontalGrid").data([ 0, 3, 6, 9, 12, 15, 18 ]).enter().append("line").attr({
        "class": "horizontalGrid",
        x1: context.xScale(context.xScale.domain()[0]),
        x2: context.xScale(context.xScale.domain()[1]),
        y1: function(d) {
            return context.yScale(d);
        },
        y2: function(d) {
            return context.yScale(d);
        },
        "shape-rendering": "cripsEdges",
        stroke: "rgba(0,0,0,0.1)",
        "stroke-width": "1px"
    });
    context.obj.append("g").attr("class", "x axis").call(context.xAxis);
    context.obj.append("g").attr({
        "class": "y axis",
        transform: "translate(5,0)"
    }).call(context.yAxis);
    if (!svg.isMob) {
        context.brush = d3.svg.brush().x(context.xScale).on("brush", brushed);
        context.obj.append("g").attr("class", "x brush").call(context.brush).selectAll("rect").attr("y", -6).attr("height", context.height + 7).style({
            fill: "#333",
            opacity: "0.5"
        });
    }
    context.area = d3.svg.line().interpolate("step-after").defined(function(d) {
        if (d.obs.score > -1) {
            return d;
        }
    }).x(function(d) {
        return context.xScale(d.obsStart);
    }).y(function(d) {
        return context.yScale(d.obs.score);
    });
    context.obj.append("path").datum(svg.data).attr("d", context.area).style({
        stroke: "#555555",
        "stroke-width": "1",
        fill: "none"
    }).attr("class", "contextPath");
    context.obj.selectAll("circle.contextPoint").data(svg.data.filter(function(d) {
        if (d.obs.score > -1) {
            return d;
        }
    })).enter().append("circle").attr("cx", function(d) {
        return context.xScale(d.obsStart);
    }).attr("cy", function(d) {
        return context.yScale(d.obs.score);
    }).attr("r", 3).attr("class", "contextPoint").on("mouseover", function(d) {
        return contextMouseOver(d.obs.score);
    }).on("mouseout", contextMouseOut);
    context.obj.selectAll("circle.emptyContextPoint").data(svg.data.filter(function(d) {
        console.log(typeof d.obs.score);
        if (d.obs.score == undefined) {
            return d;
        }
    })).enter().append("circle").attr("cx", function(d) {
        return context.xScale(d.obsStart);
    }).attr("cy", function(d) {
        return context.yScale(context.yScale.domain()[1] / 2);
    }).attr("r", 3).attr("class", "emptyContextPoint").on("mouseover", function(d) {
        return contextMouseOver("Partial observation");
    }).on("mouseout", contextMouseOut);
    svg.popup = d3.select("body").append("div").attr("class", "contextPopup").style("opacity", 1e-6);
    context.obj.selectAll(".x.axis g text").each(insertLinebreaks);
    focus.obj = svg.obj.focus.append("g").attr("transform", "translate(" + svg.margins.left + "," + focus.margins.top + ")");
    focus.obj.append("defs").append("clipPath").attr("id", "clip").append("rect").attr("width", svg.width - svg.infoAreaRight).attr("height", focus.height - focus.margins.bottom).attr("y", -20);
    focus.obj.append("g").attr("class", "x axis").attr("transform", "translate(0,-20)").call(focus.xAxis);
    focus.obj.selectAll(".x.axis g text").each(insertLinebreaks);
}

function drawGraph() {
    for (var i = 0; i < focus.graphs.length; i++) {
        var thisEntry = focus.graphs[i];
        thisEntry.group = focus.obj.append("g").attr("class", "g-" + thisEntry.label);
        thisEntry.offset = i * focus.chartHeight + focus.chartPadding * (i - 1);
        thisEntry.yScale = d3.scale.linear().domain([ thisEntry.min, thisEntry.max ]).range([ focus.chartHeight + thisEntry.offset, thisEntry.offset ]);
        thisEntry.diffNorm = thisEntry.yScale(thisEntry.normMin) - thisEntry.yScale(thisEntry.normMax);
        thisEntry.group.append("line").attr("x1", 5).attr("x2", svg.width - svg.infoAreaRight - 11).attr("y1", focus.chartHeight + thisEntry.offset).attr("y2", focus.chartHeight + thisEntry.offset).style("stroke", "black").style("opacity", 1).style("stroke-width", 2).attr("class", "line line-" + thisEntry.label);
        if (thisEntry.label != "BP") {
            thisEntry.group.append("rect").attr("x", 5).attr("y", thisEntry.yScale(thisEntry.normMax)).attr("width", svg.width - svg.infoAreaRight - 16).attr("height", thisEntry.diffNorm).style("fill", "#CCCCCC").style("opacity", .75).attr("class", "norm norm-" + thisEntry.label);
        } else {
            thisEntry.group.append("line").attr("x1", 5).attr("x2", svg.width - svg.infoAreaRight - 11).attr("y1", thisEntry.yScale(100)).attr("y2", thisEntry.yScale(100)).style("stroke", "black").style("opacity", 1).style("stroke-width", 1).attr("class", "line norm line-" + thisEntry.label);
        }
        thisEntry.group.append("text").text(thisEntry.normMin).attr("x", -5).attr("y", thisEntry.yScale(thisEntry.normMin)).attr("font-family", "sans-serif").attr("font-size", "10px").attr("font-weight", "normal").attr("text-anchor", "middle").attr("dominant-baseline", "hanging").attr("class", "min normLabel-" + thisEntry.label);
        thisEntry.group.append("text").text(thisEntry.normMax).attr("x", -5).attr("y", thisEntry.yScale(thisEntry.normMax)).attr("font-family", "sans-serif").attr("font-size", "10px").attr("font-weight", "normal").attr("text-anchor", "middle").attr("class", "max normLabel-" + thisEntry.label);
        var shift = thisEntry.diffNorm - 10;
        if (shift > 0) shift = 0;
        var hTicks = d3.svg.axis().scale(thisEntry.yScale).orient("left").ticks(10);
        var ti = thisEntry.group.append("g").call(hTicks);
        hTicks = thisEntry.yScale.ticks();
        ti.remove();
        thisEntry.group.selectAll("line.verticalGrid.focus" + thisEntry.label).data(focus.xScale.ticks()).enter().append("line").attr({
            "class": "verticalGrid focus" + thisEntry.label,
            x1: function(d) {
                return focus.xScale(d);
            },
            x2: function(d) {
                return focus.xScale(d);
            },
            y1: thisEntry.yScale.range()[0],
            y2: thisEntry.yScale.range()[1],
            "shape-rendering": "crispEdges",
            stroke: "rgba(0,0,0,0.1)",
            "stroke-width": "1px"
        });
        thisEntry.group.selectAll("line.horizontalGrid.focus" + thisEntry.label).data(hTicks).enter().append("line").attr({
            "class": "horizontalGrid focus" + thisEntry.label,
            x1: 5,
            x2: svg.width - svg.infoAreaRight - 11,
            y1: function(d) {
                return thisEntry.yScale(d);
            },
            y2: function(d) {
                return thisEntry.yScale(d);
            },
            "shape-rendering": "crispEdges",
            stroke: "rgba(0,0,0,0.1)",
            "stroke-width": "1px"
        });
        if (thisEntry.label == "BP") {
            thisEntry.group.selectAll("." + thisEntry.label + "up-arrows").data(svg.data.filter(function(d) {
                if (d.obs.blood_pressure_systolic) {
                    return d;
                }
            })).enter().append("path").attr({
                d: d3.svg.symbol().size(function(d) {
                    return 45;
                }).type(function(d) {
                    return "triangle-up";
                }),
                transform: function(d) {
                    return "translate(" + context.xScale(d.obsStart) + "," + (thisEntry.yScale(d.obs.blood_pressure_systolic) + 3) + ")";
                },
                "class": "data_symbols " + thisEntry.label + "up-arrows"
            }).style("display", function(d) {
                if (d.obs["blood_pressure_systolic"] === null) {
                    return "none";
                } else {
                    return null;
                }
            }).on("mouseover", function(d) {
                return contextMouseOver("s:" + d.obs["blood_pressure_systolic"] + " d:" + d.obs["blood_pressure_diastolic"]);
            }).on("mouseout", contextMouseOut);
            thisEntry.group.selectAll("." + thisEntry.label + "down-arrows").data(svg.data.filter(function(d) {
                if (d.obs.blood_pressure_diastolic) {
                    return d;
                }
            })).enter().append("path").attr({
                d: d3.svg.symbol().size(function(d) {
                    return 45;
                }).type(function(d) {
                    return "triangle-down";
                }),
                transform: function(d) {
                    return "translate(" + context.xScale(d.obsStart) + "," + (thisEntry.yScale(d.obs.blood_pressure_diastolic) - 3) + ")";
                },
                "class": "data_symbols " + thisEntry.label + "down-arrows"
            }).style("display", function(d) {
                if (d.obs["blood_pressure_diastolic"] === null) {
                    return "none";
                } else {
                    return null;
                }
            }).on("mouseover", function(d) {
                return contextMouseOver("s:" + d.obs["blood_pressure_systolic"] + " d:" + d.obs["blood_pressure_diastolic"]);
            }).on("mouseout", contextMouseOut);
            thisEntry.group.selectAll("#" + thisEntry.label).data(svg.data.filter(function(d) {
                if (d.obs.blood_pressure_diastolic && d.obs.blood_pressure_systolic) {
                    return d;
                }
            })).enter().append("rect").attr({
                width: 2,
                height: function(d) {
                    return thisEntry.yScale(d.obs["blood_pressure_diastolic"]) - thisEntry.yScale(d.obs["blood_pressure_systolic"]);
                },
                x: function(d) {
                    return focus.xScale(d.obsStart) - 1;
                },
                y: function(d) {
                    return thisEntry.yScale(d.obs["blood_pressure_systolic"]);
                },
                "clip-path": "url(#clip)",
                "class": "data_lines data-" + thisEntry.label
            }).style("display", function(d) {
                if (d.obs["blood_pressure_systolic"] === null || d.obs["blood_pressure_diastolic"] === null) {
                    return "none";
                } else {
                    return null;
                }
            }).style({
                stroke: "rgba(0,0,0,0)",
                "stroke-width": "3"
            }).on("mouseover", function(d) {
                return contextMouseOver("s:" + d.obs["blood_pressure_systolic"] + " d:" + d.obs["blood_pressure_diastolic"]);
            }).on("mouseout", contextMouseOut);
            thisEntry.group.append("text").text(thisEntry.label).attr("y", thisEntry.yScale(thisEntry.normMax) + shift).attr("x", svg.width - svg.infoAreaRight).attr({
                "font-family": "sans-serif",
                "font-size": "12px",
                "font-weight": "bold",
                fill: "#BBBBBB",
                "text-anchor": "start",
                "class": "info infoname-" + thisEntry.label
            });
            thisEntry.group.append("text").text(function() {
                if (svg.data[svg.data.length - 1]["obs"]["blood_pressure_systolic"]) {
                    return svg.data[svg.data.length - 1]["obs"]["blood_pressure_systolic"];
                } else {
                    return "";
                }
            }).attr("y", thisEntry.yScale(thisEntry.normMin) - 20).attr("x", svg.width - svg.infoAreaRight).attr({
                "font-family": "sans-serif",
                "font-size": "12px",
                "font-weight": "bold",
                "text-anchor": "start",
                "class": "info infovalue1-" + thisEntry.label
            });
            thisEntry.group.append("text").text(function() {
                if (svg.data[svg.data.length - 1]["obs"]["blood_pressure_diastolic"]) {
                    return svg.data[svg.data.length - 1]["obs"]["blood_pressure_diastolic"];
                } else {
                    return "";
                }
            }).attr("y", thisEntry.yScale(thisEntry.normMin) - 10).attr("x", svg.width - svg.infoAreaRight).attr({
                "font-family": "sans-serif",
                "font-size": "12px",
                "font-weight": "bold",
                "text-anchor": "start",
                "class": "info infovalue2-" + thisEntry.label
            });
            thisEntry.group.append("text").text(function() {
                return thisEntry.measurement;
            }).attr("y", thisEntry.yScale(thisEntry.normMin) - 10).attr("x", svg.width - svg.infoAreaRight + svg.labelGap * 2).attr({
                "font-family": "sans-serif",
                "font-size": "9px",
                "font-weight": "bold",
                "text-anchor": "start",
                "class": "info infovalue3-" + thisEntry.label
            });
        } else {
            thisEntry.area = d3.svg.line().interpolate("linear").defined(function(d) {
                if (d.obs[thisEntry.key]) {
                    return d;
                }
            }).x(function(d) {
                return focus.xScale(d.obsStart);
            }).y(function(d) {
                return thisEntry.yScale(d.obs[thisEntry.key]);
            });
            thisEntry.group.append("path").datum(svg.data.filter(function(d) {
                if (d.obs[thisEntry.key]) {
                    return d;
                }
            })).attr("d", thisEntry.area).style({
                stroke: "#888888",
                "stroke-width": "1",
                fill: "none"
            }).attr("class", "focusPath").attr("id", "path-" + thisEntry.key).attr("clip-path", "url(#clip)");
            thisEntry.group.selectAll("#" + thisEntry.label).data(svg.data.filter(function(d) {
                if (d.obs[thisEntry.key]) {
                    return d;
                }
            })).enter().append("circle").attr("cx", function(d) {
                return focus.xScale(d.obsStart);
            }).attr("cy", function(d) {
                return thisEntry.yScale(d.obs[thisEntry.key]);
            }).attr("r", 3).attr("class", "data_points data-" + thisEntry.label).style("display", function(d) {
                if (d.obs[thisEntry.key]) {
                    return null;
                } else {
                    return "none";
                }
            }).attr("clip-path", "url(#clip)").on("mouseover", function(d) {
                return contextMouseOver(d.obs[thisEntry.label]);
            }).on("mouseout", contextMouseOut);
            thisEntry.group.append("text").text(thisEntry.label).attr("y", thisEntry.yScale(thisEntry.normMax) + shift).attr("x", svg.width - svg.infoAreaRight).attr({
                "font-family": "sans-serif",
                "font-size": "12px",
                "font-weight": "bold",
                fill: "#BBBBBB",
                "text-anchor": "start",
                "class": "info infoname-" + thisEntry.label
            });
            thisEntry.group.append("text").text(function() {
                if (svg.data[svg.data.length - 1]["obs"][thisEntry.key]) {
                    return svg.data[svg.data.length - 1]["obs"][thisEntry.key] + thisEntry.measurement;
                } else {
                    return "";
                }
            }).attr("y", thisEntry.yScale(thisEntry.normMin) - shift).attr("x", svg.width - svg.infoAreaRight).attr({
                "font-family": "sans-serif",
                "font-size": "12px",
                "font-weight": "bold",
                "text-anchor": "start",
                "class": "info infovalue-" + thisEntry.label
            });
        }
    }
}

function redrawFocus(transition) {
    focus.obj.selectAll(".data_points").transition().duration(svg.transitionDuration).attr("cx", function(d) {
        return focus.xScale(d.obsStart);
    });
    if (transition) {
        svg.transitionDuration = 1e3;
    } else {
        svg.transitionDuration = 0;
    }
    for (var i = 0; i < focus.graphs.length; i++) {
        var thisEntry = focus.graphs[i];
        thisEntry.area = d3.svg.line().interpolate("linear").x(function(d) {
            return focus.xScale(d.obsStart);
        }).y(function(d) {
            return thisEntry.yScale(d.obs[thisEntry.key]);
        });
        thisEntry.group.select("#path-" + thisEntry.key).transition().duration(svg.transitionDuration).attr("d", thisEntry.area);
        thisEntry.group.selectAll("line.verticalGrid.focus" + thisEntry.label).remove().data(focus.xScale.ticks()).enter().append("line").attr({
            "class": "verticalGrid focus" + thisEntry.label,
            x1: function(d) {
                return focus.xScale(d);
            },
            x2: function(d) {
                return focus.xScale(d);
            },
            y1: thisEntry.yScale.range()[0],
            y2: thisEntry.yScale.range()[1],
            "shape-rendering": "crispEdges",
            stroke: "rgba(0,0,0,0.1)",
            "stroke-width": "1px"
        });
    }
    focus.obj.select(".x.axis").call(focus.xAxis);
    focus.obj.selectAll(".data_points").transition().duration(svg.transitionDuration).attr("cx", function(d) {
        return focus.xScale(d.obsStart);
    });
    focus.obj.selectAll(".data_lines").transition().duration(svg.transitionDuration).attr("x", function(d) {
        return focus.xScale(d.obsStart);
    });
    focus.obj.select(".g-BP").selectAll(".data_symbols").remove();
    focus.obj.select(".g-BP").selectAll(".BPup-arrows").data(svg.data.filter(function(d) {
        if (d.obs.blood_pressure_systolic && d.obsStart >= focus.xScale.domain()[0] && d.obsStart <= focus.xScale.domain()[1]) {
            console.log(d);
            return d;
        }
    })).enter().append("path").attr({
        d: d3.svg.symbol().size(function(d) {
            console.log("calling size");
            return 45;
        }).type(function(d) {
            console.log("calling type");
            return "triangle-up";
        }),
        transform: function(d) {
            console.log("calling transform");
            return "translate(" + (focus.xScale(d.obsStart) + 1) + "," + (focus.graphs[focus.graphs.length - 1].yScale(d.obs.blood_pressure_systolic) + 3) + ")";
        },
        "class": "data_symbols BPup-arrows"
    }).style("display", function(d) {
        if (d.obs["blood_pressure_systolic"] === null) {
            return "none";
        } else {
            return null;
        }
    }).on("mouseover", function(d) {
        return contextMouseOver("s:" + d.obs["blood_pressure_systolic"] + " d:" + d.obs["blood_pressure_diastolic"]);
    }).on("mouseout", contextMouseOut);
    focus.obj.select(".g-BP").selectAll(".BPdown-arrows").data(svg.data.filter(function(d) {
        if (d.obs.blood_pressure_diastolic && d.obsStart >= focus.xScale.domain()[0] && d.obsStart <= focus.xScale.domain()[1]) {
            return d;
        }
    })).enter().append("path").attr({
        d: d3.svg.symbol().size(function(d) {
            return 45;
        }).type(function(d) {
            return "triangle-down";
        }),
        transform: function(d) {
            return "translate(" + (focus.xScale(d.obsStart) + 1) + "," + (focus.graphs[focus.graphs.length - 1].yScale(d.obs.blood_pressure_diastolic) - 3) + ")";
        },
        "class": "data_symbols BPdown-arrows"
    }).style("display", function(d) {
        if (d.obs["blood_pressure_diastolic"] === null) {
            return "none";
        } else {
            return null;
        }
    }).on("mouseover", function(d) {
        return contextMouseOver("s:" + d.obs["blood_pressure_systolic"] + " d:" + d.obs["blood_pressure_diastolic"]);
    }).on("mouseout", contextMouseOut);
    focus.obj.select(".x.axis").call(focus.xAxis);
    focus.obj.selectAll(".horizontalGrid").transition().duration(svg.transitionDuration).attr("x2", focus.xScale(focus.xScale.domain()[1]));
    initTable();
    focus.obj.selectAll(".x.axis g text").each(insertLinebreaks);
}

function resizeGraphs() {
    var win = $(svg.el);
    var ori = win.width() > win.height() ? "landscape" : "portrait";
    w = win.width() - svg.margins.left - svg.margins.right;
    svg.width = w + svg.margins.left + svg.margins.right;
    svg.obj = d3.select("svg").transition().duration(svg.transitionDuration).attr("width", svg.width);
    context.xScale.range([ svg.margins.left / 4, w - (svg.infoAreaRight + svg.margins.right / 4) ]);
    context.xAxis.scale(context.xScale);
    context.obj.selectAll(".x.axis").call(context.xAxis);
    context.area.x(function(d) {
        return context.xScale(d.obsStart);
    }).y(function(d) {
        return context.yScale(d.obs.score);
    });
    context.obj.selectAll(".contextPath").transition().duration(svg.transitionDuration).attr("d", context.area);
    context.obj.selectAll(".contextPoint").transition().duration(svg.transitionDuration).attr("cx", function(d) {
        return context.xScale(d.obsStart);
    });
    context.obj.selectAll(".x.axis g text").each(insertLinebreaks);
    context.obj.selectAll(".horizontalGrid").transition().duration(svg.transitionDuration).attr("x2", w - svg.infoAreaRight - 10);
    context.obj.selectAll(".green").transition().duration(svg.transitionDuration).attr("width", w - (svg.infoAreaRight + svg.margins.right / 3));
    context.obj.selectAll(".amber").transition().duration(svg.transitionDuration).attr("width", w - (svg.infoAreaRight + svg.margins.right / 3));
    context.obj.selectAll(".red").transition().duration(svg.transitionDuration).attr("width", w - (svg.infoAreaRight + svg.margins.right / 3));
    context.obj.selectAll(".verticalGrid").remove().data(context.xScale.ticks()).enter().append("line").attr({
        "class": "verticalGrid",
        x1: function(d) {
            return context.xScale(d);
        },
        x2: function(d) {
            return context.xScale(d);
        },
        y1: 0,
        y2: context.height,
        "shape-rendering": "crispEdges",
        stroke: "rgba(0,0,0,0.1)",
        "stroke-width": "1px"
    });
    if (!svg.isMob) {
        context.brush.x(context.xScale);
    }
    focus.obj.select("#clip").transition().duration(svg.transitionDuration).attr("width", w - (svg.infoAreaRight + svg.margins.right / 4));
    focus.obj.select("#clip").transition().duration(svg.transitionDuration).select("rect").attr("width", w - (svg.infoAreaRight + svg.margins.right / 4));
    focus.xScale.range([ svg.margins.left / 4, w - (svg.infoAreaRight + svg.margins.right / 4) ]);
    focus.xAxis.scale(focus.xScale);
    d3.select("#focusChart").select("svg").transition().duration(svg.transitionDuration).attr("width", w + svg.infoAreaRight + svg.margins.right);
    focus.obj.selectAll(".line").transition().duration(svg.transitionDuration).attr("x2", w - (svg.infoAreaRight + svg.margins.right / 4));
    focus.obj.selectAll(".norm").transition().duration(svg.transitionDuration).attr("width", w - (svg.infoAreaRight + svg.margins.right / 3));
    focus.obj.selectAll(".info").transition().duration(svg.transitionDuration).attr("x", w - (svg.infoAreaRight + svg.margins.right / 4) + svg.labelGap);
    focus.obj.selectAll(".infovalue3-BP").transition().duration(svg.transitionDuration).attr("x", w - (svg.infoAreaRight + svg.margins.right / 4) + svg.labelGap * 3);
    redrawFocus(false);
}

function initTable() {
    var headerData = [ "Type" ];
    d3.select("#chartTable").selectAll("tr").remove();
    var startDate = new Date(focus.xScale.domain()[0]);
    var endDate = new Date(focus.xScale.domain()[1]);
    for (var i = 0; i < svg.data.length; i++) {
        if (svg.data[i].obsStart >= startDate && svg.data[i].obsStart <= endDate) {
            headerData.push(svg.data[i].obsStart);
        }
    }
    dataTableTr = d3.select("#chartTable").append("tr");
    dataTableTr.selectAll("th").data(headerData).enter().append("th").html(function(d) {
        if (d == "Type") {
            return d;
        } else {
            return ("0" + d.getDate()).slice(-2) + "/" + ("0" + (d.getMonth() + 1)).slice(-2) + "<br>" + ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2);
        }
    }).style("width", 90 / headerData.length + "%");
    drawTable();
}

function drawTable() {
    for (var i = 0; i < focus.tables.length; i++) {
        var thisEntry = focus.tables[i];
        var tableData = [ thisEntry.label ];
        var startDate = new Date(focus.xScale.domain()[0]);
        var endDate = new Date(focus.xScale.domain()[1]);
        for (var j = 0; j < svg.data.length; j++) {
            if (svg.data[j].obsStart >= startDate && svg.data[j].obsStart <= endDate) {
                tableData.push(svg.data[j]["obs"][thisEntry.key]);
            }
        }
        var tableTR = d3.select("#chartTable").append("tr");
        tableTR.selectAll("td." + thisEntry.label).data(tableData).enter().append("td").html(function(d) {
            return d;
        }).attr("class", thisEntry.label);
    }
}