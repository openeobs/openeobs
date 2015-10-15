###
  Created by Jon Wyatt on 14/10/15
###

describe 'Background', ->

  graphlib = null
  graph = null
  context = null
  focus = null
  test_area = null


  beforeEach ->

    body_el = document.getElementsByTagName('body')[0]
    test_area = document.createElement('div')
    test_area.setAttribute('id', 'test_area')
    test_area.style.width = '500px'
    body_el.appendChild(test_area)

    if (graphlib == null)
      graphlib = new NHGraphLib '#test_area'

    if (graph == null)
      graph = new NHGraph()

    if (context == null)
      context = new NHContext()

    if (focus == null)
      focus = new NHFocus()

    # set up a demo graph
    graph.options.keys = ['respiration_rate']
    graph.options.label = 'RR'
    graph.options.measurement = '/min'
    graph.axes.y.min = 0
    graph.axes.y.max = 60
    graph.options.normal.min = 12
    graph.options.normal.max = 20
    graph.style.dimensions.height = 250
    graph.style.data_style = 'linear'
    graph.style.label_width = 60

    focus.graphs.push graph
    graphlib.focus = focus
    graphlib.data.raw = ews_data.single_record

  afterEach ->

    if (graphlib != null)
      graphlib = null

    if (graph != null)
      graph = null

    if (context != null)
      context = null

    if (focus != null)
      focus = null

    if (test_area != null)
      test_area.parentNode.removeChild test_area


  describe "Ranges", ->

    describe "Object properties", ->

      beforeEach ->
        graphlib.init()

      it "NHGraphLib_Graph has properties for normal ranges", ->
        expect(graph.options.normal.min).toBeDefined()
        expect(graph.options.normal.max).toBeDefined()

      it "NHGraphLib_Graph has properties for abnormal ranges", ->
        expect(graph.drawables.background.obj).toBeDefined()
        expect(graph.drawables.background.data).toBeDefined()

    describe "Data", ->

      it "catches invalid normal range data", ->

      it "catches invalid abnormal range data", ->

    describe "Normal", ->

      it "handles 1 normal defined", ->

      it "handles no normal defined", ->

      it "blows up when many normals defined", ->

    describe "Abnormal", ->

      it "handles 1 abnormal range", ->

      it "handles no abnormal ranges", ->

      it "handles multiple abnormal ranges", ->


  describe "Grid Lines", ->




