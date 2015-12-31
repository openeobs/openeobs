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
  range = null

  # Function to simulate 'click' event
  click = (el) ->
    ev = document.createEvent 'MouseEvent'
    ev.initMouseEvent(
      'click',
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

    # Add rangify checkbox
    range = document.createElement('input')
    range.setAttribute('id','rangify')
    range.setAttribute('type','checkbox')
    test_area.appendChild(range)

    graphlib.options.controls.rangify = range
    graphlib.focus = focus
    graphlib.context = context
    graphlib.data.raw = ews_data.multi_partial


  afterEach ->

    if (graphlib != null)
      graphlib = null

    if (pulse_graph != null)
      pulse_graph = null

    if (score_graph != null)
      score_graph = null

    if (bp_graph != null)
      bp_graph = null

    if (context != null)
      context = null

    if (focus != null)
      focus = null

    if (test_area != null)
      test_area.parentNode.removeChild test_area

  describe "Pop-ups", ->

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

      points = null
      ranges = null

      beforeEach ->
        spyOn(NHGraph.prototype, 'show_popup').and.callThrough()
        spyOn(NHGraph.prototype, 'hide_popup').and.callThrough()

        graphlib.init()
        graphlib.draw()


      describe "Linear / Stepped Points", ->

        beforeEach ->
          points = document.querySelectorAll '.point'

        it "mouse over event calls show_popup method on all points", ->

          expect(points.length).toBeGreaterThan(1)

          for point in points
            mouseover(point)

          setTimeout( ->
            console.log 'waited'
          ,100)

          c = NHGraph.prototype.show_popup.calls.count()
          expect(c).toBe points.length

        it "mouse out event calls hide_popup method on all points", ->

          for point in points
            mouseout(point)

          setTimeout( ->
            console.log 'waited'
          ,100)

          c = NHGraph.prototype.hide_popup.calls.count()
          expect(c).toBe points.length


      describe "Linear / Stepped Empty Points", ->

        beforeEach ->
          points = document.querySelectorAll '.empty_point'

        it "mouse over event calls show_popup method on all points", ->

          expect(points.length).toBeGreaterThan(1)

          for point in points
            mouseover(point)

          setTimeout( ->
            console.log 'waited'
          ,100)

          c = NHGraph.prototype.show_popup.calls.count()
          expect(c).toBe points.length

        it "mouse out event calls hide_popup method on all points", ->

          for point in points
            mouseout(point)

          setTimeout( ->
            console.log 'waited'
          ,100)

          c = NHGraph.prototype.hide_popup.calls.count()
          expect(c).toBe points.length

      describe "Range Bars", ->

        beforeEach ->
          ranges = document.querySelectorAll '.data .range'

        it "mouseover event calls show_popup method on all range elements", ->

          expect(ranges.length).toBeGreaterThan(1)

          for range in ranges
            mouseover(range)

          setTimeout( ->
            console.log 'waited'
          ,100)

          c = NHGraph.prototype.show_popup.calls.count()
          expect(c).toBe ranges.length

        it "mouseout event calls hide_popup method on all range elements", ->

          expect(ranges.length).toBeGreaterThan(1)

          for range in ranges
            mouseout(range)

          setTimeout( ->
            console.log 'waited'
          ,100)

          c = NHGraph.prototype.hide_popup.calls.count()
          expect(c).toBe ranges.length


  describe "Rangify", ->

    describe "Properties", ->

      beforeEach ->
        graphlib.init()

      it "nhgraphlib.graph has ranged_extent property", ->
        expect(bp_graph.axes.y.ranged_extent).toBeDefined

      it "nhgraphlib.graph initialises range_extent with correct range", ->

        #expect(bp_graph.axes.y.ranged_extent[0]).toBe 80
        expect(bp_graph.axes.y.ranged_extent[1]).toBe 120

      it "nhgraphlib.graph has rangify method", ->
        expect(bp_graph.rangify_graph).toBeDefined()

      it "nhgraphlib has link to rangify checkbox element", ->
        expect(graphlib.options.controls.rangify).toBeDefined()

    describe "Events", ->

      graphs = null

      beforeEach ->
        ###
        spyOn(NHGraph.prototype, 'rangify_graph').and.callThrough()
        spyOn(NHGraph.prototype, 'redraw').and.callThrough()
        ###
        spyOn(bp_graph, 'redraw').and.callThrough()
        spyOn(bp_graph, 'rangify_graph').and.callThrough()
        spyOn(pulse_graph, 'redraw').and.callThrough()
        spyOn(pulse_graph, 'rangify_graph').and.callThrough()


        graphs = [bp_graph, pulse_graph, score_graph]

        graphlib.init()
        graphlib.draw()

        click(range)

        setTimeout( ->
          console.log 'waited'
        ,100)




      describe "Check", ->

        it "calls rangify method on all graphs when checkbox clicked", ->
          ###
          count = NHGraph.prototype.rangify_graph.calls.count()
          expect(count).toBe 3
          ###
          count = bp_graph.rangify_graph.calls.count()
          count += pulse_graph.rangify_graph.calls.count()

          expect(count).toBe 2

        it "calls redraw method on all graphs", ->

          count = bp_graph.redraw.calls.count()
          count += pulse_graph.redraw.calls.count()

          expect(count).toBe 2

        it "switches axes to ranged min/max", ->

          for graph in graphs

            padding = graph.style.range_padding

            expectedMin = graph.axes.y.ranged_extent[0] - padding
            expectedMax = graph.axes.y.ranged_extent[1] + padding

            ticks = graph.axes.obj[0][0].querySelectorAll '.tick text'

            expect(ticks.length).toBeGreaterThan 2

            # Get min axis label
            min = 300
            for tick in ticks
              if tick.textContent != ''
                val = +tick.textContent
                if val < min
                  min = val

            expect(min).toBeGreaterThan expectedMin - 2


            # Get max axis label
            max = 0
            for tick in ticks
              if tick.textContent != ''
                val = +tick.textContent
                if val > max
                  max = val

            expect(max).toBeLessThan expectedMax + 2



      describe "Uncheck", ->

        beforeEach ->

          range.checked = true
          click(range)
          setTimeout( ->
            console.log 'waited'
          ,100)

        it "calls rangify method on all graphs when checkbox clicked", ->

          count = bp_graph.rangify_graph.calls.count()
          count += pulse_graph.rangify_graph.calls.count()

          expect(count).toBe 4

        it "calls redraw method on all graphs", ->

          count = bp_graph.redraw.calls.count()
          count += pulse_graph.redraw.calls.count()

          expect(count).toBe 4

        it "switches axes back to initial min/max on all graphs", ->

          # actually just checks score graph..

          expectedMin = score_graph.axes.y.min
          expectedMax = score_graph.axes.y.max

          ticks = score_graph.axes.obj[0][0].querySelectorAll '.tick text'

          expect(ticks.length).toBeGreaterThan 2

          # Get min axis label
          min = 300
          for tick in ticks
            if tick.textContent != ''
              val = +tick.textContent
              if val < min
                min = val

          expect(min).toBe expectedMin


          # Get max axis label
          max = 0
          for tick in ticks
            if tick.textContent != ''
              val = +tick.textContent
              if val > max
                max = val

          expect(max).toBe expectedMax

