class NHFocus

  constructor: () ->
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
    }
    @graphs = new Array()
    @tables = new Array()
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
    self = @

  init: (parent_svg) =>
    if parent_svg?
      # add element to DOM
      @.parent_obj = parent_svg
      @.obj = parent_svg.obj.append('g')
      @.obj.attr('class', 'nhfocus')
      if parent_svg.context?
        @.obj.attr('transform', 'translate('+(parent_svg.style.padding.left + @.style.margin.left)+','+(((parent_svg.context.style.dimensions.height + parent_svg.context.style.margin.bottom) + parent_svg.style.padding.top) + @.style.margin.top)+')')
      else
        @.obj.attr('transform', 'translate('+(parent_svg.style.padding.left + @.style.margin.left)+','+(parent_svg.style.padding.top + @.style.margin.top)+')')
      @.style.dimensions.width = parent_svg.style.dimensions.width - ((parent_svg.style.padding.left + parent_svg.style.padding.right) + (@.style.margin.left + @.style.margin.right))
      @.obj.attr('width', @.style.dimensions.width)
      @.axes.x.min = parent_svg.data.extent.start
      @.axes.x.max = parent_svg.data.extent.end

      # figure out how big the focus is going to be
      for graph in @.graphs
        graph.init(@)
        @.style.dimensions.height += graph.style.dimensions.height + @.style.spacing
      for table in @.tables
        table.init(@)

      parent_svg.style.dimensions.height += @.style.dimensions.height + (@.style.margin.top + @.style.margin.bottom)

      self = @
      window.addEventListener('focus_resize', (event) ->
        self.style.dimensions.width = self.parent_obj.style.dimensions.width - ((self.parent_obj.style.padding.left + self.parent_obj.style.padding.right) + (self.style.margin.left + self.style.margin.right))
        self.obj.attr('width', self.style.dimensions.width)
        self.axes.x.scale?.range()[1] = self.style.dimensions.width
        if self.parent_obj.options.mobile.is_mob
          if window.innerWidth > window.innerHeight
            new_date = new Date(self.axes.x.max)
            d = new_date.getDate()-self.parent_obj.options.mobile.date_range.landscape
            new_date.setDate(d)
            self.redraw([new_date, self.axes.x.max])
          else
            new_date = new Date(self.axes.x.max)
            d = new_date.getDate()-self.parent_obj.options.mobile.date_range.portrait
            new_date.setDate(d)
            self.redraw([new_date, self.axes.x.max])
        else
          self.redraw([self.axes.x.min, self.axes.x.max])
      )
    else
      throw new Error('Focus init being called before SVG initialised')

  draw: (parent_svg) =>
    for graph in @.graphs
      graph.draw(@)

    for table in @.tables
      table.draw(@)

    return

  redraw: (extent) =>
    #@.axes.x.min = extent[0]
    #@.axes.x.max = extent[1]
    for graph in @.graphs
      graph.axes.x.scale.domain([extent[0], extent[1]])
      graph.axes.x.axis.ticks((@.style.dimensions.width/70))
      graph.axes.x.scale.range([0, @.style.dimensions.width - graph.style.label_width])
      graph.redraw(@)

    for table in @.tables
      table.range = extent
      table.redraw(@)
    return

if !window.NH
  window.NH = {}
window.NH.NHFocus = NHFocus