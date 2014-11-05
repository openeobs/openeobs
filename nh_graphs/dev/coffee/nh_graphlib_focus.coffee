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
        left: 20,
        right: 20,
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
    self = @

  init: (parent_svg) =>
    if parent_svg?
      # add element to DOM
      @.obj = parent_svg.obj.append('g')
      @.obj.attr('class', 'nhfocus')
      if parent_svg.context?
        @.obj.attr('transform', 'translate('+(parent_svg.style.padding.left + @.style.margin.left)+','+(((parent_svg.context.style.dimensions.height + parent_svg.context.style.margin.bottom) + parent_svg.style.padding.top) + @.style.margin.top)+')')
      else
        @.obj.attr('transform', 'translate('+(parent_svg.style.padding.left + @.style.margin.left)+','+(parent_svg.style.padding.top + @.style.margin.top)+')')
      @.style.dimensions.width = parent_svg.style.dimensions.width - ((parent_svg.style.padding.left + parent_svg.style.padding.right) + (@.style.margin.left + @.style.margin.right))
      @.obj.attr('width', @.style.dimensions.width)
      # figure out how big the focus is going to be
      for graph in @.graphs
        graph.init(@)
        @.style.dimensions.height += graph.style.dimensions.height + @.style.spacing
      parent_svg.style.dimensions.height += @.style.dimensions.height + (@.style.margin.top + @.style.margin.bottom)
    else
      throw new Error('Focus init being called before SVG initialised')

  draw: () =>
    for graph in @.graphs
      graph.draw()
    return

if !window.NH
  window.NH = {}
window.NH.NHFocus = NHFocus