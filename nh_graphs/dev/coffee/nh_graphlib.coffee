class NHGraphLib

  constructor: (element) ->
    @style = {
      margin: {
        top: 40,
        right: 60,
        left: 40,
        bottom: 40
      },
      padding: {
        top: 10,
        right: 20,
        left: 30,
        bottom: 40
      },
      dimensions: {
        height: 0,
        width: 0
      },
      label_gap: 10,
      transition_duration: 1e3
    }
    @patient = {
      id: 0,
      name: ''
    }
    @options = {
      mobile: {
        is_mob: false,
        date_range: {
          portrait: 1,
          landscape: 5
        }
      }
    }
    @el = if element then element else null
    @popup = null
    @data = null
    @obj = null
    @context = null
    @focus = null
    self = @
    #@init(self)
    #return self


  init: () ->
    # check to see if element to put svg in is defined
    if @.el?
      # figure out dimensions of svg object
      container_el = nh_graphs.select(@.el)
      @.style.dimensions.width = container_el?[0]?[0].clientWidth - (@.style.margin.left + @.style.margin.right)
      @.obj = container_el.append('svg')
      #initialise context
      @.context?.init(@)
      #initalise focus
      @.focus?.init(@)

      # append svg element to container
      @.obj.attr('width', @.style.dimensions.width)
      @.obj.attr('height', @.style.dimensions.height)
      return
    else
      throw new Error('No element specified')


if !window.NH
  window.NH = {}
window.NH.NHGraphLib = NHGraphLib