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

      parent_svg.style.dimensions.height += @.style.dimensions.height + (@.style.margin.top + @.style.margin.bottom)
    else
      throw new Error('Focus init being called before SVG initialised')

  draw: (parent_svg) =>
    for graph in @.graphs
      graph.draw(@)
    return

  redraw: (extent) =>
    #@.axes.x.min = extent[0]
    #@.axes.x.max = extent[1]
    for graph in @.graphs
      graph.axes.x.scale.domain([extent[0], extent[1]])
      graph.redraw(@)
    return

if !window.NH
  window.NH = {}
window.NH.NHFocus = NHFocus