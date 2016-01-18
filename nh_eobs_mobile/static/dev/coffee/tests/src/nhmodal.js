
/* istanbul ignore next */
var NHModal,
  bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

NHModal = (function(superClass) {
  extend(NHModal, superClass);

  function NHModal(id1, title1, content1, options1, popupTime, el1) {
    var body, cover, dialog, self;
    this.id = id1;
    this.title = title1;
    this.content = content1;
    this.options = options1;
    this.popupTime = popupTime;
    this.el = el1;
    this.handle_button_events = bind(this.handle_button_events, this);
    this.close_modal = bind(this.close_modal, this);
    self = this;
    dialog = this.create_dialog(self, this.id, this.title, this.content, this.options);
    body = document.getElementsByTagName('body')[0];
    cover = document.createElement('div');
    cover.setAttribute('class', 'cover');
    cover.setAttribute('id', 'cover');
    cover.setAttribute('data-action', 'close');
    if (this.id === 'submit_observation' || this.id === 'partial_reasons') {
      cover.setAttribute('data-action', 'renable');
    }
    cover.setAttribute('data-target', this.id);
    cover.addEventListener('click', function(e) {
      return self.handle_event(e, self.handle_button_events, false);
    });
    this.lock_scrolling();
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
      }
      fn = function(self) {
        var a_button, option_button, ref;
        option_button = document.createElement('li');
        option_button.innerHTML = button;
        a_button = (ref = option_button.getElementsByTagName('a')) != null ? ref[0] : void 0;
        a_button.addEventListener('click', function(e) {
          return self.handle_event(e, self.handle_button_events, false);
        });
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
    available_space = function(dialog, el, dialog_content) {
      var dc_height, dh, dhh, dialog_height, dialog_total, dopt, dopth, elh;
      dh = dialog.getElementsByTagName('h2');
      dhh = parseInt(document.defaultView.getComputedStyle(dh != null ? dh[0] : void 0, '').getPropertyValue('height').replace('px', ''));
      dopt = dialog.getElementsByClassName('options');
      dopth = parseInt(document.defaultView.getComputedStyle(dopt != null ? dopt[0] : void 0, '').getPropertyValue('height').replace('px', ''));
      elh = parseInt(document.defaultView.getComputedStyle(el, '').getPropertyValue('height').replace('px', ''));
      dialog_height = (dhh + dopth) + (margins.top + margins.bottom);
      dc_height = parseInt(document.defaultView.getComputedStyle(dialog_content, '').getPropertyValue('height').replace('px', ''));
      dialog_total = dialog_height + dc_height;
      if (elh > window.innerHeight) {
        return window.innerHeight - dialog_height;
      }
      if (dialog_total > window.innerHeight) {
        return window.innerHeight - dialog_height;
      }
    };
    max_height = available_space(dialog, el, dialog_content);
    top_offset = el.offsetTop + margins.top;
    dialog.style.top = top_offset + 'px';
    dialog.style.display = 'inline-block';
    if (max_height) {
      dialog_content.style.maxHeight = max_height + 'px';
    }
  };

  NHModal.prototype.close_modal = function(modal_id) {
    var cover, dialog_id, self;
    self = this;
    dialog_id = document.getElementById(modal_id);
    if (typeof dialog_id !== 'undefined' && dialog_id) {
      cover = document.querySelectorAll('#cover[data-target="' + modal_id + '"]')[0];
      document.getElementsByTagName('body')[0].removeChild(cover);
      dialog_id.parentNode.removeChild(dialog_id);
      return self.unlock_scrolling();
    }
  };

  NHModal.prototype.handle_button_events = function(event) {
    var accept_detail, accept_event, action_buttons, assign_detail, assign_event, button, claim_event, data_action, data_target, dialog, dialog_form, el, element, form, forms, i, j, len, len1, nurses, reject_detail, reject_event, submit_detail, submit_event, target_el;
    target_el = event.src_el;
    data_target = target_el.getAttribute('data-target');
    data_action = target_el.getAttribute('data-ajax-action');
    switch (target_el.getAttribute('data-action')) {
      case 'close':
        event.preventDefault();
        return this.close_modal(data_target);
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
        return this.close_modal(data_target);
      case 'submit':
        event.preventDefault();
        submit_event = document.createEvent('CustomEvent');
        submit_detail = {
          'endpoint': target_el.getAttribute('data-ajax-action')
        };
        submit_event.initCustomEvent('post_score_submit', true, false, submit_detail);
        document.dispatchEvent(submit_event);
        return this.close_modal(data_target);
      case 'partial_submit':
        event.preventDefault();
        submit_event = document.createEvent('CustomEvent');
        submit_detail = {
          'action': data_action,
          'target': data_target
        };
        submit_event.initCustomEvent('partial_submit', false, true, submit_detail);
        return document.dispatchEvent(submit_event);
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
        return document.dispatchEvent(assign_event);
      case 'claim':
        event.preventDefault();
        claim_event = document.createEvent('CustomEvent');
        claim_event.initCustomEvent('claim_patients', false, true, false);
        return document.dispatchEvent(claim_event);
      case 'accept':
        event.preventDefault();
        accept_event = document.createEvent('CustomEvent');
        accept_detail = {
          'invite_id': target_el.getAttribute('data-invite-id')
        };
        accept_event.initCustomEvent('accept_invite', false, true, accept_detail);
        return document.dispatchEvent(accept_event);
      case 'reject':
        event.preventDefault();
        reject_event = document.createEvent('CustomEvent');
        reject_detail = {
          'invite_id': target_el.getAttribute('data-invite-id')
        };
        reject_event.initCustomEvent('reject_invite', false, true, reject_detail);
        return document.dispatchEvent(reject_event);
    }
  };

  NHModal.prototype.lock_scrolling = function() {
    var body;
    body = document.getElementsByTagName('body')[0];
    return body.classList.add('no-scroll');
  };

  NHModal.prototype.unlock_scrolling = function() {
    var body, dialogs;
    body = document.getElementsByTagName('body')[0];
    dialogs = document.getElementsByClassName('dialog');
    if (dialogs.length < 1) {
      return body.classList.remove('no-scroll');
    }
  };

  return NHModal;

})(NHLib);


/* istanbul ignore if */

if (!window.NH) {
  window.NH = {};
}


/* istanbul ignore else */

if (typeof window !== "undefined" && window !== null) {
  window.NH.NHModal = NHModal;
}
