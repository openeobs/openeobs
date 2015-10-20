###
  Created by Jon Wyatt on 18/10/15
###

describe 'Data', ->

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


  describe "Properties", ->

    beforeEach ->
      graphlib.init()

    it "NHGraphLib_Graph has properties for data", ->
      expect(graph.drawables.data).toBeDefined()
      expect(graph.drawables.area).toBeDefined()
      expect(graph.options.keys).toBeDefined()
      expect(graph.options.plot_partial).toBeDefined()


    it "NHGraphLib_Graph has properties for data styles", ->
      expect(graph.style.data_style).toBeDefined()
      expect(graph.style.range.cap.height).toBeDefined()
      expect(graph.style.range.cap.width).toBeDefined()
      expect(graph.style.range.width).toBeDefined()
      expect(graph.style.range_padding).toBeDefined()


  describe "Data", ->

    describe "Invalid Data", ->

      it "handles no observation data (e.g. no properties for given key)", ->
        graph.options.keys = ['fake_key']
        expect(graphlib.data.raw[0].fake_key).not.toBeDefined()

        err = new Error("No data for 'fake_key'")
        expect(-> graphlib.init()).toThrow(err)

      it "handles invalid observation values (e.g. non-numeric values)", ->

        graphlib.data.raw[0].fake_key = 'Hello you'
        graph.options.keys = ['fake_key']

        err = new Error("Invalid data for 'fake_key'")
        expect(-> graphlib.init()).toThrow(err)

      it "catches erroneous obs values (values outside of min/max range)", ->
        graphlib.data.raw[0].respiration_rate = 200
        err = new Error("Out of bounds data for 'respiration_rate'")
        expect(-> graphlib.init()).toThrow(err)


  describe "Styles", ->

    graph = null
    graphHeight = null
    graphWidth = null

    circles = null
    paths = null

    it "throws error if no style defined", ->
      graph.style.data_style = null
      graphlib.init()
      expect(-> graphlib.draw()()).toThrow(new Error("no graph style defined"))

    describe "Linear", ->

      clipURL = 'url(#respiration_rate-clip)'

      describe "Single observation", ->

        beforeEach ->

          graphlib.init()
          graphlib.draw()

          graph = document.querySelectorAll '.nhgraph'

          graphHeight = +graph[0].getAttribute 'height'
          graphWidth = +graph[0].getAttribute 'width'

          circles = document.querySelectorAll '.nhgraph .data circle'
          paths = document.querySelectorAll '.nhgraph .data path'

        it "creates a single circle element", ->
          expect(paths.length).toBe 0
          expect(circles.length).toBe 1

        it "..that has class of 'point'", ->
          expect(circles[0].getAttribute 'class').toBe 'point'

        it "..which is the right size", ->
          expect(circles[0].getAttribute 'r').toBe '3'

        it "..and close to the expected position", ->
          # graph height - (( value / axis max ) * graph height ) = cy
          value = graphlib.data.raw[0].respiration_rate
          expected = graphHeight - ((value/60) * graphHeight)
          expect(circles[0].getAttribute 'cy').toBeCloseTo(expected, 1)


      describe "Multiple observations", ->

        beforeEach ->

          graphlib.data.raw = ews_data.multiple_records

          graphlib.init()
          graphlib.draw()

          graph = document.querySelectorAll '.nhgraph'

          graphHeight = +graph[0].getAttribute 'height'
          graphWidth = +graph[0].getAttribute 'width'

          circles = document.querySelectorAll '.nhgraph .data circle'
          paths = document.querySelectorAll '.nhgraph .data path'

        describe "Circles", ->

          it "creates a circle for each data point", ->
            expect(circles.length).toBe graphlib.data.raw.length

          it "..which is the right size", ->
            for circle in circles
              expect(circle.getAttribute 'r').toBe '3'

          it "..and close to it's expected positions", ->
            for i in [0..circles.length-1]
              # graph height - (( value / axis max ) * graph height ) = cy
              value = graphlib.data.raw[i].respiration_rate
              expected = graphHeight - ((value/60) * graphHeight)
              expect(circles[i].getAttribute 'cy').toBeCloseTo(expected, 1)

        describe "Path/s", ->

          it "creates expected number of path elements", ->
            expect(paths.length).toBe graphlib.data.raw.length-1

          it "has a class of 'path'", ->
            for path in paths
              expect(path.getAttribute 'class').toBe 'path'

          it "has a clip path to prevent overflow", ->
            for path in paths
              expect(path.getAttribute 'clip-path').toBe clipURL

          it "starts and finishes at data points", ->
            for i in [0..paths.length-1]

              # Get start and end cx and cy of data point
              expectedStartX = +circles[i].getAttribute 'cx'
              #expectedStartY = +circles[i].getAttribute 'cy'

              expectedEndX = +circles[i+1].getAttribute 'cx'
              #expectedEndY = +circles[i+1].getAttribute 'cy'


              # Get start co-oridinates in path.d string
              dString = paths[i].getAttribute('d')

              startX = +dString.substr(1,4)
              #startY = +dString.match(/,(.*)/)[0].substr(0,6)

              endX = +dString.match(/L(.*)/)[1].substr(0,6)
              #endY = +dString.match(/,(.*)/)[1].substr(0,6)

              expect(startX).toBeCloseTo(expectedStartX,0)
              expect(endX).toBeCloseTo(expectedEndX,0)


      describe "Incomplete observations", ->

        beforeEach ->

          graphlib.data.raw = ews_data.multi_partial
          graph.options.plot_partial = true

          graphlib.init()
          graphlib.draw()

          graph = document.querySelectorAll '.nhgraph'

          graphHeight = +graph[0].getAttribute 'height'
          graphWidth = +graph[0].getAttribute 'width'

          circles = document.querySelectorAll '.nhgraph .data circle'
          paths = document.querySelectorAll '.nhgraph .data path'

        it "doesn't create empty data points", ->
          expect(circles.length).toBe 3
          expect(paths.length).toBe 1


    describe "Stepped", ->

      clipURL = 'url(#respiration_rate-clip)'

      beforeEach ->
        graph.style.data_style = 'stepped'

      describe "Single observation", ->

        beforeEach ->

          graphlib.init()
          graphlib.draw()

          graph = document.querySelectorAll '.nhgraph'

          graphHeight = +graph[0].getAttribute 'height'
          graphWidth = +graph[0].getAttribute 'width'

          circles = document.querySelectorAll '.nhgraph .data circle'
          paths = document.querySelectorAll '.nhgraph .data path'

        it "creates a single circle element", ->
          expect(paths.length).toBe 0
          expect(circles.length).toBe 1

        it "..that has class of 'point'", ->
          expect(circles[0].getAttribute 'class').toBe 'point'

        it "..which is the right size", ->
          expect(circles[0].getAttribute 'r').toBe '3'

        it "..and close to the expected position", ->
          # graph height - (( value / axis max ) * graph height ) = cy
          value = graphlib.data.raw[0].respiration_rate
          expected = graphHeight - ((value/60) * graphHeight)
          expect(circles[0].getAttribute 'cy').toBeCloseTo(expected, 1)


      describe "Multiple observations", ->

        beforeEach ->

          graphlib.data.raw = ews_data.multiple_records

          graphlib.init()
          graphlib.draw()

          graph = document.querySelectorAll '.nhgraph'

          graphHeight = +graph[0].getAttribute 'height'
          graphWidth = +graph[0].getAttribute 'width'

          circles = document.querySelectorAll '.nhgraph .data circle'
          paths = document.querySelectorAll '.nhgraph .data path'

        describe "Circles", ->

          it "creates a circle for each data point", ->
            expect(circles.length).toBe graphlib.data.raw.length

          it "..which is the right size", ->
            for circle in circles
              expect(circle.getAttribute 'r').toBe '3'

          it "..and close to it's expected positions", ->
            for i in [0..circles.length-1]
              # graph height - (( value / axis max ) * graph height ) = cy
              value = graphlib.data.raw[i].respiration_rate
              expected = graphHeight - ((value/60) * graphHeight)
              expect(circles[i].getAttribute 'cy').toBeCloseTo(expected, 1)

        describe "Path/s", ->

          it "creates single path element", ->
            expect(paths.length).toBe 1

          it "has a class of 'path'", ->
            for path in paths
              expect(path.getAttribute 'class').toBe 'path'

          it "has a clip path to prevent overflow", ->
            for path in paths
              expect(path.getAttribute 'clip-path').toBe clipURL

          xit "starts and finishes at data points", ->
            for i in [0..paths.length-1]

              # Get start and end cx and cy of data point
              expectedStartX = +circles[i].getAttribute 'cx'
              #expectedStartY = +circles[i].getAttribute 'cy'

              expectedEndX = +circles[i+1].getAttribute 'cx'
              #expectedEndY = +circles[i+1].getAttribute 'cy'

              # Get start co-oridinates in path.d string
              dString = paths[i].getAttribute('d')

              startX = +dString.substr(1,4)
              #startY = +dString.match(/,(.*)/)[0].substr(0,6)

              endX = +dString.match(/L(.*)/)[1].substr(0,6)
              #endY = +dString.match(/,(.*)/)[1].substr(0,6)

              expect(startX).toBeCloseTo(expectedStartX,0)
              expect(endX).toBeCloseTo(expectedEndX,0)

      describe "Incomplete observations", ->

         beforeEach ->

          graphlib.data.raw = ews_data.multi_partial
          graph.options.plot_partial = true

          graphlib.init()
          graphlib.draw()

          graph = document.querySelectorAll '.nhgraph'

          graphHeight = +graph[0].getAttribute 'height'
          graphWidth = +graph[0].getAttribute 'width'

          circles = document.querySelectorAll '.nhgraph .data circle'
          paths = document.querySelectorAll '.nhgraph .data path'

        it "doesn't create empty data points", ->
          expect(circles.length).toBe 2
          expect(paths.length).toBe 1

    describe "Range", ->

      tops = null
      extents = null
      bottoms = null
      bar = null

      capWidth = null
      capHeight = null
      rangeWidth = null

      clipURL = 'url(#blood_pressure_systolic-blood_pressure_diastolic-clip)'

      beforeEach ->
        graph.style.data_style = 'range'
        keys = ['blood_pressure_systolic','blood_pressure_diastolic']
        graph.options.keys = keys
        graph.options.label = 'BP'
        graph.options.measurement = 'mmHg'
        graph.axes.y.min = 0
        graph.axes.y.max = 250
        graph.options.normal.min = 100
        graph.options.normal.max = 140

        capWidth = graph.style.range.cap.width
        capHeight = graph.style.range.cap.height
        rangeWidth = graph.style.range.width

      it "throws error if 2 keys are not defined", ->
        keys = ['blood_pressure_systolic']
        msg = 'Cannot plot ranged graph with '
        msg += graph.options.keys.length
        msg += ' data point(s)'
        err = new Error msg

        graphlib.init()
        expect(-> graphlib.draw()()).toThrow(new Error())

      describe "Single Record", ->

        beforeEach ->
          graphlib.data.raw = ews_data.single_record

          graphlib.init()
          graphlib.draw()

          tops = document.querySelectorAll '.range.top'
          bottoms = document.querySelectorAll '.range.bottom'
          extents = document.querySelectorAll '.range.extent'
          bar = [tops[0],extents[0],bottoms[0]]

        it "has a single range bar made of 3 rects", ->
          expect(tops.length).toBe 1
          expect(bottoms.length).toBe 1
          expect(extents.length).toBe 1

        it "has bar caps that are the defined size", ->

          expect(+tops[0].getAttribute 'width').toBe capWidth
          expect(+tops[0].getAttribute 'height').toBe capHeight
          expect(+bottoms[0].getAttribute 'width').toBe capWidth
          expect(+bottoms[0].getAttribute 'height').toBe capHeight

        it "has an extent that is the correct size", ->
          expect(+extents[0].getAttribute 'width').toBe rangeWidth

          sys = graphlib.data.raw[0].blood_pressure_systolic
          dia = graphlib.data.raw[0].blood_pressure_diastolic
          dif = sys - dia
          expected = (dif/graph.axes.y.max)*graphHeight
          expect(+extents[0].getAttribute 'height').toBeCloseTo(expected,0)

        it "is positioned correctly", ->
          # graph height - (( systolic / axis max ) * graph height ) = extentY
          systolic = graphlib.data.raw[0].blood_pressure_systolic
          expected = graphHeight - ((systolic/250) * graphHeight)
          expect(+extents[0].getAttribute 'y').toBeCloseTo(expected, 0)

        it "has the correct clip-path attribute", ->
          for el in bar
            expect(el.getAttribute 'clip-path').toBe clipURL

      describe "Multiple Records", ->

        beforeEach ->
          graphlib.data.raw = ews_data.multiple_records

          graphlib.init()
          graphlib.draw()

          tops = document.querySelectorAll '.range.top'
          bottoms = document.querySelectorAll '.range.bottom'
          extents = document.querySelectorAll '.range.extent'

        it "has the correct number of range bars", ->
          expect(tops.length).toBe graphlib.data.raw.length
          expect(bottoms.length).toBe graphlib.data.raw.length
          expect(extents.length).toBe graphlib.data.raw.length

        it "has correct sized bar caps", ->
          for top in tops
            expect(+top.getAttribute 'width').toBe capWidth
            expect(+top.getAttribute 'height').toBe capHeight

          for bottom in bottoms
            expect(+bottom.getAttribute 'width').toBe capWidth
            expect(+bottom.getAttribute 'height').toBe capHeight


        it "has an extent that is the correct size", ->

          for i in [0..extents.length-1]

            expect(+extents[i].getAttribute 'width').toBe rangeWidth

            sys = graphlib.data.raw[i].blood_pressure_systolic
            dia = graphlib.data.raw[i].blood_pressure_diastolic
            dif = sys - dia
            expected = (dif/graph.axes.y.max)*graphHeight
            expect(+extents[i].getAttribute 'height').toBeCloseTo(expected,0)

        it "is positioned correctly", ->
          for i in [0..extents.length-1]
            # graph height - (( systolic / axis max ) * graph height )
            # = extentY
            sys = graphlib.data.raw[i].blood_pressure_systolic
            expected = graphHeight - ((sys/250) * graphHeight)
            expect(+extents[i].getAttribute 'y').toBeCloseTo(expected, 0)

        it "has the correct clip-path attribute", ->

          for el in bar
            expect(el.getAttribute 'clip-path').toBe clipURL


      describe "Incomplete Record", ->

        beforeEach ->

          graphlib.data.raw = ews_data.incomplete_record
          none = "['blood_pressure_systolic','blood_pressure_diastolic']"
          graphlib.data.raw[0].none_values = none
          graphlib.data.raw[0].blood_pressure_diastolic = false
          graphlib.data.raw[0].blood_pressure_systolic = false

          graphlib.init()
          graphlib.draw()

          tops = document.querySelectorAll '.range.top'
          bottoms = document.querySelectorAll '.range.bottom'
          extents = document.querySelectorAll '.range.extent'

        it "doesn't create empty data points", ->
          expect(tops.length).toBe 0
          expect(bottoms.length).toBe 0
          expect(extents.length).toBe 0


