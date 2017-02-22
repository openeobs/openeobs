function setUpContainers(settings){
    var containersInDom = settings.hasOwnProperty("containers_set") ? settings.containers_set : false;
    if(!containersInDom){
        var chartEl = document.getElementById(settings.chart_element);
        chartEl.innerHTML = "<div id=\"eyes\"></div><div id=\"verbal\"></div><div id=\"motor\"></div>";
    }
    return containersInDom;
}

function setUpControls() {
    // hide controls
    var controls = document.getElementById("controls");
    if(controls){
        controls.style.display = "none";
    }
}

function convertValue(value, valueToChange, substituteValue){
    return value === valueToChange ? substituteValue : value;
}

function processNeurologicalData(obs){
    for (var i = 0; i < obs.length; i++) {
        var ob = obs[i];
        if(ob["eyes"] && ob["verbal"] && ob["motor"]){
            ob["none_values"] = "[]"
        }
        ob["completed_by"] = ob["write_uid"][1];
        ob["chart_eyes"] = convertValue(ob["eyes"], "NT", false);
        ob["chart_verbal"] = convertValue(ob["verbal"], "NT", false);
        ob["chart_motor"] = convertValue(ob["motor"], "NT", false);
        ob["table_eyes"] = convertValue(ob["eyes"], "0" , "NT");
        ob["table_verbal"] = convertValue(ob["verbal"], "0", "NT");
        ob["table_motor"] = convertValue(ob["motor"], "0", "NT");

        ob["table_pupil_right_size"] = convertValue(ob["pupil_right_size"], null, "");
        ob["table_pupil_right_reaction"] = convertValue(ob["pupil_right_reaction"], "not testable", "NT");
        ob["table_pupil_right_reaction"] = convertValue(ob["pupil_right_reaction"], null, "");
        ob["table_pupil_left_size"] = convertValue(ob["pupil_left_size"], "not observable", "NO");
        ob["table_pupil_left_size"] = convertValue(ob["pupil_left_size"], null, "");
        ob["table_pupil_left_reaction"] = convertValue(ob["pupil_left_reaction"], "not testable", "NT");
        ob["table_pupil_left_reaction"] = convertValue(ob["pupil_left_reaction"], null, "");
        ob["table_limb_movement_left_arm"] = convertValue(ob["limb_movement_left_arm"], "not observable", "NO");
        ob["table_limb_movement_left_arm"] = convertValue(ob["limb_movement_left_arm"], null, "");
        ob["table_limb_movement_right_arm"] = convertValue(ob["limb_movement_right_arm"], "not observable", "NO");
        ob["table_limb_movement_right_arm"] = convertValue(ob["limb_movement_right_arm"], null, "");
        ob["table_limb_movement_left_leg"] = convertValue(ob["limb_movement_left_leg"], "not observable", "NO");
        ob["table_limb_movement_left_leg"] = convertValue(ob["limb_movement_left_leg"], null, "");
        ob["table_limb_movement_right_leg"] = convertValue(ob["limb_movement_right_leg"], "not observable", "NO");
        ob["table_limb_movement_right_leg"] = convertValue(ob["limb_movement_right_leg"], null, "");
    }
    return obs;
}

function drawNeurologicalChart(settings, serverData){
    var obs = serverData;
    var containersInDom = setUpContainers(settings);
    setUpControls();

    var eyesEl = new window.NH.NHGraphLib("#eyes");
    var verbalEl = new window.NH.NHGraphLib("#verbal");
    var motorEl = new window.NH.NHGraphLib("#motor");
    var eyesGraph = new window.NH.NHGraph();
    var verbalGraph = new window.NH.NHGraph();
    var motorGraph = new window.NH.NHGraph();

    eyesGraph.options.keys = ["chart_eyes"];
    eyesGraph.options.label = "";
    eyesGraph.options.measurement = "";
    eyesGraph.options.title = "Coma Scale - Eyes";
    eyesGraph.axes.y.min = 1;
    eyesGraph.axes.y.max = 4;
    eyesGraph.options.normal.min = 0;
    eyesGraph.options.normal.max = 0;
    eyesGraph.style.dimensions.height = 250;
    eyesGraph.style.pointRadius = 5;
    eyesGraph.style.data_style = "linear";
    eyesGraph.style.label_width = 60;
    eyesGraph.drawables.background.data = [];

    verbalGraph.options.keys = ["chart_verbal"];
    verbalGraph.options.label = "";
    verbalGraph.options.measurement = "";
    verbalGraph.options.title = "Coma Scale - Verbal";
    verbalGraph.axes.y.min = 1;
    verbalGraph.axes.y.max = 5;
    verbalGraph.options.normal.min = 0;
    verbalGraph.options.normal.max = 0;
    verbalGraph.style.dimensions.height = 250;
    verbalGraph.style.pointRadius = 5;
    verbalGraph.style.data_style = "linear";
    verbalGraph.style.label_width = 60;
    verbalGraph.style.padding.top = 10;
    verbalGraph.drawables.background.data = [];

    motorGraph.options.keys = ["chart_motor"];
    motorGraph.options.label = "";
    motorGraph.options.measurement = "";
    motorGraph.options.title = "Coma Scale - Motor";
    motorGraph.axes.y.min = 1;
    motorGraph.axes.y.max = 6;
    motorGraph.options.normal.min = 0;
    motorGraph.options.normal.max = 0;
    motorGraph.style.dimensions.height = 250;
    motorGraph.style.pointRadius = 5;
    motorGraph.style.data_style = "linear";
    motorGraph.style.label_width = 60;
    motorGraph.style.padding.top = 10;
    motorGraph.drawables.background.data = [];


    var eyesFocus = new window.NH.NHFocus();
    var verbalFocus = new window.NH.NHFocus();
    var motorFocus = new window.NH.NHFocus();
    eyesFocus.graphs.push(eyesGraph);
    verbalFocus.graphs.push(verbalGraph);
    motorFocus.graphs.push(motorGraph);
    eyesFocus.title = "Coma Scale - Eyes Open";
    verbalFocus.title = "Coma Scale - Best Verbal Response";
    motorFocus.title = "Coma Scale - Best Motor Response";
    if(!containersInDom){
        eyesFocus.style.margin.top = 70;
        verbalFocus.style.margin.top = 70;
        motorFocus.style.margin.top = 70;
    }
    eyesEl.focus = eyesFocus;
    verbalEl.focus = verbalFocus;
    motorEl.focus = motorFocus;
    var data = processNeurologicalData(obs);


    eyesEl.data.raw = data;
    verbalEl.data.raw = data;
    motorEl.data.raw = data;

    eyesEl.init();
    verbalEl.init();
    motorEl.init();


    eyesEl.draw();
    verbalEl.draw();
    motorEl.draw();

}

function drawNeurologicalTable(settings, serverData){
    var obs = serverData.reverse();
    var tableEl = new window.NH.NHGraphLib("#table");
    tableEl.table = {
        element: "#table",
        keys: [
            {
                title: "Coma Scale",
                keys: [],
                presentation: "bold"
            },
            {
                title: "Eyes",
                keys: ["table_eyes"]
            },
            {
                title: "Verbal",
                keys: ["table_verbal"]
            },
            {
                title: "Motor",
                keys: ["table_motor"]
            },
            {
                title: "Total Score",
                keys: ["score"],
                presentation: "bold"
            },
            {
                title: "Pupils",
                keys: [],
                presentation: "bold"
            },
            {
                title: "Right - Size",
                keys: ["table_pupil_right_size"]
            },
            {
                title: "Right - Reaction",
                keys: ["table_pupil_right_reaction"]
            },
            {
                title: "Left - Size",
                keys: ["table_pupil_left_size"]
            },
            {
                title: "Left - Reaction",
                keys: ["table_pupil_left_reaction"]
            },
            {
                title: "Limbs",
                keys: [],
                presentation: "bold"
            },
            {
                title: "Left Arm",
                keys: ["table_limb_movement_left_arm"]
            },
            {
                title: "Right Arm",
                keys: ["table_limb_movement_right_arm"]
            },
            {
                title: "Left Leg",
                keys: ["table_limb_movement_left_leg"]
            },
            {
                title: "Right Leg",
                keys: ["table_limb_movement_right_leg"]
            },
            {
                title: "Completed By",
                keys: ["completed_by"]
            }
        ]
    };
    tableEl.data.raw = processNeurologicalData(obs);
    tableEl.draw();
}