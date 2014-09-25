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
    svg.obj.context = d3.select("#contextChart").append("svg").attr("width", svg.width + svg.margins.left + svg.margins.right).attr("height", context.height + context.margins.bottom + context.margins.top).append("g").attr("transform", "translate(" + 0 + "," + context.margins.top + ")");
    svg.obj.focus = d3.select("#focusChart").append("svg").attr("width", svg.width + svg.margins.left + svg.margins.right).attr("height", focus.height + focus.margins.bottom + focus.margins.top).append("g").attr("transform", "translate(" + 0 + "," + focus.margins.top / 3 + ")");
    context.yScale = d3.scale.linear().domain([ 0, maxScore ]).range([ context.height, 0 ]);
    context.yAxis = d3.svg.axis().scale(context.yScale).orient("left");


    var earliestDate = new Date(context.earliestDate.toString());
    var now = new Date(context.now.toString());
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

    context.now = now;
    context.xScale = d3.time.scale().domain([ earliestDate, now ]).range([context.chartXOffset, svg.width - (svg.infoAreaRight + svg.margins.right / 4) ]);
    context.xAxis = d3.svg.axis().scale(context.xScale).orient("top");
    focus.xScale = d3.time.scale().domain([ earliestDate, now ]).range([context.chartXOffset, svg.width - (svg.infoAreaRight + svg.margins.right / 4) ]);
    focus.xAxis = d3.svg.axis().scale(focus.xScale).orient("top");

    this.drawChart();
    this.drawGraph();
},