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
     input.classList.remove('error')
     error_el.innerHTML = ''
     if input.step is '1' and value % 1 isnt 0
       container_el.classList.add('error')
       input.classList.add('error')
       error_el.innerHTML = '<label for="'+input.name+'" class="error">Must be whole number</label>'
       return
     if value < min
       container_el.classList.add('error')
       input.classList.add('error')
       error_el.innerHTML = '<label for="'+input.name+'" class="error">Input too low</label>'
       return
     if value > max
       container_el.classList.add('error')
       input.classList.add('error')
       error_el.innerHTML = '<label for="'+input.name+'" class="error">Input too high</label>'
       return
     if input.getAttribute('data-validation')
       criteria = eval(input.getAttribute('data-validation'))[0]
       other_input = document.getElementById(criteria[1])?.value
       if other_input and not eval(value + ' ' + criteria[0] + ' ' + other_input)
         container_el.classList.add('error')
         input.classList.add('error')
         error_el.innerHTML = '<label for="'+input.name+'" class="error">Input must be ' + criteria[0] + ' ' + criteria[1] + '</label>'
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
       inp = document.getElementById(field)
       inp.classList.add('exclude')
       console.log('hiding')
     for field in actions[value]?['show']
       el = document.getElementById('parent_'+field)
       el.style.display = 'block'
       inp = document.getElementById(field)
       inp.classList.remove('exclude')
       console.log('showing')
   
 submit: (event) =>
   event.preventDefault()
   clearTimeout(window.form_timeout)
   window.form_timeout = setTimeout(@timeout_func, @form_timeout)
   form_elements = (element for element in @form.elements when not element.classList.contains('exclude'))
   valid_form = () ->
     for element in form_elements
       if element.classList.contains('error') or not element.value
         return false
     return true
   if valid_form()
     # do something with the form
     @submit_observation(@, form_elements, @form.getAttribute('ajax-action'), @form.getAttribute('ajax-args'))
     console.log('submit')
   else
     # display the partial obs dialog
     @display_partial_reasons(@)

 display_partial_reasons: (self) =>
   Promise.when(@call_resource(@.urls.json_partial_reasons())).then (data) ->
     console.log(data)
     options = ''
     for option in data[0]
       option_val = option[0]
       option_name = option[1]
       options += '<option value="'+option_val+'">'+option_name+'</option>'
     select = '<select name="partial_reason">'+options+'</select>'
     new window.NH.NHModal('partial_reasons', 'Submit partial observation', '<p class="block">Please state reason for submitting partial observation</p>'+select, ['<a href="#" data-action="close" data-target="partial_reasons">Cancel</a>', '<a href="#" data-action="confirm">Confirm</a>'], 0, self.form)

 submit_observation: (self, elements, endpoint, args) =>
   # turn form data in to serialised string and ping off to server
   serialised_string = (el.name+'='+el.value for el in elements).join("&")
   url = @.urls[endpoint].apply(this, args.split(','))
   Promise.when(@call_resource(url, serialised_string)).then (data) ->
     new window.NH.NHModal('submit_success', 'Observation successfully submitted', '<p class="block">Observation was submitted</p>', ['<a href="#" data-action="close" data-target="submit_success">Cancel</a>', '<a href="#" data-action="confirm">Confirm</a>'], 0, self.form)
   console.log(serialised_string)


if !window.NH
  window.NH = {}
window?.NH.NHMobileForm = NHMobileForm

