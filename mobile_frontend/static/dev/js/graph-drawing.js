/**
 * Created by colin on 10/02/14.
 */

/*
    GRAPHS
 */
// function that draws the charts (not the data)
function drawChart(){
    // setup context itself
    context.obj = svg.obj.context.append("g").attr("transform", "translate(" + svg.margins.left + "," + context.margins.top + ")");
    //var tickMod = calcTicks(svg.width, context.earliestDate, context.now);
    // add the score range rectangles
    context.obj.selectAll("rect.scoreRange")
        .data(context.scoreRange)
        .enter()
        .append("rect")
        .attr({
            "class": function(d) { return d.class; },
            "x": context.xScale(context.xScale.domain()[0]),
            "y": function(d){ return context.yScale(d.e) -1},
            "width": svg.width - (svg.infoAreaRight + (svg.margins.right/3)),
            "height": function(d){ return context.yScale(d.s) - (context.yScale(d.e) -1); }
        });

    // add the vertical grid to context
    context.obj.selectAll("line.verticalGrid")
        .data(context.xScale.ticks())
        .enter()
        .append("line")
        .attr({
            "class":"verticalGrid",
            "x1" : function(d){ return context.xScale(d);},
            "x2" : function(d){ return context.xScale(d);},
            "y1" : 0,
            "y2" : context.height,
            "shape-rendering": "cripsEdges",
            "stroke" : "rgba(0,0,0,0.1)",
            "stroke-width": "1px"
        });

    // add the horizontal grid
    context.obj.selectAll("line.horizontalGrid")
        .data([0,3,6,9,12,15,18])
        .enter()
        .append("line")
        .attr({
            "class":"horizontalGrid",
            "x1" : context.xScale(context.xScale.domain()[0]),
            "x2" : context.xScale(context.xScale.domain()[1]),
            "y1" : function(d) { return context.yScale(d)},
            "y2" : function(d) { return context.yScale(d)},
            "shape-rendering": "cripsEdges",
            "stroke" : "rgba(0,0,0,0.1)",
            "stroke-width": "1px"
        });

    // add the x axis
    context.obj.append("g")
        .attr("class", "x axis")
        .call(context.xAxis);

    // add the y axis
    context.obj.append("g").attr({"class": "y axis", "transform": "translate(5,0)"}).call(context.yAxis);

    // only want brushing if on a desktop
    if(!svg.isMob) {
        //setup context brush
        context.brush = d3.svg.brush()
            .x(context.xScale)
            .on("brush", brushed);

        // add it to context
        context.obj.append("g")
            .attr("class", "x brush")
            .call(context.brush)
            .selectAll("rect")
            .attr("y", -6)
            .attr("height", context.height + 7)
            .style({"fill": "#333", "opacity": "0.5"});
    }

    // create line for context values
    context.area = d3.svg.line()
        .interpolate("step-after")
        .defined(function(d){ if(d.obs.score > -1){ return d; }})
        .x(function(d) { return context.xScale(d.obsStart); })
        .y(function(d) { return context.yScale(d.obs.score);});

    // add area to context
    context.obj.append("path")
        .datum(svg.data)
        .attr("d", context.area)
        .style({"stroke":"#555555", "stroke-width": "1", "fill":"none"})
        .attr("class", "contextPath");


    // add circles to represent values and also so can be selected
    context.obj.selectAll("circle.contextPoint").data(svg.data.filter(function(d){ if(d.obs.score > -1){ return d; }}))
        .enter()
        .append("circle")
        .attr("cx", function (d) {
            return context.xScale(d.obsStart)
        })
        .attr("cy", function(d){ return context.yScale(d.obs.score); })
        .attr("r", 3)
        .attr("class", "contextPoint")
        .on("mouseover", function(d){ return contextMouseOver(d.obs.score);})
        .on("mouseout", contextMouseOut);

    context.obj.selectAll("circle.emptyContextPoint").data(svg.data.filter(function(d){ console.log(typeof(d.obs.score)); if(d.obs.score == undefined){ return d; }}))
        .enter()
        .append("circle")
        .attr("cx", function (d) {
            return context.xScale(d.obsStart)
        })
        .attr("cy", function(d){ return context.yScale(context.yScale.domain()[1] / 2); })
        .attr("r", 3)
        .attr("class", "emptyContextPoint")
        .on("mouseover", function(d){ return contextMouseOver("Partial observation");})
        .on("mouseout", contextMouseOut);


    // add popup so selection works
    svg.popup = d3.select("body").append("div").attr("class", "contextPopup").style("opacity", 1e-6);

    // make the x axis text look good
    context.obj.selectAll(".x.axis g text").each(insertLinebreaks);

    // add focus itself
    focus.obj = svg.obj.focus.append("g").attr("transform", "translate(" + svg.margins.left + "," + focus.margins.top + ")");

    // add a clipping path so can brush / extent change properly
    focus.obj.append("defs").append("clipPath")
        .attr("id", "clip")
        .append("rect")
        .attr("width", svg.width - svg.infoAreaRight)
        .attr("height", (focus.height - focus.margins.bottom))
        .attr("y", -20);

    // add the x axis
    focus.obj.append("g").attr("class", "x axis").attr("transform", "translate(0,-20)").call(focus.xAxis);

    // make the x axis text look good
    focus.obj.selectAll(".x.axis g text").each(insertLinebreaks);

}

// draw the data points on the graph takes: graph height, graph offset (basically calculate how many charts there's been), max and min of data, max and min of normals, key used in JSON, name to use in class and units of measurement
function drawGraph() {
    // interate through all the graphs
    for(var i = 0; i < focus.graphs.length; i++){
        // setup an object for easy access to variables
        var thisEntry = focus.graphs[i];

        // figure out the offset
        thisEntry.offset = ((i * focus.chartHeight) + (focus.chartPadding * (i -1)));

        // setup the y scale
        thisEntry.yScale = d3.scale.linear().domain([thisEntry.min, thisEntry.max]).range([focus.chartHeight + thisEntry.offset, thisEntry.offset]);

        // figure out the difference in the normals
        thisEntry.diffNorm = thisEntry.yScale(thisEntry.normMin) - thisEntry.yScale(thisEntry.normMax);

        // draw a black line across the bottom of the graph
        focus.obj.append("line").attr("x1", 5).attr("x2", ((svg.width - svg.infoAreaRight) -11)).attr("y1", focus.chartHeight + thisEntry.offset).attr("y2", focus.chartHeight + thisEntry.offset).style("stroke", "black").style("opacity", 1).style("stroke-width", 2).attr("class", "line line-" + thisEntry.label);

        // draw a light gray rect to show the normal range
        if(thisEntry.label != "BP"){
            focus.obj.append("rect").attr("x", 5).attr("y", thisEntry.yScale(thisEntry.normMax)).attr("width",  ((svg.width - svg.infoAreaRight) -16)).attr("height", thisEntry.diffNorm).style("fill", "#CCCCCC").style("opacity", .75).attr("class", "norm norm-" + thisEntry.label);
        }else{
            focus.obj.append("line").attr("x1", 5).attr("x2", ((svg.width - svg.infoAreaRight) -11)).attr("y1", thisEntry.yScale(100)).attr("y2", thisEntry.yScale(100)).style("stroke", "black").style("opacity", 1).style("stroke-width", 1).attr("class", "line line-" + thisEntry.label);
        }

        // add text to show the normal min and max values
        focus.obj.append("text").text(thisEntry.normMin).attr("x", - 5).attr("y", thisEntry.yScale(thisEntry.normMin)).attr("font-family", "sans-serif").attr("font-size", "10px").attr("font-weight", "normal").attr("text-anchor", "middle").attr("dominant-baseline", "hanging");
        focus.obj.append("text").text(thisEntry.normMax).attr("x", - 5).attr("y", thisEntry.yScale(thisEntry.normMax)).attr("font-family", "sans-serif").attr("font-size", "10px").attr("font-weight", "normal").attr("text-anchor", "middle");

        // calculate value to get text to line up with data point
        var shift = thisEntry.diffNorm - 10;
        if (shift > 0) shift = 0;

        // draw horizontal grid
        var hTicks = d3.svg.axis().scale(thisEntry.yScale).orient("left").ticks(10);
        var ti = focus.obj.append("g").call(hTicks);
        hTicks = thisEntry.yScale.ticks();
        ti.remove();

        // add the vertical grid
       // var tickMod = calcTicks(svg.width, context.earliestDate, context.now);
        focus.obj.selectAll("line.verticalGrid.focus"+thisEntry.label)
            .data(focus.xScale.ticks())
            .enter()
            .append("line")
            .attr({
                "class":"verticalGrid focus" + thisEntry.label,
                "x1" : function(d){ return focus.xScale(d);},
                "x2" : function(d){ return focus.xScale(d);},
                "y1" : thisEntry.yScale.range()[0],
                "y2" : thisEntry.yScale.range()[1],
                "shape-rendering": "crispEdges",
                "stroke" : "rgba(0,0,0,0.1)",
                "stroke-width": "1px"
            });


        focus.obj.selectAll("line.horizontalGrid.focus"+thisEntry.label)
            .data(hTicks)
            .enter()
            .append("line")
            .attr({
                "class":"horizontalGrid focus" + thisEntry.label,
                "x1" : 5,
                "x2" : ((svg.width - svg.infoAreaRight) - 11),
                "y1" : function(d) { return thisEntry.yScale(d)},
                "y2" : function(d) { return thisEntry.yScale(d)},
                "shape-rendering": "crispEdges",
                "stroke" : "rgba(0,0,0,0.1)",
                "stroke-width": "1px"
            });

        // plot points
        if (thisEntry.label == "BP") {

            // if BP data points then add up arrows
            focus.obj.selectAll("." + thisEntry.label + "up-arrows")
                .data(svg.data.filter(function(d){ if(d.obs.blood_pressure_systolic){ return d; }}))
                .enter()
                .append("path")
                .attr({
                    "d": d3.svg.symbol().size(function(d){ return 45; }).type(function(d){ return 'triangle-up'}),
                    "transform": function(d){ return "translate(" + context.xScale(d.obsStart) +  "," + (thisEntry.yScale(d.obs.blood_pressure_systolic) + 3) + ")"; },
                    "class": "data_symbols " + thisEntry.label + "up-arrows"
                })
                .style("display", function(d){
                    if(d.obs["blood_pressure_systolic"] === null){
                        return "none";
                    }else{
                        return null;
                    }
                })
                .on("mouseover", function(d){ return contextMouseOver("s:" + d.obs["blood_pressure_systolic"] + " d:" + d.obs["blood_pressure_diastolic"]);})
                .on("mouseout", contextMouseOut);

            // if BP data points then add up arrows
            focus.obj.selectAll("." + thisEntry.label + "down-arrows")
                .data(svg.data.filter(function(d){ if(d.obs.blood_pressure_diastolic){ return d; }}))
                .enter()
                .append("path")
                .attr({
                    "d": d3.svg.symbol().size(function(d){ return 45; }).type(function(d){ return 'triangle-down'}),
                    "transform": function(d){ return "translate(" + context.xScale(d.obsStart) +  "," + (thisEntry.yScale(d.obs.blood_pressure_diastolic) - 3) + ")"; },
                    "class": "data_symbols " + thisEntry.label + "down-arrows"
                })
                .style("display", function(d){
                    if(d.obs["blood_pressure_diastolic"] === null){
                        return "none";
                    }else{
                        return null;
                    }
                })
                .on("mouseover", function(d){ return contextMouseOver("s:" + d.obs["blood_pressure_systolic"] + " d:" + d.obs["blood_pressure_diastolic"]);})
                .on("mouseout", contextMouseOut);

            // if BP data points then select / create the BP graph, use the data to append a line at the date the observation was taken that goes from systolic to diastolic on the y axis
            focus.obj.selectAll("#" + thisEntry.label)
                .data(svg.data.filter(function(d){ if(d.obs.blood_pressure_diastolic && d.obs.blood_pressure_systolic){ return d; }}))
                .enter()
                .append("rect")
                .attr({
                    "width": 2,
                    "height": function(d) { return thisEntry.yScale(d.obs["blood_pressure_diastolic"]) - thisEntry.yScale(d.obs["blood_pressure_systolic"]);},
                    "x": function(d){ return focus.xScale(d.obsStart) - 1;},
                    "y": function(d){ return thisEntry.yScale(d.obs["blood_pressure_systolic"]);},
                    "clip-path": "url(#clip)",
                    "class": "data_lines data-" + thisEntry.label
                })
                .style("display", function(d){
                    if(d.obs["blood_pressure_systolic"] === null || d.obs["blood_pressure_diastolic"] === null){
                        return "none";
                    }else{
                        return null;
                    }
                })
                .style({"stroke":"rgba(0,0,0,0)", "stroke-width": "3"})
                .on("mouseover", function(d){ return contextMouseOver("s:" + d.obs["blood_pressure_systolic"] + " d:" + d.obs["blood_pressure_diastolic"]);})
                .on("mouseout", contextMouseOut);

            // append the name to the label area in line with the top of the normal rect
            focus.obj.append("text")
                .text(thisEntry.label)
                .attr("y", thisEntry.yScale(thisEntry.normMax) + shift)
                .attr("x", svg.width - svg.infoAreaRight)
                .attr({"font-family": "sans-serif", "font-size": "12px", "font-weight": "bold", "fill": "#BBBBBB", "text-anchor": "start", "class": "info infoname-" + thisEntry.label});

            // append the latest systolic value to just above the normal min
            focus.obj.append("text").text(function () {
                if(svg.data[svg.data.length -1]["obs"]["blood_pressure_systolic"]){
                    return svg.data[svg.data.length - 1]["obs"]["blood_pressure_systolic"]
                }else{
                    return "";
                }})
                .attr("y", thisEntry.yScale(thisEntry.normMin) - 20)
                .attr("x", svg.width - svg.infoAreaRight)
                .attr({"font-family": "sans-serif","font-size": "12px","font-weight": "bold", "text-anchor": "start", "class": "info infovalue1-" + thisEntry.label});

            // append the latest diastolic value below the systolic one
            focus.obj.append("text").text(function () {
                if(svg.data[svg.data.length -1]["obs"]["blood_pressure_diastolic"]){
                    return svg.data[svg.data.length - 1]["obs"]["blood_pressure_diastolic"]
                }else{
                    return "";
                }})
                .attr("y", thisEntry.yScale(thisEntry.normMin) - 10)
                .attr("x", svg.width - svg.infoAreaRight)
                .attr({"font-family": "sans-serif","font-size": "12px","font-weight": "bold","text-anchor": "start","class": "info infovalue2-" + thisEntry.label});

            // append the units measurement next to the systolic value
            focus.obj.append("text").text(function () { return thisEntry.measurement })
                .attr("y", thisEntry.yScale(thisEntry.normMin) - 10)
                .attr("x", svg.width - svg.infoAreaRight + (svg.labelGap*2))
                .attr({"font-family": "sans-serif", "font-size": "9px", "font-weight": "bold", "text-anchor": "start", "class": "info infovalue3-" + thisEntry.label});
        } else {
            // if not BP then select / create a chart with the name and add a circle for that data point
            thisEntry.area = d3.svg.line()
                .interpolate("linear")
                .defined(function(d){ if(d.obs[thisEntry.key]){ return d; }})
                .x(function(d) { return focus.xScale(d.obsStart); })
                .y(function(d) { return thisEntry.yScale(d.obs[thisEntry.key]); });

            // add area to context
            focus.obj.append("path")
                .datum(svg.data.filter(function(d){ if(d.obs[thisEntry.key]){ return d; }}))
                .attr("d", thisEntry.area)
                .style({"stroke":"#888888", "stroke-width": "1", "fill":"none"})
                .attr("class", "focusPath")
                .attr("id", "path-" + thisEntry.key)
                .attr("clip-path", "url(#clip)");

            focus.obj.selectAll("#" + thisEntry.label)
                .data(svg.data.filter(function(d){ if(d.obs[thisEntry.key]){ return d; }}))
                .enter()
                .append("circle")
                .attr("cx", function (d) {
                    return focus.xScale(d.obsStart)
                }).attr("cy", function (d) {
                    return thisEntry.yScale(d.obs[thisEntry.key]);
                }).attr("r", 3)
                .attr("class", "data_points data-" + thisEntry.label)
                .style("display", function(d){ if(d.obs[thisEntry.key]){ return null; }else{ return "none"; }})
                .attr("clip-path", "url(#clip)")
                .on("mouseover", function(d){  return contextMouseOver(d.obs[thisEntry.label]);})
                .on("mouseout", contextMouseOut);

            // append the name of the dataset
            focus.obj.append("text")
                .text(thisEntry.label)
                .attr("y", thisEntry.yScale(thisEntry.normMax) + shift)
                .attr("x", svg.width - svg.infoAreaRight)
                .attr({"font-family": "sans-serif", "font-size": "12px", "font-weight": "bold", "fill": "#BBBBBB", "text-anchor": "start", "class": "info infoname-" + thisEntry.label});

            // append the latest value and the unit of measure
            focus.obj.append("text")
                .text(function () {
                    if(svg.data[svg.data.length-1]["obs"][thisEntry.key]){
                        return svg.data[svg.data.length - 1]["obs"][thisEntry.key] + thisEntry.measurement ;
                    }else{
                        return "";
                    }})
                .attr("y", thisEntry.yScale(thisEntry.normMin) - shift)
                .attr("x", svg.width - svg.infoAreaRight)
                .attr({"font-family": "sans-serif", "font-size": "12px", "font-weight": "bold", "text-anchor": "start", "class": "info infovalue-" + thisEntry.label});
        }
    }
}

function drawTabularObs(el){
    //var container = d3.select(el).append('div');
    var container = d3.select('#table-content').append('div').attr('style', 'padding-top: 1em');
    var cards = container.selectAll('.card').data(svg.data.reverse()).enter().append('div').attr('class','card');
    var header = cards.append('h3').text(function(d){
        return ("0" + d.obsStart.getHours()).slice(-2) + ":" + ("0" + d.obsStart.getMinutes()).slice(-2) + " " + ("0" + d.obsStart.getDate()).slice(-2) + "/" + ("0" + (d.obsStart.getMonth() + 1)).slice(-2) + "/" + d.obsStart.getFullYear(); });
    var list = cards.append('table');
    var list_items = list.selectAll('tr').data(function(d){ return $.map(d.obs, function(v,k){ if(k !== "indirect_oxymetry_spo2_label"){return {key: process_obs_name(k), value: v};} }); }).enter();
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
}

function redrawFocus(transition){
    // redraw the focus graph based on the new domain
    focus.obj.selectAll(".data_points").transition().duration(svg.transitionDuration).attr("cx", function(d){return focus.xScale(d.obsStart);});

    if(transition){
        svg.transitionDuration = 1000;
    }else{
        svg.transitionDuration = 0;
    }
     for(var i = 0; i < focus.graphs.length; i++){
        var thisEntry = focus.graphs[i];
        thisEntry.area = d3.svg.line().interpolate("linear").x(function(d){  return focus.xScale(d.obsStart); }).y(function(d){ return thisEntry.yScale(d.obs[thisEntry.key]); });
        focus.obj.select("#path-"+ thisEntry.key).transition().duration(svg.transitionDuration).attr("d", thisEntry.area);

         //var tickMod = calcTicks(svg.width, focus.xScale.domain()[0], focus.xScale.domain()[1]);

         focus.obj.selectAll("line.verticalGrid.focus"+thisEntry.label)
             .remove()
             .data(focus.xScale.ticks())
             .enter()
             .append("line")
             .attr({
                 "class":"verticalGrid focus" + thisEntry.label,
                 "x1" : function(d){ return focus.xScale(d);},
                 "x2" : function(d){ return focus.xScale(d);},
                 "y1" : thisEntry.yScale.range()[0],
                 "y2" : thisEntry.yScale.range()[1],
                 "shape-rendering": "crispEdges",
                 "stroke" : "rgba(0,0,0,0.1)",
                 "stroke-width": "1px"
             });

     }

    // replace this with draw function
    focus.obj.select(".x.axis").call(focus.xAxis);
    focus.obj.selectAll(".data_points").transition().duration(svg.transitionDuration).attr("cx", function(d){return focus.xScale(d.obsStart);});
    focus.obj.selectAll(".data_symbols").remove();
    // if BP data points then add up arrows
    focus.obj.selectAll(".BPup-arrows")
        .data(svg.data.filter(function(d){ if(d.obs.blood_pressure_systolic && d.obsStart >= focus.xScale.domain()[0] && d.obsStart <= focus.xScale.domain()[1]){ console.log(d); return d; }}))
        .enter()
        .append("path")
        .attr({
            "d": d3.svg.symbol().size(function(d){ console.log("calling size"); return 45; }).type(function(d){ console.log("calling type"); return 'triangle-up';}),
            "transform": function(d){ console.log("calling transform"); return "translate(" + (focus.xScale(d.obsStart) + 1) +  "," + (focus.graphs[focus.graphs.length -1].yScale(d.obs.blood_pressure_systolic) + 3) + ")"; },
            "class": "data_symbols BPup-arrows"
        })
        .style("display", function(d){
            if(d.obs["blood_pressure_systolic"] === null){
                return "none";
            }else{
                return null;
            }
        })
        .on("mouseover", function(d){ return contextMouseOver("s:" + d.obs["blood_pressure_systolic"] + " d:" + d.obs["blood_pressure_diastolic"]);})
        .on("mouseout", contextMouseOut);

    // if BP data points then add up arrows
    focus.obj.selectAll(".BPdown-arrows")
        .data(svg.data.filter(function(d){ if(d.obs.blood_pressure_diastolic && d.obsStart >= focus.xScale.domain()[0] && d.obsStart <= focus.xScale.domain()[1]){ return d; }}))
        .enter()
        .append("path")
        .attr({
            "d": d3.svg.symbol().size(function(d){ return 45; }).type(function(d){ return 'triangle-down'}),
            "transform": function(d){ return "translate(" + (focus.xScale(d.obsStart) + 1) +  "," + (focus.graphs[focus.graphs.length -1].yScale(d.obs.blood_pressure_diastolic) - 3) + ")"; },
            "class": "data_symbols BPdown-arrows"
        })
        .style("display", function(d){
            if(d.obs["blood_pressure_diastolic"] === null){
                return "none";
            }else{
                return null;
            }
        })
        .on("mouseover", function(d){ return contextMouseOver("s:" + d.obs["blood_pressure_systolic"] + " d:" + d.obs["blood_pressure_diastolic"]);})
        .on("mouseout", contextMouseOut);

    focus.obj.selectAll(".data_lines").transition().duration(svg.transitionDuration).attr("x", function(d){ return focus.xScale(d.obsStart) });


    //update the ticks for the focus x scale
    //var tmod = calcTicks($("#focusChart svg").width() - (svg.infoAreaRight + (svg.margins.right/3)), focus.xScale.domain()[0], focus.xScale.domain()[1]);
    //focus.xAxis.ticks(svg.ticks);
    focus.obj.select(".x.axis").call(focus.xAxis);

    focus.obj.selectAll(".horizontalGrid").transition().duration(svg.transitionDuration).attr("x2", focus.xScale(focus.xScale.domain()[1]));


    // redraw the unplottable values table
    initTable();
    //drawTable();

    // insert line breaks into the axis text
    focus.obj.selectAll(".x.axis g text").each(insertLinebreaks);
}

function resizeGraphs() {
    // select the element that the graph is in
    var win = $(svg.el);

    // use the width and height to determine orientation. If width is larger than height it's landscape
    var ori = win.width() > win.height() ? "landscape" : "portrait";
    // set up the w variable to reflect the new width
    w = win.width() - svg.margins.left - svg.margins.right;

    svg.width =  w + svg.margins.left + svg.margins.right;

    // change the svg element's size attributes to reflect this
    svg.obj = d3.select("svg").transition().duration(svg.transitionDuration).attr("width", svg.width);//.attr("height", svg.height + svg.margins.bottom);

    // update the context with new width
    context.xScale.range([(svg.margins.left/4), w - (svg.infoAreaRight + (svg.margins.right/4))]);
    context.xAxis.scale(context.xScale);
    context.obj.selectAll(".x.axis").call(context.xAxis)
    //var tMod = calcTicks(w - (svg.infoAreaRight + (svg.margins.right/3)), context.xScale.domain()[0], context.xScale.domain()[1]);
    //context.xAxis.ticks(svg.ticks);

    context.area.x(function(d) { return context.xScale(d.obsStart); }).y(function(d) { return context.yScale(d.obs.score);});
    context.obj.selectAll(".contextPath").transition().duration(svg.transitionDuration).attr("d", context.area);

    context.obj.selectAll(".contextPoint").transition().duration(svg.transitionDuration).attr("cx", function(d){ return context.xScale(d.obsStart); });
    context.obj.selectAll(".x.axis g text").each(insertLinebreaks);
    context.obj.selectAll(".horizontalGrid").transition().duration(svg.transitionDuration).attr("x2", (w - svg.infoAreaRight) -10);
    context.obj.selectAll(".green").transition().duration(svg.transitionDuration).attr("width", w - (svg.infoAreaRight + (svg.margins.right/3)));
    context.obj.selectAll(".amber").transition().duration(svg.transitionDuration).attr("width", w - (svg.infoAreaRight + (svg.margins.right/3)));
    context.obj.selectAll(".red").transition().duration(svg.transitionDuration).attr("width", w - (svg.infoAreaRight + (svg.margins.right/3)));
    // add the vertical grid to context

    //var tickMod = calcTicks(svg.width, context.earliestDate, context.now);

    context.obj.selectAll(".verticalGrid").remove()
        .data(context.xScale.ticks())
        .enter()
        .append("line")
        .attr({
            "class":"verticalGrid",
            "x1" : function(d){ return context.xScale(d);},
            "x2" : function(d){ return context.xScale(d);},
            "y1" : 0,
            "y2" : context.height,
            "shape-rendering": "crispEdges",
            "stroke" : "rgba(0,0,0,0.1)",
            "stroke-width": "1px"
        });
    // adjust the brush
    if(!svg.isMob){
        context.brush.x(context.xScale);
       /* console.log(context.brush.extent()[0]);
        context.obj.select(".x.brush").select("rect.extent").attr("x", context.xScale(context.brush.extent()[0]));
        context.obj.select(".x.brush").select("rect.background").attr("width",  w - (svg.infoAreaRight + (svg.margins.right/3)));  */
    }

    focus.obj.select("#clip").transition().duration(svg.transitionDuration).attr("width", w - (svg.infoAreaRight + (svg.margins.right/4)));
    focus.obj.select("#clip").transition().duration(svg.transitionDuration).select("rect").attr("width", w - (svg.infoAreaRight + (svg.margins.right/4)));
    focus.xScale.range([(svg.margins.left/4), w - (svg.infoAreaRight + (svg.margins.right/4))]);
    focus.xAxis.scale(focus.xScale);
    d3.select("#focusChart").select("svg").transition().duration(svg.transitionDuration).attr("width",  w + svg.infoAreaRight + svg.margins.right);
    // change the second x value of any lines
    focus.obj.selectAll(".line").transition().duration(svg.transitionDuration).attr("x2", w - (svg.infoAreaRight + (svg.margins.right/4)));

    // change the width of any rects (that show normal values)
    focus.obj.selectAll(".norm").transition().duration(svg.transitionDuration).attr("width", w - (svg.infoAreaRight + (svg.margins.right/3)));

    focus.obj.selectAll(".info").transition().duration(svg.transitionDuration).attr("x",w - (svg.infoAreaRight + (svg.margins.right/4)) + svg.labelGap);

    focus.obj.selectAll(".infovalue3-BP").transition().duration(svg.transitionDuration).attr("x",w - (svg.infoAreaRight + (svg.margins.right/4)) + (svg.labelGap*3));

    redrawFocus(false);
}




/*
    TABLES
 */

// function to create a table object with columns for each time inside of the extent
function initTable(){
    // setup the array to hold headers
    var headerData = ["Type"];

    // remove all existing <tr> from the table
    d3.select("#chartTable").selectAll("tr").remove();

    var startDate = new Date(focus.xScale.domain()[0]);
    var endDate = new Date(focus.xScale.domain()[1]);

    // go through the data to table and add the dates that are inclusive to the headerData array
    for(var i =0; i < svg.data.length; i++){
        if(svg.data[i].obsStart >= startDate && svg.data[i].obsStart <= endDate){
            headerData.push(svg.data[i].obsStart);
        }
    }

    // create a tr just for headers
    dataTableTr = d3.select("#chartTable").append("tr");

    // Select all <th> (there should be none) and add a <th> for each time in headerData array make the width of the object adapt to the space
    dataTableTr.selectAll("th")
        .data(headerData)
        .enter()
        .append("th")
        .html(function(d) {
            if(d == "Type"){
                return d;
            }else{
                return ("0" + (d.getDate())).slice(-2) +  "/" + ("0" + (d.getMonth()+1)).slice(-2) + "<br>" + ("0" + (d.getHours())).slice(-2) + ":" + ("0" + (d.getMinutes())).slice(-2);
            } })
        .style("width", (90 / headerData.length)+"%");

    drawTable();
}

// function to draw each row of data
function drawTable(){
    // array to hold the data
    for(var i = 0; i < focus.tables.length; i++){
        var thisEntry = focus.tables[i];
        var tableData = [thisEntry.label];

        // set up the extent dates
        var startDate = new Date(focus.xScale.domain()[0]);
        var endDate = new Date(focus.xScale.domain()[1]);

        // go through the data and for the data inside of the extent add it to the array
        for(var j=0; j < svg.data.length; j++){
            if(svg.data[j].obsStart >= startDate && svg.data[j].obsStart <= endDate){
                tableData.push(svg.data[j]["obs"][thisEntry.key]);
            }
        }

        // add a row for the data
        var tableTR = d3.select("#chartTable").append("tr");

        // for each entry add a column with that value
        tableTR.selectAll("td."+thisEntry.label)
            .data(tableData)
            .enter()
            .append("td")
            .html(function(d) { return d; })
            .attr("class", thisEntry.label);
    }
}