graph_lib = function() {
    var t = {
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
            ticks: 10,
            printing: !1,
            focusOnly: !1,
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
        initGraph: function(t) {
            console.log("Calling initVGraph");
            var e = this.context, a = this.focus, r = this.svg;
            "undefined" == typeof t && (t = 10), e.maxScore = t, r.width = $(r.el).width() - r.margins.left - r.margins.right, 
            r.infoAreaRight = r.width / 18, a.height = (a.graphs.length + 1) * a.chartHeight, 
            r.height = e.height + a.height + e.margins.bottom + e.margins.top + a.margins.bottom + a.margins.top, 
            r.obj.context = d3.select("#contextChart").append("svg").attr("width", r.width + r.margins.left + r.margins.right).attr("height", e.height + e.margins.bottom + e.margins.top).append("g").attr("transform", "translate(0," + e.margins.top + ")"), 
            r.obj.focus = d3.select("#focusChart").append("svg").attr("width", r.width + r.margins.left + r.margins.right).attr("height", a.height + a.margins.bottom + a.margins.top).append("g").attr("transform", "translate(0," + a.margins.top / 3 + ")"), 
            e.yScale = d3.scale.linear().domain([ 0, t ]).range([ e.height, 0 ]), e.yAxis = d3.svg.axis().scale(e.yScale).orient("left");
            var i = new Date(e.earliestDate.toString()), n = new Date(e.now.toString()), s = (n - i) / 1e3 / 60 / 60;
            s >= 2 ? (i.setHours(i.getHours() - 1), i.setMinutes(0), i.setSeconds(0), n.setHours(n.getHours() + 1), 
            n.setMinutes(0), n.setSeconds(0)) : (i.setMinutes(i.getMinutes() - r.timePadding), 
            n.setMinutes(n.getMinutes() + r.timePadding)), r.printing && (i.setMinutes(i.getMinutes() - r.printTimePadding), 
            n.setMinutes(n.getMinutes() + r.printTimePadding), r.obj.context.attr("printing", "true")), 
            e.now = n, e.xScale = d3.time.scale().domain([ i, n ]).range([ e.chartXOffset, r.width - (r.infoAreaRight + r.margins.right / 4) ]), 
            e.xAxis = d3.svg.axis().scale(e.xScale).orient("top"), a.xScale = d3.time.scale().domain([ i, n ]).range([ e.chartXOffset, r.width - (r.infoAreaRight + r.margins.right / 4) ]), 
            a.xAxis = d3.svg.axis().scale(a.xScale).orient("top"), this.drawChart(), this.drawGraph();
        },
        insertLinebreaks: function(t) {
            var e = (this.context, this.focus, this.svg, d3.select(this)), a = 10, r = [ "Sun", "Mon", "Tues", "Wed", "Thu", "Fri", "Sat" ], i = r[t.getDay()] + " " + t.getDate() + "/" + ("0" + (t.getMonth() + 1)).slice(-2) + " " + ("0" + t.getHours()).slice(-2) + ":" + ("0" + t.getMinutes()).slice(-2), n = i.split(" ");
            e.text("");
            for (var s = 0; s < n.length; s++) {
                var l = e.append("tspan").text(n[s]);
                s > 0 && l.attr("x", 0).attr("dy", "15");
            }
            e.attr("y", "-" + (n.length * a + a));
        },
        contextMouseOver: function(t, e) {
            var a = (this.context, this.focus, this.svg), r = {
                top: 0,
                left: 3,
                right: 0,
                bottom: 20
            };
            a.popup.style("left", e.left + r.left + "px").style("top", e.top - r.bottom + "px").text(t), 
            a.popup.transition().duration(500).style("opacity", 1);
        },
        contextMouseOut: function() {
            this.svg.popup.transition().duration(500).style("opacity", 1e-6);
        },
        brushed: function() {
            var t = this.context, e = this.focus;
            if (e.xScale.domain(t.brush.empty() ? t.xScale.domain() : t.brush.extent()), t.brush.empty()) $("#x_range").html(""); else {
                var a = t.brush.extent()[0], r = t.brush.extent()[1], i = ("0" + a.getHours()).slice(-2) + ":" + ("0" + a.getMinutes()).slice(-2) + " " + ("0" + a.getDate()).slice(-2) + "/" + ("0" + a.getMonth()).slice(-2), n = ("0" + r.getHours()).slice(-2) + ":" + ("0" + r.getMinutes()).slice(-2) + " " + ("0" + r.getDate()).slice(-2) + "/" + ("0" + r.getMonth()).slice(-2);
                $("#x_range").html("for " + i + " - " + n);
            }
            this.redrawFocus(!1);
        },
        rangifyFocus: function() {
            var t = this.context, e = this.focus, a = this.svg;
            if (a.data.length > 1) {
                t.yScale.domain(t.scoreExtent);
                for (var r = 0; r < e.graphs.length; r++) {
                    var i = e.graphs[r];
                    i.yScale.domain([ i.rangified_extent[0] - e.rangePadding, i.rangified_extent[1] + e.rangePadding ]);
                }
                this.redrawContext(), this.redrawFocus(), this.redrawFocusYAxis();
            }
        },
        derangifyFocus: function() {
            var t = this.context, e = this.focus, a = this.svg;
            if (a.data.length > 1) {
                t.yScale.domain([ 0, t.maxScore ]);
                for (var r = 0; r < e.graphs.length; r++) {
                    var i = e.graphs[r];
                    i.yScale.domain(i.default_extent);
                }
                this.redrawContext(), this.redrawFocus(), this.redrawFocusYAxis();
            }
        },
        resizeGraphs: function() {
            {
                var t = this.context, e = this.focus, a = this.svg, r = $(a.el);
                r.width() > r.height() ? "landscape" : "portrait";
            }
            w = r.width() - a.margins.left - a.margins.right, a.width = w + a.margins.left + a.margins.right, 
            a.obj = d3.select("svg").transition().duration(a.transitionDuration).attr("width", a.width), 
            t.xScale.range([ a.margins.left / 4, w - (a.infoAreaRight + a.margins.right / 4) ]), 
            t.xAxis.scale(t.xScale), t.obj.selectAll(".x.axis").call(t.xAxis).style("stroke-width", "1"), 
            t.area.x(function(e) {
                return t.xScale(e.date_started);
            }).y(function(e) {
                return t.yScale(e.score);
            }), t.obj.selectAll(".contextPath").transition().duration(a.transitionDuration).attr("d", t.area), 
            t.obj.selectAll(".contextPoint").transition().duration(a.transitionDuration).attr("cx", function(e) {
                return t.xScale(e.date_started);
            }), t.obj.selectAll(".x.axis g text").each(this.insertLinebreaks), t.obj.selectAll(".horizontalGrid").transition().duration(a.transitionDuration).attr("x2", w - a.infoAreaRight - 10), 
            t.obj.selectAll(".green").transition().duration(a.transitionDuration).attr("width", w - (a.infoAreaRight + a.margins.right / 3)), 
            t.obj.selectAll(".amber").transition().duration(a.transitionDuration).attr("width", w - (a.infoAreaRight + a.margins.right / 3)), 
            t.obj.selectAll(".red").transition().duration(a.transitionDuration).attr("width", w - (a.infoAreaRight + a.margins.right / 3)), 
            t.obj.selectAll(".verticalGrid").remove().data(t.xScale.ticks()).enter().append("line").attr({
                "class": "verticalGrid",
                x1: function(e) {
                    return t.xScale(e);
                },
                x2: function(e) {
                    return t.xScale(e);
                },
                y1: 0,
                y2: t.height,
                "shape-rendering": "crispEdges",
                stroke: a.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
                "stroke-width": "1px"
            }), e.obj.select("#clip").transition().duration(a.transitionDuration).attr("width", w - (a.infoAreaRight + a.margins.right / 4)), 
            e.obj.select("#clip").transition().duration(a.transitionDuration).select("rect").attr("width", w - (a.infoAreaRight + a.margins.right / 4)), 
            e.xScale.range([ a.margins.left / 4, w - (a.infoAreaRight + a.margins.right / 4) ]), 
            e.xAxis.scale(e.xScale), d3.select("#focusChart").select("svg").transition().duration(a.transitionDuration).attr("width", w + a.infoAreaRight + a.margins.right), 
            e.obj.selectAll(".line").transition().duration(a.transitionDuration).attr("x2", w - (a.infoAreaRight + a.margins.right / 4)), 
            e.obj.selectAll(".norm").transition().duration(a.transitionDuration).attr("width", w - (a.infoAreaRight + a.margins.right / 3)), 
            e.obj.selectAll(".info").transition().duration(a.transitionDuration).attr("x", w - (a.infoAreaRight + a.margins.right / 4) + a.labelGap), 
            e.obj.selectAll(".infovalue3-BP").transition().duration(a.transitionDuration).attr("x", w - (a.infoAreaRight + a.margins.right / 4) + 3 * a.labelGap), 
            this.redrawFocus(!1);
        },
        initTable: function() {
            var t = (this.context, this.focus), e = this.svg;
            if (0 != t.tables.length) {
                var a = [ "Type" ];
                d3.select("#chartTable").selectAll("tr").remove();
                for (var r = new Date(t.xScale.domain()[0]), i = new Date(t.xScale.domain()[1]), n = 0; n < e.data.length; n++) e.data[n].date_started >= r && e.data[n].date_started <= i && a.push(e.data[n].date_started);
                dataTableTr = d3.select("#chartTable").append("tr"), dataTableTr.selectAll("th").data(a).enter().append("th").html(function(t) {
                    return "Type" == t ? t : ("0" + t.getDate()).slice(-2) + "/" + ("0" + (t.getMonth() + 1)).slice(-2) + "<br>" + ("0" + t.getHours()).slice(-2) + ":" + ("0" + t.getMinutes()).slice(-2);
                }).style({
                    width: 90 / a.length + "%",
                    "border-bottom": "1px solid #262626",
                    "text-align": function(t) {
                        return "Type" != t ? "center" : void 0;
                    },
                    "border-left": function(t) {
                        return "Type" != t ? "1px solid #262626" : void 0;
                    }
                }), this.drawTable();
            } else $("#the_unplottables").remove();
        },
        drawChart: function() {
            var t = this.context, e = this.focus, a = this.svg, r = this;
            a.focusOnly || (t.obj = a.obj.context.append("g").attr("transform", "translate(" + a.margins.left + "," + t.margins.top + ")"), 
            t.obj.append("defs").append("clipPath").attr("id", "context-clip").append("rect").attr("width", a.width - a.infoAreaRight - (10 + t.chartXOffset)).attr("height", t.height).attr("y", 0).attr("x", t.chartXOffset), 
            t.obj.selectAll("rect.scoreRange").data(t.scoreRange).enter().append("rect").attr({
                "class": function(t) {
                    return t.class + " scoreRange";
                },
                fill: function(t) {
                    return "red" == t.class ? "#ffcccc" : "amber" == t.class ? "#ffe9c8" : "green" == t.class ? "#ccffcc" : void 0;
                },
                x: t.xScale(t.xScale.domain()[0]),
                y: function(e) {
                    return t.yScale(e.e) - 1;
                },
                width: a.width - (a.infoAreaRight + a.margins.right / 3),
                "clip-path": "url(#context-clip)",
                height: function(e) {
                    return t.yScale(e.s) - (t.yScale(e.e) - 1);
                }
            }), t.obj.selectAll("line.verticalGrid").data(t.xScale.ticks()).enter().append("line").attr({
                "class": "verticalGrid",
                x1: function(e) {
                    return t.xScale(e);
                },
                x2: function(e) {
                    return t.xScale(e);
                },
                y1: 0,
                y2: t.height,
                "shape-rendering": "cripsEdges",
                stroke: a.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
                "stroke-width": "1px"
            }), t.obj.selectAll("line.horizontalGrid").data([ 0, 3, 6, 9, 12, 15, 18 ]).enter().append("line").attr({
                "class": "horizontalGrid",
                x1: t.xScale(t.xScale.domain()[0]),
                x2: t.xScale(t.xScale.domain()[1]),
                y1: function(e) {
                    return t.yScale(e);
                },
                y2: function(e) {
                    return t.yScale(e);
                },
                "shape-rendering": "cripsEdges",
                stroke: a.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
                "stroke-width": "1px"
            }), t.obj.append("g").attr("class", "x axis").call(t.xAxis).style("stroke-width", "1"), 
            t.obj.append("g").attr({
                "class": "y axis",
                transform: "translate(" + t.chartXOffset + ",0)"
            }).call(t.yAxis).style("stroke-width", "1"), t.brush = d3.svg.brush().x(t.xScale).on("brush", r.brushed), 
            t.obj.append("g").attr("class", "x brush").call(t.brush).selectAll("rect").attr("y", -6).attr("height", t.height + 7).style({
                fill: "#333",
                opacity: "0.5"
            }), t.area = d3.svg.line().interpolate("step-after").defined(function(t) {
                return t.complete === !0 ? t : void 0;
            }).x(function(e) {
                return t.xScale(e.date_started);
            }).y(function(e) {
                return t.yScale(e.score);
            }), t.obj.append("path").datum(a.data).attr("d", t.area).style({
                stroke: "#555555",
                "stroke-width": "1",
                fill: "none"
            }).attr("class", "contextPath"), t.obj.selectAll("circle.contextPoint").data(a.data.filter(function(t) {
                return t.complete === !0 ? t : void 0;
            })).enter().append("circle").attr("cx", function(e) {
                return t.xScale(e.date_started);
            }).attr("cy", function(e) {
                return t.yScale(e.score);
            }).attr("r", 3).attr("class", "contextPoint").on("mouseover", function(t) {
                return r.contextMouseOver(t.score, $(this).position());
            }).on("mouseout", r.contextMouseOut).style({
                fill: "#000000",
                stroke: "rgba(0,0,0,0)",
                "stroke-width": "3"
            }), t.obj.selectAll("circle.emptyContextPoint").data(a.data.filter(function(t) {
                return t.complete === !1 ? t : void 0;
            })).enter().append("circle").attr("cx", function(e) {
                return t.xScale(e.date_started);
            }).attr("cy", function() {
                return t.yScale(t.yScale.domain()[1] / 2);
            }).attr("r", 3).attr("class", "emptyContextPoint").on("mouseover", function() {
                return r.contextMouseOver("Partial observation", $(this).position());
            }).on("mouseout", r.contextMouseOut).style({
                fill: "white",
                stroke: "rgba(0,0,0,1)",
                "stroke-width": "1"
            }), t.obj.selectAll(".x.axis g text").each(this.insertLinebreaks), t.obj.selectAll(".axis .domain").style({
                "stroke-width": "1",
                fill: "none",
                "shape-rendering": "crispEdges",
                stroke: "black"
            }), t.obj.selectAll(".axis .tick line").style({
                "stroke-width": "1",
                fill: "none",
                "shape-rendering": "crispEdges",
                stroke: "black"
            })), a.popup = d3.select(".t4skr_ewschart").append("div").attr("class", "contextPopup").style({
                opacity: "0",
                position: "absolute",
                "text-align": "center",
                width: "5%",
                padding: "0.4em 0.25%",
                font: "0.8em sans-serif",
                background: "rgba(0,0,0,0.7)",
                border: "solid 0px rgba(0,0,0,0.7)",
                "border-radius": "8px",
                "border-bottom-left-radius": "0px",
                "pointer-events": "none",
                color: "white"
            }), e.obj = a.obj.focus.append("g").attr("transform", "translate(" + a.margins.left + "," + e.margins.top + ")"), 
            a.focusOnly || e.obj.append("defs").append("clipPath").attr("id", "clip").append("rect").attr("width", a.width - a.infoAreaRight - (10 + t.chartXOffset)).attr("height", e.height - e.margins.bottom).attr("y", -20).attr("x", e.chartXOffset), 
            e.obj.append("g").attr("class", "x axis").attr("transform", "translate(0,-20)").call(e.xAxis).style("stroke-width", "1"), 
            e.obj.selectAll(".x.axis g text").each(this.insertLinebreaks), e.obj.selectAll(".axis .domain").style({
                "stroke-width": "1",
                fill: "none",
                "shape-rendering": "crispEdges",
                stroke: "black"
            }), e.obj.selectAll(".axis .tick line").style({
                "stroke-width": "1",
                fill: "none",
                "shape-rendering": "crispEdges",
                stroke: "black"
            });
        },
        drawGraph: function() {
            for (var t = (this.context, this.focus), e = this.svg, a = this, r = 0; r < t.graphs.length; r++) {
                var i = t.graphs[r];
                i.offset = r * t.chartHeight + t.chartPadding * (r - 1), t.obj.select("defs").append("clipPath").attr("id", "clip-" + i.label).append("rect").attr("width", e.width - e.infoAreaRight - (10 + t.chartXOffset)).attr("height", t.chartHeight).attr("y", i.offset).attr("x", t.chartXOffset), 
                i.yScale = d3.scale.linear().domain([ i.min, i.max ]).range([ t.chartHeight + i.offset, i.offset ]), 
                i.diffNorm = i.yScale(i.normMin) - i.yScale(i.normMax), t.obj.append("line").attr("x1", t.chartXOffset).attr("x2", e.width - e.infoAreaRight - 11).attr("y1", t.chartHeight + i.offset).attr("y2", t.chartHeight + i.offset).style("stroke", "black").style("opacity", 1).style("stroke-width", 2).attr("class", "line line-" + i.label), 
                "BP" != i.label ? t.obj.append("rect").attr("x", t.chartXOffset).attr("y", i.yScale(i.normMax)).attr("width", e.width - e.infoAreaRight - 16).attr("height", i.diffNorm).style("fill", e.printing ? "#eaeaea" : "#CCCCCC").style("opacity", .75).attr("class", "norm norm-" + i.label).attr("clip-path", "url(#clip-" + i.label + ")") : t.obj.append("line").attr("x1", t.chartXOffset).attr("x2", e.width - e.infoAreaRight - 11).attr("y1", i.yScale(100)).attr("y2", i.yScale(100)).style("stroke", "black").style("opacity", 1).style("stroke-width", 1).attr("class", "line normal-line-" + i.label + " line-" + i.label).attr("clip-path", "url(#clip-" + i.label + ")");
                var n = i.diffNorm - 10;
                n > 0 && (n = 0), i.yAxis = d3.svg.axis().scale(i.yScale).orient("left").ticks(10);
                var s = (t.obj.append("g").call(i.yAxis).style("stroke-width", "1").attr("transform", "translate(" + t.chartXOffset + ",0)").attr("class", "y axis axis-" + i.label), 
                i.yScale.ticks());
                t.obj.selectAll("line.verticalGrid.focus" + i.label).data(t.xScale.ticks()).enter().append("line").attr({
                    "class": "verticalGrid focus" + i.label,
                    x1: function(e) {
                        return t.xScale(e);
                    },
                    x2: function(e) {
                        return t.xScale(e);
                    },
                    y1: i.yScale.range()[0],
                    y2: i.yScale.range()[1],
                    "shape-rendering": "crispEdges",
                    stroke: e.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
                    "stroke-width": "1px"
                }), t.obj.selectAll("line.horizontalGrid.focus" + i.label).data(s).enter().append("line").attr({
                    "class": "horizontalGrid focus" + i.label,
                    x1: t.chartXOffset,
                    x2: e.width - e.infoAreaRight - 11,
                    y1: function(t) {
                        return i.yScale(t);
                    },
                    y2: function(t) {
                        return i.yScale(t);
                    },
                    "shape-rendering": "crispEdges",
                    stroke: e.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
                    "stroke-width": "1px"
                }), "BP" == i.label ? (t.obj.selectAll("." + i.label + "-top-line").data(e.data.filter(function(t) {
                    return t.blood_pressure_systolic ? t : void 0;
                })).enter().append("rect").attr({
                    y: function(t) {
                        return i.yScale(t.blood_pressure_systolic);
                    },
                    x: function(e) {
                        return t.xScale(e.date_started) - t.BPWidth / 2;
                    },
                    height: 2,
                    width: t.BPWidth,
                    "class": i.label + "-top-line",
                    "clip-path": "url(#clip-" + i.label + ")"
                }).style("display", function(t) {
                    return null === t.blood_pressure_systolic ? "none" : null;
                }).on("mouseover", function(t) {
                    return a.contextMouseOver("s:" + t.blood_pressure_systolic + " d:" + t.blood_pressure_diastolic, $(this).position());
                }).on("mouseout", a.contextMouseOut), t.obj.selectAll("." + i.label + "-bottom-line").data(e.data.filter(function(t) {
                    return t.blood_pressure_diastolic ? t : void 0;
                })).enter().append("rect").attr({
                    y: function(t) {
                        return i.yScale(t.blood_pressure_diastolic);
                    },
                    x: function(e) {
                        return t.xScale(e.date_started) - t.BPWidth / 2;
                    },
                    height: 2,
                    width: t.BPWidth,
                    "class": i.label + "-bottom-line",
                    "clip-path": "url(#clip-" + i.label + ")"
                }).style("display", function(t) {
                    return null === t.blood_pressure_diastolic ? "none" : null;
                }).on("mouseover", function(t) {
                    return a.contextMouseOver("s:" + t.blood_pressure_systolic + " d:" + t.blood_pressure_diastolic, $(this).position());
                }).on("mouseout", a.contextMouseOut), t.obj.selectAll("#" + i.label).data(e.data.filter(function(t) {
                    return t.blood_pressure_diastolic_null || t.blood_pressure_systolic_null ? void 0 : t;
                })).enter().append("rect").attr({
                    width: 2,
                    height: function(t) {
                        return i.yScale(t.blood_pressure_diastolic) - i.yScale(t.blood_pressure_systolic);
                    },
                    x: function(e) {
                        return t.xScale(e.date_started) - 1;
                    },
                    y: function(t) {
                        return i.yScale(t.blood_pressure_systolic);
                    },
                    "clip-path": "url(#clip)",
                    "class": "data_lines data-" + i.label
                }).style("display", function(t) {
                    return null === t.blood_pressure_systolic || null === t.blood_pressure_diastolic ? "none" : null;
                }).style({
                    stroke: "rgba(0,0,0,0)",
                    "stroke-width": "3"
                }).on("mouseover", function(t) {
                    return a.contextMouseOver("s:" + t.blood_pressure_systolic + " d:" + t.blood_pressure_diastolic, $(this).position());
                }).on("mouseout", a.contextMouseOut), t.obj.append("text").text(i.label).attr("y", i.yScale(i.normMax) + n).attr("x", e.width - e.infoAreaRight).attr({
                    "font-family": "sans-serif",
                    "font-size": "12px",
                    "font-weight": "bold",
                    fill: "#BBBBBB",
                    "text-anchor": "start",
                    "class": "info infoname-" + i.label
                }), t.obj.append("text").text(function() {
                    return e.data[e.data.length - 1].blood_pressure_systolic ? e.data[e.data.length - 1].blood_pressure_systolic : "";
                }).attr("y", i.yScale(i.normMin) - 20).attr("x", e.width - e.infoAreaRight).attr({
                    "font-family": "sans-serif",
                    "font-size": "12px",
                    "font-weight": "bold",
                    "text-anchor": "start",
                    "class": "info infovalue1-" + i.label
                }), t.obj.append("text").text(function() {
                    return e.data[e.data.length - 1].blood_pressure_diastolic ? e.data[e.data.length - 1].blood_pressure_diastolic : "";
                }).attr("y", i.yScale(i.normMin) - 10).attr("x", e.width - e.infoAreaRight).attr({
                    "font-family": "sans-serif",
                    "font-size": "12px",
                    "font-weight": "bold",
                    "text-anchor": "start",
                    "class": "info infovalue2-" + i.label
                }), t.obj.append("text").text(function() {
                    return i.measurement;
                }).attr("y", i.yScale(i.normMin) - 10).attr("x", e.width - e.infoAreaRight + 2 * e.labelGap).attr({
                    "font-family": "sans-serif",
                    "font-size": "9px",
                    "font-weight": "bold",
                    "text-anchor": "start",
                    "class": "info infovalue3-" + i.label
                })) : (i.area = d3.svg.line().interpolate("linear").defined(function(t) {
                    return t[i.key + "_null"] === !1 ? t : void 0;
                }).x(function(e) {
                    return t.xScale(e.date_started);
                }).y(function(t) {
                    return i.yScale(t[i.key]);
                }), t.obj.append("path").datum(e.data.filter(function(t) {
                    return t[i.key + "_null"] === !1 ? t : void 0;
                })).attr("d", i.area).style({
                    stroke: e.printing ? "#222222" : "#888888",
                    "stroke-width": "1",
                    fill: "none"
                }).attr("class", "focusPath").attr("id", "path-" + i.key).attr("clip-path", "url(#clip)"), 
                t.obj.selectAll("#" + i.label).data(e.data.filter(function(t) {
                    return t[i.key + "_null"] === !1 ? t : void 0;
                })).enter().append("circle").attr("cx", function(e) {
                    return t.xScale(e.date_started);
                }).attr("cy", function(t) {
                    return i.yScale(t[i.key]);
                }).attr("r", 3).attr("class", "data_points data-" + i.label).style("display", function(t) {
                    return t[i.key] ? null : "none";
                }).attr("clip-path", "url(#clip)").attr("data-label", i.key).on("mouseover", function(t) {
                    return a.contextMouseOver(t[$(this).attr("data-label")], $(this).position());
                }).on("mouseout", a.contextMouseOut), t.obj.append("text").text(i.label).attr("y", i.yScale(i.normMax) + n).attr("x", e.width - e.infoAreaRight).attr({
                    "font-family": "sans-serif",
                    "font-size": "12px",
                    "font-weight": "bold",
                    fill: "#BBBBBB",
                    "text-anchor": "start",
                    "class": "info infoname-" + i.label
                }), t.obj.append("text").text(function() {
                    return e.data[e.data.length - 1][i.key] ? e.data[e.data.length - 1][i.key] + i.measurement : "";
                }).attr("y", i.yScale(i.normMin) - n).attr("x", e.width - e.infoAreaRight).attr({
                    "font-family": "sans-serif",
                    "font-size": "12px",
                    "font-weight": "bold",
                    "text-anchor": "start",
                    "class": "info infovalue-" + i.label
                }));
            }
            t.obj.selectAll(".axis path").style({
                "stroke-width": "1",
                fill: "none",
                "shape-rendering": "crispEdges",
                stroke: "black"
            }), t.obj.selectAll(".axis .tick line").style({
                "stroke-width": "1",
                fill: "none",
                "shape-rendering": "crispEdges",
                stroke: "black"
            });
        },
        redrawContext: function() {
            var t = this.context, e = (this.focus, this.svg);
            t.obj.selectAll("rect.scoreRange").attr({
                y: function(e) {
                    return t.yScale(e.e) - 1;
                },
                height: function(e) {
                    return t.yScale(e.s) - (t.yScale(e.e) - 1);
                }
            }), t.obj.selectAll("line.verticalGrid").data(t.xScale.ticks()).enter().append("line").attr({
                "class": "verticalGrid",
                x1: function(e) {
                    return t.xScale(e);
                },
                x2: function(e) {
                    return t.xScale(e);
                },
                y1: 0,
                y2: t.height,
                "shape-rendering": "cripsEdges",
                stroke: e.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
                "stroke-width": "1px"
            }), t.obj.selectAll("line.horizontalGrid").data([ 0, 3, 6, 9, 12, 15, 18 ]).enter().append("line").attr({
                "class": "horizontalGrid",
                x1: t.xScale(t.xScale.domain()[0]),
                x2: t.xScale(t.xScale.domain()[1]),
                y1: function(e) {
                    return t.yScale(e);
                },
                y2: function(e) {
                    return t.yScale(e);
                },
                "shape-rendering": "cripsEdges",
                stroke: e.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
                "stroke-width": "1px"
            }), t.area = d3.svg.line().interpolate("step-after").defined(function(t) {
                return t.complete === !0 ? t : void 0;
            }).x(function(e) {
                return t.xScale(e.date_started);
            }).y(function(e) {
                return t.yScale(e.score);
            }), t.obj.select(".contextPath").attr("d", t.area), t.obj.selectAll("circle.contextPoint").attr("cy", function(e) {
                return t.yScale(e.score);
            }), t.obj.selectAll("circle.emptyContextPoint").attr("cy", function() {
                return t.yScale(t.yScale.domain()[1] / 2);
            }), t.yAxis = d3.svg.axis().scale(t.yScale).orient("left").tickFormat(d3.format("d")), 
            t.obj.select(".y.axis").call(t.yAxis);
        },
        redrawFocusYAxis: function() {
            for (var t = (this.context, this.focus), e = this.svg, a = 0; a < t.graphs.length; a++) {
                var r = t.graphs[a], i = r.yScale(r.normMin) - r.yScale(r.normMax), n = i - 10;
                n > 0 && (n = 0), r.yAxis = "Temp" != r.label ? d3.svg.axis().scale(r.yScale).orient("left").tickFormat(d3.format("d")) : d3.svg.axis().scale(r.yScale).orient("left").ticks(10), 
                t.obj.select(".y.axis-" + r.label).call(r.yAxis), hTicks = r.yScale.ticks(), t.obj.selectAll("line.verticalGrid.focus" + r.label).data(t.xScale.ticks()).enter().append("line").attr({
                    "class": "verticalGrid focus" + r.label,
                    x1: function(e) {
                        return t.xScale(e);
                    },
                    x2: function(e) {
                        return t.xScale(e);
                    },
                    y1: r.yScale.range()[0],
                    y2: r.yScale.range()[1],
                    "shape-rendering": "crispEdges",
                    stroke: e.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
                    "stroke-width": "1px"
                }), t.obj.selectAll("line.horizontalGrid.focus" + r.label).remove(), t.obj.selectAll("line.horizontalGrid.focus" + r.label).data(hTicks).enter().append("line").attr({
                    "class": "horizontalGrid focus" + r.label,
                    x1: t.chartXOffset,
                    x2: e.width - e.infoAreaRight - 11,
                    y1: function(t) {
                        return r.yScale(t);
                    },
                    y2: function(t) {
                        return r.yScale(t);
                    },
                    "shape-rendering": "crispEdges",
                    stroke: e.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
                    "stroke-width": "1px"
                }), "BP" != r.label && t.obj.selectAll("rect.norm-" + r.label).attr("y", r.yScale(r.normMax)).attr("height", i);
            }
            t.obj.selectAll(".axis .tick line").style({
                "stroke-width": "1",
                fill: "none",
                "shape-rendering": "crispEdges",
                stroke: "black"
            }), t.obj.selectAll(".axis path").style({
                "stroke-width": "1",
                fill: "none",
                "shape-rendering": "crispEdges",
                stroke: "black"
            });
        },
        redrawFocus: function(t) {
            var e = (this.context, this.focus), a = this.svg;
            e.obj.selectAll(".data_points").transition().duration(a.transitionDuration).attr("cx", function(t) {
                return e.xScale(t.date_started);
            }), a.transitionDuration = t ? 1e3 : 0;
            for (var r = 0; r < e.graphs.length; r++) {
                var i = e.graphs[r];
                i.area = d3.svg.line().interpolate("linear").x(function(t) {
                    return e.xScale(t.date_started);
                }).y(function(t) {
                    return i.yScale(t[i.key]);
                }), e.obj.selectAll("circle.data-" + i.label).attr("cy", function(t) {
                    return i.yScale(t[i.key]);
                }), e.obj.select("#path-" + i.key).transition().duration(a.transitionDuration).attr("d", i.area), 
                e.obj.selectAll("line.verticalGrid.focus" + i.label).remove().data(e.xScale.ticks()).enter().append("line").attr({
                    "class": "verticalGrid focus" + i.label,
                    x1: function(t) {
                        return e.xScale(t);
                    },
                    x2: function(t) {
                        return e.xScale(t);
                    },
                    y1: i.yScale.range()[0],
                    y2: i.yScale.range()[1],
                    "shape-rendering": "crispEdges",
                    stroke: a.printing ? "#eeeeee" : "rgba(0,0,0,0.1)",
                    "stroke-width": "1px"
                }), "BP" == i.label && (e.obj.selectAll(".data_lines").transition().duration(a.transitionDuration).attr("x", function(t) {
                    return e.xScale(t.date_started);
                }).attr("y", function(t) {
                    return i.yScale(t.blood_pressure_systolic);
                }).attr("height", function(t) {
                    return i.yScale(t.blood_pressure_diastolic) - i.yScale(t.blood_pressure_systolic);
                }), e.obj.selectAll("line.normal-line-BP").attr("y1", i.yScale(100)).attr("y2", i.yScale(100)));
            }
            e.obj.select(".x.axis").call(e.xAxis).style("stroke-width", "1"), e.obj.selectAll(".data_points").transition().duration(a.transitionDuration).attr("cx", function(t) {
                return e.xScale(t.date_started);
            }), e.obj.selectAll("." + i.label + "-top-line").attr({
                y: function(t) {
                    return i.yScale(t.blood_pressure_systolic);
                },
                x: function(t) {
                    return e.xScale(t.date_started) - (e.BPWidth / 2 - 1);
                }
            }), e.obj.selectAll("." + i.label + "-bottom-line").attr({
                y: function(t) {
                    return i.yScale(t.blood_pressure_diastolic);
                },
                x: function(t) {
                    return e.xScale(t.date_started) - (e.BPWidth / 2 - 1);
                }
            }), e.obj.selectAll(".horizontalGrid").transition().duration(a.transitionDuration).attr("x2", e.xScale(e.xScale.domain()[1])), 
            e.obj.selectAll(".x.axis g text").each(this.insertLinebreaks), this.initTable();
        },
        drawTable: function() {
            for (var t = (this.context, this.focus), e = this.svg, a = 0; a < t.tables.length; a++) {
                for (var r = t.tables[a], i = [ r.label ], n = new Date(t.xScale.domain()[0]), s = new Date(t.xScale.domain()[1]), l = 0; l < e.data.length; l++) e.data[l].date_started >= n && e.data[l].date_started <= s && i.push(e.data[l][r.key]);
                var o = d3.select("#chartTable").append("tr").style({
                    "background-color": a % 2 == 0 ? "#ffffff" : "#eeeeee"
                });
                o.selectAll("td." + r.label).data(i).enter().append("td").html(function(t) {
                    return t;
                }).attr("class", r.label).style({
                    padding: "0.3em 0.5%",
                    "text-align": function(t) {
                        return t != r.label ? "center" : void 0;
                    },
                    "border-left": function(t) {
                        return t != r.label ? "1px solid #262626" : void 0;
                    }
                });
            }
        }
    };
    return t;
}();