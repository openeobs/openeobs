# Add min ability to Array class to find smallest value in Array

### istanbul ignore next ###
Array::min=->
  Math.min.apply(null, this)

# NHGraph provides a graphic view of data which can be manipulated via a brush
# or other method that changes the range of the axis


class NHGraph extends NHGraphLib
  constructor: () ->
    # X & Y axis for the graph and the object that holds them
    # - Scale: The D3 scale used for the axis
    # - Axis: The D3 axis used for the the axis
    # - Min & Max: The extent of the axis
    # - Obj: The object that holds the axis
    @axes = {
      x: {
        scale: null,
        axis: null,
        min: 0,
        max: 0,
        obj: null
      }
      y: {
        scale: null,
        axis: null,
        min: 0,
        max: 0,
        obj: null,
        ranged_extent: null
      }
      obj: null
    }
    # Style for the graph
    # - Dimensions: The height and width of the graph
    # - Margin: The offset from the parent focus / context
    # - Padding: The offset internally
    # - Axis: the size and visibility of X & Y axis objects
    # - Data Style: The style of the graph can be one of:
    #   - Stepped: A line graph with stepping on the line
    #   - Linear: A line graph with a linear line between points
    #   - Range: Used for plotting a range on a graph will draw a rect between
    # the points passed over and put caps on the ends for easier reading
    #   - Star: Not implemented
    #   - Pie: Not implemented
    #   - Sparkline: Not implemented
    # - Norm Style: The method used to display the normal range of a graph can
    # be one of:
    #   - Rect: A rectangle that shows a range
    #   - Line: A line that shows a value considered to be normal
    # - Axis Label Font Size: Font size for the x axis label
    # - Axis Label Line Height: The line height for the x axis label
    # - Axis label height: text height of the axis labels
    # - Axis label padding: The amount of padding applied between each label
    # - Label text height: Font size of the labels used on graphs
    # - Label width: The width designated for graph labels, this stops the graph
    # from overlapping the label
    # - Range Cap: The dimensions for the caps on the ranged graph
    # - Range Width: The width of the rectangle used for ranged graphs
    # - Range Padding: The padding applied to ranged graphs so the values don't
    # fall of the chart
    @style = {
      dimensions: {
        height: 200,
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
      },
      axis: {
        step: 0,
        x: {
          hide: false,
          size: null
        },
        y: {
          hide: false
          size: null
        }
      }
      data_style: '',
      norm_style: '',
      axis_label_font_size: 12,
      axis_label_line_height: 1.2,
      axis_label_text_height: 10,
      axis_label_text_padding: 50,
      label_text_height: 18,
      label_width: 100,
      range: {
        cap: {
          height: 2,
          width: 9
        }
        width: 2
      },
      range_padding: 1
    }
    # Options
    # - Keys: The keys from the dataset to plot. Normal a single item for
    # stepped/linear graphs, two for ranged
    # - Label: The name for the graph
    # - Measurement: The measurement of the dataset
    # - Normal: The normal range of the dataset and the difference between the
    # two values
    @options = {
      keys: new Array(),
      plot_partial: true,
      label: null,
      measurement: '',
      normal: {
        min: 0,
        max: 0,
        diff: 0
      }
    }
    # Drawables; each graph has three layers; background, area & data
    # - Area: Used by Step / Linear graphs to store the line
    # - Graph: Used to store the D3 object for the graph
    # - Data: Used to store the data points
    # - Initial values: Stores the initial range so can reset from ranged graph
    # - Ranged valued: Stores the ranged range so can switch to it
    # - Background: Stores the background layer
    #   - Obj: D3 object for background layer
    #   - Data: The data used to plot the background rectangles
    #     - [{"class": "green",s: 1, e: 4},{"class": "amber",s: 4,e: 6}]
    # - Brush: Stores the brush if the graph is associated with a NHContext
    @drawables = {
      area: null,
      graph_object: null,
      data: null,
      initial_values: null,
      ranged_values: null,
      background: {
        obj: null,
        data: null
      },
      brush: null
    }
    # Stores D3 for graph
    @obj = null
    # Link to parent NHContext or NHFocus object
    @parent_obj = null

  # Show popup at x,y position with string and remove hidden class
  show_popup: (string, x, y) ->
    cp = document.getElementById('chart_popup')
    cp.innerHTML = string
    cp.style.top = y+'px'
    cp.style.left = x+'px'
    cp.classList.remove('hidden')

  # Add hidden class to popup
  hide_popup: () ->
    cp = document.getElementById('chart_popup')
    cp.classList.add('hidden')

  # Handles rangify input event which changes the Y Axis to it's ranged scale
  # or to initial scale
  rangify_graph: (self, event) ->
    if event.target.checked
      d0 = self.axes.y.ranged_extent[0]-self.style.range_padding
      d1 = self.axes.y.ranged_extent[1]+self.style.range_padding
      self.axes.y.scale.domain([(if d0 > 0 then d0 else 0), d1])
    else
      self.axes.y.scale.domain([self.axes.y.min, self.axes.y.max])
    self.redraw(self.parent_obj)
    self.axes.y.obj.selectAll('.tick line').filter((d) ->
      if self.style.axis.step < 1
        if not (d % 1 is 0)
          return d
    ).attr('class', 'y-minor-tick')
    return

  # Handle window resize event
  resize_graph: (self, event) ->
    self.style.dimensions.width = self.parent_obj.style.dimensions.width -
      ((self.parent_obj.style.padding.left +
      self.parent_obj.style.padding.right) + (self.style.margin.left +
      self.style.margin.right)) - @.style.label_width
    self.obj.attr('width', self.style.dimensions.width)
    self.axes.x.scale?.range()[1] = self.style.dimensions.width
    self.redraw(self.parent_obj)
    return

  # Setup graph which involves:
  # 1. Append a new group to the parent NHFocus or NHContext
  # 2. Set the width and offsets for the graph
  # 3. Add groups for the drawable layers
  # 4. Setup X Axis
  # 5. Append X Axis if not set to hidden
  # 6. Process X Axis labels to add line breaks
  # 7. Amend height of graph with X Axis height
  # 8. Append the clip path so only draws data that is within range
  # 9. Set up Y Axis
  # 10. Set up labels for graph (name, measurement)
  # 11. Add graph resize event listener
  init: (parent_obj) =>
    @.parent_obj = parent_obj
    @.obj = parent_obj.obj.append('g')
    @.obj.attr('class', 'nhgraph')
    @.style.dimensions.width = parent_obj.style.dimensions.width -
      ((parent_obj.style.padding.left + parent_obj.style.padding.right) +
      (@.style.margin.left + @.style.margin.right)) - @.style.label_width
    @.obj.attr('width', @.style.dimensions.width)
    left_offset = (parent_obj.style.padding.left + @.style.margin.left)
    top_offset = (parent_obj.style.dimensions.height + @.style.margin.top)
    @.drawables.background.obj = @.obj.append('g').attr('class', 'background')
    @.axes.obj = @.obj.append('g').attr('class', 'axes')
    @.drawables.data = @.obj.append('g').attr('class', 'data')

    @.axes.x.min = parent_obj.axes.x.min
    @.axes.x.max = parent_obj.axes.x.max
    @.axes.x.scale = nh_graphs.time.scale()
    .domain([@.axes.x.min, @.axes.x.max]).range([left_offset,
      @.style.dimensions.width])

    @.axes.x.axis = nh_graphs.svg.axis().scale(@.axes.x.scale).orient("top")
    .ticks((@.style.dimensions.width/100))
    if not @.style.axis.x.hide
      @.axes.x.obj = @.axes.obj.append("g").attr("class", "x axis")
      .call(@.axes.x.axis)

      line_self = @
      tick_font_size = line_self.style.axis_label_font_size
      tick_line_height = line_self.style.axis_label_line_height
      adjusted_line = \
        Math.round(((tick_font_size * tick_line_height) * 10) / 10)
      @.axes.obj.selectAll(".x.axis g text").each( (d) ->
        el = nh_graphs.select(@)
        words = line_self.date_to_string(d).split(" ")
        el.text("")
        for word, i in words
          tspan = el.append("tspan").text(word)
          tspan.attr("style", "font-size: " + tick_font_size + "px;")
          if i > 0
            tspan.attr("x", 0).attr("dy", adjusted_line)
        top_lines = ((words.length - 1) * adjusted_line) + tick_font_size
        el.attr("y", "-" + Math.round((top_lines * 10) / 10))
      )
      @.style.axis.x.size = @.axes.x.obj[0][0].getBBox()
      @.style.dimensions.height -= @.style.axis.x.size.height
    @.obj.attr('height', @.style.dimensions.height)

    @.obj.append("defs").append("clipPath").attr("class", "clip")
    .attr('id', @.options.keys.join('-')+'-clip').append("rect")
    .attr("width",  @.style.dimensions.width)
    .attr("height", @.style.dimensions.height + 3)
    .attr("y", top_offset).attr("x", left_offset)

    @.axes.y.scale = nh_graphs.scale.linear()
    .domain([@.axes.y.min, @.axes.y.max])
    .range([top_offset+@style.dimensions.height, top_offset])
    self = @
    @.axes.y.axis = nh_graphs.svg.axis().scale(@.axes.y.scale).orient('left')
    .tickFormat(if @.style.axis.step > 0 then \
      nh_graphs.format(",." + @.style.axis.step + "f") else \
      nh_graphs.format("d")).tickSubdivide(@.style.axis.step)
    if not @.style.axis.y.hide
      @.axes.y.obj = @.axes.obj.append('g').attr('class', 'y axis')
      .call(@.axes.y.axis)
      @.style.axis.y.size = @.axes.y.obj[0][0].getBBox()

    if self.options.keys.length>1
      values = []
      for key in self.options.keys
        for ob in self.parent_obj.parent_obj.data.raw
          ## Push null if false so that extent doesn't count it as a value
          if typeof ob[key] == 'number'
            values.push(ob[key])
          else values.push(null)
      @.axes.y.ranged_extent = nh_graphs.extent(values.concat.apply([], values))
    else
      @.axes.y.ranged_extent = \
      nh_graphs.extent(self.parent_obj.parent_obj.data.raw, (d) ->
        if (typeof d[self.options.keys[0]] == 'number')
          return d[self.options.keys[0]]
        else return null
      )

    if @.options.label?
      y_label = @.axes.y.scale(@.axes.y.min) -
        (@.style.label_text_height*(@.options.keys.length+1))
      @.drawables.background.obj.append('text').text(@.options.label).attr({
        'x': @.style.dimensions.width + @.style.label_text_height,
        'y': y_label,
        'class': 'label'
      })
      self = @
      @.drawables.background.obj.selectAll('text.measurement')
      .data(@.options.keys).enter().append('text').text((d, i) ->
        raw = self.parent_obj.parent_obj.data.raw
        if i isnt self.options.keys.length-1
          ## Used in case of partial observation
          if raw[raw.length-1][d] != false
            return raw[raw.length-1][d]
          else return 'NA'
        else
          if raw[raw.length-1][d] != false
            return raw[raw.length-1][d] + '' + self.options.measurement
          else return 'NA'
      ).attr({
        'x': self.style.dimensions.width + self.style.label_text_height,
        'y': (d, i) ->
          self.axes.y.scale(self.axes.y.min) -
            (self.style.label_text_height*(self.options.keys.length-i))
        ,'class': 'measurement'
      })

    # Check normal range background data validity
    ((self) ->
      valid = true
      # Check if both have been defined
      if self.options.normal.min? and self.options.normal.max?
        min = self.options.normal.min
        max = self.options.normal.max

        # Get axis min / max values
        yMin = self.axes.y.min
        yMax = self.axes.y.max

        # Throw error if either value is NaN
        if isNaN(min) or isNaN(max)
          valid = false

        # Check values are valid
        else
          if min > yMax or min < yMin or min > max then valid = false
          if max < yMin or max > yMax or max < min then valid = false
      else
        valid = false

      if !valid
        console.log 'Invalid normal range defined'

        self.options.normal.min = 0
        self.options.normal.max = 0
    )(@)
    return

  # Draw graph which involves:
  # 1. Drawing Background objects
  #    1. Drawing background.data ranges
  #    2. Drawing Normal range
  #    3. Drawing Vertical grid
  #    4. Drawing Horizontal grid
  # 2. Drawing Area
  # 3. Drawing Data
  draw: (parent_obj) =>
    self = @
    if self.drawables.background.data?
      for background_object in self.drawables.background.data
        self.drawables.background.obj.selectAll(".range")
        .data(self.drawables.background.data).enter().append("rect").attr({
          "class": (d) ->
            return d.class + ' range'
          ,
          x: self.axes.x.scale(self.axes.x.scale.domain()[0]),
          y: (d) ->
            return self.axes.y.scale(d.e) - 1
          ,
          width: self.style.dimensions.width,
          "clip-path": "url(#"+ self.options.keys.join('-')+'-clip' +")",
          height: (d) ->
            return self.axes.y.scale(d.s) - (self.axes.y.scale(d.e) - 1)
        })

    self.drawables.background.obj.selectAll('.normal')
    .data([self.options.normal]).enter().append("rect")
    .attr({
      'class': 'normal'
      'y': (d) ->
        return self.axes.y.scale(d.max)
      ,
      'x': self.axes.x.scale(self.axes.x.scale.domain()[0]),
      'width': self.style.dimensions.width,
      'clip-path': 'url(#'+self.options.keys.join('-')+'-clip'+')',
      'height': (d) ->
        return self.axes.y.scale(d.min) - (self.axes.y.scale(d.max))
    })

    self.drawables.background.obj.selectAll(".grid.vertical")
    .data(self.axes.x.scale.ticks()).enter().append("line").attr({
      "class": "vertical grid",
      x1: (d) ->
        return self.axes.x.scale(d)
      ,
      x2: (d) ->
        return self.axes.x.scale(d)
      ,
      y1: self.axes.y.scale.range()[1],
      y2: self.axes.y.scale.range()[0],
    })

    self.drawables.background.obj.selectAll(".grid.horizontal")
    .data(self.axes.y.scale.ticks()).enter().append("line").attr({
      "class": "horizontal grid",
      x1: self.axes.x.scale(self.axes.x.scale.domain()[0]),
      x2: self.axes.x.scale(self.axes.x.scale.domain()[1]),
      y1: (d) ->
        return self.axes.y.scale(d)
      ,
      y2: (d) ->
        return self.axes.y.scale(d)
      ,
    })

    switch self.style.data_style
      # Draw a stepped or linear graph, which involves:
      # 1. Plot the line using the iterpolate style of choice
      #    1. If inconsistent values due then break the line
      # 2. Append and draw the line using the plotted points
      # 3. For each point in the line append a circle which event listeners for
      # mouseover and mouseout to control the tool tips
      # 4. For each empty point (normally used for partial observations) append
      # a circle with class 'empty_point'
      when 'stepped', 'linear' then (
        self.drawables.area = nh_graphs.svg.line()
        .interpolate(if self.style.data_style is \
          'stepped' then "step-after" else "linear")
        .defined((d) ->
          if d.none_values is "[]"
            return d
        )
        .x((d) ->
          return self.axes.x.scale(self.date_from_string(d.date_terminated))
        )
        .y((d) ->
          return self.axes.y.scale(d[self.options.keys[0]])
        )

        if self.parent_obj.parent_obj.data.raw.length > 1
          self.drawables.data.append("path")
          .datum(self.parent_obj.parent_obj.data.raw)
          .attr("d", self.drawables.area)
          .attr("clip-path", "url(#"+ self.options.keys.join('-')+'-clip' +")")
          .attr("class", "path")

        self.drawables.data.selectAll(".point")
        .data(self.parent_obj.parent_obj.data.raw.filter((d) ->
          if d.none_values is "[]"
            return d
          )
        )
        .enter().append("circle").attr("cx", (d) ->
          return self.axes.x.scale(self.date_from_string(d.date_terminated))
        ).attr("cy", (d) ->
          return self.axes.y.scale(d[self.options.keys[0]])
        ).attr("r", 3).attr("class", "point")
        .attr("clip-path", "url(#"+ self.options.keys.join('-')+'-clip' +")")
        .on('mouseover', (d) ->
          self.show_popup(d[self.options.keys[0]],event.pageX,event.pageY)
        )
        .on('mouseout', (d) ->
          self.hide_popup()
        )
        self.drawables.data.selectAll(".empty_point")
        .data(self.parent_obj.parent_obj.data.raw.filter((d) ->
          none_vals = d.none_values
          key = self.options.keys[0]
          partial = self.options.plot_partial
          if none_vals isnt "[]" and d[key] isnt false and partial
            return d
          )
        )
        .enter().append("circle")
        .attr("cx", (d) ->
          return self.axes.x.scale(self.date_from_string(d.date_terminated))
        )
        .attr("cy", (d) ->
          return self.axes.y.scale(d[self.options.keys[0]])
        )
        .attr("r", 3)
        .attr("class", "empty_point")
        .attr("clip-path", "url(#"+ self.options.keys.join('-')+'-clip' +")")
        .on('mouseover', (d) ->
          self.show_popup('Partial observation: ' + d[self.options.keys[0]],
            event.pageX,
            event.pageY)
        )
        .on('mouseout', (d) ->
          self.hide_popup()
        )
      )
      # Draw a ranged graph, which involves:
      # 1. Check that given two keys otherwise can't draw graph properly
      # 2. Draw the top caps of the range using the dimensions and offsets
      # defined in the style and add mouseover and mouseout event listeners for
      # popups
      # 3. Draw the bottom caps for the range using the dimensions and offsets
      # defined in the style and add mouseover and mouseout event listeners for
      # popups
      # 4. Draw the rectangle for the range using the dimension in the style and
      # add mouseover and mouseout event listeners for popups
      when 'range' then (
        if self.options.keys.length is 2
          self.drawables.data.selectAll(".range.top")
          .data(self.parent_obj.parent_obj.data.raw.filter((d) ->
            if d.none_values is "[]" and d[self.options.keys[0]]
              return d
            )
          ).enter()
          .append("rect")
          .attr({
            'y': (d) ->
              return self.axes.y.scale(d[self.options.keys[0]])
            ,
            'x': (d) ->
              return \
                self.axes.x.scale(self.date_from_string(d.date_terminated)) -
                (self.style.range.cap.width/2)+1
            ,
            'height': self.style.range.cap.height,
            'width': self.style.range.cap.width,
            'class': 'range top',
            'clip-path': 'url(#'+ self.options.keys.join('-')+'-clip' +')'
          })
          .on('mouseover', (d) ->
            string_to_use = ''
            for key in self.options.keys
              string_to_use += key.replace(/_/g, ' ') + ': ' + d[key] + '<br>'
            self.show_popup('<p>'+string_to_use+'</p>',event.pageX,event.pageY)
          )
          .on('mouseout', (d) ->
            self.hide_popup()
          )


          self.drawables.data.selectAll(".range.bottom")
          .data(self.parent_obj.parent_obj.data.raw.filter((d) ->
            if d.none_values is "[]" and d[self.options.keys[1]]
              return d
            )
          ).enter()
          .append("rect")
          .attr({
            'y': (d) ->
              return self.axes.y.scale(d[self.options.keys[1]])
            ,
            'x': (d) ->
              return \
                self.axes.x.scale(self.date_from_string(d.date_terminated)) -
                (self.style.range.cap.width/2)+1
            ,
            'height': self.style.range.cap.height,
            'width': self.style.range.cap.width,
            'class': 'range bottom',
            'clip-path': 'url(#'+ self.options.keys.join('-')+'-clip' +')'
          }).on('mouseover', (d) ->
            string_to_use = ''
            for key in self.options.keys
              string_to_use += key.replace(/_/g, ' ') + ': ' + d[key] + '<br>'
            self.show_popup('<p>'+string_to_use+'</p>',event.pageX,event.pageY)
          )
          .on('mouseout', (d) ->
            self.hide_popup()
          )

          self.drawables.data.selectAll(".range.extent")
          .data(self.parent_obj.parent_obj.data.raw.filter((d) ->
            top = d[self.options.keys[0]]
            bottom = d[self.options.keys[1]]
            if d.none_values is "[]" and top and bottom
              return d
            )
          ).enter()
          .append("rect")
          .attr({
            'y': (d) ->
              return self.axes.y.scale(d[self.options.keys[0]])
            ,
            'x': (d) ->
              return self.axes.x.scale(self.date_from_string(d.date_terminated))
            ,
            'height': (d) ->
              self.axes.y.scale(d[self.options.keys[1]]) -
                self.axes.y.scale(d[self.options.keys[0]])
            ,
            'width': self.style.range.width,
            'class': 'range extent',
            'clip-path': 'url(#'+ self.options.keys.join('-')+'-clip' +')'
          }).on('mouseover', (d) ->
            string_to_use = ''
            for key in self.options.keys
              string_to_use += key.replace(/_/g, ' ') + ': ' + d[key] + '<br>'
            self.show_popup('<p>'+string_to_use+'</p>',event.pageX,event.pageY)
          )
          .on('mouseout', (d) ->
            self.hide_popup()
          )

          self.drawables.data.selectAll(".range.top.empty_point")
          .data(self.parent_obj.parent_obj.data.raw.filter((d) ->
            none_vals = d.none_values
            key = self.options.keys[0]
            partial = self.options.plot_partial
            if none_vals isnt "[]" and d[key] isnt false and partial
              return d
            )
          ).enter()
          .append("rect")
          .attr({
            'y': (d) ->
              return self.axes.y.scale(d[self.options.keys[0]])
            ,
            'x': (d) ->
              return \
                self.axes.x.scale(self.date_from_string(d.date_terminated)) -
                (self.style.range.cap.width/2)+1
            ,
            'height': self.style.range.cap.height,
            'width': self.style.range.cap.width,
            'class': 'range top empty_point',
            'clip-path': 'url(#'+ self.options.keys.join('-')+'-clip' +')'
          })
          .on('mouseover', (d) ->
            string_to_use = 'Partial Observation:<br>'
            for key in self.options.keys
              string_to_use += key.replace(/_/g, ' ') + ': ' + d[key] + '<br>'
            self.show_popup('<p>'+string_to_use+'</p>',
              event.pageX,
              event.pageY)
          )
          .on('mouseout', (d) ->
            self.hide_popup()
          )


          self.drawables.data.selectAll(".range.bottom.empty_point")
          .data(self.parent_obj.parent_obj.data.raw.filter((d) ->
            none_vals = d.none_values
            key = self.options.keys[1]
            partial = self.options.plot_partial
            if none_vals isnt "[]" and d[key] isnt false and partial
              return d
            )
          ).enter()
          .append("rect")
          .attr({
            'y': (d) ->
              return self.axes.y.scale(d[self.options.keys[1]])
            ,
            'x': (d) ->
              return \
                self.axes.x.scale(self.date_from_string(d.date_terminated)) -
                (self.style.range.cap.width/2)+1
            ,
            'height': self.style.range.cap.height,
            'width': self.style.range.cap.width,
            'class': 'range bottom empty_point',
            'clip-path': 'url(#'+ self.options.keys.join('-')+'-clip' +')'
          }).on('mouseover', (d) ->
            string_to_use = 'Partial Observation:<br>'
            for key in self.options.keys
              string_to_use += key.replace(/_/g, ' ') + ': ' + d[key] + '<br>'
            self.show_popup('<p>'+string_to_use+'</p>',
              event.pageX,
              event.pageY)
          )
          .on('mouseout', (d) ->
            self.hide_popup()
          )

          self.drawables.data.selectAll(".range.extent.empty_point")
          .data(self.parent_obj.parent_obj.data.raw.filter((d) ->
            partial = self.options.plot_partial
            top = d[self.options.keys[0]]
            bottom = d[self.options.keys[1]]
            none_vals = d.none_values
            keys_valid = top isnt false and bottom isnt false
            if none_vals isnt "[]" and keys_valid and partial
              return d
            )
          ).enter()
          .append("rect")
          .attr({
            'y': (d) ->
              return self.axes.y.scale(d[self.options.keys[0]])
            ,
            'x': (d) ->
              return self.axes.x.scale(
                self.date_from_string(d.date_terminated))
            ,
            'height': (d) ->
              self.axes.y.scale(d[self.options.keys[1]]) -
                self.axes.y.scale(d[self.options.keys[0]])
            ,
            'width': self.style.range.width,
            'class': 'range extent empty_point',
            'clip-path': 'url(#'+ self.options.keys.join('-')+'-clip' +')'
          }).on('mouseover', (d) ->
            string_to_use = 'Partial Observation<br>'
            for key in self.options.keys
              string_to_use += key.replace(/_/g, ' ') + ': ' + d[key] + '<br>'
            self.show_popup('<p>'+string_to_use+'</p>',
              event.pageX,
              event.pageY)
          )
          .on('mouseout', (d) ->
            self.hide_popup()
          )
        else
          # Throw error if given incorrect number of keys to plot
          throw new Error('Cannot plot ranged graph with ' +
            self.options.keys.length + ' data point(s)')
     )
      when 'star' then console.log('star')
      when 'pie' then console.log('pie')
      when 'sparkline' then console.log('sparkline')
      # Throw an error if graph style isn't defined
      else throw new Error('no graph style defined')

  # Redraw graph data on changes from NHFocus or NHContext, which involves:
  # 1. Redrawing Axis
  # 2. Reformatting the X Axis tick labels
  # 3. Redrawing the background layer ranges with the new Axis scales
  # 4. Redrawing the normal ranges with the new Axis scales
  # 5. Redrawing the Vertical Grid
  # 6. Redrawing the Horizontal Grid
  # 7. Redrawing the clip path so it hides everything properly
  # 8. Redrawing the data
  redraw: (parent_obj) =>
    self = @
    self.axes.obj.select('.x.axis').call(self.axes.x.axis)
    self.axes.obj.select('.y.axis').call(self.axes.y.axis)
    tick_font_size = self.style.axis_label_font_size
    tick_line_height = self.style.axis_label_line_height
    adjusted_line = tick_font_size * tick_line_height
    @.axes.obj.selectAll(".x.axis g text").each( (d) ->
      el = nh_graphs.select(@)
      words = self.date_to_string(d).split(" ")
      el.text("")
      for word, i in words
        tspan = el.append("tspan").text(word)
        tspan.attr("style", "font-size: " + tick_font_size + "px;")
        if i > 0
          tspan.attr("x", 0).attr("dy", adjusted_line)
      top_lines = ((words.length - 1) * adjusted_line) + tick_font_size
      el.attr("y", "-" + Math.round((top_lines * 10) / 10))
    )

    self.drawables.background.obj.selectAll('.range')
    .attr('width', self.axes.x.scale.range()[1])
    .attr('y': (d) ->
      return self.axes.y.scale(d.e) - 1
    ).attr('height': (d) ->
      return self.axes.y.scale(d.s) - (self.axes.y.scale(d.e) - 1)
    )

    self.drawables.background.obj.selectAll('.normal')
    .attr({
      'width': self.axes.x.scale.range()[1],
      'y': (d) ->
        return self.axes.y.scale(d.max)
      'height': (d) ->
        return self.axes.y.scale(d.min) - (self.axes.y.scale(d.max))
    })

    self.drawables.background.obj.selectAll('.label')
    .attr('x': self.axes.x.scale.range()[1] + self.style.label_text_height)
    self.drawables.background.obj.selectAll('.measurement')
    .attr('x': self.axes.x.scale.range()[1] + self.style.label_text_height)

    self.drawables.background.obj.selectAll(".grid.vertical")
    .data(self.axes.x.scale.ticks())
    .attr('x1', (d) ->
      return self.axes.x.scale(d)
    ).attr('x2', (d) ->
      return self.axes.x.scale(d)
    )

    self.drawables.background.obj.selectAll('.grid.horizontal')
    .data(self.axes.y.scale.ticks())
    .attr('x2', self.axes.x.scale.range()[1])
    .attr('y1', (d) ->
      return self.axes.y.scale(d)
    )
    .attr('y2', (d) ->
      return self.axes.y.scale(d)
    )
    self.obj.selectAll('.clip').selectAll('rect')
    .attr('width', self.axes.x.scale.range()[1])

    switch self.style.data_style
      # Redraw the line and points of the stepped and linear graphs with the
      # new scales
      when 'stepped', 'linear' then (
        self.drawables.data.selectAll('.path').attr("d", self.drawables.area)
        self.drawables.data.selectAll('.point').attr('cx', (d) ->
          return self.axes.x.scale(self.date_from_string(d.date_terminated))
        ).attr('cy', (d) ->
          return self.axes.y.scale(d[self.options.keys[0]])
        )
        self.drawables.data.selectAll('.empty_point').attr('cx', (d) ->
          return self.axes.x.scale(self.date_from_string(d.date_terminated))
        ).attr("cy", (d) ->
          return self.axes.y.scale(d[self.options.keys[0]])
        )
      )
      # Redraw the range caps and extent with the new scales
      when 'range' then (
        self.drawables.data.selectAll('.range.top').attr('x', (d) ->
          return self.axes.x.scale(self.date_from_string(d.date_terminated)) -
            (self.style.range.cap.width/2)+1
        ).attr('y': (d) ->
          return self.axes.y.scale(d[self.options.keys[0]])
        )

        self.drawables.data.selectAll('.range.bottom').attr('x', (d) ->
          return self.axes.x.scale(self.date_from_string(d.date_terminated)) -
            (self.style.range.cap.width/2)+1
        ).attr('y': (d) ->
          return self.axes.y.scale(d[self.options.keys[1]])
        )

        self.drawables.data.selectAll('.range.extent').attr('x', (d) ->
          return self.axes.x.scale(self.date_from_string(d.date_terminated))
        ).attr('y': (d) ->
          return self.axes.y.scale(d[self.options.keys[0]])
        ).attr('height': (d) ->
          return self.axes.y.scale(d[self.options.keys[1]]) -
            self.axes.y.scale(d[self.options.keys[0]])
        )
      )

      when 'star' then console.log('star')

      when 'pie' then console.log('pie')

      when 'sparkline' then console.log('sparkline')
      # If no graph style defined throw an error
      else throw new Error('no graph style defined')
    return

### istanbul ignore if ###
if !window.NH
  window.NH = {}
window.NH.NHGraph = NHGraph

