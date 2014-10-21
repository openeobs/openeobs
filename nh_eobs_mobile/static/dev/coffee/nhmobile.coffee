# NHMobile contains utilities for working with the nh_eobs_mobile controllers as well as AJAX
class NHMobile extends NHLib

 process_request: (verb, resource) ->
   req = new XMLHttpRequest()
   req.addEventListener 'readystatechange', ->
     if req.readyState is 4                        # ReadyState Complete
       successResultCodes = [200, 304]
       if req.status in successResultCodes
         data = eval '(' + req.responseText + ')'
         console.log 'data message: ', data.message
       else
         new NHModal('data_error', 'Error while processing request', 'The server returned an error while processing the request. Please check your input and resubmit', ['<a href="#" data-action="close" data-target="data_error">Ok</a>'], 0, document.getElementsByTagName('body')[0])
     else
         new NHModal('ajax_error', 'Error communicating with server', 'There was an error communicating with the server, please check your network connection and try again', ['<a href="#" data-action="close" data-target="ajax_error">Ok</a>'], 0, document.getElementsByTagName('body')[0])
   req.open verb, resource, false
   req.send()

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

