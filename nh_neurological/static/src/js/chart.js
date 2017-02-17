function draw_neurological_chart(settings, server_data){
    var obs = server_data;
    var containers_in_dom = settings.hasOwnProperty('containers_set') ? settings.containers_set : false;

    if(!containers_in_dom){
        var chart_el = document.getElementById(settings.chart_element);
        chart_el.innerHTML = '<div id="eyes"></div><div id="verbal"></div><div id="motor"></div>';
    }

    // hide controls
    var controls = document.getElementById('controls');
    if(controls){
        controls.style.display = 'none';
    }

    var eyes_el = new window.NH.NHGraphLib('#eyes');
    var verbal_el = new window.NH.NHGraphLib('#verbal');
    var motor_el = new window.NH.NHGraphLib('#motor');
    var eyes_graph = new window.NH.NHGraph();
    var verbal_graph = new window.NH.NHGraph();
    var motor_graph = new window.NH.NHGraph();

    eyes_graph.options.keys = ['chart_eyes'];
    eyes_graph.options.label = '';
    eyes_graph.options.measurement = '';
    eyes_graph.options.title = 'Coma Scale - Eyes Open';
    eyes_graph.axes.y.min = 0;
    eyes_graph.axes.y.max = 4;
    eyes_graph.options.normal.min = 0;
    eyes_graph.options.normal.max = 0;
    eyes_graph.style.dimensions.height = 250;
    eyes_graph.style.data_style = 'stepped';
    eyes_graph.style.label_width = 60;
    eyes_graph.drawables.background.data = [];

    verbal_graph.options.keys = ['chart_verbal'];
    verbal_graph.options.label = '';
    verbal_graph.options.measurement = '';
    verbal_graph.options.title = 'Coma Scale - Best Verbal Response';
    verbal_graph.axes.y.min = 0;
    verbal_graph.axes.y.max = 5;
    verbal_graph.options.normal.min = 0;
    verbal_graph.options.normal.max = 0;
    verbal_graph.style.dimensions.height = 250;
    verbal_graph.style.data_style = 'stepped';
    verbal_graph.style.label_width = 60;
    verbal_graph.style.padding.top = 10;
    verbal_graph.drawables.background.data = [];

    motor_graph.options.keys = ['chart_motor'];
    motor_graph.options.label = '';
    motor_graph.options.measurement = '';
    motor_graph.options.title = 'Coma Scale - Best Motor Response';
    motor_graph.axes.y.min = 0;
    motor_graph.axes.y.max = 6;
    motor_graph.options.normal.min = 0;
    motor_graph.options.normal.max = 0;
    motor_graph.style.dimensions.height = 250;
    motor_graph.style.data_style = 'stepped';
    motor_graph.style.label_width = 60;
    motor_graph.style.padding.top = 10;
    motor_graph.drawables.background.data = [];


    var eyes_focus = new window.NH.NHFocus();
    var verbal_focus = new window.NH.NHFocus();
    var motor_focus = new window.NH.NHFocus();
    eyes_focus.graphs.push(eyes_graph);
    verbal_focus.graphs.push(verbal_graph);
    motor_focus.graphs.push(motor_graph);
    eyes_focus.title = 'Coma Scale - Eyes Open';
    verbal_focus.title = 'Coma Scale - Best Verbal Response';
    motor_focus.title = 'Coma Scale - Best Motor Response';
    if(!containers_in_dom){
        eyes_focus.style.margin.top = 70;
        verbal_focus.style.margin.top = 70;
        motor_focus.style.margin.top = 70;
    }
    eyes_el.focus = eyes_focus;
    verbal_el.focus = verbal_focus;
    motor_el.focus = motor_focus;
    var data = process_neurological_data(obs);


    eyes_el.data.raw = data;
    verbal_el.data.raw = data;
    motor_el.data.raw = data;

    eyes_el.init();
    verbal_el.init();
    motor_el.init();


    eyes_el.draw();
    verbal_el.draw();
    motor_el.draw();

}

function draw_neurological_table(settings, server_data){
    var obs = server_data.reverse();
    var table_el = new window.NH.NHGraphLib('#table');
    table_el.table = {
        element: '#table',
        keys: [
            {
                title: 'Coma Scale',
                keys: [],
                presentation: 'bold'
            },
            {
                title: 'Eyes',
                keys: ['table_eyes']
            },
            {
                title: 'Verbal',
                keys: ['table_verbal']
            },
            {
                title: 'Motor',
                keys: ['table_motor']
            },
            {
                title: 'Total Score',
                keys: ['score'],
                presentation: 'bold'
            },
            {
                title: 'Pupils',
                keys: [],
                presentation: 'bold'
            },
            {
                title: 'Right - Size',
                keys: ['table_pupil_right_size']
            },
            {
                title: 'Right - Reaction',
                keys: ['table_pupil_right_reaction']
            },
            {
                title: 'Left - Size',
                keys: ['table_pupil_left_size']
            },
            {
                title: 'Left - Reaction',
                keys: ['table_pupil_left_reaction']
            },
            {
                title: 'Limbs',
                keys: [],
                presentation: 'bold'
            },
            {
                title: 'Left Arm',
                keys: ['table_limb_movement_left_arm']
            },
            {
                title: 'Right Arm',
                keys: ['table_limb_movement_right_arm']
            },
            {
                title: 'Left Leg',
                keys: ['table_limb_movement_left_leg']
            },
            {
                title: 'Right Leg',
                keys: ['table_limb_movement_right_leg']
            },
            {
                title: 'Completed By',
                keys: ['completed_by']
            }
        ]
    };
    table_el.data.raw = process_neurological_data(obs);
    table_el.draw();
}

function process_neurological_data(obs){
    for (var i = 0; i < obs.length; i++) {
        var ob = obs[i];
        ob['completed_by'] = ob['write_uid'][1];
        ob['chart_eyes'] = ob['eyes'] === 'NT' ? false: parseInt(ob['eyes']);
        ob['chart_verbal'] = ob['verbal'] === 'NT' ? false: parseInt(ob['verbal']);
        ob['chart_motor'] = ob['motor'] === 'NT' ? false: parseInt(ob['motor']);
        ob['table_eyes'] = ob['eyes'] === '0' ? 'NT' : ob['eyes'];
        ob['table_verbal'] = ob['verbal'] === '0' ? 'NT' : ob['verbal'];
        ob['table_motor'] = ob['motor'] === '0' ? 'NT' : ob['motor'];
        ob['table_pupil_right_size'] = ob['pupil_right_size'] === 'not observable' ? 'NO': ob['pupil_right_size'];
        ob['table_pupil_right_reaction'] = ob['pupil_right_reaction'] === 'not testable' ? 'NT' : ob['pupil_right_reaction'];
        ob['table_pupil_left_size'] = ob['pupil_left_size'] === 'not observable' ? 'NO' : ob['pupil_left_size'];
        ob['table_pupil_left_reaction'] = ob['pupil_left_reaction'] === 'not testable' ? 'NT' : ob['pupil_left_reaction'];
        ob['table_limb_movement_left_arm'] = ob['limb_movement_left_arm'] === 'not observable' ? 'NO' : ob['limb_movement_left_arm'];
        ob['table_limb_movement_right_arm'] = ob['limb_movement_right_arm'] === 'not observable' ? 'NO' : ob['limb_movement_right_arm'];
        ob['table_limb_movement_left_leg'] = ob['limb_movement_left_leg'] === 'not observable' ? 'NO' : ob['limb_movement_left_leg'];
        ob['table_limb_movement_right_leg'] = ob['limb_movement_right_leg'] === 'not observable' ? 'NO' : ob['limb_movement_right_leg'];
    }
    return obs;
}