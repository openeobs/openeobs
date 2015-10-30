
/*
  Created by Jon Wyatt on 18/10/15
  Stripped down set-up and tear down from resize and context suites
  that causes karma to hang and crash when running in phantomJS

 */

describe('Bugger', function() {
  var
  graphlib = null,
  pulse_graph = null,
  bp_graph = null,
  score_graph = null,
  focus = null,
  context = null,
  test_area = null;

  beforeEach(function() {
    var body_el, keys;

    body_el = document.getElementsByTagName('body')[0];
    test_area = document.createElement('div');
    test_area.setAttribute('id', 'test_area');
    test_area.style.width = '500px';
    body_el.appendChild(test_area);

    if (graphlib === null) {
      graphlib = new NHGraphLib('#test_area');
    }
    if (pulse_graph === null) {
      pulse_graph = new NHGraph();
    }
    if (bp_graph === null) {
      bp_graph = new NHGraph();
    }
    if (score_graph === null) {
      score_graph = new NHGraph();
    }
    if (context === null) {
      context = new NHContext();
    }
    if (focus === null) {
      focus = new NHFocus();
    }

    pulse_graph.options.keys = ['pulse_rate'];
    pulse_graph.options.label = 'HR';
    pulse_graph.options.measurement = '/min';
    pulse_graph.axes.y.min = 30;
    pulse_graph.axes.y.max = 200;
    pulse_graph.options.normal.min = 50;
    pulse_graph.options.normal.max = 100;
    pulse_graph.style.dimensions.height = 70;
    pulse_graph.style.axis.x.hide = true;
    pulse_graph.style.data_style = 'linear';
    pulse_graph.style.label_width = 60;

    keys = ['blood_pressure_systolic', 'blood_pressure_diastolic'];
    bp_graph.options.keys = keys;
    bp_graph.options.label = 'BP';
    bp_graph.options.measurement = 'mmHg';
    bp_graph.axes.y.min = 30;
    bp_graph.axes.y.max = 260;
    bp_graph.options.normal.min = 150;
    bp_graph.options.normal.max = 151;
    bp_graph.style.dimensions.height = 90;
    bp_graph.style.axis.x.hide = true;
    bp_graph.style.data_style = 'range';
    bp_graph.style.label_width = 60;

    score_graph.options.keys = ['score'];
    score_graph.style.dimensions.height = 132.5;
    score_graph.style.data_style = 'stepped';
    score_graph.axes.y.min = 0;
    score_graph.axes.y.max = 22;
    score_graph.drawables.background.data = [
      {
        "class": "green",
        s: 1,
        e: 4
      }, {
        "class": "amber",
        s: 4,
        e: 6
      }, {
        "class": "red",
        s: 6,
        e: 22
      }
    ];
    score_graph.style.label_width = 60;

    focus.graphs.push(pulse_graph);
    focus.graphs.push(bp_graph);
    focus.title = 'Individual values';
    focus.style.padding.right = 0;
    focus.style.margin.top = 0;
    focus.style.padding.top = 0;

    context.graph = score_graph;
    context.title = 'NEWS Score';
    context.style.margin.bottom = 0;

    graphlib.focus = focus;
    graphlib.context = context;
    graphlib.data.raw = ews_data.multi_partial;
  });

  afterEach(function() {

    if (graphlib !== null) {
      graphlib = null;
    }
    if (pulse_graph !== null) {
      pulse_graph = null;
    }
    if (bp_graph !== null) {
      bp_graph = null;
    }
    if (score_graph !== null) {
      score_graph = null;
    }
    if (focus !== null) {
      focus = null;
    }
    if (context !== null) {
      context = null;
    }
    if (test_area !== null) {
      test_area.parentNode.removeChild(test_area);
      test_area = null;
    }

    var pops = document.querySelectorAll('#chart_popup');
    if (pops.length > 0) {
      for (var i = 0; i < pops.length; i++) {
        var pop = pops[i];
        pop.parentNode.removeChild(pop);
      }
    }
    var tests = document.querySelectorAll('#test_area');
    if (tests.length > 0) {
      for (var i = 0; i < tests.length; i++) {
        var test = tests[i];
        test.parentNode.removeChild(test);
      }
    }
  });

  describe("Pre-init", function() {

    it("has right number of test elements pre-init", function() {
      var tests;
      tests = document.querySelectorAll('#test_area');
      expect(tests.length).toBe(1);
    });

    it("has right number of pop-ups pre-init", function() {
      var pops;
      pops = document.querySelectorAll('#chart_popup');
      expect(pops.length).toBe(0);
    });

    it("has right number of svg's pre-init", function() {
      var svgs;
      svgs = document.querySelectorAll('svg');
      expect(svgs.length).toBe(0);
    });

    it("has right number of input elements pre-init", function() {
      var inputs;
      inputs = document.querySelectorAll('input');
      expect(inputs.length).toBe(0);
    });

    it("has right number of context elements pre-init", function() {
      var contexts;
      contexts = document.querySelectorAll('.nhcontext');
      expect(contexts.length).toBe(0);
    });

    it("has right number of focus elements pre-init", function() {
      var foci;
      foci = document.querySelectorAll('.nhfocus');
      expect(foci.length).toBe(0);
    });

    it("has right number of context elements pre-init", function() {
      var conG;
      conG = document.querySelectorAll('.nhcontext .nhgraph');
      expect(conG.length).toBe(0);
    });

    it("has right number of focus elements pre-init", function() {
      var focG;
      focG = document.querySelectorAll('.nhfocus .nhgraph');
      expect(focG.length).toBe(0);
    });
  });

  describe("Post-init", function() {

    beforeEach(function() {
      graphlib.init();
    });

    it("has right number of test elements post-init", function() {
      var tests;
      tests = document.querySelectorAll('#test_area');
      expect(tests.length).toBe(1);
    });
    it("has right number of pop-ups post-init", function() {
      var pops;
      pops = document.querySelectorAll('#chart_popup');
      expect(pops.length).toBe(1);
    });
    it("has right number of svg's post-init", function() {
      var svgs;
      svgs = document.querySelectorAll('svg');
      expect(svgs.length).toBe(1);
    });
    it("has right number of input elements post-init", function() {
      var inputs;
      inputs = document.querySelectorAll('input');
      expect(inputs.length).toBe(0);
    });
    it("has right number of context elements post-init", function() {
      var contexts;
      contexts = document.querySelectorAll('.nhcontext');
      expect(contexts.length).toBe(1);
    });
    it("has right number of focus elements post-init", function() {
      var foci;
      foci = document.querySelectorAll('.nhfocus');
      expect(foci.length).toBe(1);
    });
    it("has right number of context elements post-init", function() {
      var conG;
      conG = document.querySelectorAll('.nhcontext .nhgraph');
      expect(conG.length).toBe(1);
    });
    it("has right number of focus elements post-init", function() {
      var focG;
      focG = document.querySelectorAll('.nhfocus .nhgraph');
      expect(focG.length).toBe(2);
    });
  });

  describe("Post-draw", function() {

    beforeEach(function() {
      graphlib.init();
      //graphlib.draw();
    });

    it("has right number of test elements post-init", function() {
      var tests;
      tests = document.querySelectorAll('#test_area');
      expect(tests.length).toBe(1);
    });
    it("has right number of pop-ups post-init", function() {
      var pops;
      pops = document.querySelectorAll('#chart_popup');
      expect(pops.length).toBe(1);
    });
    it("has right number of svg's post-init", function() {
      var svgs;
      svgs = document.querySelectorAll('svg');
      expect(svgs.length).toBe(1);
    });
    it("has right number of input elements post-init", function() {
      var inputs;
      inputs = document.querySelectorAll('input');
      expect(inputs.length).toBe(0);
    });
    it("has right number of context elements post-init", function() {
      var contexts;
      contexts = document.querySelectorAll('.nhcontext');
      expect(contexts.length).toBe(1);
    });
    it("has right number of focus elements post-init", function() {
      var foci;
      foci = document.querySelectorAll('.nhfocus');
      expect(foci.length).toBe(1);
    });
    it("has right number of context elements post-init", function() {
      var conG;
      conG = document.querySelectorAll('.nhcontext .nhgraph');
      expect(conG.length).toBe(1);
    });
    it("has right number of focus elements post-init", function() {
      var focG;
      focG = document.querySelectorAll('.nhfocus .nhgraph');
      expect(focG.length).toBe(2);
    });
  });

  describe("Post-init round 3", function() {

    beforeEach(function() {
      graphlib.init();
    });

    it("has right number of test elements post-init", function() {
      var tests;
      tests = document.querySelectorAll('#test_area');
      expect(tests.length).toBe(1);
    });
    it("has right number of pop-ups post-init", function() {
      var pops;
      pops = document.querySelectorAll('#chart_popup');
      expect(pops.length).toBe(1);
    });
    it("has right number of svg's post-init", function() {
      var svgs;
      svgs = document.querySelectorAll('svg');
      expect(svgs.length).toBe(1);
    });
    it("has right number of input elements post-init", function() {
      var inputs;
      inputs = document.querySelectorAll('input');
      expect(inputs.length).toBe(0);
    });
    it("has right number of context elements post-init", function() {
      var contexts;
      contexts = document.querySelectorAll('.nhcontext');
      expect(contexts.length).toBe(1);
    });
    it("has right number of focus elements post-init", function() {
      var foci;
      foci = document.querySelectorAll('.nhfocus');
      expect(foci.length).toBe(1);
    });
    it("has right number of context elements post-init", function() {
      var conG;
      conG = document.querySelectorAll('.nhcontext .nhgraph');
      expect(conG.length).toBe(1);
    });
    it("has right number of focus elements post-init", function() {
      var focG;
      focG = document.querySelectorAll('.nhfocus .nhgraph');
      expect(focG.length).toBe(2);
    });
  });
});
