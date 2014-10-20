# NHMobileForm contains utilities for working with the nh_eobs_mobile observation form
class NHMobileForm extends NHMobile

 constructor: () ->
   # find the form on the page
   @form = document.getElementsByTagName('form')?[0]
   
   # for each input in the form set up the event listeners
   for input in @form.elements
     do () ->
       switch input.localName
         when 'input'
           switch input.type
             when 'number' then input.addEventListener('change', (event) ->
               event.preventDefault()
               console.log('validate')
             )
             when 'submit' then input.addEventListener('click', (event) ->
               event.preventDefault()
               console.log('submit')
             )
         when 'select' then input.addEventListener('change', (event) ->
           event.preventDefault()
           console.log('trigger')
         )
   
 validate: (event) ->
   event.preventDefault()
   console.log('validate')
   
 trigger_actions: (event) ->
   event.preventDefault()
   console.log('trigger')
   
 submit: (event) ->
   event.preventDefault()
   console.log('submit')
   
module?.exports.NHMobileForm = NHMobileForm
window?.NH = {}
window?.NH.NHMobileForm = NHMobileForm

