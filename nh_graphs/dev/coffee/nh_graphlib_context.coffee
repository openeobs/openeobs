class NHContext

  constructor: () ->
    @style = {
      margin: {
        top: 0,
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
    self = @

  init: (parent_svg) =>
    if parent_svg?
      # add element to DOM
      @.obj = parent_svg.obj.append('g')
      @.obj.attr('class', 'nhcontext')
      @.obj.attr('transform', 'translate('+(parent_svg.style.padding.left + @.style.margin.left)+','+(parent_svg.style.padding.top + @.style.margin.top)+')')
      @.style.dimensions.width = parent_svg.style.dimensions.width - ((parent_svg.style.padding.left + parent_svg.style.padding.right) + (@.style.margin.left + @.style.margin.right))
      @.obj.attr('width', @.style.dimensions.width)

      @.graph.init(@)
      # figure out how big the focus is going to be
      @.style.dimensions.height += @.graph.style.dimensions.height
      @.obj.attr('height', @.style.dimensions.height)
      parent_svg.style.dimensions.height += @.style.dimensions.height + (@.style.margin.top + @.style.margin.bottom)
    else
      throw new Error('Context init being called before SVG initialised')

  draw: () ->
    @.graph.draw()
    return

if !window.NH
  window.NH = {}
window.NH.NHContext = NHContext