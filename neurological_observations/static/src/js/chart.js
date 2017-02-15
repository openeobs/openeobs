function get_neurological_chart(settings, server_data){
    var obs = server_data.reverse();
    var svg = new window.NH.NHGraphLib('#' + settings.chart_element);
    var eyes_graph = new window.NH.NHGraph();
    var verbal_graph = new window.NH.NHGraph();
    var motor_graph = new window.NH.NHGraph();

    eyes_graph.options.keys = ['eyes'];
    eyes_graph.options.label = '';
    eyes_graph.options.measurement = '';
    eyes_graph.axes.y.min = 1;
    eyes_graph.axes.y.max = 4;
    eyes_graph.options.normal.min = 0;
    eyes_graph.options.normal.max = 0;
    eyes_graph.style.dimensions.height = 250;
    eyes_graph.style.data_style = 'stepped';
    eyes_graph.style.label_width = 60;
    eyes_graph.drawables.background.data = [];

    verbal_graph.options.keys = ['verbal'];
    verbal_graph.options.label = '';
    verbal_graph.options.measurement = '';
    verbal_graph.axes.y.min = 1;
    verbal_graph.axes.y.max = 5;
    verbal_graph.options.normal.min = 0;
    verbal_graph.options.normal.max = 0;
    verbal_graph.style.dimensions.height = 250;
    verbal_graph.style.data_style = 'stepped';
    verbal_graph.style.label_width = 60;
    verbal_graph.drawables.background.data = [];

    motor_graph.options.keys = ['motor'];
    motor_graph.options.label = '';
    motor_graph.options.measurement = '';
    motor_graph.axes.y.min = 1;
    motor_graph.axes.y.max = 6;
    motor_graph.options.normal.min = 0;
    motor_graph.options.normal.max = 0;
    motor_graph.style.dimensions.height = 250;
    motor_graph.style.data_style = 'stepped';
    motor_graph.style.label_width = 60;
    motor_graph.drawables.background.data = [];

    focus = new window.NH.NHFocus();
    // context = new window.NHContext();
    focus.graphs.push(eyes_graph);
    focus.graphs.push(verbal_graph);
    focus.graphs.push(motor_graph);
    focus.title = 'Coma Scale values';
    // context.title = 'Coma scale values';
    svg.focus = focus;
    // svg.context = context;
    svg.options.controls.date.start = document.getElementById('start_date');
    svg.options.controls.date.end = document.getElementById('end_date');
    svg.options.controls.time.start = document.getElementById('start_time');
    svg.options.controls.time.end = document.getElementById('end_time');
    svg.options.controls.rangify = document.getElementById('rangify');
    svg.options.refused = settings.refused;
    svg.options.partial_type = settings.partial_type;
    svg.data.raw = process_neurological_data(obs);
    return svg;
}

function get_neurological_table(){
    return {
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
}

function process_neurological_data(obs){
    for (var i = 0; i < obs.length; i++) {
        var ob = obs[i];
        ob['completed_by'] = ob['write_uid'][1];
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