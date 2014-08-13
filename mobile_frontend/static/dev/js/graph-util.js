/**
 * Created by colin on 07/02/14.
 */

// a function to take work out what time scale and tick spacing to use
//function calcTicks(width, contextEarliest, contextLatest){
//    var axisWidth = width; // width of the axis
//    var tickWidth = 80; // width of an individual tick including padding
//    var optTicks = Math.floor(axisWidth / tickWidth); // simple division to see how many ticks can safely fit in axis at given width
//    var dateDiff = contextLatest - contextEarliest; // see the difference in the dates
//    var dateDiffSecs = Math.floor(dateDiff/1000); // calc seconds
//    var dateDiffMins = Math.floor((dateDiff/1000)/60); // minutes
//    var dateDiffHours = Math.floor((((dateDiff/1000)/60)/60)); // hours
//    var dateDiffDays = Math.floor(((((dateDiff/1000)/60)/60)/60)/24); // calc days
//    if(dateDiffHours <= optTicks){
//        if(dateDiffHours <= 2){
//            if(dateDiffMins <= 10){
//                if(dateDiffMins <= 1){
//                    if(dateDiffSecs <= 10){
//                        var tickMod = 10;
//                        return [d3.time.seconds, tickMod];
//                    }
//                    var tickMod = 10;
//                    return [d3.time.minutes, tickMod];
//                }
//                var tickMod = 1;
//                return [d3.time.minutes, tickMod];
//            }
//            var tickMod = Math.floor(dateDiffMins / optTicks);
//            tickMod = tickMod - (tickMod % 2);
//            if(tickMod <2){
//                tickMod = 2;
//            }else if(tickMod == 8){
//                tickMod = 6;
//            }
//            return [d3.time.minutes, tickMod];
//        }else{
//            var tickMod = Math.floor(dateDiffHours / optTicks);
//            tickMod = tickMod - (tickMod % 2);
//            if(tickMod <2){
//                tickMod = 2;
//            }
//            return [d3.time.hours, tickMod];
//        }
//    }else{
//        if(dateDiffDays <= 1){
//            var tickMod = Math.floor(dateDiffHours / optTicks);
//            tickMod = tickMod - (tickMod % 2);
//            if(tickMod <2){
//                tickMod = 2;
//            }
//            return [d3.time.hours, tickMod];
//        }else{
//            var tickMod = Math.floor(dateDiffDays / optTicks);
//            console.log(dateDiffDays);
//            console.log(optTicks);
//            console.log(tickMod);
//
//            tickMod = tickMod - (tickMod % 2);
//            console.log(tickMod);
//            if(tickMod <2){
//                tickMod = 2;
//            }
//            return [d3.time.days, tickMod];
//        }
//
//    }
//}

// is called on the selection of text nodes in an axis and will reformat the text to a three line day \n month \n time format using tspan
function insertLinebreaks(d) {
    var el = d3.select(this);
    var textHeight = 10;
    var days = ["Sun", "Mon", "Tues", "Wed", "Thu", "Fri", "Sat"]; // days of the week so can get out as a string
    var dateString = days[d.getDay()] + " " + d.getDate() + "/" + ("0" + (d.getMonth() +1)).slice(-2) + " " + ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2); // format for the string, a space between values will result in a line break
    var words = dateString.split(' '); // create an array using the dateString format that will be used to create linebreaks
    el.text(''); // empty the text of the element
    for (var i = 0; i < words.length; i++) { // iterate through each line and add a tspan with those words and offset by y
        var tspan = el.append('tspan').text(words[i]);
        if (i > 0)
            tspan.attr('x', 0).attr('dy', '15');
    }
    el.attr("y", "-" + ((words.length*textHeight) + textHeight)); // pushes the element up on the Y axis to accommodate the text
}

// function to join points together into a line
function lineGen(points){
    return points.join("L");
}

function handleResize(){
    var wid = $("#chart").width() - (svg.margins.right + svg.margins.left); // get the new width of the chart

    //svg.width = wid;
    // if the device is a mobile and dates weren't changed
    if(svg.isMob && !svg.datesChanged){

        // get the two dates we're plotting on
        var now, earliestDate;
        now = new Date(context.now);//svg.data[svg.data.length-1].obsStart;
        earliestDate = new Date(context.now);


        // depending on orientation data will be plotted for 1 day or 5 days
        if($(window).width() > $(window).height()){
            earliestDate.setDate(now.getDate() - svg.dateRange.landscape);
        }else{
            earliestDate.setDate(now.getDate() - svg.dateRange.portrait);
        }

        // update the inputs for mobile date entry
        var lD = earliestDate.getFullYear()  + "-" + ("0" + (earliestDate.getMonth()+1)).slice(-2) + "-" + ("0" + (earliestDate.getDate())).slice(-2);
        var lT = ("0" + (earliestDate.getHours())).slice(-2) + ":" + ("0" + (earliestDate.getMinutes())).slice(-2) + ":" + "00";
        var eD =  now.getFullYear()  + "-" + ("0" + (now.getMonth()+1)).slice(-2) + "-" + ("0" + (now.getDate())).slice(-2);
        var eT = ("0" + (now.getHours())).slice(-2) + ":" + ("0" + (now.getMinutes())).slice(-2) + ":" + "00";
        $("#contextStartD").val(lD);
        $("#contextStartT").val(lT);
        $("#contextEndD").val(eD);
        $("#contextEndT").val(eT);

        // update the domain of the focus x scale with the new times
        focus.xScale.domain([earliestDate, now]);
    }
   // initTable();
    resizeGraphs();
}
// function to handle resizing of window
$(window).resize(function(){
    if($(window).width() != svg.windowWidthDelta){
        setTimeout(function(){ handleResize() }, 1000);
        svg.windowWidthDelta = $(window).width();
    }
});
function process_obs_name(key_name){
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
}