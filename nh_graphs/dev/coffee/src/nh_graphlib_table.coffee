# NHTable provides a table presentation of data which like a graph can be
# changed via brushing

### istanbul ignore next ###
class NHTable extends NHGraphLib

  # Properties of the table
  # - Range: is the X axis of table (i.e. like a graph's x axis based on time)
  # - Keys: An array keys to draw a table for (i.e. the columns)
  # - Obj: the table object in D3
  # - Header Row: The D3 object for the header row
  # - Data Rows: The D3 object for the table rows containing the data
  # - Title: String for the title
  # - Title Object: The D3 object containing the title
  constructor: () ->
    @range = null
    @keys = new Array()
    @obj = null
    @header_row = null
    @data_rows = null
    @title = null
    @title_obj = null
    @data = null

  # Setup the the table, which involves:
  # 1. Get the parent object (NHFocus) to render the table into
  # 2. If table has a title add it
  # 3. Setup table object and append to DOM
  # 4. Setup the range
  # 5. Setup the header row and render the column titles
  # 6. Append the tbody element to the DOM ready for drawing
  init: (parent_obj) =>
    @.parent_obj = parent_obj
    @data = @.parent_obj.parent_obj.data.raw.concat()
    @data.reverse()
    if @.title?
      @.title_obj = nh_graphs.select(@.parent_obj.parent_obj.el)
      .append('h3').html(@.title)
    @.obj = nh_graphs.select(parent_obj.parent_obj.el).append('table')
    @.obj.attr('class', 'nhtable')
    @.range =  [parent_obj.axes.x.min, parent_obj.axes.x.max]
    header = ['Date']
    for key in @.keys
      header.push(key['title'])
    @.header_row = @.obj.append('thead').append('tr')
    @.header_row.selectAll('th').data(header).enter()
    .append('th').text((d) -> return d)
    @.data_rows = @.obj.append('tbody')
    return

  # Draw the table's data rows which involves:
  # 1. Select all the tr elements in the tbody (should be none)
  # 2. For each key to be drawn see if it's within the range and return the
  # ranged subset
  # 3. For each key in subset attend a tr with the data for that key
  # 4. For each entry select all td and append a td with the value as it's
  # inner HTML value
  draw: (parent_obj) =>
    self = @
    keys = ['date_terminated']
    for key in self.keys
      keys.push(key['key'])
    self.data_rows.selectAll('tr')
    .data(() ->
      data_map = self.data.map((row) ->
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
    .html((d) ->
      data = d.value
      if d.column is 'date_terminated'
        data = self.date_to_string( \
          self.date_from_string(data), false)
        date_rotate = data.split(' ')
        if date_rotate.length is 1
          data = date_rotate[0]
        data = date_rotate[1] + ' ' + date_rotate[0]
      data)
    return

  # Draw the table's data rows which involves:
  # 1. Remove all the existing tr elements
  # 2. Select all the tr elements in the tbody (should be none)
  # 3. For each key to be drawn see if it's within the range and return the
  # ranged subset
  # 4. For each key in subset append a tr with the data for that key
  # 5. For each entry select all td and append a td with the value as it's
  # inner HTML value
  redraw: (parent_obj) =>
    self = @
    keys = ['date_terminated']
    for key in self.keys
      keys.push(key['key'])
    self.data_rows.selectAll('tr').remove()
    self.data_rows.selectAll('tr')
    .data(() ->
      data_map = self.data.map((row) ->
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
    .html((d) ->
      data = d.value
      if d.column is 'date_terminated'
        data = self.date_to_string( \
          self.date_from_string(data), false)
        date_rotate = data.split(' ')
        if date_rotate.length is 1
          data = date_rotate[0]
        data = date_rotate[1] + ' ' + date_rotate[0]
      data)
    return

### istanbul ignore if ###
if !window.NH
  window.NH = {}
window.NH.NHTable = NHTable


