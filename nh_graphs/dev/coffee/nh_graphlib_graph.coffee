Array::min=->
  Math.min.apply(null, this)

class NHGraph

  constructor: () ->
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
    @options = {
      keys: new Array(),
      label: null,
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
      ranged_values: null,
      background: {
        obj: null,
        data: null
      },
      brush: null
    }
    @obj = null
    @parent_obj = null

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

  show_popup: (string, x, y) =>
    cp = document.getElementById('chart_popup')
    cp.innerHTML = string;
    cp.style.top = y+'px'
    cp.style.left = x+'px'
    cp.classList.remove('hidden')

  hide_popup: () =>
    cp = document.getElementById('chart_popup')
    cp.classList.add('hidden')

  rangify_graph: (self, event) =>
    if event.srcElement.checked
      self.axes.y.scale.domain([self.axes.y.ranged_extent[0]-self.style.range_padding, self.axes.y.ranged_extent[1]+self.style.range_padding])
    else
      self.axes.y.scale.domain([self.axes.y.min, self.axes.y.max])
    self.redraw(self.parent_obj)
    return

  init: (parent_obj) =>
    # add element to DOM
    @.parent_obj = parent_obj
    @.obj = parent_obj.obj.append('g')
    @.obj.attr('class', 'nhgraph')
    @.style.dimensions.width = parent_obj.style.dimensions.width - ((parent_obj.style.padding.left + parent_obj.style.padding.right) + (@.style.margin.left + @.style.margin.right)) - @.style.label_width
    @.obj.attr('width', @.style.dimensions.width)
    left_offset = (parent_obj.style.padding.left + @.style.margin.left)
    top_offset = (parent_obj.style.dimensions.height + @.style.margin.top)
    #@.obj.attr('transform', 'translate('+left_offset+','+top_offset+')')
    @.drawables.background.obj = @.obj.append('g').attr('class', 'background')
    @.axes.obj = @.obj.append('g').attr('class', 'axes')
    @.drawables.data = @.obj.append('g').attr('class', 'data')

    # add xscale
    @.axes.x.min = parent_obj.axes.x.min
    @.axes.x.max = parent_obj.axes.x.max
    @.axes.x.scale = nh_graphs.time.scale().domain([@.axes.x.min, @.axes.x.max]).range([left_offset, @.style.dimensions.width])

    # add xaxis
    @.axes.x.axis = nh_graphs.svg.axis().scale(@.axes.x.scale).orient("top").ticks((@.style.dimensions.width/100)) # .tickPadding(@.style.axis_label_text_padding)
    if not @.style.axis.x.hide
      @.axes.x.obj = @.axes.obj.append("g").attr("class", "x axis").call(@.axes.x.axis)

      # sort line breaks out
      line_self = @
      @.axes.obj.selectAll(".x.axis g text").each( (d) ->
        el = nh_graphs.select(@)
        words = line_self.date_to_string(d).split(" ")
        el.text("")
        for word, i in words
          tspan = el.append("tspan").text(word)
          if i > 0
            tspan.attr("x", 0).attr("dy", "15")
        el.attr("y", "-" + (words.length * line_self.style.axis_label_text_height + line_self.style.axis_label_text_height))
      )
      @.style.axis.x.size = @.axes.x.obj[0][0].getBBox()
      @.style.dimensions.height -= @.style.axis.x.size.height
    @.obj.attr('height', @.style.dimensions.height)


    # add clippath
    @.obj.append("defs").append("clipPath").attr("class", "clip").attr('id', @.options.keys.join('-')+'-clip').append("rect").attr("width",  @.style.dimensions.width).attr("height", @.style.dimensions.height).attr("y", top_offset).attr("x", left_offset);

    # add yscale
    @.axes.y.scale = nh_graphs.scale.linear().domain([@.axes.y.min, @.axes.y.max]).range([top_offset+@style.dimensions.height, top_offset])

    #add yaxis
    @.axes.y.axis = nh_graphs.svg.axis().scale(@.axes.y.scale).orient('left')
    if not @.style.axis.y.hide
      @.axes.y.obj = @.axes.obj.append('g').attr('class', 'y axis').call(@.axes.y.axis)
      @.style.axis.y.size = @.axes.y.obj[0][0].getBBox()
    self = @
    if self.options.keys.length>1
      values = []
      for ob in self.parent_obj.parent_obj.data.raw
        values.push(ob[key] for key in self.options.keys)
      @.axes.y.ranged_extent = nh_graphs.extent(values.concat.apply([], values))
    else
      @.axes.y.ranged_extent = nh_graphs.extent(self.parent_obj.parent_obj.data.raw, (d) ->
        return d[self.options.keys[0]]
      )


    if @.options.label?
      @.drawables.background.obj.append('text').text(@.options.label).attr({
        'x': @.style.dimensions.width + @.style.label_text_height,
        'y': @.axes.y.scale(@.axes.y.min) - (@.style.label_text_height*(@.options.keys.length+1)),
        'class': 'label'
      })
      self = @
      @.drawables.background.obj.selectAll('text.measurement').data(@.options.keys).enter().append('text').text((d, i) ->
        if i isnt self.options.keys.length-1
          return self.parent_obj.parent_obj.data.raw[self.parent_obj.parent_obj.data.raw.length-1][d]
        else
          return self.parent_obj.parent_obj.data.raw[self.parent_obj.parent_obj.data.raw.length-1][d] + '' + self.options.measurement
      ).attr({
          'x': self.style.dimensions.width + self.style.label_text_height,
          'y': (d, i) ->
            self.axes.y.scale(self.axes.y.min) - (self.style.label_text_height*(self.options.keys.length-i))
          ,'class': 'measurement'
        })


    window.addEventListener('graph_resize', (event) ->
      self.style.dimensions.width = self.parent_obj.style.dimensions.width - ((self.parent_obj.style.padding.left + self.parent_obj.style.padding.right) + (self.style.margin.left + self.style.margin.right)) - @.style.label_width
      self.obj.attr('width', self.style.dimensions.width)
      self.axes.x.scale?.range()[1] = self.style.dimensions.width
      self.redraw(self.parent_obj)
    )
    self.parent_obj.parent_obj.options.controls.rangify?.addEventListener('click', (event) ->
        self.rangify_graph(self, event)
    )
    return



  draw: (parent_obj) =>
    # draw background
    self = @
    if self.drawables.background.data?
      for background_object in self.drawables.background.data
        self.drawables.background.obj.selectAll(".range").data(self.drawables.background.data).enter().append("rect").attr({
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
        });

    # draw normals
    self.drawables.background.obj.selectAll('.normal').data([self.options.normal]).enter().append("rect")
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

    # draw gridlines
    self.drawables.background.obj.selectAll(".grid.vertical").data(self.axes.x.scale.ticks()).enter().append("line").attr({
      "class": "vertical grid",
      x1: (d) ->
        return self.axes.x.scale(d)
      ,
      x2: (d) ->
        return self.axes.x.scale(d)
      ,
      y1: self.axes.y.scale.range()[1],
      y2: self.axes.y.scale.range()[0],
    });

    self.drawables.background.obj.selectAll(".grid.horizontal").data(self.axes.y.scale.ticks()).enter().append("line").attr({
      "class": "horizontal grid",
      x1: self.axes.x.scale(self.axes.x.scale.domain()[0]),
      x2: self.axes.x.scale(self.axes.x.scale.domain()[1]),
      y1: (d) ->
        return self.axes.y.scale(d)
      ,
      y2: (d) ->
        return self.axes.y.scale(d)
      ,
    });

    # draw data
    switch self.style.data_style
      when 'stepped', 'linear' then (
        self.drawables.area = nh_graphs.svg.line()
        .interpolate(if self.style.data_style is 'stepped' then "step-after" else "linear")
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
          self.drawables.data.append("path").datum(self.parent_obj.parent_obj.data.raw).attr("d", self.drawables.area).attr("clip-path", "url(#"+ self.options.keys.join('-')+'-clip' +")").attr("class", "path");

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



        self.drawables.data.selectAll(".empty_point").data(self.parent_obj.parent_obj.data.raw.filter((d) ->
          if d.none_values isnt "[]"
            return d
          )
        )
        .enter().append("circle")
        .attr("cx", (d) ->
          return self.axes.x.scale(self.date_from_string(d.date_terminated))
        )
        .attr("cy", (d) ->
          return self.axes.y.scale(self.axes.y.scale.domain()[1] / 2)
        )
        .attr("r", 3)
        .attr("class", "empty_point")
        .attr("clip-path", "url(#"+ self.options.keys.join('-')+'-clip' +")")
        .on('mouseover', (d) ->
          self.show_popup('Partial observation',event.pageX,event.pageY)
        )
        .on('mouseout', (d) ->
          self.hide_popup()
        )
      )
      when 'range' then (
        if self.options.keys.length is 2
          self.drawables.data.selectAll(".range.top").data(self.parent_obj.parent_obj.data.raw.filter((d) ->
            if d[self.options.keys[0]]
              return d
            )
          ).enter()
          .append("rect")
          .attr({
            'y': (d) ->
               return self.axes.y.scale(d[self.options.keys[0]])
            ,
            'x': (d) ->
               return self.axes.x.scale(self.date_from_string(d.date_terminated)) - (self.style.range.cap.width/2)+1
            ,
            'height': self.style.range.cap.height,
            'width': self.style.range.cap.width,
            'class': 'range top',
            'clip-path': 'url(#'+ self.options.keys.join('-')+'-clip' +')'
          })
          .on('mouseover', (d) ->
            string_to_use = ''
            for key in self.options.keys
              string_to_use += key + ': ' + d[key] + '<br>'
            self.show_popup('<p>'+string_to_use+'</p>',event.pageX,event.pageY)
          )
          .on('mouseout', (d) ->
            self.hide_popup()
          )


          self.drawables.data.selectAll(".range.bottom").data(self.parent_obj.parent_obj.data.raw.filter((d) ->
              if d[self.options.keys[1]]
                return d
            )
          ).enter()
          .append("rect")
          .attr({
              'y': (d) ->
                return self.axes.y.scale(d[self.options.keys[1]])
              ,
              'x': (d) ->
                return self.axes.x.scale(self.date_from_string(d.date_terminated)) - (self.style.range.cap.width/2)+1
              ,
              'height': self.style.range.cap.height,
              'width': self.style.range.cap.width,
              'class': 'range bottom',
              'clip-path': 'url(#'+ self.options.keys.join('-')+'-clip' +')'
            }).on('mouseover', (d) ->
            string_to_use = ''
            for key in self.options.keys
              string_to_use += key + ': ' + d[key] + '<br>'
            self.show_popup('<p>'+string_to_use+'</p>',event.pageX,event.pageY)
          )
          .on('mouseout', (d) ->
            self.hide_popup()
          )

          self.drawables.data.selectAll(".range.extent").data(self.parent_obj.parent_obj.data.raw.filter((d) ->
              if d[self.options.keys[0]] and d[self.options.keys[1]]
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
                self.axes.y.scale(d[self.options.keys[1]]) - self.axes.y.scale(d[self.options.keys[0]])
              ,
              'width': self.style.range.width,
              'class': 'range extent',
              'clip-path': 'url(#'+ self.options.keys.join('-')+'-clip' +')'
            }).on('mouseover', (d) ->
            string_to_use = ''
            for key in self.options.keys
              string_to_use += key + ': ' + d[key] + '<br>'
            self.show_popup('<p>'+string_to_use+'</p>',event.pageX,event.pageY)
          )
          .on('mouseout', (d) ->
            self.hide_popup()
          )
        else
          throw new Error('Cannot plot ranged graph with ' + self.options.keys.length + 'data points')
     )
      when 'star' then console.log('star')
      when 'pie' then console.log('pie')
      when 'sparkline' then console.log('sparkline')
      else throw new Error('no graph style defined')

  redraw: (parent_obj) =>
    self = @

    self.axes.obj.select('.x.axis').call(self.axes.x.axis)
    self.axes.obj.select('.y.axis').call(self.axes.y.axis)
    # sort line breaks out
    @.axes.obj.selectAll(".x.axis g text").each( (d) ->
      el = nh_graphs.select(@)
      words = self.date_to_string(d).split(" ")
      el.text("")
      for word, i in words
        tspan = el.append("tspan").text(word)
        if i > 0
          tspan.attr("x", 0).attr("dy", "15")
      el.attr("y", "-" + (words.length * self.style.axis_label_text_height + self.style.axis_label_text_height))
    )

    self.drawables.background.obj.selectAll('.normal')
    .attr({
        'width': self.axes.x.scale.range()[1],
        'y': (d) ->
          return self.axes.y.scale(d.max)
        'height': (d) ->
          return self.axes.y.scale(d.min) - (self.axes.y.scale(d.max))
    })

    self.drawables.background.obj.selectAll('.label').attr('x': self.axes.x.scale.range()[1] + self.style.label_text_height)
    self.drawables.background.obj.selectAll('.measurement').attr('x': self.axes.x.scale.range()[1] + self.style.label_text_height)


    # redraw grid
    self.drawables.background.obj.selectAll(".grid.vertical")
    .data(self.axes.x.scale.ticks())
    #.enter()
    .attr('x1', (d) ->
      return self.axes.x.scale(d)
    ).attr('x2', (d) ->
      return self.axes.x.scale(d)
    )
    self.drawables.background.obj.selectAll('.range')
    .attr('width', self.axes.x.scale.range()[1])
    .attr('y': (d) ->
      return self.axes.y.scale(d.e) - 1
    ).attr('height': (d) ->
      return self.axes.y.scale(d.s) - (self.axes.y.scale(d.e) - 1)
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
    self.obj.selectAll('.clip').selectAll('rect').attr('width', self.axes.x.scale.range()[1])

    #redraw data
    switch self.style.data_style
      when 'stepped', 'linear' then (
        self.drawables.data.selectAll('.path').attr("d", self.drawables.area)
        self.drawables.data.selectAll('.point').attr('cx', (d) ->
          return self.axes.x.scale(self.date_from_string(d.date_terminated))
        ).attr('cy', (d) ->
          return self.axes.y.scale(d[self.options.keys[0]])
        )
      )
      when 'range' then (
        self.drawables.data.selectAll('.range.top').attr('x', (d) ->
          return self.axes.x.scale(self.date_from_string(d.date_terminated)) - (self.style.range.cap.width/2)+1
        ).attr('y': (d) ->
          return self.axes.y.scale(d[self.options.keys[0]])
        )

        self.drawables.data.selectAll('.range.bottom').attr('x', (d) ->
          return self.axes.x.scale(self.date_from_string(d.date_terminated)) - (self.style.range.cap.width/2)+1
        ).attr('y': (d) ->
            return self.axes.y.scale(d[self.options.keys[1]])
        )

        self.drawables.data.selectAll('.range.extent').attr('x', (d) ->
          return self.axes.x.scale(self.date_from_string(d.date_terminated))
        ).attr('y': (d) ->
          return self.axes.y.scale(d[self.options.keys[0]])
        ).attr('height': (d) ->
          return self.axes.y.scale(d[self.options.keys[1]]) - self.axes.y.scale(d[self.options.keys[0]])
        )
      )
      when 'star' then console.log('star')
      when 'pie' then console.log('pie')
      when 'sparkline' then console.log('sparkline')
      else throw new Error('no graph style defined')
    return

if !window.NH
  window.NH = {}
window.NH.NHGraph = NHGraph

