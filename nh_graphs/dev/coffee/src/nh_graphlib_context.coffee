# NHContext provides a context graph for modifying the focus graphs via a brush
# or input boxes
class NHContext extends NHGraphLib
  constructor: () ->
    # Style defines the styling of the main SVG block:
    # - Margin: The offset of the SVG
    # - Padding: The internal offset of elements drawn within the SVG
    # - Dimensions: The required height and width of the SVG
    # - Title Height: The height of the title used above context graph
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
      },
      title_height: 80
    }
    # The graph that the context is associated with
    @graph = null
    # The X & Y axes used with the graph
    # - Scale: The scale that the axis is drawn to
    # - Axis: The D3 axis object
    # - Min & Max: The start and end of the scale
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
    # The parent SVG object
    @parent_obj = null
    # The brush object used for selecting a subset of data points in the context
    @brush = null
    # The string for the title and the object it creates
    @title = null
    @title_obj = null
    self = @

  # Handle resize events and update focus and controls
  # 1. update width of context
  # 2. Update range extent to new width
  # 3. fire of the focus resize event
  # 4. If mobile check rotation and use this update the scale and update the
  # control inputs
  # 5. Update the range and ticks for the X axis
  # 6. Redraw the graph
  handle_resize: (self, parent_svg, event) =>
    self.style.dimensions.width = self.parent_obj.style.dimensions.width -
          ((self.parent_obj.style.padding.left +
          self.parent_obj.style.padding.right) +
          (self.style.margin.left + self.style.margin.right))
    self.obj.attr('width', self.style.dimensions.width)
    self.axes.x.scale?.range()[1] = self.style.dimensions.width
    graph_event = document.createEvent('HTMLEvents')
    graph_event.initEvent('focus_resize', true, true)
    window.dispatchEvent(graph_event)
    if self.parent_obj.options.mobile.is_mob
      new_date = new Date(self.axes.x.max)
      if window.innerWidth > window.innerHeight
        d = new_date.getDate()-
          self.parent_obj.options.mobile.date_range.landscape
        new_date.setDate(d)
        self.graph.axes.x.scale.domain([new_date, self.axes.x.max])
      else
        d = new_date.getDate()-
          self.parent_obj.options.mobile.date_range.portrait
        new_date.setDate(d)
        self.graph.axes.x.scale.domain([new_date, self.axes.x.max])

      self.parent_obj.options.controls.date.start?.value = \
        new_date.getFullYear() + '-' +
        self.leading_zero(new_date.getMonth()+1) + '-' +
        self.leading_zero(new_date.getDate())
      self.parent_obj.options.controls.date.end?.value = \
        self.axes.x.max.getFullYear() + '-' +
        self.leading_zero(self.axes.x.max.getMonth()+1) + '-' +
        self.leading_zero(self.axes.x.max.getDate())
      self.parent_obj.options.controls.time.start?.value = \
        self.leading_zero(new_date.getHours()) + ':' +
        self.leading_zero(new_date.getMinutes())
      self.parent_obj.options.controls.time.end?.value = \
        self.leading_zero(self.axes.x.max.getHours()) + ':' +
        self.leading_zero(self.axes.x.max.getMinutes())

    self.graph.axes.x.scale.range([0, self.style.dimensions.width -
      self.graph.style.label_width])
    self.graph.axes.x.axis.ticks((self.style.dimensions.width/100))
    self.graph.redraw(@)
    return

  # Handle brush events and update focus and controls
  # 1. Get new extent from brush
  # 2. Check the extent of the brush if the extent is zero difference then reset
  # the extent to the normal extent
  # 3. Update the controls with the next values for the extent
  handle_brush: (self, context) ->
    new_extent_start = nh_graphs.event.target.extent()[0]
    new_extent_end = nh_graphs.event.target.extent()[1]
    if new_extent_start.getTime() is new_extent_end.getTime()
      new_extent_start = context.axes.x.min
      new_extent_end = context.axes.x.max
      context.parent_obj.focus.redraw([context.axes.x.min,
        context.axes.x.max])
    else
      context.parent_obj.focus.redraw(nh_graphs.event.target.extent())

    self.parent_obj.options.controls.date.start?.value = \
      new_extent_start.getFullYear() + '-' +
      self.leading_zero(new_extent_start.getMonth()+1) + '-' +
      self.leading_zero(new_extent_start.getDate())
    self.parent_obj.options.controls.date.end?.value =  \
      new_extent_end.getFullYear() + '-' +
      self.leading_zero(new_extent_end.getMonth()+1) + '-' +
      self.leading_zero(new_extent_end.getDate())
    self.parent_obj.options.controls.time.start?.value = \
      self.leading_zero(new_extent_start.getHours()) + ':' +
        self.leading_zero(new_extent_start.getMinutes())
    self.parent_obj.options.controls.time.end?.value = \
      self.leading_zero(new_extent_end.getHours()) + ':' +
        self.leading_zero(new_extent_end.getMinutes())

  # Setup the context object, this involves:
  # 1. Setup up the parent SVG object
  # 2. Setting up the left offset for the axis labels
  # 3. Add title if needed
  # 4. Add the context group to the SVG and position it properly
  # 5. Setup the axis based on the axis of the parent SVG object
  # 6. Initialise the graph associated with the context
  # 7. Show/Hide the axis if needed
  # 8. Setup the brush object and event listener
  # 9. Setup the values on the control inputs
  # 10. Add the brush to the SVG
  # 11. Setup the resize event listener
  init: (parent_svg) =>
    if parent_svg?
      @.parent_obj = parent_svg
      left_offset = parent_svg.style.padding.left + @.style.margin.left
      if @.title?
        @.title_obj = parent_svg.obj.append('text').text(@.title)
        .attr('class', 'title').attr('transform', 'translate(0,'+
          (parent_svg.style.padding.top + @.style.margin.top)+')')
      @.obj = parent_svg.obj.append('g')
      @.obj.attr('class', 'nhcontext')
      if @.title?
        @.obj.attr('transform', 'translate('+left_offset+','+
          (parent_svg.style.padding.top + @.style.margin.top +
          @.style.title_height)+')')
      else
        @.obj.attr('transform', 'translate('+left_offset+','+
          (parent_svg.style.padding.top + @.style.margin.top)+')')

      @.style.dimensions.width = parent_svg.style.dimensions.width -
        ((parent_svg.style.padding.left + parent_svg.style.padding.right) +
        (@.style.margin.left + @.style.margin.right))
      @.obj.attr('width', @.style.dimensions.width)
      @.axes.x.min = parent_svg.data.extent.start
      @.axes.x.max = parent_svg.data.extent.end
      @.axes.x.scale = nh_graphs.time.scale()
      .domain([@.axes.x.min, @.axes.x.max])
      .range([left_offset, @.style.dimensions.width])


      @.graph.init(@)
      if @.title? and not @.graph.style.axis.x.hide
        @.style.dimensions.height += @.graph.style.dimensions.height +
          (@.graph.style.axis.x.size.height*2) + @.style.title_height
      else
        @.style.dimensions.height += @.graph.style.dimensions.height
      parent_svg.style.dimensions.height += @.style.dimensions.height +
        (@.style.margin.top + @.style.margin.bottom)

      @.graph.drawables.brush = @.graph.obj.append('g').attr('class',
        'brush-container')
      self = @
      @.brush = nh_graphs.svg.brush().x(@.graph.axes.x.scale)
      .on("brush", (context=self) ->
        self.handle_brush(self, context)
      )
      @.graph.drawables.brush.append("g").attr("class", "x brush")
      .call(@.brush).selectAll("rect").attr("y", 0)
      .attr("height", @.graph.style.dimensions.height)
      self = @
      window.addEventListener('context_resize', (event) ->
        self.handle_resize(self, parent_svg, event)
      )
      return
    # If no parent SVG object then it either doesn't exist or the context has
    # been initialised before the SVG has been
    else
      throw new Error('Context init being called before SVG initialised')

  # Draw the graph assigned to the context
  draw: (parent_svg) ->
    @.graph.draw(@)
    return

if !window.NH
  window.NH = {}
window.NH.NHContext = NHContext


