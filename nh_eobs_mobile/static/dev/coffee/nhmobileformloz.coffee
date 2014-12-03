# Class that overrides specific functionality of NHMobileForm
class NHMobileFormLoz extends NHMobileForm

  constructor: () ->
    super()
    @patient_name_el = document.getElementsByClassName('news-name')[0]
    @patient_name = () ->
      @patient_name_el.textContent
    self = @


  submit_observation: (self, elements, endpoint, args) =>
    # turn form data in to serialised string and ping off to server
    serialised_string = (el.name+'='+el.value for el in elements).join("&")
    url = @.urls[endpoint].apply(this, args.split(','))
    Promise.when(@call_resource(url, serialised_string)).then (server_data) ->
      data = server_data[0][0]
      if data and data.status is 3
        new window.NH.NHModal('submit_observation', data.modal_vals['title'] + ' for ' + self.patient_name() + '?', data.modal_vals['content'], ['<a href="#" data-action="close" data-target="submit_observation">Cancel</a>', '<a href="#" data-target="submit_observation" data-action="submit" data-ajax-action="'+data.modal_vals['next_action']+'">Submit</a>'], 0, self.form)
        if 'clinical_risk' in data.score
          document.getElementById('submit_observation').classList.add('clinicalrisk-'+data.score['clinical_risk'].toLowerCase())
      else if data and data.status is 1
        triggered_tasks = ''
        buttons = ['<a href="'+self.urls['task_list']().url+'" data-action="confirm">Go to My Tasks</a>']
        if data.related_tasks.length is 1
          triggered_tasks = '<p>' + data.related_tasks[0].summary + '</p>'
          buttons.push('<a href="'+self.urls['single_task'](data.related_tasks[0].id).url+'">Confirm</a>')
        else if data.related_tasks.length > 1
          tasks = ''
          for task in data.related_tasks
           tasks += '<li><a href="'+self.urls['single_task'](task.id).url+'">'+task.summary+'</a></li>'
          triggered_tasks = '<ul class="menu">'+tasks+'</ul>'
        task_list = if triggered_tasks then triggered_tasks else '<p>Observation was submitted</p>'
        title = if triggered_tasks then 'Action required' else 'Observation successfully submitted'
        new window.NH.NHModal('submit_success', title , task_list, buttons, 0, document.getElementsByTagName('body')[0])
      else if data and data.status is 4
        new window.NH.NHModal('cancel_success', 'Task successfully cancelled', '', ['<a href="'+self.urls['task_list']().url+'" data-action="confirm" data-target="cancel_success">Go to My Tasks</a>'], 0, self.form)
      else
        new window.NH.NHModal('submit_error', 'Error submitting observation', 'Server returned an error', ['<a href="#" data-action="close" data-target="submit_error">Cancel</a>'], 0, self.form)


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