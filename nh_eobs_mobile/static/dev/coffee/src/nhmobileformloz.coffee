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
        sub = '<a href="#" data-target="submit_observation" ' +
          'data-action="submit" data-ajax-action="'+
           data.modal_vals['next_action']+'">Submit</a>'
        cancel = '<a href="#" data-action="close" ' +
          'data-target="submit_observation">Cancel</a>'
        new window.NH.NHModal('submit_observation',
            data.modal_vals['title'] + ' for ' + self.patient_name() + '?',
            data.modal_vals['content'],
            [cancel, sub],
            0, self.form)
        if 'clinical_risk' in data.score
          sub_ob = document.getElementById('submit_observation')
          cls = 'clinicalrisk-'+data.score['clinical_risk'].toLowerCase()
          sub_ob.classList.add(cls)
      else if data and data.status is 1
        triggered_tasks = ''
        task_url = self.urls['task_list']().url
        btn_str = '<a href="'+task_url+'" data-action="confirm">' +
          'Go to My Tasks</a>'
        buttons = [btn_str]
        if data.related_tasks.length is 1
          triggered_tasks = '<p>' + data.related_tasks[0].summary + '</p>'
          task_url = self.urls['single_task'](data.related_tasks[0].id).url
          buttons.push('<a href="'+task_url+'">Confirm</a>')
        else if data.related_tasks.length > 1
          tasks = ''
          for task in data.related_tasks
            task_url = self.urls['single_task'](task.id).url
            tasks += '<li><a href="'+task_url+'">'+task.summary+'</a></li>'
          triggered_tasks = '<ul class="menu">'+tasks+'</ul>'
        obs_sub = '<p>Observation was submitted</p>'
        task_list = if triggered_tasks then triggered_tasks else obs_sub
        ob_s = 'Observation successfully submitted'
        title = if triggered_tasks then 'Action required' else ob_s
        new window.NH.NHModal('submit_success',
        title , task_list,
        buttons, 0, document.getElementsByTagName('body')[0])
      else if data and data.status is 4
        task_button = '<a href="'+self.urls['task_list']().url +
            '" data-action="confirm" data-target="cancel_success">' +
            'Go to My Tasks</a>'
        new window.NH.NHModal('cancel_success',
          'Task successfully cancelled', '',
          [task_button],
          0, self.form)
      else
        cancel_button = '<a href="#" data-action="close" ' +
          'data-target="submit_error">Cancel</a>'

        new window.NH.NHModal('submit_error',
          'Error submitting observation',
          'Server returned an error',
          [cancel_button],
          0, self.form)


  reset_input_errors: (input) ->
    container_el = input.parentNode
    error_el = container_el.getElementsByClassName('errors')[0]
    container_el.classList.remove('error')
    input.classList.remove('error')
    if error_el
      container_el.removeChild(error_el)

  add_input_errors: (input, error_string) ->
    container_el = input.parentNode
    error_el = document.createElement('div')
    error_el.setAttribute('class', 'errors')
    container_el.classList.add('error')
    input.classList.add('error')
    error_el.innerHTML = '<label for="'+input.name+'" class="error">' +
      error_string+'</label>'
    container_el.appendChild(error_el)

  hide_triggered_elements: (field) ->
    el = document.getElementById('parent_'+field)
    el.style.display = 'none'
    inp = document.getElementById(field)
    inp.classList.add('exclude')

  show_triggered_elements: (field) ->
    el = document.getElementById('parent_'+field)
    el.style.display = 'inline-block'
    inp = document.getElementById(field)
    inp.classList.remove('exclude')


if !window.NH
  window.NH = {}
window?.NH.NHMobileFormLoz = NHMobileFormLoz