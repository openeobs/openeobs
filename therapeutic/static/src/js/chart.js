// Only exists to hide the 'ranged values' checkbox at the moment.
function drawTherapeuticChart(settings, serverData) {
    var svg = new window.NH.NHGraphLib("#" + settings.chart_element);
}

function drawTherapeuticTable(settings, serverData){
    var obs = serverData.reverse();
    var tableEl = new window.NH.NHGraphLib("#table");
    tableEl.table = {
        element: "#table",
        keys: [
            {
                title: "Patient Status",
                keys: ["table_patient_status"]
            },
            {
                title: "Location",
                keys: ["table_location"]
            },
            {
                title: "Areas of Concern",
                keys: ["table_areas_of_concern"]
            },
            {
                title: "Intervention Needed?",
                keys: ["table_one_to_one_intervention_needed"]
            },
            {
                title: "Other Staff",
                keys: ["table_other_staff_during_intervention"]
            },
            {
                title: "Completed By",
                keys: ["table_completed_by"]
            },
            {
                title: "Other Notes",
                keys: ["table_other_notes"]
            }
        ]
    };
    tableEl.data.raw = processTherapeuticData(obs);
    tableEl.draw();
}

function hideRangedValuesCheckbox() {
    var rangeCheckbox = document.getElementById('range');
    rangeCheckbox.style.display = 'none';
}

function convertValue(value, valueToChange, substituteValue){
    return value === valueToChange ? substituteValue : value;
}

function processTherapeuticData(obs){
    for (var i = 0; i < obs.length; i++) {
        var ob = obs[i];
        ob["table_patient_status"] = convertValue(ob["patient_status"], null, "");
        ob["table_location"] = convertValue(ob["location"], null, "");
        ob["table_areas_of_concern"] = convertValue(ob["areas_of_concern"], null, "");
        ob["table_one_to_one_intervention_needed"] = convertValue(ob["one_to_one_intervention_needed"], null, "");
        ob["table_other_staff_during_intervention"] = convertValue(ob["other_staff_during_intervention"], null, "");
        ob["table_completed_by"] = convertValue(ob["terminate_uid"][1], null, "");
        ob["table_other_notes"] = convertValue(ob["other_notes"], null, "");
    }
    return obs;
}