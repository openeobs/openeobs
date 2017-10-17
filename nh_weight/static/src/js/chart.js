function setUpControls() {
    // hide controls
    var controls = document.getElementById("controls");
    if(controls){
        controls.style.display = "none";
    }
}

function processWeightData(obs){
    for (var i = 0; i < obs.length; i++) {
        var ob = obs[i];
        ob["completed_by"] = ob["write_uid"][1];
        if(ob["weight"] === null || ob["weight"] === false){
            ob["table_weight"] = "";
            ob["weight"] = false;
        }else{
            ob["table_weight"] = ob["weight"] + "kg";
        }
        if(ob["waist_measurement"] === null || ob["waist_measurement"] === false){
            ob["waist_measurement"] = false;
            ob["table_waist_measurement"] = "";
        }else{
            ob["table_waist_measurement"] = ob["waist_measurement"] + "cm";
        }
        if(ob["score"] === null || ob["score"] === false){
            ob["score"] = "";
        }
    }
    return obs;
}

function drawWeightChart(settings, obs){
    // Falses are later passed to the d3.extent method which always results in
    // 0 for the minimum.
    // Would have liked to have replaced False with None on the server-side
    // rather than the client-side but Odoo's Javascript for the views expect
    // falses and so things break if they are replaced with nulls.
    for (var i = 0; i < obs.length; i++) {
        var ob = obs[i];
        if (ob.weight === false) { ob.weight = null; }
    }
    setUpControls();
    var wExtent = nh_graphs.extent(obs, function (d) {
        return d['weight'];
    });
    if(wExtent.indexOf(null) > -1 || wExtent.indexOf(undefined) > -1 || wExtent.indexOf(false) > -1){
        wExtent = [10, 10];
    }
    var weightEl = new window.NH.NHGraphLib('#' + settings.chart_element);
    var wGraph = new window.NH.NHGraph();
    wGraph.options.keys = ['weight'];
    wGraph.options.label = 'W';
    wGraph.options.measurement = 'kg';
    wGraph.axes.y.min = wExtent[0] - 10;
    wGraph.axes.y.max = wExtent[1] + 10;
    wGraph.style.dimensions.height = 250;
    wGraph.style.data_style = 'linear';
    wGraph.style.label_width = 60;

    var focus = new window.NH.NHFocus();
    focus.graphs.push(wGraph);
    focus.style.padding.right = 0;
    focus.style.margin.top = settings.hideTitle ? 0 : 20;
    focus.title = settings.hideTitle ? "" : "Weight";
    weightEl.focus = focus;
    weightEl.data.raw = processWeightData(obs);
    weightEl.init();
    weightEl.draw();
}

function drawWeightTable(settings, serverData){
    var tableEl = new window.NH.NHGraphLib("#table");
    tableEl.table = {
        element: "#table",
        keys: [
            {
                title: "Weight",
                keys: ["table_weight"]
            },
            {
                title: "Waist Measurement",
                keys: ["table_waist_measurement"]
            },
            {
                title: "BMI",
                keys: ["score"]
            },
            {
                title: "Completed By",
                keys: ["completed_by"]
            }
        ]
    };
    tableEl.data.raw = processWeightData(serverData);
    tableEl.draw();
}
