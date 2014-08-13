/**
 * Created by colin on 12/02/14.
 */

function myCalcTicks(width, earliestDate, latestDate){
    var axisWidth = width; // width of the axis
    var tickWidth = 60; // width of an individual tick including padding
    var optTicks = Math.floor(axisWidth / tickWidth); // simple division to see how many ticks can safely fit in axis at given width
    var dateDiff = contextLatest - contextEarliest; // see the difference in the dates
    var dateDiffSecs = Math.floor(dateDiff/1000); // calc seconds
    var dateDiffMins = Math.floor((dateDiff/1000)/60); // minutes
    var dateDiffHours = Math.floor((((dateDiff/1000)/60)/60)); // hours

    if(dateDiffHours <= optTicks){
        if(dateDiffHours <= 2){
            if(dateDiffMins <= 10){
                if(dateDiffMins <= 1){
                    if(dateDiffSecs <= 10){
                        var tickMod = 10;
                        return [d3.time.seconds, tickMod];
                    }
                    var tickMod = 10;
                    return [d3.time.minutes, tickMod];
                }
                var tickMod = 1;
                return [d3.time.minutes, tickMod];
            }
            var tickMod = Math.floor(dateDiffMins / optTicks);
            tickMod = tickMod - (tickMod % 2);
            if(tickMod <2){
                tickMod = 2;
            }else if(tickMod == 8){
                tickMod = 6;
            }
            return [d3.time.minutes, tickMod];
        }else{
            var tickMod = Math.floor(dateDiffHours / optTicks);
            tickMod = tickMod - (tickMod % 2);
            if(tickMod <2){
                tickMod = 2;
            }
            return [d3.time.hours, tickMod];
        }
    }else{
        var tickMod = Math.floor(dateDiffHours / optTicks);
        tickMod = tickMod - (tickMod % 2);
        if(tickMod <2){
            tickMod = 2;
        }
        return [d3.time.hours, tickMod];
    }
}

function getTicksVsWidth(width, earliestDate, latestDate){
    var testTicks = calcTicks(width, earliestDate, latestDate);
    var svg = d3.select("#testArea").append("svg").attr({
        "width" : width,
        "height": 100})
        .append("g")
    var testScale = d3.time.scale().domain([earliestDate, latestDate]).range([0, width]);
    var testAxis = d3.svg.axis().scale(testScale).orient("top").ticks(testTicks[0], testTicks[1]);
    return (60 * testAxis.ticks().length)<width;
}

JSC.group("TICKMOD");

JSC.claim("TICKMOD", function(width, earliestDate, latestDate){
        //return verdict(calcTicks(width, earliestDate, latestDate) == myCalcTicks(width, earliestDate, latestDate))

        console.log(getTicksVsWidth(width, earliestDate, latestDate));
        return verdict(getTicksVsWidth(width, earliestDate, latestDate) == true);
    },
    [
        JSC.integer(0,3840), // width
        JSC.literal(getRandomDate()), // earliest date
        JSC.literal(new Date()) // latest date
    ]
);

JSC.reps(10);

JSC.on_report(function(str) {
    document.getElementById("results").innerHTML += str;
    document.getElementById("results").innerHTML += "<br>";
});

function getRandomDate(){
    var d = new Date();
    d.setDate(d.getDate() - Math.floor((Math.random()*31)+1));
    return d;
}