var NHGraphLib,
  bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

NHGraphLib = (function() {
  function NHGraphLib(element) {
    this.date_to_string = bind(this.date_to_string, this);
    var self;
    this.style = {
      margin: {
        top: 40,
        right: 0,
        left: 0,
        bottom: 40
      },
      padding: {
        top: 10,
        right: 30,
        left: 40,
        bottom: 40
      },
      dimensions: {
        height: 0,
        width: 0
      },
      label_gap: 10,
      transition_duration: 1e3,
      axis_label_text_height: 10,
      timePadding: null
    };
    this.patient = {
      id: 0,
      name: ''
    };
    this.options = {
      mobile: {
        is_mob: false,
        date_range: {
          portrait: 1,
          landscape: 5
        }
      },
      ranged: null,
      refused: false,
      partial_type: 'dot',
      controls: {
        date: {
          start: null,
          end: null
        },
        time: {
          start: null,
          end: null
        },
        rangify: null
      },
      handler: {
        rangify: null,
        resize: null
      }
    };
    this.el = element ? element : null;
    this.popup = null;
    this.data = {
      raw: null,
      extent: {
        end: null,
        start: null
      }
    };
    this.obj = null;
    this.context = null;
    this.focus = null;
    this.table = {
      element: null,
      keys: null,
      type: null
    };
    this.version = '0.0.1';
    self = this;
  }

  NHGraphLib.prototype.date_from_string = function(date_string) {
    var date;
    date = new Date(date_string);
    if (isNaN(date.getTime())) {
      date = new Date(date_string.replace(' ', 'T'));
    }
    if (isNaN(date.getTime())) {
      throw new Error("Invalid date format");
    }
    return date;
  };

  NHGraphLib.prototype.date_to_string = function(date, day_flag) {
    var days, final;
    if (day_flag == null) {
      day_flag = true;
    }
    if (isNaN(date.getTime())) {
      throw new Error("Invalid date format");
    }
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    final = '';
    if (day_flag) {
      final += days[date.getDay()] + " ";
    }
    return final += date.getDate() + '/' + this.leading_zero(date.getMonth() + 1) + "/" + this.leading_zero(date.getFullYear()) + " " + this.leading_zero(date.getHours()) + ":" + this.leading_zero(date.getMinutes());
  };

  NHGraphLib.prototype.leading_zero = function(date_element) {
    return ("0" + date_element).slice(-2);
  };

  NHGraphLib.prototype.mobile_date_start_change = function(self, event) {
    var current_date, dates, new_date;
    if (self.focus != null) {
      current_date = self.focus.axes.x.min;
      dates = event.target.value.split('-');
      new_date = new Date(current_date.setFullYear(dates[0], parseInt(dates[1]) - 1, dates[2]));
      self.focus.axes.x.min = new_date;
      self.focus.redraw([new_date, self.focus.axes.x.max]);
    }
  };

  NHGraphLib.prototype.mobile_date_end_change = function(self, event) {
    var current_date, dates, new_date;
    if (self.focus != null) {
      current_date = self.focus.axes.x.max;
      dates = event.target.value.split('-');
      new_date = new Date(current_date.setFullYear(dates[0], parseInt(dates[1]) - 1, dates[2]));
      self.focus.axes.x.max = new_date;
      self.focus.redraw([self.focus.axes.x.min, new_date]);
    }
  };

  NHGraphLib.prototype.is_landscape = function() {
    if (window.innerWidth > window.innerHeight) {
      return 1;
    } else {
      return 0;
    }
  };

  NHGraphLib.prototype.mobile_time_start_change = function(self, event) {
    var current_date, new_time, time;
    if (self.focus != null) {
      current_date = self.focus.axes.x.min;
      time = event.target.value.split(':');
      new_time = new Date(current_date.setHours(time[0], time[1]));
      self.focus.axes.x.min = new_time;
      self.focus.redraw([new_time, self.focus.axes.x.max]);
    }
  };

  NHGraphLib.prototype.mobile_time_end_change = function(self, event) {
    var current_date, new_time, time;
    if (self.focus != null) {
      current_date = self.focus.axes.x.max;
      time = event.target.value.split(':');
      new_time = new Date(current_date.setHours(time[0], time[1]));
      self.focus.axes.x.max = new_time;
      self.focus.redraw([self.focus.axes.x.min, new_time]);
    }
  };

  NHGraphLib.prototype.redraw_resize = function(event) {
    var ref, ref1, ref2, ref3, ref4;
    if (this.is_alive() && !event.handled) {
      this.style.dimensions.width = ((ref = nh_graphs.select(this.el)) != null ? (ref1 = ref[0]) != null ? (ref2 = ref1[0]) != null ? ref2.clientWidth : void 0 : void 0 : void 0) - (this.style.margin.left + this.style.margin.right);
      if ((ref3 = this.obj) != null) {
        ref3.attr('width', this.style.dimensions.width);
      }
      if ((ref4 = this.context) != null) {
        ref4.handle_resize(this.context, this.obj, event);
      }
      event.handled = true;
    }
  };

  NHGraphLib.prototype.rangify_graphs = function() {
    var graph, i, len, ranged, ref;
    this.options.ranged = this.options.controls.rangify.checked;
    ranged = this.options.ranged;
    if (this.is_alive()) {
      this.context.graph.rangify_graph(this.context.graph, ranged);
      ref = this.focus.graphs;
      for (i = 0, len = ref.length; i < len; i++) {
        graph = ref[i];
        graph.rangify_graph(graph, ranged);
      }
    }
  };

  NHGraphLib.prototype.add_listeners = function() {
    var rangify;
    if (typeof _ !== "undefined" && _ !== null) {
      this.options.handler.resize = _.debounce(this.redraw_resize.bind(this), 250);
    } else {
      this.options.handler.resize = this.redraw_resize.bind(this);
    }
    window.addEventListener('resize', this.options.handler.resize);
    rangify = this.options.controls.rangify;
    this.options.handler.rangify = this.rangify_graphs.bind(this);
    if (rangify != null) {
      rangify.addEventListener('click', this.options.handler.rangify);
    }
  };

  NHGraphLib.prototype.remove_listeners = function() {
    var rangify;
    window.removeEventListener('resize', this.options.handler.resize);
    rangify = this.options.controls.rangify;
    if (rangify != null) {
      rangify.removeEventListener('click', this.options.handler.rangify);
    }
  };

  NHGraphLib.prototype.is_alive = function() {
    if (this.obj[0][0].baseURI) {
      return true;
    } else {
      this.remove_listeners();
      return false;
    }
  };

  NHGraphLib.prototype.init = function() {
    var container_el, end, ref, ref1, ref2, ref3, ref4, ref5, ref6, self, start;
    if (this.el != null) {
      container_el = nh_graphs.select(this.el);
      this.style.dimensions.width = (container_el != null ? (ref = container_el[0]) != null ? ref[0].clientWidth : void 0 : void 0) - (this.style.margin.left + this.style.margin.right);
      this.obj = container_el.append('svg');
      if (this.data.raw.length < 2 && !this.style.timePadding) {
        this.oneHundredSecondsInMilliseconds = 6000000;
        this.style.timePadding = this.oneHundredSecondsInMilliseconds;
      }
      if (this.data.raw.length > 0) {
        start = this.date_from_string(this.data.raw[0]['date_terminated']);
        end = this.date_from_string(this.data.raw[this.data.raw.length - 1]['date_terminated']);
        if (!this.style.timePadding) {
          this.rangeInMilliseconds = end.getTime() - start.getTime();
          this.fivePercentOfRange = this.rangeInMilliseconds * 0.05;
          this.style.timePadding = this.fivePercentOfRange;
        }
        start.setTime(start.getTime() - this.style.timePadding);
        this.data.extent.start = start;
        end.setTime(end.getTime() + this.style.timePadding);
        this.data.extent.end = end;
        if ((ref1 = this.context) != null) {
          ref1.init(this);
        }
        if ((ref2 = this.focus) != null) {
          ref2.init(this);
        }
      }
      this.obj.attr('width', this.style.dimensions.width);
      this.obj.attr('height', this.style.dimensions.height);
      this.popup = document.createElement('div');
      this.popup.setAttribute('class', 'hidden');
      this.popup.setAttribute('id', 'chart_popup');
      document.getElementsByTagName('body')[0].appendChild(this.popup);
      self = this;
      if ((ref3 = this.options.controls.date.start) != null) {
        ref3.addEventListener('change', function(event) {
          self.mobile_date_start_change(self, event);
        });
      }
      if ((ref4 = this.options.controls.date.end) != null) {
        ref4.addEventListener('change', function(event) {
          self.mobile_date_end_change(self, event);
        });
      }
      if ((ref5 = this.options.controls.time.start) != null) {
        ref5.addEventListener('change', function(event) {
          self.mobile_time_start_change(self, event);
        });
      }
      if ((ref6 = this.options.controls.time.end) != null) {
        ref6.addEventListener('change', function(event) {
          self.mobile_time_end_change(self, event);
        });
      }
      this.add_listeners();
    } else {
      throw new Error('No element specified');
    }
  };

  NHGraphLib.prototype.draw = function() {
    var ref, ref1;
    if (this.data.raw.length > 0) {
      if ((ref = this.context) != null) {
        ref.draw(this);
      }
      if ((ref1 = this.focus) != null) {
        ref1.draw(this);
      }
      if (this.table.element != null) {
        return this.draw_table(this);
      }
    } else {
      throw new Error('No raw data provided');
    }
  };

  NHGraphLib.prototype.draw_table = function(self) {
    var cells, container, first_row, header_row, raw_data, rows, table_el, tbody, thead;
    table_el = nh_graphs.select(self.table.element);
    container = nh_graphs.select('#table-content').append('table');
    thead = container.append('thead').attr('class', 'thead');
    tbody = container.append('tbody').attr('class', 'tbody');
    header_row = [
      {
        'date_terminated': 'Date'
      }
    ];
    raw_data = self.data.raw.reverse();
    if (self.table.type === 'nested') {
      first_row = [
        {
          'period_title': '',
          'observations': [{}]
        }
      ];
      thead.append('tr').selectAll('.group-header').data(first_row.concat(raw_data)).enter().append('th').html(function(d) {
        return d.period_title;
      }).attr('colspan', function(d) {
        return d.observations.length;
      }).attr('class', 'group-header');
      raw_data = raw_data.reduce(function(a, b) {
        return a.concat(b.observations);
      }, []);
    }
    thead.append('tr').selectAll('.column-header').data(header_row.concat(raw_data)).enter().append('th').html(function(d) {
      var date_rotate, term_date;
      term_date = d.date_terminated;
      if (d.date_terminated !== "Date") {
        term_date = self.date_to_string(self.date_from_string(d.date_terminated), false);
      }
      date_rotate = term_date.split(' ');
      if (date_rotate.length === 1) {
        return date_rotate[0];
      }
      return date_rotate[1] + '<br>' + date_rotate[0];
    }).attr('class', function(d) {
      var cls;
      cls = 'column-header ';
      if (d["class"]) {
        cls += d["class"];
      }
      return cls;
    });
    rows = tbody.selectAll('tr.row').data(self.table.keys).enter().append('tr').attr('class', 'row');
    return cells = rows.selectAll('td').data(function(d) {
      var data, fix_val, i, j, key, len, len1, o, obj, p, ref, t, v;
      data = [
        {
          title: d['title'],
          value: d['title'],
          presentation: d['presentation'],
          "class": false
        }
      ];
      for (i = 0, len = raw_data.length; i < len; i++) {
        obj = raw_data[i];
        if (d['keys'].length === 1) {
          key = d['keys'][0];
          if (obj.hasOwnProperty(key)) {
            fix_val = obj[key];
            if (fix_val === false) {
              fix_val = 'No';
            }
            if (fix_val === true) {
              fix_val = 'Yes';
            }
            if (d['title']) {
              data.push({
                title: d['title'],
                value: fix_val,
                presentation: d['presentation'],
                "class": obj["class"]
              });
            }
          }
        } else {
          t = d['title'];
          v = [];
          p = d['presentation'];
          ref = d['keys'];
          for (j = 0, len1 = ref.length; j < len1; j++) {
            o = ref[j];
            v.push({
              title: o['title'],
              value: obj[o['keys'][0]],
              presentation: p,
              "class": obj[o["class"]]
            });
          }
          if (t) {
            data.push({
              title: t,
              value: v,
              presentation: p,
              "class": false
            });
          }
        }
      }
      return data;
    }).enter().append('td').html(function(d) {
      var i, len, o, ref, text;
      if (typeof d.value === 'object') {
        text = '';
        ref = d.value;
        for (i = 0, len = ref.length; i < len; i++) {
          o = ref[i];
          if (o.value) {
            if (Array.isArray(o.value) && o.value.length > 1) {
              o.value = o.value[1];
            }
            text += '<strong>' + o.title + ':</strong> ' + o.value + '<br>';
          }
        }
        return text;
      } else {
        if (d.presentation === 'bold') {
          return '<strong>' + d.value + '</strong>';
        } else {
          return d.value;
        }
      }
    }).attr("class", function(d) {
      return d["class"];
    });
  };

  return NHGraphLib;

})();


/* istanbul ignore if */

if (!window.NH) {
  window.NH = {};
}

window.NH.NHGraphLib = NHGraphLib;
