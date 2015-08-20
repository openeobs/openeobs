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
    if (this.id === 'submit_observation') {
      cover.setAttribute('data-action', 'renable');
    }
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
    margins = {
      top: 80,
      bottom: 300,
      right: 0,
      left: 0
    };
    available_space = function(dialog, el) {
      var dh, dhh, dialog_height, dopt, dopth, elh;
      dh = dialog.getElementsByTagName('h2');
      dhh = parseInt(document.defaultView.getComputedStyle(dh != null ? dh[0] : void 0, '').getPropertyValue('height').replace('px', ''));
      dopt = dialog.getElementsByClassName('options');
      dopth = parseInt(document.defaultView.getComputedStyle(dopt != null ? dopt[0] : void 0, '').getPropertyValue('height').replace('px', ''));
      elh = parseInt(document.defaultView.getComputedStyle(el, '').getPropertyValue('height').replace('px', ''));
      dialog_height = (dhh + dopth) + (margins.top + margins.bottom);
      if (elh > window.innerHeight) {
        return window.innerHeight - dialog_height;
      }
      return elh - dialog_height;
    };
    max_height = available_space(dialog, el);
    top_offset = el.offsetTop + margins.top;
    dialog.style.top = top_offset + 'px';
    dialog.style.display = 'inline-block';
    if (max_height) {
      dialog_content.style.maxHeight = max_height + 'px';
    }
  };

  NHModal.prototype.handle_button_events = function(event) {
    var accept_detail, accept_event, action_buttons, assign_detail, assign_event, button, claim_event, cover, data_action, data_target, dialog, dialog_form, dialog_id, el, element, form, forms, i, invite, j, len, len1, nurses, reject_detail, reject_event, submit_detail, submit_event;
    data_target = event.srcElement.getAttribute('data-target');
    data_action = event.srcElement.getAttribute('data-ajax-action');
    switch (event.srcElement.getAttribute('data-action')) {
      case 'close':
        event.preventDefault();
        dialog_id = document.getElementById(data_target);
        cover = document.getElementById('cover');
        document.getElementsByTagName('body')[0].removeChild(cover);
        dialog_id.parentNode.removeChild(dialog_id);
        break;
      case 'renable':
        event.preventDefault();
        forms = document.getElementsByTagName('form');
        for (i = 0, len = forms.length; i < len; i++) {
          form = forms[i];
          action_buttons = (function() {
            var j, len1, ref, ref1, results;
            ref = form.elements;
            results = [];
            for (j = 0, len1 = ref.length; j < len1; j++) {
              element = ref[j];
              if ((ref1 = element.getAttribute('type')) === 'submit' || ref1 === 'reset') {
                results.push(element);
              }
            }
            return results;
          })();
          for (j = 0, len1 = action_buttons.length; j < len1; j++) {
            button = action_buttons[j];
            button.removeAttribute('disabled');
          }
        }
        dialog_id = document.getElementById(data_target);
        cover = document.getElementById('cover');
        document.getElementsByTagName('body')[0].removeChild(cover);
        dialog_id.parentNode.removeChild(dialog_id);
        break;
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
        dialog_id.parentNode.removeChild(dialog_id);
        break;
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
          event.handled = true;
        }
        break;
      case 'assign':
        event.preventDefault();
        dialog = document.getElementById(data_target);
        dialog_form = dialog.getElementsByTagName('form')[0];
        nurses = (function() {
          var k, len2, ref, results;
          ref = dialog_form.elements;
          results = [];
          for (k = 0, len2 = ref.length; k < len2; k++) {
            el = ref[k];
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
        document.dispatchEvent(assign_event);
        break;
      case 'claim':
        event.preventDefault();
        claim_event = document.createEvent('CustomEvent');
        claim_event.initCustomEvent('claim_patients', false, true);
        document.dispatchEvent(claim_event);
        break;
      case 'accept':
        event.preventDefault();
        accept_event = document.createEvent('CustomEvent');
        invite = event.srcElement ? event.srcElement : event.target;
        accept_detail = {
          'invite_id': invite.getAttribute('data-invite-id')
        };
        accept_event.initCustomEvent('accept_invite', false, true, accept_detail);
        document.dispatchEvent(accept_event);
        break;
      case 'reject':
        event.preventDefault();
        reject_event = document.createEvent('CustomEvent');
        invite = event.srcElement ? event.srcElement : event.target;
        reject_detail = {
          'invite_id': invite.getAttribute('data-invite-id')
        };
        reject_event.initCustomEvent('reject_invite', false, true, reject_detail);
        document.dispatchEvent(reject_event);
    }
  };

  return NHModal;

})();


/* istanbul ignore else */

if (!window.NH) {
  window.NH = {};
}

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHModal = NHModal;
}
