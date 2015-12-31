
/*
  Created by Jon Wyatt on 13/10/15 (copied from Colin Wren 29/06/15).
 */
describe('Ranges', function() {
  var context, focus, graph, graphlib, test_area;
  graphlib = null;
  graph = null;
  context = null;
  focus = null;
  test_area = null;
  beforeEach(function() {
    var body_el;
    body_el = document.getElementsByTagName('body')[0];
    test_area = document.createElement('div');
    test_area.setAttribute('id', 'test_area');
    test_area.style.width = '500px';
    body_el.appendChild(test_area);
    if (graphlib === null) {
      graphlib = new NHGraphLib('#test_area');
    }
    if (graph === null) {
      graph = new NHGraph();
    }
    if (context === null) {
      context = new NHContext();
    }
    if (focus === null) {
      focus = new NHFocus();
    }
    graph.options.keys = ['respiration_rate'];
    graph.options.label = 'RR';
    graph.options.measurement = '/min';
    graph.axes.y.min = 0;
    graph.axes.y.max = 60;
    graph.options.normal.min = 12;
    graph.options.normal.max = 20;
    graph.style.dimensions.height = 250;
    graph.style.data_style = 'linear';
    graph.style.label_width = 60;
    focus.graphs.push(graph);
    graphlib.focus = focus;
    return graphlib.data.raw = ews_data.single_record;
  });
  return afterEach(function() {
    if (graphlib !== null) {
      graphlib = null;
    }
    if (graph !== null) {
      graph = null;
    }
    if (context !== null) {
      context = null;
    }
    if (focus !== null) {
      focus = null;
    }
    if (test_area !== null) {
      return test_area.parentNode.removeChild(test_area);
    }
  });
});
