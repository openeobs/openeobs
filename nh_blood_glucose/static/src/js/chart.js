function setUpControls() {
    // hide controls
    var controls = document.getElementById("controls");
    if(controls){
        controls.style.display = "none";
    }
}

function processBlood_glucoseData(obs){
    for (var i = 0; i < obs.length; i++) {
        var ob = obs[i];
        ob["completed_by"] = ob["write_uid"][1];
        if(ob["blood_glucose"] === null || ob["blood_glucose"] === false){
            ob["table_blood_glucose"] = "";
        }else{
            ob["table_blood_glucose"] = ob["blood_glucose"];
        }
    }
    return obs;
}

function drawBlood_glucoseChart(settings, obs){
    // Falses are later passed to the d3.extent method which always results in
    // 0 for the minimum.
    // Would have liked to have replaced False with None on the server-side
    // rather than the client-side but Odoo's Javascript for the views expect
    // falses and so things break if they are replaced with nulls.
    for (var i = 0; i < obs.length; i++) {
        var ob = obs[i];
        if (ob.blood_glucose === false) { ob.blood_glucose = null; }
    }
    setUpControls();
    var dataExtent = nh_graphs.extent(obs, function (d) {
        return d['blood_glucose'];
    });
    if(dataExtent.indexOf(null) > -1 || dataExtent.indexOf(undefined) > -1 || dataExtent.indexOf(false) > -1){
        dataExtent = [10, 10];
    }
    var bloodGlucoseEl = new window.NH.NHGraphLib('#' + settings.chart_element);
    var bloodGluoseGraph = new window.NH.NHGraph();
    bloodGluoseGraph.options.keys = ['blood_glucose'];
    bloodGluoseGraph.options.label = 'BG';
    bloodGluoseGraph.options.measurement = 'mmol/L';
    bloodGluoseGraph.axes.y.min = dataExtent[0] - 10;
    bloodGluoseGraph.axes.y.max = dataExtent[1] + 10;
    bloodGluoseGraph.style.dimensions.height = 250;
    bloodGluoseGraph.style.data_style = 'linear';
    bloodGluoseGraph.style.label_width = 80;

    var focus = new window.NH.NHFocus();
    focus.graphs.push(bloodGluoseGraph);
    focus.style.padding.right = 0;
    focus.style.margin.top = settings.hideTitle ? 0 : 20;
    focus.title = settings.hideTitle ? "" : "Blood Glucose";
    bloodGlucoseEl.focus = focus;
    bloodGlucoseEl.data.raw = processBlood_glucoseData(obs);
    bloodGlucoseEl.init();
    bloodGlucoseEl.draw();
}

function drawBlood_glucoseTable(settings, serverData){
    var tableEl = new window.NH.NHGraphLib("#table");
    tableEl.table = {
        element: "#table",
        keys: [
            {
                title: "Blood Glucose (mmol/L)",
                keys: ["table_blood_glucose"]
            },
            {
                title: "Completed By",
                keys: ["completed_by"]
            }
        ]
    };
    tableEl.data.raw = processBlood_glucoseData(serverData);
    tableEl.draw();
}
