function draw_neurological_chart(settings, server_data){
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
    focus.graphs.push(eyes_graph);
    focus.graphs.push(verbal_graph);
    focus.graphs.push(motor_graph);
    focus.title = 'Coma scale values';
    svg.focus = focus;
    svg.data.raw = obs;
    svg.init();
    svg.draw();
}