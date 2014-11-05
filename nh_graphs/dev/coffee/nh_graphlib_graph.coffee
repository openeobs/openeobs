class NHGraph

  constructor: () ->
    @axes = {
      x: {
        scale: null,
        axis: null,
        min: 0,
        max: 0
      }
      y: {
        scale: null,
        axis: null,
        min: 0,
        max: 0
      }
    }
    @style = {
      dimensions: {
        height: 100,
        width: 0,
      },
      margin: {
        top:0,
        right:0,
        bottom:0,
        left: 0,
      },
      padding: {
        top:0,
        right:0,
        bottom: 0,
        left: 0
      }
      data_style: '',
      norm_style: ''
    }
    @options = {
      keys: new Array(),
      label: '',
      measurement: '',
      normal: {
        min: 0,
        max: 0,
        diff: 0
      }
    }
    @drawables = {
      area: null,
      graph_object: null,
      data: null,
      initial_values: null,
      ranged_values: null
    }
    @obj = null

  init: (parent_obj) =>
    # add element to DOM
    @.obj = parent_obj.obj.append('g')
    @.obj.attr('class', 'nhgraph')
    @.obj.attr('width', parent_obj.style.dimensions.width - ((parent_obj.style.padding.left + parent_obj.style.padding.right) + (@.style.margin.left + @.style.margin.right)))
    @.obj.attr('transform', 'translate('+(parent_obj.style.padding.left + @.style.margin.left)+','+(parent_obj.style.dimensions.height + @.style.margin.top)+')')
  #@.style.dimensions.height += @.style.dimensions.height + (@.style.margin.top + @.style.margin.bottom)

  draw: () =>
    console.log('woo')

if !window.NH
  window.NH = {}
window.NH.NHGraph = NHGraph