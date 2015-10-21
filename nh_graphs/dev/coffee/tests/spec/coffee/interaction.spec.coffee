###
  Created by Jon Wyatt on 18/10/15
###

describe 'Interaction', ->

  graphlib = null
  pulse_graph = null
  bp_graph = null
  score_graph = null
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

    if (pulse_graph == null)
      pulse_graph = new NHGraph()

    if (bp_graph == null)
      bp_graph = new NHGraph()

    if (score_graph == null)
      score_graph = new NHGraph()

    if (context == null)
      context = new NHContext()

    if (focus == null)
      focus = new NHFocus()

    pulse_graph.options.keys = ['pulse_rate']
    pulse_graph.options.label = 'HR'
    pulse_graph.options.measurement = '/min'
    pulse_graph.axes.y.min = 30
    pulse_graph.axes.y.max = 200
    pulse_graph.options.normal.min = 50
    pulse_graph.options.normal.max = 100
    pulse_graph.style.dimensions.height = 70
    pulse_graph.style.axis.x.hide = true
    pulse_graph.style.data_style = 'linear'
    pulse_graph.style.label_width = 60

    keys = ['blood_pressure_systolic', 'blood_pressure_diastolic']
    bp_graph.options.keys = keys
    bp_graph.options.label = 'BP'
    bp_graph.options.measurement = 'mmHg'
    bp_graph.axes.y.min = 30
    bp_graph.axes.y.max = 260
    bp_graph.options.normal.min = 150
    bp_graph.options.normal.max = 151
    bp_graph.style.dimensions.height = 90
    bp_graph.style.axis.x.hide = true
    bp_graph.style.data_style = 'range'
    bp_graph.style.label_width = 60

    score_graph.options.keys = ['score']
    score_graph.style.dimensions.height = 132.5
    score_graph.style.data_style = 'stepped'
    score_graph.axes.y.min = 0
    score_graph.axes.y.max = 22
    score_graph.drawables.background.data =  [
      {"class": "green",s: 1, e: 4},
      {"class": "amber",s: 4,e: 6},
      {"class": "red",s: 6,e: 22}
    ]
    score_graph.style.label_width = 60

    focus.graphs.push(pulse_graph)
    focus.graphs.push(bp_graph)
    focus.title = 'Individual values'
    focus.style.padding.right = 0
    focus.style.margin.top = 0
    focus.style.padding.top = 0

    context.graph = score_graph
    context.title = 'NEWS Score'
    context.style.margin.bottom = 0

    graphlib.focus = focus
    graphlib.context = context
    graphlib.data.raw = ews_data.multi_partial


  afterEach ->

    if (graphlib != null)
      graphlib = null

    if (pulse_graph != null)
      pulse_graph = null

    if (bp_graph != null)
      bp_graph = null

    if (context != null)
      context = null

    if (focus != null)
      focus = null

    if (test_area != null)
      test_area.parentNode.removeChild test_area

  describe "Pop-ups", ->

    describe "Methods", ->

      it "nh-graphlib_graph has pop-up methods", ->
        expect(typeof bp_graph.show_popup).toBe 'function'
        expect(typeof bp_graph.hide_popup).toBe 'function'

      it "show popup works as expected", ->
        bp_graph.show_popup('Hello', 42, 69)
        pop = document.getElementById 'chart_popup'
        popX = pop.style.left
        popY = pop.style.top
        popText = pop.textContent

        expect(popX).toBe '42px'
        expect(popY).toBe '69px'
        expect(popText).toBe 'Hello'

      it "hide popup works as expected", ->
        bp_graph.hide_popup()
        pop = document.getElementById 'chart_popup'
        popClass = pop.classList
        expect(popClass[0]).toBe 'hidden'

    describe "Event listeners", ->

      # Function to simulate 'mouseover' event
      mouseover = (el) ->
        ev = document.createEvent 'MouseEvent'
        ev.initMouseEvent(
          'mouseover',
          true, #bubble
          true, #cancelable
          window,
          null,
          0,0,0,0,
          false,false,false,false, #modifier keys
          0, #left
          null
        )
        el.dispatchEvent(ev)

      # Function to simulate 'mouseout' event
      mouseout = (el) ->
        ev = document.createEvent 'MouseEvent'
        ev.initMouseEvent(
          'mouseout',
          true, #bubble
          true, #cancelable
          window,
          null,
          0,0,0,0,
          false,false,false,false, #modifier keys
          0, #left
          null
        )
        el.dispatchEvent(ev)

      beforeEach ->
        graphlib.init()
        graphlib.draw()

        spyOn(bp_graph, 'show_popup').and.callThrough()
        spyOn(pulse_graph, 'show_popup').and.callThrough()

        spyOn(bp_graph, 'hide_popup').and.callThrough()
        spyOn(pulse_graph, 'hide_popup').and.callThrough()

      describe "Linear / Stepped Points", ->

        points = null

        beforeEach ->
          points = document.querySelectorAll '.point'

        it "mouse over event calls show_popup method on all points", ->

          for i in [0..points.length-1]
            mouseover(points[i])
            setTimeout( ->
              expect(pulse_graph.show_popup.calls.count()).toBe i+1
            ,1000)

        it "mouse out event calls hide_popup method on all points", ->

          for i in [0..points.length-1]
            mouseout(points[i])
            setTimeout( ->
              expect(pulse_graph.hide_popup.calls.count()).toBe i+1
            ,1000)

      describe "Linear / Stepped Empty Points", ->

        points = null

        beforeEach ->
          points = document.querySelectorAll '.empty_point'

        it "mouseover event calls show_popup method on all empty points", ->

          for i in [0..points.length-1]
            mouseover(points[i])
            setTimeout( ->
              expect(pulse_graph.show_popup.calls.count()).toBe i+1
            ,1000)

        it "mouseout event calls hide_popup method on all empty points", ->

          for i in [0..points.length-1]
            mouseout(points[i])
            setTimeout( ->
              expect(pulse_graph.hide_popup.calls.count()).toBe i+1
            ,1000)

      describe "Range Bars", ->

        ranges = null

        beforeEach ->
           ranges = document.querySelectorAll '.range'

        it "mouseover event calls show_popup method on all range elements", ->

          for i in [0..ranges.length-1]
            mouseover(ranges[i])
            setTimeout( ->
              expect(bp_graph.show_popup.calls.count()).toBe i+1
            ,1000)

        it "mouseout event calls hide_popup method on all range elements", ->

          for i in [0..ranges.length-1]
            mouseout(ranges[i])
            setTimeout( ->
              expect(bp_graph.hide_popup.calls.count()).toBe i+1
            ,1000)


  describe "Rangify", ->

    describe "Properties", ->

      it "nhgraphlib.graph has ranged_extent property", ->
        expect(bp_graph.axes.y.ranged_extent).toBeDefined

      it "initialises with correct range", ->
        graphlib.init()
        expect(bp_graph.axes.y.ranged_extent).toBe [80, 120]

      it "nhgraphlib.graph has rangify method", ->
        expect(bp_graph.rangify_graph).toBe true

    describe "Events", ->

      it "context"