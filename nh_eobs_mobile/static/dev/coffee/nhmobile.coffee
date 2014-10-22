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
   #self = @
   super()

 call_resource: (url_object, data) =>
   @process_request(url_object.method, url_object.url, data)

 get_patient_info: (patient_id) =>
   @process_request('GET', this.urls.json_patient_info(patient_id).url)




if !window.NH
  window.NH = {}
window?.NH.NHMobile = NHMobile

