class NHContext

  constructor: () ->
    @style = {
      margin: {
        top: 50,
        left: 0,
        right: 0,
        bottom: 20
      },
      padding: {
        top: 0,
        left: 0,
        right: 0,
        bottom: 0
      },
      dimensions: {
        height: 0,
        width: 0
      }
    }
    @graph = null
    @axes = {
      x: {
        scale: null,
        axis: null,
        min: 0,
        max: 0
      },
      y: {
        scale: null,
        axis: null,
        min: 0,
        max: 0
      }
    }
    @parent_obj = null
    @brush = null
    self = @

  init: (parent_svg) =>
    if parent_svg?
      # add element to DOM
      @.parent_obj = parent_svg
      @.obj = parent_svg.obj.append('g')
      @.obj.attr('class', 'nhcontext')
      left_offset = parent_svg.style.padding.left + @.style.margin.left
      @.obj.attr('transform', 'translate('+left_offset+','+(parent_svg.style.padding.top + @.style.margin.top)+')')
      @.style.dimensions.width = parent_svg.style.dimensions.width - ((parent_svg.style.padding.left + parent_svg.style.padding.right) + (@.style.margin.left + @.style.margin.right))
      @.obj.attr('width', @.style.dimensions.width)
      @.axes.x.min = parent_svg.data.extent.start
      @.axes.x.max = parent_svg.data.extent.end
      @.axes.x.scale = nh_graphs.time.scale().domain([@.axes.x.min, @.axes.x.max]).range([left_offset, @.style.dimensions.width])


      @.graph.init(@)
      # figure out how big the focus is going to be
      @.style.dimensions.height += @.graph.style.dimensions.height + (@.graph.style.axis.x.size.height*2)
      #@.obj.attr('height', @.style.dimensions.height)
      parent_svg.style.dimensions.height += @.style.dimensions.height + (@.style.margin.top + @.style.margin.bottom)

      #@.graph.draw(@)
      @.graph.drawables.brush = @.graph.obj.append('g').attr('class', 'brush-container')
      self = @
      @.brush = nh_graphs.svg.brush().x(@.graph.axes.x.scale).on("brush", (context=self) ->
        if nh_graphs.event.target.extent()[0].getTime() is nh_graphs.event.target.extent()[1].getTime()
          context.parent_obj.focus.redraw([context.axes.x.min, context.axes.x.max])
        else
          context.parent_obj.focus.redraw(nh_graphs.event.target.extent())
      );
      @.graph.drawables.brush.append("g").attr("class", "x brush").call(@.brush).selectAll("rect").attr("y", 0).attr("height", @.graph.style.dimensions.height)
      self = @
      window.addEventListener('context_resize', (event) ->
        self.style.dimensions.width = self.parent_obj.style.dimensions.width - ((self.parent_obj.style.padding.left + self.parent_obj.style.padding.right) + (self.style.margin.left + self.style.margin.right))
        self.obj.attr('width', self.style.dimensions.width)
        self.axes.x.scale?.range()[1] = self.style.dimensions.width
        graph_event = document.createEvent('HTMLEvents')
        graph_event.initEvent('focus_resize', true, true)
        window.dispatchEvent(graph_event)
        #self.graph.axes.x.scale.domain([extent[0], extent[1]])
        self.graph.axes.x.scale.range([0, self.style.dimensions.width])
        self.graph.redraw(@)
      )

      return
    else
      throw new Error('Context init being called before SVG initialised')

  draw: (parent_svg) ->
    @.graph.draw(@)

    return
if !window.NH
  window.NH = {}
window.NH.NHContext = NHContext