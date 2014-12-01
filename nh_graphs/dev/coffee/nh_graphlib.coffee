class NHGraphLib
  constructor: (element) ->
    @style = {
      margin: {
        top: 40,
        right: 0,
        left: 0,
        bottom: 40
      },
      padding: {
        top: 10,
        right: 30,
        left: 40,
        bottom: 40
      },
      dimensions: {
        height: 0,
        width: 0
      },
      label_gap: 10,
      transition_duration: 1e3,
      axis_label_text_height: 10,
      time_padding: null
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
      },
      controls: {
        date: {
          start: null,
          end: null
        },
        time: {
          start: null,
          end: null
        },
        rangify: null
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
    @table = {
      element: null,
      keys: null
    }
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

  mobile_date_start_change: (event) =>

    console.log(event.srcElement.value)

  mobile_date_end_change: (event) =>
    console.log(event.srcElement.value)

  mobile_time_start_change: (event) =>
    console.log(event.srcElement.value)

  mobile_time_end_change: (event) =>
    console.log(event.srcElement.value)

  init: () ->
    # check to see if element to put svg in is defined
    if @.el?
      # figure out dimensions of svg object
      container_el = nh_graphs.select(@.el)
      @.style.dimensions.width = container_el?[0]?[0].clientWidth - (@.style.margin.left + @.style.margin.right)
      @.obj = container_el.append('svg')
      start = @.date_from_string(@.data.raw[0]['date_terminated'])
      end = @.date_from_string(@.data.raw[@.data.raw.length-1]['date_terminated'])
      if not @.style.time_padding
        @.style.time_padding = ((end-start)/@.style.dimensions.width)/1000
      start.setMinutes(start.getMinutes()-@.style.time_padding)
      @.data.extent.start = start
      end.setMinutes(end.getMinutes()+@.style.time_padding)
      @.data.extent.end = end
      #initialise context
      @.context?.init(@)
      #initalise focus
      @.focus?.init(@)

      # append svg element to container
      @.obj.attr('width', @.style.dimensions.width)
      @.obj.attr('height', @.style.dimensions.height)

      # add popup
      @.popup = document.createElement('div')
      @.popup.setAttribute('class', 'hidden')
      @.popup.setAttribute('id', 'chart_popup')
      document.getElementsByTagName('body')[0].appendChild(@.popup)

      # add mobile date entry
      self = @
      @.options.controls.date.start?.addEventListener('change', (event) ->
        current_date = self.focus.axes.x.min
        dates = event.srcElement.value.split('-')
        new_date = new Date(current_date.setFullYear(dates[0], parseInt(dates[1])-1, dates[2]))
        self.focus.axes.x.min = new_date
        self.focus.redraw([new_date, self.focus.axes.x.max])
      )
      @.options.controls.date.end?.addEventListener('change', (event) ->
        current_date = self.focus.axes.x.max
        dates = event.srcElement.value.split('-')
        new_date = new Date(current_date.setFullYear(dates[0], parseInt(dates[1])-1, dates[2]))
        self.focus.axes.x.max = new_date
        self.focus.redraw([self.focus.axes.x.min, new_date])
      )
      @.options.controls.time.start?.addEventListener('change', (event) ->
        current_date = self.focus.axes.x.min
        time = event.srcElement.value.split(':')
        new_time = new Date(current_date.setHours(time[0], time[1]))
        self.focus.axes.x.min = new_time
        self.focus.redraw([new_time, self.focus.axes.x.max])
      )
      @.options.controls.time.end?.addEventListener('change', (event) ->
        current_date = self.focus.axes.x.max
        time = event.srcElement.value.split(':')
        new_time = new Date(current_date.setHours(time[0], time[1]))
        self.focus.axes.x.max = new_time
        self.focus.redraw([self.focus.axes.x.min, new_time])
      )
      window.addEventListener('resize', (event) ->
        self.style.dimensions.width = container_el?[0]?[0].clientWidth - (self.style.margin.left + self.style.margin.right)
        self.obj.attr('width', self.style.dimensions.width)
        context_event = document.createEvent('HTMLEvents')
        context_event.initEvent('context_resize', true, true)
        window.dispatchEvent(context_event)
      )
      return
    else
      throw new Error('No element specified')

  draw: () ->
    @.context?.draw(@)
    @.focus?.draw(@)
    if @.table.element?
      @.draw_table(@)

  draw_table: (self) ->
     table_el = nh_graphs.select(self.table.element)
     container = nh_graphs.select('#table-content').append('div')
     cards = container.selectAll('.card').data(self.data.raw.reverse()).enter().append('div').attr('class','card')
     header = cards.append('h3').text((d) ->
       date_to_use = self.date_from_string(d.date_started)
       return ("0" + date_to_use.getHours()).slice(-2) + ":" + ("0" + date_to_use.getMinutes()).slice(-2) + " " + ("0" + date_to_use.getDate()).slice(-2) + "/" + ("0" + (date_to_use.getMonth() + 1)).slice(-2) + "/" + date_to_use.getFullYear())
     list = cards.append('table')
     list.selectAll('tr').data((d) ->
       data = []
       for key in self.table.keys
         if key['keys'].length is 1
           k = key['keys'][0]
           if d[k]?
             data.push({title: key['title'], value: d[k]})
         else
           t = key['title']
           v = []
           for o in key['keys']
             v.push({title: o['title'], value: d[o['keys'][0]]})
           data.push({title: t, value: v})
       return data
     ).enter().append('tr').html((d) ->
       text = ''
       #for item in d
       if typeof d.value is 'object'
         sub_text = '<table>'
         for item in d.value
           sub_text += '<tr><td>'+item.title+'</td><td>'+item.value+'</td></tr>' if item.value isnt false
         sub_text += '</table>'
         text += '<td>'+d.title+'</td><td>'+sub_text+'</td>'
       else
         d.value = '' if d.value is false
         text += '<td>'+ d.title+'</td><td>' + d.value + '</td>'
       return text
     )

if !window.NH
  window.NH = {}
window.NH.NHGraphLib = NHGraphLib


