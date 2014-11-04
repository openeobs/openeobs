# NHMobile contains utilities for working with the nh_eobs_mobile controllers as well as AJAX
class Promise
  @when: (tasks...) ->
    num_uncompleted = tasks.length
    args = new Array(num_uncompleted)
    promise = new Promise()

    for task, task_id in tasks
      ((task_id) ->
        task.then(() ->
          args[task_id] = Array.prototype.slice.call(arguments)
          num_uncompleted--
          promise.complete.apply(promise, args) if num_uncompleted == 0
        )
      )(task_id)

    return promise

  constructor: () ->
    @completed = false
    @callbacks = []

  complete: () ->
    @completed = true
    @data = arguments
    for callback in @callbacks
      callback.apply callback, arguments

  then: (callback) ->
    if @completed == true
      callback.apply callback, @data
      return

    @callbacks.push callback


class NHMobile extends NHLib

 process_request: (verb, resource, data) ->
   promise = new Promise()
   req = new XMLHttpRequest()
   req.addEventListener 'readystatechange', ->
     if req.readyState is 4                        # ReadyState Complete
       successResultCodes = [200, 304]
       if req.status in successResultCodes
         data = eval('['+req.responseText+']')
         console.log 'data: ', data
         promise.complete data
       else
         new NHModal('data_error', 'Error while processing request', '<div class="block">The server returned an error while processing the request. Please check your input and resubmit</div>', ['<a href="#" data-action="close" data-target="data_error">Ok</a>'], 0, document.getElementsByTagName('body')[0])
         promise.complete false
     #else
     #    new NHModal('ajax_error', 'Error communicating with server', '<div class="block">There was an error communicating with the server, please check your network connection and try again</div>', ['<a href="#" data-action="close" data-target="ajax_error">Ok</a>'], 0, document.getElementsByTagName('body')[0])
     #    return false
   req.open verb, resource, true
   if data
     req.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
     req.send(data)
   else
     req.send()
   return promise

 constructor: () ->
   @urls = frontend_routes
   self = @
   super()

 call_resource: (url_object, data) =>
   @process_request(url_object.method, url_object.url, data)

 get_patient_info: (patient_id, self) =>
   Promise.when(@process_request('GET', this.urls.json_patient_info(patient_id).url)).then (server_data) ->
     data = server_data[0][0]
     patient_name = ''
     patient_details = ''
     if data.full_name
       patient_name += " " + data.full_name
     if data.gender
       patient_name += '<span class="alignright">' + data.gender + '</span>'
     if data.dob
       patientDOB = self.date_from_string(data.dob);
       patient_details += "<dt>DOB:</dt><dd>" + self.date_to_dob_string(patientDOB) + "</dd>"
     if data.location
       patient_details += "<dt>Location:</dt><dd>" + data.location
     if data.parent_location
       patient_details += ',' + data.parent_location + '</dd>'
     else
       patient_details += '</dd>'
     if data.ews_score
       patient_details += "<dt class='twoline'>Latest Score:</dt><dd class='twoline'>" + data.ews_score + "</dd>"
     if data.other_identifier
       patient_details += "<dt>Hospital ID:</dt><dd>" + data.other_identifier + "</dd>"
     if data.patient_identifier
       patient_details += "<dt>NHS Number:</dt><dd>" + data.patient_identifier + "</dd>"
     patient_details = '<dl>'+patient_details+'</dl><p><a href="'+self.urls['single_patient'](patient_id).url+'" id="patient_obs_fullscreen" class="button patient_obs">View Patient Observation Data</a></p>'
     new NHModal('patient_info', patient_name, patient_details, ['<a href="#" data-target="patient_info" data-action="close">Cancel</a>'], 0, document.getElementsByTagName('body')[0])
     document.getElementById('patient_obs_fullscreen').addEventListener('click', self.fullscreen_patient_info)


 fullscreen_patient_info: (event) =>
   event.preventDefault()
   container = document.createElement('div')
   container.setAttribute('class', 'full-modal')
   options = document.createElement('p')
   options_close = document.createElement('a')
   options_close.setAttribute('href', '#')
   options_close.setAttribute('id', 'closeFullModal')
   options_close.innerText = 'Close popup'
   options_close.addEventListener('click', () ->
     document.getElementsByTagName('body')[0].removeChild(document.getElementsByClassName('full-modal')[0])
   )
   options.appendChild(options_close)
   container.appendChild(options)
   page = document.createElement('iframe')
   page.setAttribute('src', event.srcElement.getAttribute('href'))
   container.appendChild(page)
   document.getElementsByTagName('body')[0].appendChild(container)



if !window.NH
  window.NH = {}
window?.NH.NHMobile = NHMobile

