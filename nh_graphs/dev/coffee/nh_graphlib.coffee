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
    @version = '0.0.1'
    self = @

    #@init(self)
    #return self

  date_from_string: (date_string) =>
    date = new Date(date_string)
    if isNaN(date.getTime())
      date = new Date(date_string.replace(' ', 'T'))
    return date

  date_to_string: (date) =>
    days = [ "Sun", "Mon", "Tues", "Wed", "Thu", "Fri", "Sat" ]
    return days[date.getDay()] + " " + + date.getDate() + '/' + @leading_zero(date.getMonth() + 1) + "/" + @leading_zero(date.getFullYear()) + " " + @leading_zero(date.getHours()) + ":" + @leading_zero(date.getMinutes())

  leading_zero: (date_element) =>
    return ("0" + date_element).slice(-2)

  mobile_date_start_change: (self, event) =>
    if self.focus?
      current_date = self.focus.axes.x.min
      dates = event.srcElement.value.split('-')
      new_date = new Date(current_date.setFullYear(dates[0], parseInt(dates[1])-1, dates[2]))
      self.focus.axes.x.min = new_date
      self.focus.redraw([new_date, self.focus.axes.x.max])
    return

  mobile_date_end_change: (self, event) =>
    if self.focus?
      current_date = self.focus.axes.x.max
      dates = event.srcElement.value.split('-')
      new_date = new Date(current_date.setFullYear(dates[0], parseInt(dates[1])-1, dates[2]))
      self.focus.axes.x.max = new_date
      self.focus.redraw([self.focus.axes.x.min, new_date])
    return

  mobile_time_start_change: (self, event) =>
    if self.focus?
      current_date = self.focus.axes.x.min
      time = event.srcElement.value.split(':')
      new_time = new Date(current_date.setHours(time[0], time[1]))
      self.focus.axes.x.min = new_time
      self.focus.redraw([new_time, self.focus.axes.x.max])
    return

  mobile_time_end_change: (self, event) =>
    if self.focus?
      current_date = self.focus.axes.x.max
      time = event.srcElement.value.split(':')
      new_time = new Date(current_date.setHours(time[0], time[1]))
      self.focus.axes.x.max = new_time
      self.focus.redraw([self.focus.axes.x.min, new_time])
    return

  redraw_resize: (self, event) =>
    self.style.dimensions.width = nh_graphs.select(self.el)?[0]?[0]?.clientWidth - (self.style.margin.left + self.style.margin.right)
    self.obj?.attr('width', self.style.dimensions.width)
    context_event = document.createEvent('HTMLEvents')
    context_event.initEvent('context_resize', true, true)
    window.dispatchEvent(context_event)
    return

  init: () ->
    # check to see if element to put svg in is defined
    if @.el?
      # figure out dimensions of svg object
      container_el = nh_graphs.select(@.el)
      @.style.dimensions.width = container_el?[0]?[0].clientWidth - (@.style.margin.left + @.style.margin.right)
      @.obj = container_el.append('svg')
      if @.data.raw.length < 2 and not @.style.time_padding
        @.style.time_padding = 100
      if @.data.raw.length > 0
        start = @.date_from_string(@.data.raw[0]['date_terminated'])
        end = @.date_from_string(@.data.raw[@.data.raw.length-1]['date_terminated'])
        if not @.style.time_padding
          @.style.time_padding = ((end-start)/@.style.dimensions.width)/500
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
        self.mobile_date_start_change(self, event)
        return
      )
      @.options.controls.date.end?.addEventListener('change', (event) ->
        self.mobile_date_end_change(self, event)
        return
      )
      @.options.controls.time.start?.addEventListener('change', (event) ->
        self.mobile_time_start_change(self, event)
        return
      )
      @.options.controls.time.end?.addEventListener('change', (event) ->
        self.mobile_time_end_change(self, event)
        return
      )
      window.addEventListener('resize', (event) ->
        self.redraw_resize(self, event)
        return
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
     container = nh_graphs.select('#table-content').append('table')
#    cards = container.selectAll('.card').data(self.data.raw.reverse()).enter().append('div').attr('class','card')
#     header = cards.append('h3').text((d) ->
#       date_to_use = self.date_from_string(d.date_terminated)
#       return ("0" + date_to_use.getHours()).slice(-2) + ":" + ("0" + date_to_use.getMinutes()).slice(-2) + " " + ("0" + date_to_use.getDate()).slice(-2) + "/" + ("0" + (date_to_use.getMonth() + 1)).slice(-2) + "/" + date_to_use.getFullYear())
#     list = cards.append('table')
     thead = container.append('thead').attr('class', 'thead')
     tbody = container.append('tbody').attr('class', 'tbody')
     header_row = [{'date_terminated': 'Date'}]

     thead.append('tr').selectAll('th')
     .data(header_row.concat(self.data.raw.reverse())).enter().append('th').html((d) ->
       date_rotate = d.date_terminated.split(' ')
       return date_rotate[1] + '<br>' + date_rotate[0]
     )
     rows = tbody.selectAll('tr.row')
     .data(self.table.keys).enter()
     .append('tr').attr('class', 'row')

     cells = rows.selectAll('td').data((d) ->
       data = [{title: d['title'], value: d['title']}]
       for obj in self.data.raw.reverse()
         if d['keys'].length is 1
           key = d['keys'][0]
           if obj[key]
             fix_val = obj[key]
             fix_val = 'False' if fix_val is false
             if d['title']
               data.push {title: d['title'], value: fix_val}
         else
           t = d['title']
           v = []
           for o in d['keys']
             v.push {title: o['title'], value: obj[o['keys'][0]]}
          if t
            data.push {title: t, value: v}
       return data
     ).enter().append('td').html((d) ->
       if typeof d.value is 'object'
         text = ''
         for o in d.value
           if o.value
             text += '<strong>'+ o.title + ':</strong> ' + o.value + '<br>'
         return text
       else
         return d.value
#       text = ''
#       if typeof d.value is 'object'
#         sub_text = '<table>'
#         for item in d.value
#            sub_text += '<tr><td>'+item.title+'</td><td>'+item.value+'</td></tr>' if item.value isnt false
#         sub_text += '</table>'
#         text += '<td>'+d.title+'</td><td>'+sub_text+'</td>'
#       else
#         d.value = 'False' if d.value is false
#         text += '<td>'+ d.title+'</td><td>' + d.value + '</td>'
#       return text
     )

#     list.selectAll('tr').data((d) ->
#       data = []
#       for key in self.table.keys
#         if key['keys'].length is 1
#           k = key['keys'][0]
#           if d[k]?
#             data.push({title: key['title'], value: d[k]})
#         else
#           t = key['title']
#           v = []
#           for o in key['keys']
#             v.push({title: o['title'], value: d[o['keys'][0]]})
#           data.push({title: t, value: v})
#       return data
#     ).enter().append('tr').html((d) ->
#       text = ''
#       #for item in d
#       if typeof d.value is 'object'
#         sub_text = '<table>'
#         for item in d.value
#           sub_text += '<tr><td>'+item.title+'</td><td>'+item.value+'</td></tr>' if item.value isnt false
#         sub_text += '</table>'
#         text += '<td>'+d.title+'</td><td>'+sub_text+'</td>'
#       else
#         d.value = 'False' if d.value is false
#         text += '<td>'+ d.title+'</td><td>' + d.value + '</td>'
#       return text
#     )

if !window.NH
  window.NH = {}
window.NH.NHGraphLib = NHGraphLib


