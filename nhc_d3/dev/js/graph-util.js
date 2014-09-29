insertLinebreaks: function(d) {
    var context = this.context, focus = this.focus, svg = this.svg;
    var el = nhc_d3.select(this);
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
    svg.obj = nhc_d3.select("svg").transition().duration(svg.transitionDuration).attr("width", svg.width);
    context.xScale.range([ svg.margins.left / 4, w - (svg.infoAreaRight + svg.margins.right / 4) ]);
    context.xAxis.scale(context.xScale);
    context.obj.selectAll(".x.axis").call(context.xAxis).style("stroke-width", "1");
    context.area.x(function(d) {
        return context.xScale(d.date_started);
    }).y(function(d) {
        return context.yScale(d.score);
    });
    context.obj.selectAll(".contextPath").transition().duration(svg.transitionDuration).attr("d", context.area);
    context.obj.selectAll(".contextPoint").transition().duration(svg.transitionDuration).attr("cx", function(d) {
        return context.xScale(d.date_started);
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
    nhc_d3.select("#focusChart").select("svg").transition().duration(svg.transitionDuration).attr("width", w + svg.infoAreaRight + svg.margins.right);
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
        nhc_d3.select("#chartTable").selectAll("tr").remove();
        var startDate = new Date(focus.xScale.domain()[0]);
        var endDate = new Date(focus.xScale.domain()[1]);
        for (var i = 0; i < svg.data.length; i++) {
            if (svg.data[i].date_started >= startDate && svg.data[i].date_started <= endDate) {
                headerData.push(svg.data[i].date_started);
            }
        }
        dataTableTr = nhc_d3.select("#chartTable").append("tr");
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
