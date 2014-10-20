# NHModal handles modal messages on screen
class NHModal

 constructor: (@id, @title, @content, @options, @popupTime, @el) ->
   # sanity check to ensure that el is actually present in the DOM
   #dialog_parent = document.getElementById(@el)
   #
   #if dialog_parent?
   #
   #else
   #  throw 'NHModal - Parent element not found'
   self = @

   # create the dialog
   dialog = @create_dialog(self, @id, @title, @content, @options)

   # append it to the DOM
   @el.appendChild(dialog)
   
   # calculate the size of the modal and adjust
   @calculate_dimensions(dialog, dialog.getElementsByClassName('dialogContent')[0], @el)
   
   
 # helper function to create the dialog object
 create_dialog: (self, popup_id, popup_title, popup_content, popup_options) =>
   
   # create the dialog div
   dialog_div = (id) ->
     div = document.createElement('div')
     div.setAttribute('class', 'dialog')
     div.setAttribute('id', id)
     return div
   
   # create the h2 header
   dialog_header = (title) ->
     header = document.createElement('h2')
     header.textContent = title
     return header
   
   # create the content div
   dialog_content = (message) ->
     content = document.createElement('div')
     content.setAttribute('class', 'dialogContent')
     content.innerHTML = message
     return content
   
   # create the option buttons
   dialog_options = (self, buttons) ->
     option_list = document.createElement('ul')
     switch buttons.length
     	when 1 then option_list.setAttribute('class', 'options one-col')
     	when 2 then option_list.setAttribute('class', 'options two-col')
     	when 3 then option_list.setAttribute('class', 'options three-col')
     	when 4 then option_list.setAttribute('class', 'options four-col')
     	else option_list.setAttribute('class', 'options one-col')
     for button in buttons
       do (self) ->
         option_button = document.createElement('li')
         option_button.innerHTML = button
         option_button.getElementsByTagName('a')?[0].addEventListener('click', self.handle_button_events)
         option_list.appendChild(option_button)
     return option_list
   
   # create the elements and set up DOM
   container = dialog_div(popup_id)
   header = dialog_header(popup_title)
   content = dialog_content(popup_content)
   options = dialog_options(self, popup_options)
   container.appendChild(header)
   container.appendChild(content)
   container.appendChild(options)
   
   return container
   
 # calculate the correct size of the dialog
 calculate_dimensions: (dialog, dialog_content, el) =>
   margins = 40
   #sibling_space = () ->
   #  sibling_height = 0
   #  sibling_height += child.clientHeight for child in el.children when child.innerHTML isnt el.innerHTML
   #  return sibling_height
   #sibling_height = sibling_space()
   available_space = (dialog, el) ->
     dialog_header_height = dialog.getElementsByTagName('h2')?[0]?.clientHeight
     dialog_options_height = dialog.getElementsByClassName('options')?[0]?.getElementsByTagName('li')?[0]?.clientHeight
     el_height = el.clientHeight
     return el_height - ((dialog_header_height + dialog_options_height) + (margins*2))
   max_height = available_space(dialog, el)
   dialog.style.top = margins+'px'
   if max_height
     dialog_content.style.maxHeight = max_height+'px'
   return

 handle_button_events: (event) =>
   event.preventDefault()
   switch event.srcElement.getAttribute('data-action')
     when 'close'
       dialog_id = document.getElementById(event.srcElement.getAttribute('data-target'))
       dialog_id.parentNode.removeChild(dialog_id)
     when 'confirm' then console.log('yay')







if !window.NH
  window.NH = {}
window?.NH.NHModal = NHModal