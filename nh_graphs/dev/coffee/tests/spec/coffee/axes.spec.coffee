###
  Created by Jon Wyatt on 13/10/15 (copied from Colin Wren 29/06/15).
###

describe 'Axes', ->

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

  describe "NHGraphLib, NHContext, NHFocus, NHGraph axes properties", ->

    it 'NHGraphLib has properties for setting the axis label height', ->
      expect(graphlib.style.hasOwnProperty('axis_label_text_height')).toBe true

    it 'NHContext has axes property that holds information for X and Y axes', ->
      expect(context.hasOwnProperty('axes')).toBe(true)
      expect(context.axes.hasOwnProperty('x')).toBe(true)
      expect(context.axes.hasOwnProperty('y')).toBe(true)
      expect(context.axes.x.hasOwnProperty('scale')).toBe(true)
      expect(context.axes.x.hasOwnProperty('axis')).toBe(true)
      expect(context.axes.x.hasOwnProperty('min')).toBe(true)
      expect(context.axes.x.hasOwnProperty('max')).toBe(true)
      expect(context.axes.y.hasOwnProperty('scale')).toBe(true)
      expect(context.axes.y.hasOwnProperty('axis')).toBe(true)
      expect(context.axes.y.hasOwnProperty('min')).toBe(true)
      expect(context.axes.y.hasOwnProperty('max')).toBe(true)

    it 'NHFocus has axes property that holds information for X and Y axes', ->
      expect(focus.hasOwnProperty('axes')).toBe(true)
      expect(focus.axes.hasOwnProperty('x')).toBe(true)
      expect(focus.axes.hasOwnProperty('y')).toBe(true)
      expect(focus.axes.x.hasOwnProperty('scale')).toBe(true)
      expect(focus.axes.x.hasOwnProperty('axis')).toBe(true)
      expect(focus.axes.x.hasOwnProperty('min')).toBe(true)
      expect(focus.axes.x.hasOwnProperty('max')).toBe(true)
      expect(focus.axes.y.hasOwnProperty('scale')).toBe(true)
      expect(focus.axes.y.hasOwnProperty('axis')).toBe(true)
      expect(focus.axes.y.hasOwnProperty('min')).toBe(true)
      expect(focus.axes.y.hasOwnProperty('max')).toBe(true)

    it 'NHGraph has axes property that holds information for X and Y axes', ->
      expect(graph.hasOwnProperty('axes')).toBe(true)
      expect(graph.axes.hasOwnProperty('x')).toBe(true)
      expect(graph.axes.hasOwnProperty('y')).toBe(true)
      expect(graph.axes.hasOwnProperty('obj')).toBe(true)
      expect(graph.axes.x.hasOwnProperty('scale')).toBe(true)
      expect(graph.axes.x.hasOwnProperty('axis')).toBe(true)
      expect(graph.axes.x.hasOwnProperty('min')).toBe(true)
      expect(graph.axes.x.hasOwnProperty('max')).toBe(true)
      expect(graph.axes.x.hasOwnProperty('obj')).toBe(true)
      expect(graph.axes.y.hasOwnProperty('scale')).toBe(true)
      expect(graph.axes.y.hasOwnProperty('axis')).toBe(true)
      expect(graph.axes.y.hasOwnProperty('min')).toBe(true)
      expect(graph.axes.y.hasOwnProperty('max')).toBe(true)
      expect(graph.axes.y.hasOwnProperty('obj')).toBe(true)
      expect(graph.axes.y.hasOwnProperty('ranged_extent')).toBe(true)


    it 'NHGraph has styling properties for X and Y axes', ->
      expect(graph.style.hasOwnProperty('axis')).toBe(true)
      expect(graph.style.hasOwnProperty('axis_label_text_height')).toBe(true)
      expect(graph.style.hasOwnProperty('axis_label_text_padding')).toBe(true)
      expect(graph.style.axis.hasOwnProperty('x')).toBe(true)
      expect(graph.style.axis.hasOwnProperty('y')).toBe(true)
      expect(graph.style.axis.x.hasOwnProperty('hide')).toBe(true)
      expect(graph.style.axis.y.hasOwnProperty('hide')).toBe(true)
      expect(graph.style.axis.x.hasOwnProperty('size')).toBe(true)
      expect(graph.style.axis.y.hasOwnProperty('size')).toBe(true)

  describe  "Structure", ->

    beforeEach ->
      graphlib.init()
      graphlib.draw()

    it "Creates a DOM structure for the axis which is easy to understand", ->

      # Get focus
      focus_els = document.getElementsByClassName 'nhfocus'
      expect(focus_els.length).toBe 1
      focus_el = focus_els[0]

      # Get graph
      graph_els = focus_el.getElementsByClassName 'nhgraph'
      expect(graph_els.length).toBe 1
      graph_el = graph_els[0]

      # Get X Axis
      x_els = graph_el.getElementsByClassName 'x'
      expect(x_els.length).toBe 1
      x_el = x_els[0]
      expect(x_el.getAttribute 'class').toBe 'x axis'

      # Get Y Axis
      y_els = graph_el.getElementsByClassName 'y'
      expect(y_els.length).toBe 1
      y_el = y_els[0]
      expect(y_el.getAttribute('class')).toBe 'y axis'


  describe 'X-Axis', ->

    describe "Visibility", ->

      it "is visible by default", ->
        graphlib.init()
        expect(document.querySelectorAll('.x').length).toBe 1

      it "can be hidden", ->
        graph.style.axis.x.hide = true
        graphlib.init()
        expect(document.querySelectorAll('.x').length).toBe 0


    describe 'Scale', ->

      it 'Adds time padding of 100 to the scale when plotting a single data \
        point and no time padding defined', ->

        # Set up the original extent so can check
        terminated = graphlib.data.raw[0]['date_terminated']
        data_point = graphlib.date_from_string(terminated)

        # initalise the graph
        graphlib.init()

        # As we're dealing with a single data point the initialisation should
        # pad the extent by 100 minutes
        expect(graphlib.style.time_padding).toBe(100)
        start = new Date(data_point)
        end = new Date(data_point)

        start.setMinutes(start.getMinutes()-100)
        end.setMinutes(end.getMinutes()+100)

        # Need to do string conversion as can't compare date to date
        starts = graphlib.date_to_string(start)
        ends = graphlib.date_to_string(end)
        expect(graphlib.date_to_string(graphlib.data.extent.start)).toBe(starts)
        expect(graphlib.date_to_string(graphlib.data.extent.end)).toBe(ends)


      it 'Adds time padding of 3 to the scale when plotting a single data \
        point and time padding of 3 is defined', ->

        # Set up the original extent so can check
        terminated = graphlib.data.raw[0]['date_terminated']
        data_point = graphlib.date_from_string(terminated)

        # set time padding to 3
        graphlib.style.time_padding = 3

        # initalise the graph
        graphlib.init()

        # As we're dealing with a single data point the initialisation should
        # pad the extent by 100 minutes
        expect(graphlib.style.time_padding).toBe(3)
        start = new Date(data_point)
        end = new Date(data_point)

        start.setMinutes(start.getMinutes()-3)
        end.setMinutes(end.getMinutes()+3)

        # Need to do string conversion as can't compare date to date
        starts = graphlib.date_to_string(start)
        ends = graphlib.date_to_string(end)
        expect(graphlib.date_to_string(graphlib.data.extent.start)).toBe(starts)
        expect(graphlib.date_to_string(graphlib.data.extent.end)).toBe(ends)


      it 'Adds time padding of date difference divided by SVG width divided \
        by 500 to the scale when plotting multiple data points and no time \
        padding defined', ->
        graphlib.data.raw = ews_data.multiple_records

        raw1 = graphlib.data.raw[0]['date_terminated']
        raw2 = graphlib.data.raw[1]['date_terminated']
        term1 = graphlib.date_from_string(raw1)
        term2 = graphlib.date_from_string(raw2)
        original_extent = [term1, term2]

        graphlib.init()

        # dates are 1 hour apart (3600000), svg is 500px (500px - 0 margins)
        # and 3600000 / 500 / 500 = 14.4
        expect(graphlib.style.time_padding).toBe(14.4)
        start = new Date(original_extent[0])
        end = new Date(original_extent[1])

        start.setMinutes(start.getMinutes()-14.4)
        end.setMinutes(end.getMinutes()+14.4)

        # Need to do string conversion as can't compare date to date
        starts = graphlib.date_to_string(start)
        ends = graphlib.date_to_string(end)

        expect(graphlib.date_to_string(graphlib.data.extent.start)).toBe(starts)
        expect(graphlib.date_to_string(graphlib.data.extent.end)).toBe(ends)

      it 'Adds time padding of 3 to the scale when plotting multiple data \
        points when time padding of 3 is defined', ->

        graphlib.data.raw = ews_data.multiple_records

        raw1 = graphlib.data.raw[0]['date_terminated']
        raw2 = graphlib.data.raw[1]['date_terminated']
        term1 = graphlib.date_from_string(raw1)
        term2 = graphlib.date_from_string(raw2)
        original_extent = [term1, term2]

        # set time padding to 3
        graphlib.style.time_padding = 3
        graphlib.init()

        # As we're dealing with a single data point the initialisation
        # should pad the extent by 100 minutes
        expect(graphlib.style.time_padding).toBe(3)
        start = new Date(original_extent[0])
        end = new Date(original_extent[1])

        start.setMinutes(start.getMinutes()-3)
        end.setMinutes(end.getMinutes()+3)


        # Need to do string conversion as can't compare date to date
        starts = graphlib.date_to_string(start)
        ends = graphlib.date_to_string(end)
        expect(graphlib.date_to_string(graphlib.data.extent.start)).toBe(starts)
        expect(graphlib.date_to_string(graphlib.data.extent.end)).toBe(ends)

    describe 'Ticks', ->

      it "has sensible amount", ->

        graphlib.init()
        graphlib.draw()

        # Get x axis ticks
        x_ticks = document.querySelectorAll('.x .tick')

        expect(x_ticks.length).toBeLessThan(10)
        expect(x_ticks.length).toBeGreaterThan(2)

      it "are evenly spaced", ->

        graphlib.init()
        graphlib.draw()

        x_ticks = document.querySelectorAll('.x .tick')

        xPos = []

        # Create array of tick x-values
        for tick in x_ticks
          xPos.push(+(tick.getAttribute('transform').substr(10,5)))

        # Compare difference between each value
        lastGap = null
        for i in [1..xPos.length-1]
          if lastGap != null
            expect(Math.round(xPos[i]-xPos[i-1])).toBe lastGap
          lastGap = Math.round(xPos[i]-xPos[i-1])


      describe 'Labels', ->

        it "use default size if no size defined", ->

          graphlib.init()
          graphlib.draw()

          x_ticks = document.querySelectorAll('.x .tick')

          for tick in x_ticks
            tspans = tick.getElementsByTagName 'tspan'
            expect(tspans.length).toBe 3

            # Check day tspan attributes
            expect(tspans[0].getAttribute('x')).toBe null
            expect(tspans[0].getAttribute('dy')).toBe null
            expect(tspans[0].getAttribute('style')).toBe 'font-size: 12px;'

            # Check date tspan
            expect(tspans[1].getAttribute('x')).toBe '0'
            expect(tspans[1].getAttribute('dy')).toBe '14'
            expect(tspans[1].getAttribute('style')).toBe 'font-size: 12px;'

            # Check time tspan
            expect(tspans[2].getAttribute('x')).toBe '0'
            expect(tspans[2].getAttribute('dy')).toBe '14'
            expect(tspans[2].getAttribute('style')).toBe 'font-size: 12px;'

        it "use defined size if provided", ->

          graph.style.axis_label_font_size = 30
          graph.style.axis_label_line_height = 2

          graphlib.init()
          graphlib.draw()

          x_ticks = document.querySelectorAll('.x .tick')

          for tick in x_ticks

            text_el = tick.getElementsByTagName 'text'
            expect(text_el.length).toBe 1
            # Should be 3 * axis_label_text_height + 1 * axis_label_text_height
            expect(text_el[0].getAttribute 'y').toBe '-150'

            tspans = tick.getElementsByTagName 'tspan'
            expect(tspans.length).toBe 3

            # Check day tspan attributes
            expect(tspans[0].getAttribute('x')).toBe null
            expect(tspans[0].getAttribute('dy')).toBe null
            expect(tspans[0].getAttribute('style')).toBe 'font-size: 30px;'

            # Check date tspan
            expect(tspans[1].getAttribute('x')).toBe '0'
            expect(tspans[1].getAttribute('dy')).toBe '60'
            expect(tspans[1].getAttribute('style')).toBe 'font-size: 30px;'

            # Check time tspan
            expect(tspans[2].getAttribute('x')).toBe '0'
            expect(tspans[2].getAttribute('dy')).toBe '60'
            expect(tspans[2].getAttribute('style')).toBe 'font-size: 30px;'


        it "have sensible text values for day / date/ time", ->

          graphlib.init()
          graphlib.draw()

          # Get x axis ticks
          x_ticks = document.querySelectorAll('.x .tick')

          # Set up regex for ticks
          day_re = new RegExp '[MTWFS][a-z][a-z]'
          date_re = new RegExp '[0-9]?[0-9]/[0-9]?[0-9]/[0-9]?[0-9]'
          time_re = new RegExp '[0-2]?[0-9]:[0-5]?[0-9]'

          for tick in x_ticks
            tspans = tick.getElementsByTagName 'tspan'
            expect(tspans.length).toBe 3

            # Check day tspan
            expect(day_re.exec tspans[0].textContent).not.toBe null

            # Check date
            expect(date_re.exec tspans[1].textContent).not.toBe null

            # Check time
            expect(time_re.exec tspans[2].textContent).not.toBe null

  describe 'Y-Axis', ->

    describe "Visibility", ->

      it "is visible by default", ->
        graphlib.init()
        expect(document.querySelectorAll('.y').length).toBe 1

      it "can be hidden", ->
        graph.style.axis.y.hide = true
        graphlib.init()
        expect(document.querySelectorAll('.y').length).toBe 0

    describe 'Scale', ->

      it "Uses min/max values set in graph.axes.y object", ->

        graphlib.init()
        graphlib.draw()

        y_ticks_text = document.querySelectorAll('.y .tick text')
        expect(y_ticks_text.length).toBeGreaterThan(3)

        expect(+(y_ticks_text[0].textContent)).toBe graph.axes.y.min
        lastTick = y_ticks_text[y_ticks_text.length-1].textContent
        expect(+lastTick).toBe graph.axes.y.max

    describe 'Steps', ->

      it "changes tick label format as defined", ->

        graph.style.axis.step = 2

        graphlib.init()
        graphlib.draw()

        y_ticks = document.querySelectorAll('.y .tick text')

        for tick in y_ticks
          expect(tick.textContent.substr(-2)).toBe '00'
