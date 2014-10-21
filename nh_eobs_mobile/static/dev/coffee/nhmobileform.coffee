# NHMobileForm contains utilities for working with the nh_eobs_mobile observation form
class NHMobileForm extends NHMobile

 constructor: () ->
   # find the form on the page
   @form = document.getElementsByTagName('form')?[0]
   @form_timeout = 240*1000
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
   input = event.srcElement
   container_el = input.parentNode.parentNode
   error_el = container_el.getElementsByClassName('input-body')[0].getElementsByClassName('errors')[0]
   if input.type is 'number'
     value = parseFloat(input.value)
     min = parseFloat(input.min)
     max = parseFloat(input.max)
     container_el.classList.remove('error')
     error_el.innerHTML = ''
     if input.step is '1' and value % 1 isnt 0
       container_el.classList.add('error')
       error_el.innerHTML = 'Must be whole number'
       return
     if value < min
       container_el.classList.add('error')
       error_el.innerHTML = 'Input too low'
       return
     if value > max
       container_el.classList.add('error')
       error_el.innerHTML = 'Input too high'
       return
     if input.getAttribute('data-validation')
       criteria = eval(input.getAttribute('data-validation'))[0]
       other_input = document.getElementById(criteria[1])?.value
       if other_input and not eval(value + ' ' + criteria[0] + ' ' + other_input)
         container_el.classList.add('error')
         error_el.innerHTML = 'Input must be ' + criteria[0] + ' ' + criteria[1]
         return
   else
     # to be continued

 trigger_actions: (event) =>
   event.preventDefault()
   clearTimeout(window.form_timeout)
   window.form_timeout = setTimeout(@timeout_func, @form_timeout)
   input = event.srcElement
   value = input.value
   if input.getAttribute('data-onchange')
     actions = eval(input.getAttribute('data-onchange'))[0]
     for field in actions[value]?['hide']
       el = document.getElementById('parent_'+field)
       el.style.display = 'none'
     for field in actions[value]?['show']
       el = document.getElementById('parent_'+field)
       el.style.display = 'block'


   
 submit: (event) =>
   event.preventDefault()
   clearTimeout(window.form_timeout)
   window.form_timeout = setTimeout(@timeout_func, @form_timeout)
   console.log('submit')

if !window.NH
  window.NH = {}
window?.NH.NHMobileForm = NHMobileForm

