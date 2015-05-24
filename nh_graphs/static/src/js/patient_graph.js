graph_lib = (function() {

    var graph_lib = {

svg: {
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
    startParse: nh_graphs.time.format("%Y-%m-%d %H:%M:%S").parse,
    patientId:$('.name').attr("data-id"),
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
    ticks: 10,
    printing: false,
    focusOnly: false,
    timePadding: 6,
    printTimePadding: 20
},

context: {
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
    scoreRange: [
        {
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
        }
    ],
    earliestDate: new Date(),
    now: new Date(),
    redrawFocus: null,
    initTable: null,
    drawTable: null,
    chartXOffset: 15
},

focus: {
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
    chartPadding: 20,
    rangePadding: 1,
    chartXOffset: 15,
    BPWidth: 8
},

initGraph: function(maxScore) {
    console.log("Calling initVGraph");
    var context = this.context, focus = this.focus, svg = this.svg;
    if (typeof maxScore === "undefined") {
        maxScore = 10;
    }
    context.maxScore = maxScore;
    svg.width = $(svg.el).width() - svg.margins.left - svg.margins.right;
    svg.infoAreaRight = svg.width / 18;
    focus.height = (focus.graphs.length + 1) * focus.chartHeight;
    svg.height = context.height + focus.height + context.margins.bottom + context.margins.top + focus.margins.bottom + focus.margins.top;
    svg.obj.context = nh_graphs.select("#contextChart").append("svg").attr("width", svg.width + svg.margins.left + svg.margins.right).attr("height", context.height + context.margins.bottom + context.margins.top).append("g").attr("transform", "translate(" + 0 + "," + context.margins.top + ")");
    svg.obj.focus = nh_graphs.select("#focusChart").append("svg").attr("width", svg.width + svg.margins.left + svg.margins.right).attr("height", focus.height + focus.margins.bottom + focus.margins.top).append("g").attr("transform", "translate(" + 0 + "," + focus.margins.top / 3 + ")");
    context.yScale = nh_graphs.scale.linear().domain([ 0, maxScore ]).range([ context.height, 0 ]);
    context.yAxis = nh_graphs.svg.axis().scale(context.yScale).orient("left");


    //var earliestDate = new Date(context.earliestDate.toString());
    //var now = new Date(context.now.toString());
    var earliestDate = context.earliestDate;
    var now = context.now;
    var dateDiffHours = (now - earliestDate) / 1e3 / 60 / 60;
    if (dateDiffHours >= 2) {
        earliestDate.setHours(earliestDate.getHours() - 1);
        earliestDate.setMinutes(0);
        earliestDate.setSeconds(0);
        now.setHours(now.getHours() + 1);
        now.setMinutes(0);
        now.setSeconds(0);
    } else {
        earliestDate.setMinutes(earliestDate.getMinutes() - svg.timePadding);
        now.setMinutes(now.getMinutes() + svg.timePadding);
    }

    if(svg.printing){
        earliestDate.setMinutes(earliestDate.getMinutes() - svg.printTimePadding);
        now.setMinutes(now.getMinutes() + svg.printTimePadding);
        svg.obj.context.attr("printing", "true");
    }

    //context.now = now;
    context.xScale = nh_graphs.time.scale().domain([ earliestDate, now ]).range([context.chartXOffset, svg.width - (svg.infoAreaRight + svg.margins.right / 4) ]);
    context.xAxis = nh_graphs.svg.axis().scale(context.xScale).orient("top");
    focus.xScale = nh_graphs.time.scale().domain([ earliestDate, now ]).range([context.chartXOffset, svg.width - (svg.infoAreaRight + svg.margins.right / 4) ]);
    focus.xAxis = nh_graphs.svg.axis().scale(focus.xScale).orient("top");

    this.drawChart();
    this.drawGraph();
},


drawChart: function() {
    var context = this.context, focus = this.focus, svg = this.svg;
    var self = this;
    if(!svg.focusOnly){
        context.obj = svg.obj.context.append("g").attr("transform", "translate(" + svg.margins.left + "," + context.margins.top + ")");
        context.obj.append("defs").append("clipPath").attr("id", "context-clip").append("rect").attr("width",  (svg.width - svg.infoAreaRight) - (10 + context.chartXOffset)).attr("height", context.height).attr("y", 0).attr("x", context.chartXOffset);

        context.obj.selectAll("rect.scoreRange").data(context.scoreRange).enter().append("rect").attr({
            "class": function(d) {
                return d.class + ' scoreRange';
            },
            "fill": function(d){
                if(d.class == "red"){
                    return "#ffcccc";
                }
                if(d.class == "amber"){
                    return "#ffe9c8";
                }
                if(d.class == "green"){
                    return "#ccffcc";
                }
            },
            x: context.xScale(context.xScale.domain()[0]),
            y: function(d) {
                return context.yScale(d.e) - 1;
            },
            width: svg.width - (svg.infoAreaRight + svg.margins.right / 3),
            "clip-path": "url(#context-clip)",
            height: function(d) {
                return context.yScale(d.s) - (context.yScale(d.e) - 1);
            }
        });


        context.obj.selectAll("line.verticalGrid").data(graph_lib.context.xScale.ticks()).enter().append("line").attr({
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
            stroke: svg.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
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
            stroke: svg.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
            "stroke-width": "1px"
        });
        context.obj.append("g").attr("class", "x axis").call(context.xAxis).style("stroke-width", "1");
        context.obj.append("g").attr({
            "class": "y axis",
            transform: "translate("+context.chartXOffset+",0)"
        }).call(context.yAxis).style("stroke-width", "1");
        context.brush = nh_graphs.svg.brush().x(context.xScale).on("brush", self.brushed);
        context.obj.append("g").attr("class", "x brush").call(context.brush).selectAll("rect").attr("y", -6).attr("height", context.height + 7).style({
            fill: "#333",
            opacity: "0.5"
        });

        console.log('about to draw the line');

        context.area = nh_graphs.svg.line()
            .interpolate("step-after")
            .defined(function(d){ if(d.none_values == "[]"){ return d; }})
            .x(function(d) {
                console.log(d);
                return context.xScale(d.date_terminated);
            })
            .y(function(d) {
                return context.yScale(d.score);
            });
        context.obj.append("path").datum(svg.data).attr("d", context.area).style({
            stroke: "#555555",
            "stroke-width": "1",
            fill: "none"
        }).attr("class", "contextPath");

        context.obj.selectAll("circle.contextPoint")
            .data(svg.data.filter(function(d){ if(d.none_values == "[]"){ return d; }}))
            .enter().append("circle").attr("cx", function(d) {
                return context.xScale(d.date_terminated);
            }).attr("cy", function(d) {
                return context.yScale(d.score);
            }).attr("r", 3).attr("class", "contextPoint").on("mouseover", function(d) {
                return self.contextMouseOver(d.score, $(this).position());
            }).on("mouseout", self.contextMouseOut)
            .style({
                "fill": "#000000",
                "stroke": "rgba(0,0,0,0)",
                "stroke-width": "3"
            });

        context.obj.selectAll("circle.emptyContextPoint").data(svg.data.filter(function(d){
            if(d.none_values !== "[]"){
                return d;
            }
        }))
            .enter().append("circle")
            .attr("cx", function(d) {
                return context.xScale(d.date_terminated);
            })
            .attr("cy", function(d) {
                return context.yScale(context.yScale.domain()[1] / 2);
            })
            .attr("r", 3)
            .attr("class", "emptyContextPoint")
            .on("mouseover", function(d) {
                return self.contextMouseOver("Partial observation", $(this).position());
            })
            .on("mouseout", self.contextMouseOut)
            .style({
                "fill": "white",
                "stroke": "rgba(0,0,0,1)",
                "stroke-width": "1"
            });

        context.obj.selectAll(".x.axis g text").each(this.insertLinebreaks);
        context.obj.selectAll(".axis .domain").style({"stroke-width": "1", "fill": "none","shape-rendering": "crispEdges", "stroke":"black"});
        context.obj.selectAll(".axis .tick line").style({"stroke-width": "1", "fill": "none","shape-rendering": "crispEdges", "stroke":"black"});
    }
    svg.popup = nh_graphs.select(svg.el).append("div").attr("class", "contextPopup").style({"opacity": "0",
        "position": "absolute",
        "text-align": "center",
        "width": "5%",
        "padding": "0.4em 0.25%",
        "font": "0.8em sans-serif",
        "background": "rgba(0,0,0,0.7)",
        "border": "solid 0px rgba(0,0,0,0.7)",
        "border-radius": "8px",
        "border-bottom-left-radius": "0px",
        "pointer-events": "none",
        "color": "white"
    });
    focus.obj = svg.obj.focus.append("g").attr("transform", "translate(" + svg.margins.left + "," + focus.margins.top + ")");
    if(!svg.focusOnly){
        focus.obj.append("defs").append("clipPath").attr("id", "clip").append("rect").attr("width", (svg.width - svg.infoAreaRight) - (10 + context.chartXOffset)).attr("height", focus.height - focus.margins.bottom).attr("y", -20).attr("x", focus.chartXOffset);
    }
    focus.obj.append("g").attr("class", "x axis").attr("transform", "translate(0,-20)").call(focus.xAxis).style("stroke-width", "1");
    focus.obj.selectAll(".x.axis g text").each(this.insertLinebreaks);
    focus.obj.selectAll(".axis .domain").style({"stroke-width": "1", "fill": "none","shape-rendering": "crispEdges", "stroke":"black"});
    focus.obj.selectAll(".axis .tick line").style({"stroke-width": "1", "fill": "none","shape-rendering": "crispEdges", "stroke":"black"});
},

drawGraph: function() {
    var context = this.context, focus = this.focus, svg = this.svg;
    var self = this;

    for (var i = 0; i < focus.graphs.length; i++) {
        var thisEntry = focus.graphs[i];
        thisEntry.offset = i * focus.chartHeight + focus.chartPadding * (i - 1);
        focus.obj.select("defs").append("clipPath").attr("id", "clip-" + thisEntry.label).append("rect").attr("width", (svg.width - svg.infoAreaRight) - (10 + focus.chartXOffset)).attr("height", focus.chartHeight).attr("y", thisEntry.offset).attr("x", focus.chartXOffset);

        thisEntry.yScale = nh_graphs.scale.linear().domain([ thisEntry.min, thisEntry.max ]).range([ focus.chartHeight + thisEntry.offset, thisEntry.offset ]);
        thisEntry.diffNorm = thisEntry.yScale(thisEntry.normMin) - thisEntry.yScale(thisEntry.normMax);
        focus.obj.append("line").attr("x1", focus.chartXOffset).attr("x2", svg.width - svg.infoAreaRight - 11).attr("y1", focus.chartHeight + thisEntry.offset).attr("y2", focus.chartHeight + thisEntry.offset).style("stroke", "black").style("opacity", 1).style("stroke-width", 2).attr("class", "line line-" + thisEntry.label);
        if (thisEntry.label != "BP") {
            focus.obj.append("rect").attr("x", focus.chartXOffset).attr("y", thisEntry.yScale(thisEntry.normMax)).attr("width", svg.width - svg.infoAreaRight - 16).attr("height", thisEntry.diffNorm).style("fill", svg.printing ? "#eaeaea" :"#CCCCCC").style("opacity", .75).attr("class", "norm norm-" + thisEntry.label).attr('clip-path', 'url(#clip-' + thisEntry.label + ')');
        } else {
            focus.obj.append("line").attr("x1", focus.chartXOffset).attr("x2", svg.width - svg.infoAreaRight - 11).attr("y1", thisEntry.yScale(100)).attr("y2", thisEntry.yScale(100)).style("stroke", "black").style("opacity", 1).style("stroke-width", 1).attr("class", "line normal-line-"+thisEntry.label+" line-" + thisEntry.label).attr('clip-path', 'url(#clip-'+thisEntry.label+')');
        }

        var shift = thisEntry.diffNorm - 10;
        if (shift > 0) shift = 0;
        thisEntry.yAxis = nh_graphs.svg.axis().scale(thisEntry.yScale).orient("left").ticks(10);
        var ti = focus.obj.append("g").call(thisEntry.yAxis).style("stroke-width", "1").attr('transform', 'translate('+focus.chartXOffset+',0)').attr('class', 'y axis axis-'+thisEntry.label);
        var hTicks = thisEntry.yScale.ticks();
        //ti.remove();
        focus.obj.selectAll("line.verticalGrid.focus" + thisEntry.label).data(focus.xScale.ticks()).enter().append("line").attr({
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
            stroke: svg.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
            "stroke-width": "1px"
        });
        focus.obj.selectAll("line.horizontalGrid.focus" + thisEntry.label).data(hTicks).enter().append("line").attr({
            "class": "horizontalGrid focus" + thisEntry.label,
            x1: focus.chartXOffset,
            x2: svg.width - svg.infoAreaRight - 11,
            y1: function(d) {
                return thisEntry.yScale(d);
            },
            y2: function(d) {
                return thisEntry.yScale(d);
            },
            "shape-rendering": "crispEdges",
            stroke: svg.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
            "stroke-width": "1px"
        });
        if (thisEntry.label == "BP") {
            focus.obj.selectAll("." + thisEntry.label + "-top-line").data(svg.data.filter(function(d) {
                if (d.blood_pressure_systolic) {
                    return d;
                }
            })).enter().append("rect").attr({
                'y': function(d){
                    return thisEntry.yScale(d.blood_pressure_systolic);
                },
                'x': function(d){
                    return focus.xScale(d.date_terminated) - (focus.BPWidth / 2);
                },
                'height': 2,
                'width': focus.BPWidth,
                'class': thisEntry.label + '-top-line',
                'clip-path': 'url(#clip-'+thisEntry.label+')'
            }).style("display", function(d) {
                if (d["blood_pressure_systolic"] === null) {
                    return "none";
                } else {
                    return null;
                }
            }).on("mouseover", function(d) {
                return self.contextMouseOver("s:" + d["blood_pressure_systolic"] + " d:" + d["blood_pressure_diastolic"], $(this).position());
            }).on("mouseout", self.contextMouseOut);


            focus.obj.selectAll("." + thisEntry.label + "-bottom-line").data(svg.data.filter(function(d) {
                if (d.blood_pressure_diastolic) {
                    return d;
                }
            })).enter().append("rect").attr({
                'y': function(d){
                    return thisEntry.yScale(d.blood_pressure_diastolic);
                },
                'x': function(d){
                    return focus.xScale(d.date_terminated) - (focus.BPWidth / 2);
                },
                'height': 2,
                'width': focus.BPWidth,
                'class': thisEntry.label + '-bottom-line',
                'clip-path': 'url(#clip-'+thisEntry.label+')'
            }).style("display", function(d) {
                if (d["blood_pressure_diastolic"] === null) {
                    return "none";
                } else {
                    return null;
                }
            }).on("mouseover", function(d) {
                return self.contextMouseOver("s:" + d["blood_pressure_systolic"] + " d:" + d["blood_pressure_diastolic"], $(this).position());
            }).on("mouseout", self.contextMouseOut);
            //}

            focus.obj.selectAll("#" + thisEntry.label)
                .data(svg.data.filter(function(d){ if(d.blood_pressure_diastolic && d.blood_pressure_systolic){ return d; }}))
                .enter().append("rect").attr({
                    width: 2,
                    height: function(d) {
                        return thisEntry.yScale(d["blood_pressure_diastolic"]) - thisEntry.yScale(d["blood_pressure_systolic"]);
                    },
                    x: function(d) {
                        return focus.xScale(d.date_terminated) - 1;
                    },
                    y: function(d) {
                        return thisEntry.yScale(d["blood_pressure_systolic"]);
                    },
                    "clip-path": "url(#clip)",
                    "class": "data_lines data-" + thisEntry.label
                }).style("display", function(d) {
                    if (d["blood_pressure_systolic"] === null || d["blood_pressure_diastolic"] === null) {
                        return "none";
                    } else {
                        return null;
                    }
                }).style({
                    stroke: "rgba(0,0,0,0)",
                    "stroke-width": "3"
                }).on("mouseover", function(d) {
                    return self.contextMouseOver("s:" + d["blood_pressure_systolic"] + " d:" + d["blood_pressure_diastolic"], $(this).position());
                }).on("mouseout", self.contextMouseOut);
            focus.obj.append("text").text(thisEntry.label).attr("y", thisEntry.yScale(thisEntry.normMax) + shift).attr("x", svg.width - svg.infoAreaRight).attr({
                "font-family": "sans-serif",
                "font-size": "12px",
                "font-weight": "bold",
                fill: "#BBBBBB",
                "text-anchor": "start",
                "class": "info infoname-" + thisEntry.label
            });
            focus.obj.append("text").text(function() {
                if (svg.data[svg.data.length - 1]["blood_pressure_systolic"]) {
                    return svg.data[svg.data.length - 1]["blood_pressure_systolic"];
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
            focus.obj.append("text").text(function() {
                if (svg.data[svg.data.length - 1]["blood_pressure_diastolic"]) {
                    return svg.data[svg.data.length - 1]["blood_pressure_diastolic"];
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
            focus.obj.append("text").text(function() {
                return thisEntry.measurement;
            }).attr("y", thisEntry.yScale(thisEntry.normMin) - 10).attr("x", svg.width - svg.infoAreaRight + svg.labelGap * 2).attr({
                "font-family": "sans-serif",
                "font-size": "9px",
                "font-weight": "bold",
                "text-anchor": "start",
                "class": "info infovalue3-" + thisEntry.label
            });
        } else {
            thisEntry.area = nh_graphs.svg.line().interpolate("linear")
                .defined(function(d){ if(d[thisEntry.key] !== false){ return d; }})
                .x(function(d) {
                    return focus.xScale(d.date_terminated);
                }).y(function(d) {
                    return thisEntry.yScale(d[thisEntry.key]);
                });
            focus.obj.append("path")
                .datum(svg.data.filter(function(d){ if(d[thisEntry.key] !== false){ return d; }}))
                .attr("d", thisEntry.area).style({
                    stroke: svg.printing ? "#222222" : "#888888",
                    "stroke-width": "1",
                    fill: "none"
                }).attr("class", "focusPath").attr("id", "path-" + thisEntry.key).attr("clip-path", "url(#clip)");

            focus.obj.selectAll("#" + thisEntry.label)
                .data(svg.data.filter(function(d){ if(d[thisEntry.key] !== false){ return d; }}))
                .enter().append("circle").attr("cx", function(d) {
                    return focus.xScale(d.date_terminated);
                }).attr("cy", function(d) {
                    return thisEntry.yScale(d[thisEntry.key]);
                }).attr("r", 3).attr("class", "data_points data-" + thisEntry.label).style("display", function(d) {
                    if (d[thisEntry.key]) {
                        return null;
                    } else {
                        return "none";
                    }
                }).attr("clip-path", "url(#clip)")
                .attr("data-label", thisEntry.key).on("mouseover", function(d) {
                    return self.contextMouseOver(d[$(this).attr("data-label")], $(this).position());
                }).on("mouseout", self.contextMouseOut);

            focus.obj.append("text").text(thisEntry.label).attr("y", thisEntry.yScale(thisEntry.normMax) + shift).attr("x", svg.width - svg.infoAreaRight).attr({
                "font-family": "sans-serif",
                "font-size": "12px",
                "font-weight": "bold",
                fill: "#BBBBBB",
                "text-anchor": "start",
                "class": "info infoname-" + thisEntry.label
            });
            focus.obj.append("text").text(function() {
                if (svg.data[svg.data.length - 1][thisEntry.key]) {
                    return svg.data[svg.data.length - 1][thisEntry.key] + thisEntry.measurement;
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

    focus.obj.selectAll(".axis path").style({"stroke-width": "1", "fill": "none","shape-rendering": "crispEdges", "stroke":"black"});
    focus.obj.selectAll(".axis .tick line").style({"stroke-width": "1", "fill": "none","shape-rendering": "crispEdges", "stroke":"black"});

},

redrawContext: function(){
    var context = this.context, focus = this.focus, svg = this.svg;
    var self = this;

    context.obj.selectAll("rect.scoreRange").attr({
        y: function(d) {
            return context.yScale(d.e) - 1;
        },
        height: function(d) {
            return context.yScale(d.s) - (context.yScale(d.e) - 1);
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
        stroke: svg.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
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
        stroke: svg.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
        "stroke-width": "1px"
    });

    context.area = nh_graphs.svg.line()
        .interpolate("step-after")
        .defined(function(d){ if(d.none_values == "[]"){ return d; }})
        .x(function(d) {
            return context.xScale(d.date_terminated);
        })
        .y(function(d) {
            return context.yScale(d.score);
        });
    context.obj.select(".contextPath").attr("d", context.area);

    context.obj.selectAll("circle.contextPoint").attr("cy", function(d) {
        return context.yScale(d.score);
    });

    context.obj.selectAll("circle.emptyContextPoint")
        .attr("cy", function(d) {
            return context.yScale(context.yScale.domain()[1] / 2);
        });

    context.yAxis = nh_graphs.svg.axis().scale(context.yScale).orient("left").tickFormat(nh_graphs.format("d"));
    context.obj.select('.y.axis').call(context.yAxis);
},

redrawFocusYAxis: function(){
    var context = this.context, focus = this.focus, svg = this.svg;
    var self = this;

    for (var i = 0; i < focus.graphs.length; i++) {


        var thisEntry = focus.graphs[i];


        var newDiffNorm = (thisEntry.yScale(thisEntry.normMin) - thisEntry.yScale(thisEntry.normMax));
        var shift = newDiffNorm - 10;
        if (shift > 0) shift = 0;
        if (thisEntry.label != "Temp") {
            thisEntry.yAxis = nh_graphs.svg.axis().scale(thisEntry.yScale).orient("left").tickFormat(nh_graphs.format("d"));//.ticks(10);
        }else{
            thisEntry.yAxis = nh_graphs.svg.axis().scale(thisEntry.yScale).orient("left").ticks(10);
        }
        focus.obj.select('.y.axis-'+thisEntry.label).call(thisEntry.yAxis);
        hTicks = thisEntry.yScale.ticks();
        //ti.remove();
        focus.obj.selectAll("line.verticalGrid.focus" + thisEntry.label).data(focus.xScale.ticks()).enter().append("line").attr({
            "class": "verticalGrid focus" + thisEntry.label,
            x1: function (d) {
                return focus.xScale(d);
            },
            x2: function (d) {
                return focus.xScale(d);
            },
            y1: thisEntry.yScale.range()[0],
            y2: thisEntry.yScale.range()[1],
            "shape-rendering": "crispEdges",
            stroke: svg.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
            "stroke-width": "1px"
        });

        focus.obj.selectAll("line.horizontalGrid.focus" + thisEntry.label).remove();

        focus.obj.selectAll("line.horizontalGrid.focus" + thisEntry.label).data(hTicks).enter().append("line").attr({
            "class": "horizontalGrid focus" + thisEntry.label,
            x1: focus.chartXOffset,
            x2: svg.width - svg.infoAreaRight - 11,
            y1: function (d) {
                return thisEntry.yScale(d);
            },
            y2: function (d) {
                return thisEntry.yScale(d);
            },
            "shape-rendering": "crispEdges",
            stroke: svg.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
            "stroke-width": "1px"
        });



        if (thisEntry.label != "BP") {
            focus.obj.selectAll("rect.norm-"+thisEntry.label).attr("y", thisEntry.yScale(thisEntry.normMax)).attr("height", newDiffNorm);
        } else {
            //focus.obj.selectAll(".line-BP").attr("x1", focus.chartXOffset).attr("x2", svg.width - svg.infoAreaRight - 11).attr("y1", thisEntry.yScale(100)).attr("y2", thisEntry.yScale(100));
        }
    }
    focus.obj.selectAll(".axis .tick line").style({"stroke-width": "1", "fill": "none","shape-rendering": "crispEdges", "stroke":"black"});
    focus.obj.selectAll(".axis path").style({"stroke-width": "1", "fill": "none","shape-rendering": "crispEdges", "stroke":"black"});

},




redrawFocus: function(transition) {
    var context = this.context, focus = this.focus, svg = this.svg;
    var self = this;
    focus.obj.selectAll(".data_points").transition().duration(svg.transitionDuration).attr("cx", function(d) {
        return focus.xScale(d.date_terminated);
    });



    if (transition) {
        svg.transitionDuration = 1e3;
    } else {
        svg.transitionDuration = 0;
    }
    for (var i = 0; i < focus.graphs.length; i++) {
        var thisEntry = focus.graphs[i];
        thisEntry.area = nh_graphs.svg.line().interpolate("linear").x(function(d) {
            return focus.xScale(d.date_terminated);
        }).y(function(d) {
            return thisEntry.yScale(d[thisEntry.key]);
        });

        // hoping to replot points on y-scale
        focus.obj.selectAll("circle.data-"+thisEntry.label).attr("cy", function(d){
            return thisEntry.yScale(d[thisEntry.key]);
        });


        focus.obj.select("#path-" + thisEntry.key).transition().duration(svg.transitionDuration).attr("d", thisEntry.area);
        focus.obj.selectAll("line.verticalGrid.focus" + thisEntry.label).remove().data(focus.xScale.ticks()).enter().append("line").attr({
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
            stroke: svg.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
            "stroke-width": "1px"
        });

        if(thisEntry.label == "BP"){
            focus.obj.selectAll(".data_lines").transition().duration(svg.transitionDuration).attr("x", function(d) { return focus.xScale(d.date_terminated);})
                .attr('y', function(d){ return thisEntry.yScale(d.blood_pressure_systolic); })
                .attr('height', function(d) { return thisEntry.yScale(d["blood_pressure_diastolic"]) - thisEntry.yScale(d["blood_pressure_systolic"]);});

            focus.obj.selectAll('line.normal-line-BP').attr('y1', thisEntry.yScale(100)).attr('y2', thisEntry.yScale(100));
        }
    }
    focus.obj.select(".x.axis").call(focus.xAxis).style("stroke-width", "1");



    focus.obj.selectAll(".data_points").transition().duration(svg.transitionDuration).attr("cx", function(d) {
        return focus.xScale(d.date_terminated);
    });

    focus.obj.selectAll('.'+thisEntry.label+'-top-line').attr({'y': function(d){
        return thisEntry.yScale(d.blood_pressure_systolic);
    },
        'x': function(d){
            return (focus.xScale(d.date_terminated) - ((focus.BPWidth/2)-1));
        }});
    focus.obj.selectAll('.'+thisEntry.label+'-bottom-line').attr({'y': function(d){
        return thisEntry.yScale(d.blood_pressure_diastolic);
    },
        'x': function(d){
            return (focus.xScale(d.date_terminated) - ((focus.BPWidth/2)-1));
        }});
//            }

    focus.obj.selectAll(".horizontalGrid").transition().duration(svg.transitionDuration).attr("x2", focus.xScale(focus.xScale.domain()[1]));
    focus.obj.selectAll(".x.axis g text").each(this.insertLinebreaks);
    this.initTable();
},
drawTable: function() {
    var context = this.context, focus = this.focus, svg = this.svg;
    for (var i = 0; i < focus.tables.length; i++) {
        var thisEntry = focus.tables[i];
        var tableData = [ thisEntry.label ];
        var startDate = new Date(focus.xScale.domain()[0]);
        var endDate = new Date(focus.xScale.domain()[1]);
        for (var j = 0; j < svg.data.length; j++) {
            if (svg.data[j].date_terminated >= startDate && svg.data[j].date_terminated <= endDate) {
                tableData.push(svg.data[j][thisEntry.key]);
            }
        }
        var tableTR = nh_graphs.select("#chartTable").append("tr").style({"background-color": (i % 2 == 0 ? "#ffffff" : "#eeeeee")});

        tableTR.selectAll("td." + thisEntry.label).data(tableData).enter().append("td").html(function(d) {
            return d;
        }).attr("class", thisEntry.label).style({"padding": "0.3em 0.5%",  "text-align": function(d){ if(d != thisEntry.label){ return "center";}},  "border-left": function(d){ if(d != thisEntry.label){ return "1px solid #262626";}}});
    }
},
drawTabularObs: function(el){
    //var container = nh_graphs.select(el).append('div');
    var context = this.context, focus = this.focus, svg = this.svg;
    var container = nh_graphs.select('#table-content').append('div').attr('style', 'padding-top: 1em');
    var cards = container.selectAll('.card').data(svg.data.reverse()).enter().append('div').attr('class','card');
    var header = cards.append('h3').text(function(d){
        return ("0" + d.date_terminated.getHours()).slice(-2) + ":" + ("0" + d.date_terminated.getMinutes()).slice(-2) + " " + ("0" + d.date_terminated.getDate()).slice(-2) + "/" + ("0" + (d.date_terminated.getMonth() + 1)).slice(-2) + "/" + d.date_terminated.getFullYear(); });
    var list = cards.append('table');
    var list_items = list.selectAll('tr').data(function(d){ return $.map(d, function(v,k){ if(k !== "indirect_oxymetry_spo2_label"){ var name = graph_lib.process_obs_name(k); if(typeof(name) !== "undefined"){ return {key: name, value: v};}} }); }).enter();
    list_items.append('tr').html(function(d){
        if(typeof(d.value) == "object"){
            if(d.key == "Oxygen Administration Flag"){
                //return process_oxygen_administration_flag_object(d.value);
                if(d.value.onO2 == true){
                    return '<td>' + d.key + '</td><td> true </td>';
                }else{
                    return '<td>'+ d.key+'</td><td> false </td>';
                }
            }
        }else{
            return '<td>'+ d.key+'</td><td>' + d.value + '</td>';
        }
    });
},

insertLinebreaks: function(d) {
    var context = this.context, focus = this.focus, svg = this.svg;
    var el = nh_graphs.select(this);
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
},

contextMouseOver: function(text, position) {
    var context = this.context, focus = this.focus, svg = this.svg;
    var popupMargins = {
        top: 0,
        left: 3,
        right: 0,
        bottom: 20
    };
    graph_lib.svg.popup.style("left", (position.left + popupMargins.left) + "px").style("top", (position.top - popupMargins.bottom) + "px").text(text);
    graph_lib.svg.popup.transition().duration(500).style("opacity", 1);
},

contextMouseOut: function(el) {
    graph_lib.svg.popup.transition().duration(500).style("opacity", 1e-6);
},

brushed: function() {
    var context = graph_lib.context, focus = graph_lib.focus;
    focus.xScale.domain(context.brush.empty() ? context.xScale.domain() : context.brush.extent());

    if (!context.brush.empty()) {
        var stD = context.brush.extent()[0];
        var enD = context.brush.extent()[1];
        var stdT = ("0" + stD.getHours()).slice(-2) + ":" + ("0" + stD.getMinutes()).slice(-2) + " " + ("0" + stD.getDate()).slice(-2) + "/" + ("0" + stD.getMonth()).slice(-2);
        var enT = ("0" + enD.getHours()).slice(-2) + ":" + ("0" + enD.getMinutes()).slice(-2) + " " + ("0" + enD.getDate()).slice(-2) + "/" + ("0" + enD.getMonth()).slice(-2);
        $("#x_range").html("for " + stdT + " - " + enT);
    } else {
        $("#x_range").html("");
    }
    graph_lib.redrawFocus(false);
},

rangifyFocus: function(transition) {
    var context = this.context, focus = this.focus, svg = this.svg;
    var self = this;
    if(svg.data.length > 1) {
        context.yScale.domain(context.scoreExtent);
        for (var i = 0; i < focus.graphs.length; i++) {
            var thisEntry = focus.graphs[i];
            thisEntry.yScale.domain([(thisEntry.rangified_extent[0] - focus.rangePadding), (thisEntry.rangified_extent[1] + focus.rangePadding)]);

        }
        this.redrawContext();
        this.redrawFocus();
        this.redrawFocusYAxis();
    }
},

derangifyFocus: function(transition) {
    var context = this.context, focus = this.focus, svg = this.svg;
    var self = this;
    if(svg.data.length > 1) {
        context.yScale.domain([0, context.maxScore]);
        for (var i = 0; i < focus.graphs.length; i++) {
            var thisEntry = focus.graphs[i];
            thisEntry.yScale.domain(thisEntry.default_extent);
        }
        this.redrawContext();
        this.redrawFocus();
        this.redrawFocusYAxis();
    }
},

resizeGraphs: function() {
    var context = this.context, focus = this.focus, svg = this.svg;
    var win = $(svg.el);
    var ori = win.width() > win.height() ? "landscape" : "portrait";
    w = win.width() - svg.margins.left - svg.margins.right;
    svg.width = w + svg.margins.left + svg.margins.right;
    svg.obj = nh_graphs.select("svg").transition().duration(svg.transitionDuration).attr("width", svg.width);
    context.xScale.range([ svg.margins.left / 4, w - (svg.infoAreaRight + svg.margins.right / 4) ]);
    context.xAxis.scale(context.xScale);
    context.obj.selectAll(".x.axis").call(context.xAxis).style("stroke-width", "1");
    context.area.x(function(d) {
        return context.xScale(d.date_terminated);
    }).y(function(d) {
        return context.yScale(d.score);
    });
    context.obj.selectAll(".contextPath").transition().duration(svg.transitionDuration).attr("d", context.area);
    context.obj.selectAll(".contextPoint").transition().duration(svg.transitionDuration).attr("cx", function(d) {
        return context.xScale(d.date_terminated);
    });
    context.obj.selectAll(".x.axis g text").each(this.insertLinebreaks);
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
        stroke: svg.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
        "stroke-width": "1px"
    });
    //context.brush.x(context.xScale);
    focus.obj.select("#clip").transition().duration(svg.transitionDuration).attr("width", w - (svg.infoAreaRight + svg.margins.right / 4));
    focus.obj.select("#clip").transition().duration(svg.transitionDuration).select("rect").attr("width", w - (svg.infoAreaRight + svg.margins.right / 4));
    focus.xScale.range([ svg.margins.left / 4, w - (svg.infoAreaRight + svg.margins.right / 4) ]);
    focus.xAxis.scale(focus.xScale);
    nh_graphs.select("#focusChart").select("svg").transition().duration(svg.transitionDuration).attr("width", w + svg.infoAreaRight + svg.margins.right);
    focus.obj.selectAll(".line").transition().duration(svg.transitionDuration).attr("x2", w - (svg.infoAreaRight + svg.margins.right / 4));
    focus.obj.selectAll(".norm").transition().duration(svg.transitionDuration).attr("width", w - (svg.infoAreaRight + svg.margins.right / 3));
    focus.obj.selectAll(".info").transition().duration(svg.transitionDuration).attr("x", w - (svg.infoAreaRight + svg.margins.right / 4) + svg.labelGap);
    focus.obj.selectAll(".infovalue3-BP").transition().duration(svg.transitionDuration).attr("x", w - (svg.infoAreaRight + svg.margins.right / 4) + svg.labelGap * 3);
    this.redrawFocus(false);
},

initTable: function() {
    var context = this.context, focus = this.focus, svg = this.svg;
    if (focus.tables.length != 0){
        var headerData = [ "Type" ];
        nh_graphs.select("#chartTable").selectAll("tr").remove();
        var startDate = new Date(focus.xScale.domain()[0]);
        var endDate = new Date(focus.xScale.domain()[1]);
        for (var i = 0; i < svg.data.length; i++) {
            if (svg.data[i].date_terminated >= startDate && svg.data[i].date_terminated <= endDate) {
                headerData.push(svg.data[i].date_terminated);
            }
        }
        dataTableTr = nh_graphs.select("#chartTable").append("tr");
        dataTableTr.selectAll("th").data(headerData).enter().append("th").html(function(d) {
            if (d == "Type") {
                return d;
            } else {
                return ("0" + d.getDate()).slice(-2) + "/" + ("0" + (d.getMonth() + 1)).slice(-2) + "<br>" + ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2);
            }
        }).style({"width": (90 / headerData.length + "%"), "border-bottom": "1px solid #262626", "text-align": function(d){ if(d != "Type"){ return "center";}},  "border-left": function(d){ if(d != "Type"){ return "1px solid #262626"; }}});
        this.drawTable();
    }else{
        $("#the_unplottables").remove();
    }
},

process_obs_name: function(key_name){
    switch(key_name){
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
},

};
return graph_lib;
}());
