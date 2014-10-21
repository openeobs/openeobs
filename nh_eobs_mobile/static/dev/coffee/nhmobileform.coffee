# NHMobileForm contains utilities for working with the nh_eobs_mobile observation form
class NHMobileForm extends NHMobile

 constructor: () ->
   # find the form on the page
   @form = document.getElementsByTagName('form')?[0]
   @form_timeout = 10*1000
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


   document.addEventListener 'form_timeout', (event) ->
     console.log('oh noes the form timed out')
   @timeout_func = () ->
     timeout = new CustomEvent('form_timeout', {'detail': 'form timed out'})
     document.dispatchEvent(timeout)
   window.form_timeout = setTimeout(window.timeout_func, @form_timeout)



 validate: (event) =>
   event.preventDefault()
   clearTimeout(window.form_timeout)
   window.form_timeout = setTimeout(@timeout_func, @form_timeout)

   console.log('validate')
   
 trigger_actions: (event) =>
   event.preventDefault()
   clearTimeout(window.form_timeout)
   window.form_timeout = setTimeout(@timeout_func, @form_timeout)
   console.log('trigger')
   
 submit: (event) =>
   event.preventDefault()
   clearTimeout(window.form_timeout)
   window.form_timeout = setTimeout(@timeout_func, @form_timeout)
   console.log('submit')

if !window.NH
  window.NH = {}
window?.NH.NHMobileForm = NHMobileForm

