# NHLib includes utilities that make working with Odoo easier by default
### istanbul ignore next ###
class NHLib

  # date format taken from Odoo
  @date_format = '%Y-%m-%d H:M:S'

  constructor: () ->
    @version = '0.0.1'

  # Certain browsers will use a space instead of the T between date and time
  # hacky fix to normalise this
  date_from_string: (date_string) ->
    date = new Date(date_string)
    ### istanbul ignore else ###
    if isNaN(date.getTime())
      date = new Date(date_string.replace(' ', 'T'))
    if isNaN(date.getTime())
      throw new Error("Invalid date format")
    return date

  date_to_string: (date) =>
    if isNaN(date.getTime())
      throw new Error("Invalid date format")
    return date.getFullYear() + "-" +  @leading_zero(date.getMonth() + 1) +
      "-" + @leading_zero(date.getDate()) + " " +
      @leading_zero(date.getHours()) +
      ":" + @leading_zero(date.getMinutes()) +
      ":" + @leading_zero(date.getSeconds())

  # Date of Birth doesn't include Time so this returns string in such a way
  date_to_dob_string: (date) =>
    if isNaN(date.getTime())
      throw new Error("Invalid date format")
    return date.getFullYear() + "-" +
      @leading_zero(date.getMonth() + 1) +
      "-" + @leading_zero(date.getDate())

  # return proper seconds based unix timestamp
  # instead of milliseconds based one which is JS default
  get_timestamp: () ->
    return Math.round(new Date().getTime()/1000)

  # add a zero string to the date and get the last two digits -
  # if date_element is double digit then will return them else it
  # with leading zero
  leading_zero: (date_element) ->
    return ("0" + date_element).slice(-2)

  # A utility for handling events
  handle_event: (raw_e, func, pref_dev, raw_args) ->
    if not raw_e.handled
      raw_e.src_el = if raw_e.srcElement then raw_e.srcElement else raw_e.target
      if pref_dev
        raw_e.preventDefault()
      args = [raw_e]
      if typeof(raw_args) isnt 'undefined'
        if not Array.isArray(raw_args)
          raw_args = [raw_args]
        for arg in raw_args
          args.push arg
      func.apply func, args
      raw_e.handled = true

### istanbul ignore else ###
if !window.NH
  window.NH = {}
window.NH.NHLib = NHLib

