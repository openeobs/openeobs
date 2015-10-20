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


  describe "Structure", ->

    ranges = null
    normals = null
    greens = null
    ambers = null
    reds = null

    validAbnormal = null

    countClass = (className) ->
      return document.querySelectorAll(className).length


    beforeEach ->
      graph.options.normal.min = 12
      graph.options.normal.max = 20

      validAbnormal = [
        {'class': 'green', s: 20, e: 30},
        {'class': 'amber', s: 30, e: 40},
        {'class': 'red', s: 40, e: 60}
      ]

      graph.drawables.background.data = validAbnormal

      graphlib.init()
      graphlib.draw()


    it "has one background group", ->
      expect(countClass '.background').toBe 1

    it "containing one normal rect", ->
      expect(countClass '.background .normal').toBe 1

    it "and 3 range rects", ->
      expect(countClass '.background .range').toBe 3

    it "..one green rect", ->
      expect(countClass '.background .green').toBe 1

    it "..one amber rect", ->
      expect(countClass '.background .amber').toBe 1

    it "..one red rect", ->
      expect(countClass '.background .red').toBe 1

    it "has a label", ->
      expect(countClass '.label').toBe 1

    it "has a measurement", ->
      expect(countClass '.measurement').toBe 1

    it "has at least 3 vertical grid lines", ->
      expect(countClass '.background .vertical').toBeGreaterThan 2

    it "has at least 3 horizontal grid lines", ->
      expect(countClass '.background .horizontal').toBeGreaterThan 2

  describe "Ranges", ->

    graphs = null
    graphWidth = null
    graphHeight = null

    describe "Object properties", ->

      beforeEach ->
        graphlib.init()
        graphlib.draw()

      it "NHGraphLib_Graph has properties for normal ranges", ->
        expect(graph.options.normal.min).toBeDefined()
        expect(graph.options.normal.max).toBeDefined()

      it "NHGraphLib_Graph has properties for score ranges", ->
        expect(graph.drawables.background.obj).toBeDefined()
        expect(graph.drawables.background.data).toBeDefined()


    describe "Data", ->

      describe "Normal range", ->

        it "throws error if normal range outside of axis range", ->
          graph.options.normal.min = -3
          graph.options.normal.max = 100

          graphlib.init()
          expect(-> graphlib.draw()).toThrow(new Error('Invalid normal range'))

        it "throws error if normal range data invalid", ->
          graph.options.normal.min = "yay"
          graph.options.normal.max = NaN

          graphlib.init()
          expect(-> graphlib.draw()).toThrow(new Error('Invalid normal range'))

      describe "Score range", ->

        invalidAbnormal = [
          {'class': 'green', t: 'abc', e: 30},
          {'class': 'amber', s: 30, e: 40},
          {'class': 'red', s: 40, e: 60}
        ]

        it "throws error if array not in expected format", ->
          graph.drawables.background.data = invalidAbnormal
          graphlib.init()

          err = new Error('Invalid background range data')
          expect(-> graphlib.draw()).toThrow(err)

        it "throws error if range larger than axis range", ->
          invalidAbnormal = [
            {'class': 'green', s: 20, e: 30},
            {'class': 'amber', s: 30, e: 40},
            {'class': 'red', s: 40, e: 200}
          ]
          graph.drawables.background.data = invalidAbnormal
          graphlib.init()

          err = new Error('Invalid background range data')

          expect(-> graphlib.draw()).toThrow(err)

    describe "Normal Range", ->

      normals = []

      describe "Single normal range", ->

        beforeEach ->
          graph.options.normal.min = 12
          graph.options.normal.max = 20
          graphlib.init()
          graphlib.draw()

          # Grab array of 'normal' rects
          normals = document.querySelectorAll('.normal')
          graphs = document.querySelectorAll('.nhgraph')

          graphWidth = graphs[0].getAttribute 'width'
          graphHeight = graphs[0].getAttribute 'height'

        it "renders only one normal rect inside nhgraph", ->
          expect(graphs.length).toBe 1
          expect(normals.length).toBe 1

        it "spans full width of graph", ->
          expect(+normals[0].getAttribute 'width').toBe +graphWidth

        it "is the expected height", ->

          # ( (Min/Max difference) / Axis Max ) * graph height = rectHeight
          normalHeight = normals[0].getAttribute 'height'
          expect(+normalHeight).toBeCloseTo(((8/60) * graphHeight),1)

        it "is positioned correctly", ->

          expect(normals[0].getAttribute 'x').toBe '0'

          # graph height - (( range max / axis max ) * graph height ) = rectY
          normalY = normals[0].getAttribute 'y'
          expected = graphHeight - ((20/60) * graphHeight)
          expect(+normalY).toBeCloseTo(expected,1)


      describe "No normal range", ->

        beforeEach ->
          graph.options.normal.min = null
          graph.options.normal.max = null

          graphlib.init()
          graphlib.draw()

        it "renders normal rect with height 0", ->
          norm = document.querySelectorAll '.normal'
          expect(norm[0].getAttribute 'height').toBe '0'

    describe "Score Range", ->

      describe "One range", ->

        greens = null
        singleAbnormal = null

        beforeEach ->
          singleAbnormal = [{'class': 'green', s: 20, e: 30}]

          graph.drawables.background.data = singleAbnormal

          graphlib.init()
          graphlib.draw()

          # Grab array of 'green' rects
          greens = document.querySelectorAll('.green')
          graphs = document.querySelectorAll('.nhgraph')

          graphWidth = graphs[0].getAttribute 'width'
          graphHeight = graphs[0].getAttribute 'height'

        it "renders only one green rect inside nhgraph", ->
          expect(graphs.length).toBe 1
          expect(greens.length).toBe 1

        it "spans full width of graph", ->
          expect(+greens[0].getAttribute 'width').toBe +graphWidth

        it "is the expected height", ->

          greenHeight = greens[0].getAttribute 'height'

          # ((Range min/max difference) / Axis Max ) * graph height
          # = rectHeight
          dif = singleAbnormal[0].e - singleAbnormal[0].s
          expected = (dif/60) * graphHeight

          expect(+greenHeight).toBeCloseTo(expected + 1,1)


        it "is positioned correctly", ->

          greenY = greens[0].getAttribute 'y'
          greenX = greens[0].getAttribute 'x'

          # graph height - (( range max / axis max ) * graph height ) = rectY
          expected = graphHeight - ((singleAbnormal[0].e/60) * graphHeight)

          expect(greenX).toBe '0'
          expect(+greenY).toBeCloseTo(expected-1,1)


      it "handles no abnormal ranges", ->

        graph.drawables.background.data = null

        graphlib.init()
        graphlib.draw()

        normalRects = document.querySelectorAll '.normal'
        greenRects = document.querySelectorAll '.green'
        amberRects = document.querySelectorAll '.amber'
        graphs = document.querySelectorAll '.nhgraph'

        expect(graphs.length).toBe 1
        expect(normalRects.length).toBe 1
        expect(greenRects.length).toBe 0
        expect(amberRects.length).toBe 0


      describe "Multiple score ranges", ->

        greenRects = null
        amberRects = null
        redRects = null
        rects = null

        validAbnormal = null

        beforeEach ->

          validAbnormal = [
            {'class': 'green', s: 20, e: 30},
            {'class': 'amber', s: 30, e: 40},
            {'class': 'red', s: 40, e: 60}
          ]

          graph.drawables.background.data = validAbnormal

          graphlib.init()
          graphlib.draw()

          greenRects = document.querySelectorAll '.green'
          amberRects = document.querySelectorAll '.amber'
          redRects = document.querySelectorAll '.red'

          graphs = document.querySelectorAll '.nhgraph'

          graphWidth = graphs[0].getAttribute 'width'
          graphHeight = graphs[0].getAttribute 'height'

          rects = [greenRects[0], amberRects[0], redRects[0]]

        it "creates the right number of rects", ->
          expect(greenRects.length).toBe 1
          expect(amberRects.length).toBe 1
          expect(redRects.length).toBe 1
          expect(rects.length).toBe 3

        it "creates the right size rects", ->

          for i in [0..rects.length-1]

            rectHeight = rects[i].getAttribute 'height'
            rectWidth = rects[i].getAttribute 'width'

            expect(+rectWidth).toBe +graphWidth

            # ( (Min/Max difference) / Axis Max ) * graph height = rectHeight
            dif = validAbnormal[i].e - validAbnormal[i].s
            expected = (dif/60) * graphHeight

            expect(+rectHeight).toBeCloseTo(expected + 1,1)

        it "positions each rect correctly", ->

          for i in [0..rects.length-1]

            rectX = rects[i].getAttribute 'x'
            rectY = rects[i].getAttribute 'y'

            # graph height - (( range max / axis max ) * graph height ) = rectY
            expected = graphHeight - ((validAbnormal[i].e/60) * graphHeight)

            expect(rectX).toBe '0'
            expect(+rectY).toBeCloseTo(expected-1,1)


  describe "Labels", ->

    it "displays the correct label when provided", ->

      graph.options.label = 'RR'

      graphlib.init()

      label = document.querySelectorAll '.background .label'

      expect(label.length).toBe 1
      expect(label[0].textContent).toBe 'RR'

    it "displays the correct units when provided", ->

      graph.options.keys = ['respiration_rate']
      graph.options.label = 'RR'
      graph.options.measurement = '/min'

      graphlib.init()
      graphlib.draw()

      measure = document.querySelectorAll '.background .measurement'

      expect(measure[0].textContent).toBe '18/min'

    it "displays nothing when no label specified", ->
      graph.options.label = null
      graphlib.init()
      expect(document.querySelectorAll('.label').length).toBe 0

    it "displays multiple measurements when more than one key specified", ->
      graph.options.keys = ['respiration_rate','pulse_rate']

      graph.options.label = 'RR/HR'
      graph.options.measurement = '/min'

      graphlib.init()
      graphlib.draw()

      expect(document.querySelectorAll('.measurement').length).toBe 2

    xit "uses the 'label text height' property", ->

    xit "uses 'label width' property to prevent overlap", ->


  describe "Gridlines", ->

    horis = null
    vertis = null

    beforeEach ->

      graphlib.init()
      graphlib.draw()

      vertis = document.querySelectorAll '.background .vertical'
      horis = document.querySelectorAll '.background .horizontal'

    it "has at least one vertical grid line per tick", ->
      xTicks = document.querySelectorAll '.x .tick'
      expect(horis.length).toBeGreaterThan (xTicks.length)-1

    it "has at least one horizontal grid line per tick", ->
      yTicks = document.querySelectorAll '.y .tick'
      expect(vertis.length).toBeGreaterThan (yTicks.length)-1

    it "has evenly spaced horizontal grid lines", ->

      yPos = []

      # Create array of horizontal grid line y-values
      for line in horis
        yPos.push(+(line.getAttribute 'y1'))

      # Compare difference between each value
      lastGap = null
      for i in [1..yPos.length-1]
        if lastGap != null
          expect(yPos[i]-yPos[i-1]).toBeCloseTo(lastGap,1)
        lastGap = yPos[i]-yPos[i-1]

    it "has evenly spaced vertical grid lines", ->

      xPos = []

      # Create array of vertical grid line x-values
      for line in vertis
        xPos.push(+(line.getAttribute 'x1'))

      # Compare difference between each value
      lastGap = null
      for i in [1..xPos.length-1]
        if lastGap != null
          expect(xPos[i]-xPos[i-1]).toBeCloseTo(lastGap,1)
        lastGap = xPos[i]-xPos[i-1]
