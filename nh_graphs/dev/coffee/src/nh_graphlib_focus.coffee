# NHFocus provides a grouping of many graphs together so they can all be
# manipulated at the same time
class NHFocus
  constructor: () ->
    # Style defines the styling of the main SVG block:
    # - Margin: The offset of the SVG
    # - Padding: The internal offset of elements drawn within the SVG
    # - Dimensions: The required height and width of the SVG
    # - Title Height: The height of the title used above context graph
    @style = {
      spacing: 20,
      margin: {
        top: 0,
        left: 0,
        right: 0,
        bottom: 0
      },
      padding: {
        top: 20,
        left: 0,
        right: 0,
        bottom: 20
      },
      dimensions: {
        height: 0,
        width: 0
      }
      title_height: 70
    }
    # Array of NHGraph objects for the focus to handle
    @graphs = new Array()
    # Array of NHTable objects for the focus to handle
    @tables = new Array()
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
    # The string for the title and the object it creates
    @title = null
    @title_obj = null
    self = @

  # Handle resize event
  handle_resize: (self, event) ->
    self.style.dimensions.width = self.parent_obj.style.dimensions.width -
      ((self.parent_obj.style.padding.left +
      self.parent_obj.style.padding.right) + (self.style.margin.left +
      self.style.margin.right))
    self.obj.attr('width', self.style.dimensions.width)
    self.axes.x.scale?.range()[1] = self.style.dimensions.width
    if self.parent_obj.options.mobile.is_mob
      if window.innerWidth > window.innerHeight
        new_date = new Date(self.axes.x.max)
        d = new_date.getDate()-
          self.parent_obj.options.mobile.date_range.landscape
        new_date.setDate(d)
        self.redraw([new_date, self.axes.x.max])
      else
        new_date = new Date(self.axes.x.max)
        d = new_date.getDate()-
          self.parent_obj.options.mobile.date_range.portrait
        new_date.setDate(d)
        self.redraw([new_date, self.axes.x.max])
    else
      self.redraw([self.axes.x.min, self.axes.x.max])

  # Setup the focus object, this involves:
  # 1. Setup up the parent SVG object
  # 2. Add title if needed
  # 3. Setup the title offset from context if present
  # 4. Add the focus group to the SVG and position it properly
  # 5. Setup the focus offset from context if present
  # 6. Setup the axis based on the axis of the parent SVG object
  # 7. Initialise the graphs and tables associated with the focus. For each
  # graph add the height to the height of the focus so it contains them all
  # 8. Setup the resize event listener
  init: (parent_svg) =>
    if parent_svg?
      @.parent_obj = parent_svg
      if @.title?
        @.title_obj = @.parent_obj.obj.append('text').text(@.title)
        .attr('class', 'title')
        if parent_svg.context?
          h_mb = parent_svg.context.style.dimensions.height +
            parent_svg.context.style.margin.bottom
          h_mn_pt = h_mb + parent_svg.style.padding.top
          final = h_mn_pt + @.style.margin.top
          @.title_obj.attr('transform', 'translate(0,'+final+')')
        else
          h_mt = parent_svg.style.padding.top + @.style.margin.top
          @.title_obj.attr('transform', 'translate(0,'+h_mt+')')
      @.obj = parent_svg.obj.append('g')
      @.obj.attr('class', 'nhfocus')
      top_offset = (parent_svg.style.padding.top + @.style.margin.top)
      if @.title?
        top_offset += @.style.title_height
      if parent_svg.context?
        pl_ml = parent_svg.style.padding.left + @.style.margin.left
        h_mb = parent_svg.context.style.dimensions.height +
          parent_svg.context.style.margin.bottom
        final = h_mb + top_offset
        @.obj.attr('transform', 'translate('+pl_ml+','+final+')')
      else
        @.obj.attr('transform', 'translate('+
          (parent_svg.style.padding.left + @.style.margin.left)+
          ','+top_offset+')')
      @.style.dimensions.width = parent_svg.style.dimensions.width -
        ((parent_svg.style.padding.left + parent_svg.style.padding.right) +
        (@.style.margin.left + @.style.margin.right))
      @.obj.attr('width', @.style.dimensions.width)
      @.axes.x.min = parent_svg.data.extent.start
      @.axes.x.max = parent_svg.data.extent.end

      for graph in @.graphs
        graph.init(@)
        @.style.dimensions.height += graph.style.dimensions.height +
          @.style.spacing

      for table in @.tables
        table.init(@)

      if @.title?
        @.style.dimensions.height += @.style.title_height


      parent_svg.style.dimensions.height += @.style.dimensions.height +
        (@.style.margin.top + @.style.margin.bottom)

      self = @
      window.addEventListener('focus_resize', (event) ->
        self.handle_resize(self, event)
      )
    # If no parent SVG object then it either doesn't exist or the focus has
    # been initialised before the SVG has been
    else
      throw new Error('Focus init being called before SVG initialised')

  # Draw the graphs and tables associated with the focus
  draw: (parent_svg) =>
    for graph in @.graphs
      graph.draw(@)
    for table in @.tables
      table.draw(@)
    return

  # Redraw the graphs and tables
  # 1. Update the axis and scales with new extent
  # 2. Trigger the redraw on the NHGraph object
  redraw: (extent) =>
    for graph in @.graphs
      graph.axes.x.scale.domain([extent[0], extent[1]])
      graph.axes.x.axis.ticks((@.style.dimensions.width/100))
      graph.axes.x.scale.range([0, @.style.dimensions.width -
        graph.style.label_width])
      graph.redraw(@)

    for table in @.tables
      table.range = extent
      table.redraw(@)
    return

if !window.NH
  window.NH = {}
window.NH.NHFocus = NHFocus

