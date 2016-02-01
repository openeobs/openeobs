# NHGraphLib includes utilities to deal with date conversion, event listening,
# drawing a tabular view of the data (for mobile) and managing a collection of
# Context, Focus, Graphs and Tables
class NHGraphLib
  constructor: (element) ->
    # Style defines the styling of the main SVG block:
    # - Margin: The offset of the SVG
    # - Padding: The internal offset of elements drawn within the SVG
    # - Dimensions: The required height and width of the SVG
    # - Label Gap: The pseudo line height of labels in SVG
    # - Axis Label Text Height: The psuedo font size of axis labels in SVG
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
    # Patient defines the details of the patient
    # - ID: The patient_id from the server
    # - Name: The name of the patient
    @patient = {
      id: 0,
      name: ''
    }
    # Options for devices and controls
    # - Mobile: Handling if is displayed on 'mobile' device and ranges for
    # device rotation
    # - Controls: collects the inputs used for date_start, date_end, time_start,
    # time_end and rangify checkbox
    # - Handler: Holds handler function's bound to this so that they can be
    # removed when graph is no longer being displayed
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
      },
      handler: {
        rangify: null,
        resize: null
      }
    }
    # Handle the DOM element to draw SVG into
    @el = if element then element else null
    # Handle the popup to show on hover on data point
    @popup = null
    # Collect the data used for graphing
    # - Raw: unmodified version of the data
    # - Extent: The date range the chart will cover
    @data = {
      raw: null,
      extent: {
        end: null,
        start: null
      }
    }
    # The JS object for the overall graph
    @obj = null
    # The JS object for the graph's context object
    @context = null
    # The JS object for the graph's focus object
    @focus = null
    # The JS object for the graph's tabular representation
    # - Element: Element to render the table into
    # - Keys: List of keys to use with the data set to render table
    @table = {
      element: null,
      keys: null
    }
    @version = '0.0.1'
    self = @

  # Create a Date Object from a string. As Odoo gives dates in a silly string
  # format need to convert to proper Date to use with D3. Attempts to convert;
  # falls back to use hack with T instead of space and finally throws error if
  # cannot convert
  date_from_string: (date_string) ->
    date = new Date(date_string)
    if isNaN(date.getTime())
      date = new Date(date_string.replace(' ', 'T'))
    if isNaN(date.getTime())
      throw new Error("Invalid date format")
    return date

  # Create a String in either Day DD/MM/YY HH:MM or DD/MM/YY HH:MM depending
  # if day flag set, throws error if invalid date passed over
  date_to_string: (date, day_flag=true) =>
    if isNaN(date.getTime())
      throw new Error("Invalid date format")
    days = [ "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat" ]
    final = ''
    if day_flag
      final += days[date.getDay()] + " "
    return  final += date.getDate() +
      '/' + @leading_zero(date.getMonth() + 1) + "/" +
      @leading_zero(date.getFullYear()) + " " + @leading_zero(date.getHours()) +
      ":" + @leading_zero(date.getMinutes())

  # Convert number like 1 into 01 and 12 into 12 (as no leading zero needed)
  leading_zero: (date_element) ->
    return ("0" + date_element).slice(-2)

  # Handle events when input defined in options.controls.date.start changed
  # 1. Gets the current date (which is graph's X axis start)
  # 2. Get the value from input
  # 3. Create date object from input value
  # 4. Set the X axis start to be the date
  # 5. Trigger redraw of focus
  mobile_date_start_change: (self, event) ->
    if self.focus?
      current_date = self.focus.axes.x.min
      dates = event.target.value.split('-')
      new_date = new Date(current_date.setFullYear(dates[0],
        parseInt(dates[1])-1, dates[2]))
      self.focus.axes.x.min = new_date
      self.focus.redraw([new_date, self.focus.axes.x.max])
    return

  # Handle events when input defined in options.controls.date.end changed
  # 1. Gets the current date (which is graph's X axis end)
  # 2. Get the value from input
  # 3. Create date object from input value
  # 4. Set the X axis end to be the date
  # 5. Trigger redraw of focus
  mobile_date_end_change: (self, event) ->
    if self.focus?
      current_date = self.focus.axes.x.max
      dates = event.target.value.split('-')
      new_date = new Date(current_date.setFullYear(dates[0],
        parseInt(dates[1])-1, dates[2]))
      self.focus.axes.x.max = new_date
      self.focus.redraw([self.focus.axes.x.min, new_date])
    return

  # Method to determine device orientation, used by NHContext and NHFocus
  # on resize event when is_mob = true
  is_landscape: () ->
    if window.innerWidth > window.innerHeight
      return 1
    else
      return 0

  # Handle events when input defined in options.controls.time.start changed
  # 1. Gets the current date (which is graph's X axis start)
  # 2. Get the value from input
  # 3. Create date object from input value
  # 4. Set the X axis start to be the date
  # 5. Trigger redraw of focus
  mobile_time_start_change: (self, event) ->
    if self.focus?
      current_date = self.focus.axes.x.min
      time = event.target.value.split(':')
      new_time = new Date(current_date.setHours(time[0], time[1]))
      self.focus.axes.x.min = new_time
      self.focus.redraw([new_time, self.focus.axes.x.max])
    return

  # Handle events when input defined in options.controls.time.end changed
  # 1. Gets the current date (which is graph's X axis end)
  # 2. Get the value from input
  # 3. Create date object from input value
  # 4. Set the X axis end to be the date
  # 5. Trigger redraw of focus
  mobile_time_end_change: (self, event) ->
    if self.focus?
      current_date = self.focus.axes.x.max
      time = event.target.value.split(':')
      new_time = new Date(current_date.setHours(time[0], time[1]))
      self.focus.axes.x.max = new_time
      self.focus.redraw([self.focus.axes.x.min, new_time])
    return

  # Handle browser resize event. Resize and redraw the graphs
  # 0. Check chart element exists
  # 1. Get the dimensions of main element
  # 2. Set the attribute for the object
  # 3. ping off a resize event to the context to handle this lower down
  redraw_resize: (event) ->
    if @is_alive() and !event.handled
      @style.dimensions.width = \
        nh_graphs.select(@el)?[0]?[0]?.clientWidth -
        (@style.margin.left + @style.margin.right)
      @obj?.attr('width', @style.dimensions.width)
      @.context.handle_resize(@.context, @.obj, event)
      event.handled = true
    return

  # Handle rangify checkbox click event
  # 1. Check graphlib element is in DOM (remove_listeners if not)
  # 2. Call rangify_graph on context graph
  # 3. Call rangify_graph on all focus graphs
  rangify_graphs: (event) ->
    if @is_alive()
      @context.graph.rangify_graph(@context.graph, event)
      for graph in @focus.graphs
        graph.rangify_graph(graph, event)

  add_listeners: () ->
    # Create debounced resize event handler bound to this
    if _?
      console.log('throttled handler used')
      @.options.handler.resize = _.debounce(
        @redraw_resize.bind(@),
        250
      )
    else
      @.options.handler.resize = @redraw_resize.bind(@)
    window.addEventListener('resize', @options.handler.resize)

    # Create rangify event handler bound to this and add listener
    rangify = @options.controls.rangify
    @options.handler.rangify = @rangify_graphs.bind(@)
    rangify?.addEventListener('click', @options.handler.rangify)

  remove_listeners: () ->
    console.log('remove listeners called')
    window.removeEventListener('resize', @options.handler.resize)
    rangify = this.options.controls.rangify
    rangify?.removeEventListener('click', this.options.handler.rangify)

  # Checks baseURI property of object (empty string if not present)
  is_alive: () ->
    if this.obj[0][0].baseURI then return true
    else
      @remove_listeners()
      return false

  # Handle the creation of the graph objects and add event listeners
  # 1. Make sure we actually have an element to draw graphs into otherwise throw
  # a 'No element specified' error
  # 2. Setup width of object based on width of the element to draw into
  # 3. Setup and append the SVG element
  # 4. Setup time padding if needed
  # 5. Ensure have data points to draw
  # 6. Set up times used for range of X axis and add/subtract minutes based on
  # time padding
  # 7. Setup focus and context if defined
  # 8. Set dimensions on SVG element
  # 9. Create popup element ready for data point roll over
  # 10. Set up event listeners for controls if present
  init: () ->
    if @.el?
      container_el = nh_graphs.select(@.el)
      @.style.dimensions.width = container_el?[0]?[0].clientWidth -
        (@.style.margin.left + @.style.margin.right)
      @.obj = container_el.append('svg')
      if @.data.raw.length < 2 and not @.style.time_padding
        @.style.time_padding = 100
      if @.data.raw.length > 0
        start = @.date_from_string(@.data.raw[0]['date_terminated'])
        end = \
          @.date_from_string(@.data.raw[@.data.raw.length-1]['date_terminated'])
        if not @.style.time_padding
          @.style.time_padding = ((end-start)/@.style.dimensions.width)/500
        start.setMinutes(start.getMinutes()-@.style.time_padding)
        @.data.extent.start = start
        end.setMinutes(end.getMinutes()+@.style.time_padding)
        @.data.extent.end = end
        @.context?.init(@)
        @.focus?.init(@)

      @.obj.attr('width', @.style.dimensions.width)
      @.obj.attr('height', @.style.dimensions.height)

      @.popup = document.createElement('div')
      @.popup.setAttribute('class', 'hidden')
      @.popup.setAttribute('id', 'chart_popup')
      document.getElementsByTagName('body')[0].appendChild(@.popup)

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
      this.add_listeners()
      return
    else
      throw new Error('No element specified')

  # Trigger the draw functions for context, focus and tabular representation
  draw: () ->
    if @.data.raw.length > 0
      @.context?.draw(@)
      @.focus?.draw(@)
      if @.table.element?
        @.draw_table(@)
    else
      throw new Error('No raw data provided')

  # Draw the tabular representation
  # 1. Get the elements
  # 2. append table header and body elements
  # 3. Create the header row using date_terminated key of date records (adding
  # Date as first header as will be used with other info). The date format used
  # is HH:MM - line break - DD/MM/YY
  # 4. For each key in the table add a new row and plot across the columns -
  # need to change booleans to Yes/No for readability
  # 5. If key is a collection of keys then need to render them inside a cell
  # used for nested info like inspired_oxygen
  draw_table: (self) ->
    table_el = nh_graphs.select(self.table.element)
    container = nh_graphs.select('#table-content').append('table')
    thead = container.append('thead').attr('class', 'thead')
    tbody = container.append('tbody').attr('class', 'tbody')
    header_row = [{'date_terminated': 'Date'}]
    raw_data = self.data.raw.reverse()
    thead.append('tr').selectAll('th')
    .data(header_row.concat(raw_data)).enter()
    .append('th').html((d) ->
      term_date = d.date_terminated
      if d.date_terminated isnt "Date"
        term_date = self.date_to_string( \
          self.date_from_string(d.date_terminated), false)
      date_rotate = term_date.split(' ')
      if date_rotate.length is 1
        return date_rotate[0]
      return date_rotate[1] + '<br>' + date_rotate[0]
    )
    rows = tbody.selectAll('tr.row')
    .data(self.table.keys).enter()
    .append('tr').attr('class', 'row')

    cells = rows.selectAll('td').data((d) ->
      data = [{title: d['title'], value: d['title']}]
      for obj in raw_data
        if d['keys'].length is 1
          key = d['keys'][0]
          if obj.hasOwnProperty(key)
            fix_val = obj[key]
            fix_val = 'No' if fix_val is false
            fix_val = 'Yes' if fix_val is true
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
            if Array.isArray(o.value) and o.value.length > 1
              o.value = o.value[1]
            text += '<strong>'+ o.title + ':</strong> ' + o.value + '<br>'
        return text
      else
        return d.value
     )

### istanbul ignore if ###
if !window.NH
  window.NH = {}

window.NH.NHGraphLib = NHGraphLib


