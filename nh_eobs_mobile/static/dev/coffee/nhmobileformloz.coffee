# Class that overrides specific functionality of NHMobileForm
class NHMobileFormLoz extends NHMobileForm

  constructor: () ->
    super()

  reset_input_errors: (input) =>
    container_el = input.parentNode
    error_el = container_el.getElementsByClassName('errors')[0]
    container_el.classList.remove('error')
    input.classList.remove('error')
    if error_el
      container_el.removeChild(error_el)

  add_input_errors: (input, error_string) =>
    container_el = input.parentNode
    error_el = document.createElement('div')
    error_el.setAttribute('class', 'errors')
    container_el.classList.add('error')
    input.classList.add('error')
    error_el.innerHTML = '<label for="'+input.name+'" class="error">'+error_string+'</label>'
    container_el.appendChild(error_el)

  show_triggered_elements: (field) =>
    el = document.getElementById('parent_'+field)
    el.style.display = 'inline-block'
    inp = document.getElementById(field)
    inp.classList.remove('exclude')


if !window.NH
  window.NH = {}
window?.NH.NHMobileFormLoz = NHMobileFormLoz