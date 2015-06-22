class NHTable extends NHGraphLib

  constructor: () ->
    @range = null
    @keys = new Array()
    @obj = null
    @header_row = null
    @data_rows = null
    @title = null
    @title_obj = null

  init: (parent_obj) =>
    # add element to DOM
    @.parent_obj = parent_obj
    if @.title?
      @.title_obj = nh_graphs.select(@.parent_obj.parent_obj.el)
      .append('h3').html(@.title)
    @.obj = nh_graphs.select(parent_obj.parent_obj.el).append('table')
    @.obj.attr('class', 'nhtable')

    @.range =  [parent_obj.axes.x.min, parent_obj.axes.x.max]

    #set up header
    header = ['Date']
    for key in @.keys
      header.push(key['title'])
    @.header_row = @.obj.append('thead').append('tr')
    @.header_row.selectAll('th').data(header).enter()
    .append('th').text((d) -> return d)
    @.data_rows = @.obj.append('tbody')
    return

  draw: (parent_obj) =>
    # draw background
    self = @
    keys = ['date_terminated']
    for key in self.keys
      keys.push(key['key'])
    self.data_rows.selectAll('tr')
    .data(() ->
      data_map = self.parent_obj.parent_obj.data.raw.map((row) ->
        if(self.date_from_string(row['date_terminated']) >= self.range[0] and \
        self.date_from_string(row['date_terminated']) <= self.range[1])
          return keys.map((column) ->
            return {column: column, value: row[column]}
          )
      )
      data_to_use = (data for data in data_map when data?)
      return data_to_use
    )
    .enter()
    .append('tr')
    .selectAll('td')
    .data((d) ->
      return d
    )
    .enter()
    .append('td')
    .html((d) -> d.value)
    return

  redraw: (parent_obj) =>
      # draw background
    self = @
    keys = ['date_terminated']
    for key in self.keys
      keys.push(key['key'])
    self.data_rows.selectAll('tr').remove()
    self.data_rows.selectAll('tr')
    .data(() ->
      data_map = self.parent_obj.parent_obj.data.raw.map((row) ->
        if(self.date_from_string(row['date_terminated']) >= self.range[0] and \
        self.date_from_string(row['date_terminated']) <= self.range[1])
          return keys.map((column) ->
            return {column: column, value: row[column]}
          )
      )
      data_to_use = (data for data in data_map when data?)
      return data_to_use
    )
    .enter()
    .append('tr')
    .selectAll('td')
    .data((d) ->
      return d
    )
    .enter()
    .append('td')
    .html((d) -> d.value)
    return

if !window.NH
  window.NH = {}
window.NH.NHTable = NHTable


