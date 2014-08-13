/**
 * Created by colin on 31/12/13.
 */

// declare variables

// svg graph variables
var svg = {
    margins: {top: 20,bottom: 20,left: 20,right: 47},
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
    isMob: $(window).width()<=600,
    datesChanged: false,
    dateRange: {portrait: 1,landscape: 5},
    data: null,
    windowWidthDelta: $(window).width(),
    ticks: 10
}

// context graph variables
var context = {
    height: 100,
    margins: {top: 30,bottom: 40},
    xAxis: null,
    yAxis: null,
    xScale: null,
    area: null,
    yScale: null,
    brush: null,
    scoreRange: [{class: "green", s:0, e:4},{class: "amber", s:4, e:6},{class: "red", s:6, e:17.9}],
    earliestDate: new Date(),
    now: new Date()
};

// focus graph(s) variables
var focus = {
    chartHeight: 100,
    margins: {top: 60,bottom: 20},
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

// Function that deals with the setup of the graphs
function initGraph(maxScore) {

    if(typeof(maxScore) === "undefined"){
        maxScore = 20;
    }


    svg.width = ($(svg.el).width() - svg.margins.left - svg.margins.right);
    svg.infoAreaRight = svg.width / 18;
    focus.height = ((focus.graphs.length+1) * focus.chartHeight);
    svg.height = (context.height + focus.height + context.margins.bottom + context.margins.top + focus.margins.bottom + focus.margins.top);

    // select the #chart element add are svg element with a width of w with margins and a height of h with margin. Then append a group element and transform it so it is in the top left margin
    svg.obj.context = d3.select("#contextChart")
        .append("svg")
        .attr("width", svg.width + svg.margins.left + svg.margins.right)
        .attr("height", (context.height + context.margins.bottom + context.margins.top))
        .append("g")
        .attr("transform", "translate(" + 0 + "," + context.margins.top + ")");

    svg.obj.focus = d3.select("#focusChart")
        .append("svg")
        .attr("width", svg.width + svg.margins.left + svg.margins.right)
        .attr("height", (focus.height + focus.margins.bottom + focus.margins.top))
        .append("g")
        .attr("transform", "translate(" + 0 + "," + focus.margins.top/3 + ")");

    // set up the context scales and axis so it plots all the data
    //context.xScale = d3.time.scale().domain([context.earliestDate, context.now]).range([(svg.margins.left/4), svg.width - (svg.infoAreaRight + (svg.margins.right/4))]);
    context.yScale = d3.scale.linear().domain([0, maxScore]).range([context.height, 0]);
    //var tickMod = calcTicks(svg.width, context.earliestDate, context.now);
    //context.xAxis = d3.svg.axis().scale(context.xScale).orient("top").ticks(svg.ticks);
    context.yAxis = d3.svg.axis().scale(context.yScale).orient("left");

    // calculate difference of dates and change so context fits properly
    var earliestDate = new Date(context.earliestDate);
    var now = new Date(context.now);

    var dateDiffHours = ((((now-earliestDate)/1000)/60)/60);
    //var tickMod = calcTicks(svg.width, earliestDate, now);

    if(dateDiffHours >= 2){
        earliestDate.setHours(earliestDate.getHours() - 1);
        earliestDate.setMinutes(0);
        earliestDate.setSeconds(0);
        now.setHours(now.getHours() + 1);
        now.setMinutes(0);
        now.setSeconds(0);
    }else{
        earliestDate.setMinutes(earliestDate.getMinutes() - 6);
        now.setMinutes(now.getMinutes() + 6) ;
    }

    context.now = now;
        // set up the context scales and axis so it plots all the data
        context.xScale = d3.time.scale().domain([earliestDate, now]).range([(svg.margins.left/4), svg.width - (svg.infoAreaRight + (svg.margins.right/4))]);
        //var tickMod = calcTicks(svg.width, earliestDate, now);
        context.xAxis = d3.svg.axis().scale(context.xScale).orient("top");

    // if mobile then
    if(svg.isMob) {
        // depending on orientation data will be plotted for 1 day or 5 days
        if($(window).width() > $(window).height()){
            earliestDate = new Date(context.now);
            earliestDate.setDate(earliestDate.getDate() - svg.dateRange.landscape);
        }else{
            earliestDate = new Date(context.now);
            earliestDate.setDate(earliestDate.getDate() - svg.dateRange.portrait);
        }

        // If android want to use date inputs
        var cED = new Date(earliestDate);
        var cN = new Date(now);
        var lD = cED.getFullYear()  + "-" + ("0" + (cED.getMonth()+1)).slice(-2) + "-" + ("0" + (cED.getDate())).slice(-2);
        var lT = ("0" + (cED.getHours())).slice(-2) + ":" + ("0" + (cED.getMinutes())).slice(-2) + ":" + "00";
        var eD =  cN.getFullYear()  + "-" + ("0" + (cN.getMonth()+1)).slice(-2) + "-" + ("0" + (cN.getDate())).slice(-2);
        var eT = ("0" + (cN.getHours())).slice(-2) + ":" + ("0" + (cN.getMinutes())).slice(-2) + ":" + "00";

        // Set values of date inputs to the dates
        $("#contextStartD").val(lD);
        $("#contextStartT").val(lT);
        $("#contextEndD").val(eD);
        $("#contextEndT").val(eT);
        $(".chartDates").show();
    }

    focus.xScale = d3.time.scale().domain([earliestDate, now]).range([(svg.margins.left/4), svg.width - (svg.infoAreaRight + (svg.margins.right/4))]);
    focus.xAxis = d3.svg.axis().scale(focus.xScale).orient("top");//.ticks(tickMod[0], tickMod[1]);

    if(svg.isMob){
        context.xAxis.ticks(5);
        focus.xAxis.ticks(5);
    }

    drawChart();
    drawGraph();
}










