function setUpControls() {
    var controls = document.getElementById("controls");
    if(controls){
        controls.style.display = "none";
    }
}

function getCurrentPeriod(obs){
    for(var i = 0; i < obs.length; i++){
        var period = obs[i];
        if(period.current_period){
            return period;
        }
    }
    return false;
}

function setUpCurrentPeriod(obs){
    var currentPeriod = getCurrentPeriod(obs);
    var tableContainer = document.getElementById("table-content");
    if(currentPeriod) {
        tableContainer.innerHTML =
            "<p class=\"food_fluid_period\"><strong>Current Period:</strong>" +
            currentPeriod["period_start_datetime"] + " - " + currentPeriod["period_end_datetime"] + "</p>" +
            "<p class=\"food_fluid_period\"><strong>Fluid Intake for current period:</strong>" + currentPeriod["total_fluid_intake"] + "ml</p>" +
            "<p class=\"food_fluid_period\"><strong>Fluid Intake score for current period:</strong>" + currentPeriod["score"] + "</p>";
    }
    tableContainer.innerHTML += "<button data-type=\"iframe\" " +
        "class=\"button dont-do-it full-width\" style=\"width: 100%;\" id=\"ff_info\">Fluid Taken Guidance</button>";
    var ffInfo = document.getElementById("ff_info");
    ffInfo.addEventListener("click", function (e) {
        return new window.NHModal(
            "popup_iframe",
            "Fluid Taken Guidance",
            "<iframe src=\"/nh_food_and_fluid/static/src/html/fluid_taken.html\"></iframe>",
            [
                "<a href=\"#\" data-action=\"close\" data-target=\"popup_iframe\">Cancel</a>"
            ],
            0,
            document.getElementsByClassName("content")[0]
        );
    });
}

function convertValue(value, valueToChange, substituteValue){
    return value === valueToChange ? substituteValue : value;
}

function processFoodFluidData(periods){
    for(var i = 0; i < periods.length; i++) {
        var period = periods[i];
        // period["observations"] = period["observations"].reverse();
        var obs = period["observations"];
        period["period_title"] = "24 Hour Period <br>" + period["period_start_datetime"] + " - " + period["period_end_datetime"];
        for (var j = 0; j < obs.length; j++) {
            var ob = obs[j];
            ob["fluid_taken"] += "ml";
            ob["class"] = "";
            if(j === 0){
                if(!period["current_period"]){
                    ob["score"] = period["score"] + "(" + period["total_fluid_intake"] + "ml)";
                }else{
                    ob["score"] = "";
                }
                ob["class"] += "nested-first ";
            }else{
                ob["score"] = "";
            }
            if(j === (obs.length - 1)){
                ob["class"] += "nested-last ";
            }

            ob["completed_by"] = ob["terminate_uid"][1];
            if (Array.isArray(ob["recorded_concerns"])) {
                ob["table_recorded_concerns"] = ob["recorded_concerns"].join("<br>");
            } else {
                ob["table_recorded_concerns"] = "";
            }
            if (Array.isArray(ob["dietary_needs"])) {
                ob["table_dietary_needs"] = ob["dietary_needs"].join("<br>");
            } else {
                ob["table_dietary_needs"] = "";
            }
            ob["fluid_intake"] = convertValue(ob["fluid_intake"], false, "");
            ob["fluid_description"] = convertValue(ob["fluid_description"], false, "");
            ob["food_taken"] = convertValue(ob["food_taken"], false, "");
            ob["food_fluid_rejected"] = convertValue(ob["food_fluid_rejected"], false, "");
        }
    }
    return periods;
}

var fluidTableDescription = {
    element: "#table-content",
    keys: [
        {
            title: "Recorded Concern",
            keys: ["table_recorded_concerns"]
        },
        {
            title: "Dietary Needs",
            keys: ["table_dietary_needs"]
        },
        {
            title: "Fluid Intake",
            keys: ["fluid_taken"]
        },
        {
            title: "Fluid Description",
            keys: ["fluid_description"]
        },
        {
            title: "Food Intake",
            keys: ["food_taken"]
        },
        {
            title: "Food and Fluid Offered But Rejected",
            keys: ["food_fluid_rejected"]
        },
        {
            title: "Passed Urine",
            keys: ["passed_urine"]
        },
        {
            title: "Bowels Open",
            keys: ["bowels_open"]
        },
        {
            title: "Fluid Intake Score",
            keys: ["score"]
        },
        {
            title: "Completed By",
            keys: ["completed_by"]
        }
    ]
};

function drawFood_fluidTable(settings, serverData){
    setUpControls();
    var processedData = processFoodFluidData(serverData);
    if(!settings.desktop){
        setUpCurrentPeriod(serverData);
        var tableEl = new window.NH.NHGraphLib("#table-content");
        fluidTableDescription.type = "nested";
        tableEl.data.raw = processedData;
        tableEl.table = fluidTableDescription;
        tableEl.draw();
    }else{
        var tableContainer = document.getElementById('table-content');
        processedData = processedData.reverse();
        for(var i = 0; i < processedData.length; i++) {
            var period = processedData[i];
            var tableId = "fftable" + i;
            tableContainer.innerHTML += "<div id=\""+ tableId + "\" class=\"food_fluid_table\"></div>";
            var tableElement = new window.NH.NHGraphLib("#"+tableId);
            var tableFocus = new window.NHFocus();
            var table = new window.NHTable();
            table.keys = fluidTableDescription.keys.map(function(a){
                a.key = a.keys[0];
                if(a.key === "food_fluid_rejected"){
                    a.title = "F&F Offered But Rejected";
                }
                return a;
            }).reduce(function(a, b){
                if(b.key !== 'score'){
                    a.push(b);
                }
                return a;
            }, []);
            table.title = period.period_start_datetime + " - " + period.period_end_datetime + "       Total Fluid Intake: "
            if(period["current_period"]){
                table.title +=  "      Score: ";
            }else {
                table.title += period.total_fluid_intake + "ml      Score: " + period.score;
            }
            tableFocus.tables.push(table);
            tableElement.focus = tableFocus;
            tableElement.data.raw = period.observations.reverse();
            tableElement.init();
            tableElement.draw();
        }
    }

}

