/**
 * Created by colin on 10/02/14.
 */

// one mousing over a data point move popup to that location (with margins) and make visible. Takes string as arguement (no linebreaks)
function contextMouseOver(text){

    var popupMargins = { top: 0, left: 3, right: 0, bottom: 40};
    svg.popup.style("left", (d3.event.pageX + popupMargins.left) + "px")
        .style("top", (d3.event.pageY - popupMargins.bottom) + "px")
        .text(text);
    svg.popup.transition().duration(500).style("opacity", 1);
}

// hides the popup on mousing out
function contextMouseOut(el){
    svg.popup.transition().duration(500).style("opacity", 1e-6);
}

// function to handle the changing of the date inputs on mobile
function contextChange(){
    // check to see if all inputs are valid
    if($("#contextStartT").val() != "" && $("#contextEndD").val() != "" && $("#contextEndT").val() != "" && $("#contextStartD").val() != ""){
        svg.datesChanged = true;

        // grab values from inputs
        var cST = $("#contextStartT").val();
        var cSD = $("#contextStartD").val();
        var cET = $("#contextEndT").val();
        var cED = $("#contextEndD").val();

        // create date strings by combining the date and time inputs
        var cS = cSD+"T"+cST;
        var cE = cED+"T"+cET;

        // turn these into dates
        var newStart = new Date(cS);
        var newEnd = new Date(cE);

        // setup the focus x scale to use these dates as it's domain
        focus.xScale.domain([newStart, newEnd]);

        // update the axis
        focus.obj.select(".x.axis").call(focus.xAxis);

        // redraw the datapoints  - replace with function to redraw
        redrawFocus(false);
        initTable();
        focus.obj.selectAll(".x.axis g text").each(insertLinebreaks);
       // $("#focusTitle").html("Individual values for " + stdT + " - " + enT);
    }
}


// function to handle brushing
function brushed() {
    focus.xScale.domain(context.brush.empty() ? context.xScale.domain() : context.brush.extent()); // set the focus x scale domain to either the extent of the brush or the domain of context

    // Update the focus title to display the extent if there is one
    if(!context.brush.empty()){
        var stD = context.brush.extent()[0];
        var enD = context.brush.extent()[1];
        var stdT = ("0" + stD.getHours()).slice(-2) + ":" + ("0" + stD.getMinutes()).slice(-2) + " " + ("0" + stD.getDate()).slice(-2) + "/" + ("0" + stD.getMonth()).slice(-2);
        var enT = ("0" + enD.getHours()).slice(-2) + ":" + ("0" + enD.getMinutes()).slice(-2) + " " + ("0" + enD.getDate()).slice(-2) + "/" + ("0" + enD.getMonth()).slice(-2);
        $("#focusTitle").html("Individual values for " + stdT + " - " + enT);
    }else{
        $("#focusTitle").html("Individual values");
    }

    redrawFocus(false);
}