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
        left: 50,
        bottom: 40
      },
      dimensions: {
        height: 0,
        width: 0
      },
      label_gap: 10,
      transition_duration: 1e3,
      axis_label_text_height: 10
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
    @data = {
      raw: null,
      extent: {
        end: null,
        start: null
      }
    }
    @obj = null
    @context = null
    @focus = null
    self = @
    #@init(self)
    #return self

  date_from_string: (date_string) =>
    return new Date(date_string)

  date_to_string: (date) =>
    days = [ "Sun", "Mon", "Tues", "Wed", "Thu", "Fri", "Sat" ]
    return days[date.getDay()] + " " + + date.getDate() + '/' + @leading_zero(date.getMonth() + 1) + "/" + @leading_zero(date.getFullYear()) + " " + @leading_zero(date.getHours()) + ":" + @leading_zero(date.getMinutes())

  leading_zero: (date_element) =>
    return ("0" + date_element).slice(-2)

  init: () ->
    # check to see if element to put svg in is defined
    if @.el?
      # figure out dimensions of svg object
      container_el = nh_graphs.select(@.el)
      @.style.dimensions.width = container_el?[0]?[0].clientWidth - (@.style.margin.left + @.style.margin.right)
      @.obj = container_el.append('svg')
      @.data.extent.start = @.date_from_string(@.data.raw[0]['date_terminated']);
      @.data.extent.end = @.date_from_string(@.data.raw[@.data.raw.length-1]['date_terminated']);
      #initialise context
      @.context?.init(@)
      #initalise focus
      @.focus?.init(@)

      # append svg element to container
      @.obj.attr('width', @.style.dimensions.width)
      @.obj.attr('height', @.style.dimensions.height)

      @.popup = document.createElement('div')
      @.popup.setAttribute('class', 'hidden')
      @.popup.setAttribute('id', 'chart_popup')
      document.getElementsByTagName('body')[0].appendChild(@.popup)



      return
    else
      throw new Error('No element specified')

  draw: () ->
    @.context?.draw(@)
    @.focus?.draw(@)


if !window.NH
  window.NH = {}
window.NH.NHGraphLib = NHGraphLib