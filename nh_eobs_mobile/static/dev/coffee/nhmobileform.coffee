# NHMobileForm contains utilities for working with the nh_eobs_mobile observation form
class NHMobileForm extends NHMobile

 constructor: () ->
   # find the form on the page
   @form = document.getElementsByTagName('form')?[0]
   self = @
   super()
   
   # for each input in the form set up the event listeners
   for input in @form.elements
     do () ->
       switch input.localName
         when 'input'
           switch input.type
             when 'number' then input.addEventListener('change', self.validate)
             when 'submit' then input.addEventListener('click', self.submit)
         when 'select' then input.addEventListener('change', self.trigger_actions)
   
 validate: (event) =>
   event.preventDefault()
   console.log('validate')
   
 trigger_actions: (event) =>
   event.preventDefault()
   console.log('trigger')
   
 submit: (event) =>
   event.preventDefault()
   console.log('submit')

if !window.NH
  window.NH = {}
window?.NH.NHMobileForm = NHMobileForm

