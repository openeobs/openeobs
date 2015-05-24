var svg = new window.NH.NHGraphLib('#chart');
svg.style.padding.top = 0;
svg.style.padding.bottom = 0;
var resp_rate_graph = new window.NH.NHGraph();
resp_rate_graph.options.keys = ['respiration_rate'];
resp_rate_graph.options.label = 'RR';
resp_rate_graph.options.measurement = '/min';
resp_rate_graph.axes.y.min = 0;
resp_rate_graph.axes.y.max = 60;
resp_rate_graph.options.normal.min = 12;
resp_rate_graph.options.normal.max = 20;
resp_rate_graph.style.dimensions.height = 142.5; //140;
resp_rate_graph.style.data_style = 'linear';
resp_rate_graph.style.label_width = 60;

var oxy_graph = new window.NH.NHGraph();
oxy_graph.options.keys = ['indirect_oxymetry_spo2'];
oxy_graph.options.label = 'Spo2';
oxy_graph.options.measurement = '%';
oxy_graph.axes.y.min = 70;
oxy_graph.axes.y.max = 100;
oxy_graph.options.normal.min = 96;
oxy_graph.options.normal.max = 100;
oxy_graph.style.dimensions.height = 70; //80;
oxy_graph.style.axis.x.hide = true;
oxy_graph.style.data_style = 'linear';
oxy_graph.style.label_width = 60;

var temp_graph = new window.NH.NHGraph();
temp_graph.options.keys = ['body_temperature'];
temp_graph.options.label = 'Temp';
temp_graph.options.measurement = '\xB0C';
temp_graph.axes.y.min = 15;
temp_graph.axes.y.max = 50;
temp_graph.options.normal.min = 35;
temp_graph.options.normal.max = 37.1;
temp_graph.style.dimensions.height = 70; //80;
temp_graph.style.axis.x.hide = true;
temp_graph.style.data_style = 'linear';
temp_graph.style.label_width = 60;

var pulse_graph = new window.NH.NHGraph();
pulse_graph.options.keys = ['pulse_rate'];
pulse_graph.options.label = 'HR';
pulse_graph.options.measurement = '/min';
pulse_graph.axes.y.min = 30;
pulse_graph.axes.y.max = 200;
pulse_graph.options.normal.min = 50;
pulse_graph.options.normal.max = 100;
pulse_graph.style.dimensions.height = 70; //80;
pulse_graph.style.axis.x.hide = true;
pulse_graph.style.data_style = 'linear';
pulse_graph.style.label_width = 60;

var bp_graph = new window.NH.NHGraph();
bp_graph.options.keys = ['blood_pressure_systolic', 'blood_pressure_diastolic'];
bp_graph.options.label = 'BP';
bp_graph.options.measurement = 'mmHg';
bp_graph.axes.y.min = 30;
bp_graph.axes.y.max = 260;
bp_graph.options.normal.min = 150;
bp_graph.options.normal.max = 151;
bp_graph.style.dimensions.height = 90; //80;
bp_graph.style.axis.x.hide = true;
bp_graph.style.data_style = 'range';
bp_graph.style.label_width = 60;

var score_graph = new window.NH.NHGraph();
score_graph.options.keys = ['score'];
score_graph.style.dimensions.height = 132.5; //140;
score_graph.style.data_style = 'stepped';
score_graph.axes.y.min = 0;
score_graph.axes.y.max = 22;
score_graph.drawables.background.data =  [
    {"class": "green",s: 1, e: 4},
{"class": "amber",s: 4,e: 6},
{"class": "red",s: 6,e: 22}
];
score_graph.style.label_width = 60;

var focus = new window.NH.NHFocus();
var context = new window.NH.NHContext();
focus.graphs.push(resp_rate_graph);
focus.graphs.push(oxy_graph);
focus.graphs.push(temp_graph);
focus.graphs.push(pulse_graph);
focus.graphs.push(bp_graph);
focus.title = 'Individual values';
focus.style.padding.right = 0;
focus.style.margin.top = 0;
focus.style.padding.top = 0;
context.graph = score_graph;
context.title = 'NEWS Score';
context.style.margin.bottom = 0;
//context.style.margin.top = 35;
svg.focus = focus;
svg.context = context;
svg.data.raw = obs_data;
svg.init();
svg.draw();


//var table = new window.NH.NHGraphLib('#table');
//var tabular_obs = new window.NH.NHTable();
//tabular_obs.keys = ['avpu_text', 'oxygen_administration_flag'];
//tabular_obs.title = 'Tabular EWS values';
//var table_focus = new window.NH.NHFocus();
//table_focus.tables.push(tabular_obs);
//table.focus = table_focus;
//table.data.raw = obs_data;
//table.init();
//table.draw();