var NHModal;

NHModal = (function() {
  function NHModal(id1, title1, content1, options1, popupTime, el1) {
    var body, cover, dialog, self;
    this.id = id1;
    this.title = title1;
    this.content = content1;
    this.options = options1;
    this.popupTime = popupTime;
    this.el = el1;
    self = this;
    dialog = this.create_dialog(self, this.id, this.title, this.content, this.options);
    body = document.getElementsByTagName('body')[0];
    cover = document.createElement('div');
    cover.setAttribute('class', 'cover');
    cover.setAttribute('id', 'cover');
    cover.setAttribute('data-action', 'close');
    cover.setAttribute('data-target', this.id);
    cover.style.height = body.clientHeight + 'px';
    cover.addEventListener('click', self.handle_button_events);
    body.appendChild(cover);
    this.el.appendChild(dialog);
    this.calculate_dimensions(dialog, dialog.getElementsByClassName('dialogContent')[0], this.el);
  }

  NHModal.prototype.create_dialog = function(self, popup_id, popup_title, popup_content, popup_options) {
    var container, content, dialog_content, dialog_div, dialog_header, dialog_options, header, options;
    dialog_div = function(id) {
      var div;
      div = document.createElement('div');
      div.setAttribute('class', 'dialog');
      div.setAttribute('id', id);
      return div;
    };
    dialog_header = function(title) {
      var header;
      header = document.createElement('h2');
      header.innerHTML = title;
      return header;
    };
    dialog_content = function(message) {
      var content;
      content = document.createElement('div');
      content.setAttribute('class', 'dialogContent');
      content.innerHTML = message;
      return content;
    };
    dialog_options = function(self, buttons) {
      var button, fn, i, len, option_list;
      option_list = document.createElement('ul');
      switch (buttons.length) {
        case 1:
          option_list.setAttribute('class', 'options one-col');
          break;
        case 2:
          option_list.setAttribute('class', 'options two-col');
          break;
        case 3:
          option_list.setAttribute('class', 'options three-col');
          break;
        case 4:
          option_list.setAttribute('class', 'options four-col');
      }
      fn = function(self) {
        var option_button, ref;
        option_button = document.createElement('li');
        option_button.innerHTML = button;
        if ((ref = option_button.getElementsByTagName('a')) != null) {
          ref[0].addEventListener('click', self.handle_button_events);
        }
        return option_list.appendChild(option_button);
      };
      for (i = 0, len = buttons.length; i < len; i++) {
        button = buttons[i];
        fn(self);
      }
      return option_list;
    };
    container = dialog_div(popup_id);
    header = dialog_header(popup_title);
    content = dialog_content(popup_content);
    options = dialog_options(self, popup_options);
    container.appendChild(header);
    container.appendChild(content);
    container.appendChild(options);
    return container;
  };

  NHModal.prototype.calculate_dimensions = function(dialog, dialog_content, el) {
    var available_space, margins, max_height, top_offset;
    margins = 80;
    available_space = function(dialog, el) {
      var dialog_header, dialog_header_height, dialog_opt_first, dialog_options, dialog_options_height, el_height, ref, ref1, ref2;
      dialog_header = dialog.getElementsByTagName('h2');
      dialog_header_height = dialog_header != null ? (ref = dialog_header[0]) != null ? ref.clientHeight : void 0 : void 0;
      dialog_options = dialog.getElementsByClassName('options');
      dialog_opt_first = dialog_options != null ? (ref1 = dialog_options[0]) != null ? ref1.getElementsByTagName('li') : void 0 : void 0;
      dialog_options_height = dialog_opt_first != null ? (ref2 = dialog_opt_first[0]) != null ? ref2.clientHeight : void 0 : void 0;
      el_height = el.clientHeight;
      return el_height - ((dialog_header_height + dialog_options_height) + (margins * 2));
    };
    max_height = available_space(dialog, el);
    top_offset = el.offsetTop + margins;
    dialog.style.top = top_offset + 'px';
    dialog.style.display = 'inline-block';
    if (max_height) {
      dialog_content.style.maxHeight = max_height + 'px';
    }
  };

  NHModal.prototype.handle_button_events = function(event) {
    var assign_detail, assign_event, claim_event, cover, data_action, data_target, dialog, dialog_form, dialog_id, el, nurses, submit_detail, submit_event;
    data_target = event.srcElement.getAttribute('data-target');
    data_action = event.srcElement.getAttribute('data-ajax-action');
    switch (event.srcElement.getAttribute('data-action')) {
      case 'close':
        event.preventDefault();
        dialog_id = document.getElementById(data_target);
        cover = document.getElementById('cover');
        document.getElementsByTagName('body')[0].removeChild(cover);
        return dialog_id.parentNode.removeChild(dialog_id);
      case 'submit':
        event.preventDefault();
        submit_event = document.createEvent('CustomEvent');
        submit_detail = {
          'endpoint': event.srcElement.getAttribute('data-ajax-action')
        };
        submit_event.initCustomEvent('post_score_submit', true, false, submit_detail);
        document.dispatchEvent(submit_event);
        dialog_id = document.getElementById(data_target);
        cover = document.getElementById('cover');
        document.getElementsByTagName('body')[0].removeChild(cover);
        return dialog_id.parentNode.removeChild(dialog_id);
      case 'partial_submit':
        event.preventDefault();
        if (!event.handled) {
          submit_event = document.createEvent('CustomEvent');
          submit_detail = {
            'action': data_action,
            'target': data_target
          };
          submit_event.initCustomEvent('partial_submit', false, true, submit_detail);
          document.dispatchEvent(submit_event);
          return event.handled = true;
        }
        break;
      case 'assign':
        event.preventDefault();
        dialog = document.getElementById(data_target);
        dialog_form = dialog.getElementsByTagName('form')[0];
        nurses = (function() {
          var i, len, ref, results;
          ref = dialog_form.elements;
          results = [];
          for (i = 0, len = ref.length; i < len; i++) {
            el = ref[i];
            if (el.checked) {
              results.push(el.value);
            }
          }
          return results;
        })();
        assign_event = document.createEvent('CustomEvent');
        assign_detail = {
          'action': data_action,
          'target': data_target,
          'nurses': nurses
        };
        assign_event.initCustomEvent('assign_nurse', false, true, assign_detail);
        return document.dispatchEvent(assign_event);
      case 'claim':
        event.preventDefault();
        claim_event = document.createEvent('CustomEvent');
        claim_event.initCustomEvent('claim_patients', false, true);
        return document.dispatchEvent(claim_event);
    }
  };

  return NHModal;

})();

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHModal = NHModal;
}
