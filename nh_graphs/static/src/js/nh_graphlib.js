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
      time_padding: null
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
      keys: null
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
      dates = event.srcElement.value.split('-');
      new_date = new Date(current_date.setFullYear(dates[0], parseInt(dates[1]) - 1, dates[2]));
      self.focus.axes.x.min = new_date;
      self.focus.redraw([new_date, self.focus.axes.x.max]);
    }
  };

  NHGraphLib.prototype.mobile_date_end_change = function(self, event) {
    var current_date, dates, new_date;
    if (self.focus != null) {
      current_date = self.focus.axes.x.max;
      dates = event.srcElement.value.split('-');
      new_date = new Date(current_date.setFullYear(dates[0], parseInt(dates[1]) - 1, dates[2]));
      self.focus.axes.x.max = new_date;
      self.focus.redraw([self.focus.axes.x.min, new_date]);
    }
  };

  NHGraphLib.prototype.mobile_time_start_change = function(self, event) {
    var current_date, new_time, time;
    if (self.focus != null) {
      current_date = self.focus.axes.x.min;
      time = event.srcElement.value.split(':');
      new_time = new Date(current_date.setHours(time[0], time[1]));
      self.focus.axes.x.min = new_time;
      self.focus.redraw([new_time, self.focus.axes.x.max]);
    }
  };

  NHGraphLib.prototype.mobile_time_end_change = function(self, event) {
    var current_date, new_time, time;
    if (self.focus != null) {
      current_date = self.focus.axes.x.max;
      time = event.srcElement.value.split(':');
      new_time = new Date(current_date.setHours(time[0], time[1]));
      self.focus.axes.x.max = new_time;
      self.focus.redraw([self.focus.axes.x.min, new_time]);
    }
  };

  NHGraphLib.prototype.redraw_resize = function(self, event) {
    var context_event, ref, ref1, ref2, ref3;
    self.style.dimensions.width = ((ref = nh_graphs.select(self.el)) != null ? (ref1 = ref[0]) != null ? (ref2 = ref1[0]) != null ? ref2.clientWidth : void 0 : void 0 : void 0) - (self.style.margin.left + self.style.margin.right);
    if ((ref3 = self.obj) != null) {
      ref3.attr('width', self.style.dimensions.width);
    }
    context_event = document.createEvent('HTMLEvents');
    context_event.initEvent('context_resize', true, true);
    window.dispatchEvent(context_event);
  };

  NHGraphLib.prototype.init = function() {
    var container_el, end, ref, ref1, ref2, ref3, ref4, ref5, ref6, self, start;
    if (this.el != null) {
      container_el = nh_graphs.select(this.el);
      this.style.dimensions.width = (container_el != null ? (ref = container_el[0]) != null ? ref[0].clientWidth : void 0 : void 0) - (this.style.margin.left + this.style.margin.right);
      this.obj = container_el.append('svg');
      if (this.data.raw.length < 2 && !this.style.time_padding) {
        this.style.time_padding = 100;
      }
      if (this.data.raw.length > 0) {
        start = this.date_from_string(this.data.raw[0]['date_terminated']);
        end = this.date_from_string(this.data.raw[this.data.raw.length - 1]['date_terminated']);
        if (!this.style.time_padding) {
          this.style.time_padding = ((end - start) / this.style.dimensions.width) / 500;
        }
        start.setMinutes(start.getMinutes() - this.style.time_padding);
        this.data.extent.start = start;
        end.setMinutes(end.getMinutes() + this.style.time_padding);
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
      window.addEventListener('resize', function(event) {
        self.redraw_resize(self, event);
      });
    } else {
      throw new Error('No element specified');
    }
  };

  NHGraphLib.prototype.draw = function() {
    var ref, ref1;
    if ((ref = this.context) != null) {
      ref.draw(this);
    }
    if ((ref1 = this.focus) != null) {
      ref1.draw(this);
    }
    if (this.table.element != null) {
      return this.draw_table(this);
    }
  };

  NHGraphLib.prototype.draw_table = function(self) {
    var cells, container, header_row, raw_data, rows, table_el, tbody, thead;
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
    thead.append('tr').selectAll('th').data(header_row.concat(raw_data)).enter().append('th').html(function(d) {
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
    });
    rows = tbody.selectAll('tr.row').data(self.table.keys).enter().append('tr').attr('class', 'row');
    return cells = rows.selectAll('td').data(function(d) {
      var data, fix_val, i, j, key, len, len1, o, obj, ref, t, v;
      data = [
        {
          title: d['title'],
          value: d['title']
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
                value: fix_val
              });
            }
          }
        } else {
          t = d['title'];
          v = [];
          ref = d['keys'];
          for (j = 0, len1 = ref.length; j < len1; j++) {
            o = ref[j];
            v.push({
              title: o['title'],
              value: obj[o['keys'][0]]
            });
          }
          if (t) {
            data.push({
              title: t,
              value: v
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
        return d.value;
      }
    });
  };

  return NHGraphLib;

})();

if (!window.NH) {
  window.NH = {};
}

window.NH.NHGraphLib = NHGraphLib;

var NHContext,
  bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

NHContext = (function(superClass) {
  extend(NHContext, superClass);

  function NHContext() {
    this.init = bind(this.init, this);
    this.handle_resize = bind(this.handle_resize, this);
    var self;
    this.style = {
      margin: {
        top: 50,
        left: 0,
        right: 0,
        bottom: 20
      },
      padding: {
        top: 0,
        left: 0,
        right: 0,
        bottom: 0
      },
      dimensions: {
        height: 0,
        width: 0
      },
      title_height: 80
    };
    this.graph = null;
    this.axes = {
      x: {
        scale: null,
        axis: null,
        min: 0,
        max: 0
      },
      y: {
        scale: null,
        axis: null,
        min: 0,
        max: 0
      }
    };
    this.parent_obj = null;
    this.brush = null;
    this.title = null;
    this.title_obj = null;
    self = this;
  }

  NHContext.prototype.handle_resize = function(self, parent_svg, event) {
    var d, graph_event, new_date, ref, ref1, ref2, ref3, ref4;
    self.style.dimensions.width = self.parent_obj.style.dimensions.width - ((self.parent_obj.style.padding.left + self.parent_obj.style.padding.right) + (self.style.margin.left + self.style.margin.right));
    self.obj.attr('width', self.style.dimensions.width);
    if ((ref = self.axes.x.scale) != null) {
      ref.range()[1] = self.style.dimensions.width;
    }
    graph_event = document.createEvent('HTMLEvents');
    graph_event.initEvent('focus_resize', true, true);
    window.dispatchEvent(graph_event);
    if (self.parent_obj.options.mobile.is_mob) {
      new_date = new Date(self.axes.x.max);
      if (window.innerWidth > window.innerHeight) {
        d = new_date.getDate() - self.parent_obj.options.mobile.date_range.landscape;
        new_date.setDate(d);
        self.graph.axes.x.scale.domain([new_date, self.axes.x.max]);
      } else {
        d = new_date.getDate() - self.parent_obj.options.mobile.date_range.portrait;
        new_date.setDate(d);
        self.graph.axes.x.scale.domain([new_date, self.axes.x.max]);
      }
      if ((ref1 = self.parent_obj.options.controls.date.start) != null) {
        ref1.value = new_date.getFullYear() + '-' + self.leading_zero(new_date.getMonth() + 1) + '-' + self.leading_zero(new_date.getDate());
      }
      if ((ref2 = self.parent_obj.options.controls.date.end) != null) {
        ref2.value = self.axes.x.max.getFullYear() + '-' + self.leading_zero(self.axes.x.max.getMonth() + 1) + '-' + self.leading_zero(self.axes.x.max.getDate());
      }
      if ((ref3 = self.parent_obj.options.controls.time.start) != null) {
        ref3.value = self.leading_zero(new_date.getHours()) + ':' + self.leading_zero(new_date.getMinutes());
      }
      if ((ref4 = self.parent_obj.options.controls.time.end) != null) {
        ref4.value = self.leading_zero(self.axes.x.max.getHours()) + ':' + self.leading_zero(self.axes.x.max.getMinutes());
      }
    }
    self.graph.axes.x.scale.range([0, self.style.dimensions.width - self.graph.style.label_width]);
    self.graph.axes.x.axis.ticks(self.style.dimensions.width / 100);
    self.graph.redraw(this);
  };

  NHContext.prototype.handle_brush = function(self, context) {
    var new_extent_end, new_extent_start, ref, ref1, ref2, ref3;
    new_extent_start = nh_graphs.event.target.extent()[0];
    new_extent_end = nh_graphs.event.target.extent()[1];
    if (new_extent_start.getTime() === new_extent_end.getTime()) {
      new_extent_start = context.axes.x.min;
      new_extent_end = context.axes.x.max;
      context.parent_obj.focus.redraw([context.axes.x.min, context.axes.x.max]);
    } else {
      context.parent_obj.focus.redraw(nh_graphs.event.target.extent());
    }
    if ((ref = self.parent_obj.options.controls.date.start) != null) {
      ref.value = new_extent_start.getFullYear() + '-' + self.leading_zero(new_extent_start.getMonth() + 1) + '-' + self.leading_zero(new_extent_start.getDate());
    }
    if ((ref1 = self.parent_obj.options.controls.date.end) != null) {
      ref1.value = new_extent_end.getFullYear() + '-' + self.leading_zero(new_extent_end.getMonth() + 1) + '-' + self.leading_zero(new_extent_end.getDate());
    }
    if ((ref2 = self.parent_obj.options.controls.time.start) != null) {
      ref2.value = self.leading_zero(new_extent_start.getHours()) + ':' + self.leading_zero(new_extent_start.getMinutes());
    }
    return (ref3 = self.parent_obj.options.controls.time.end) != null ? ref3.value = self.leading_zero(new_extent_end.getHours()) + ':' + self.leading_zero(new_extent_end.getMinutes()) : void 0;
  };

  NHContext.prototype.init = function(parent_svg) {
    var left_offset, self;
    if (parent_svg != null) {
      this.parent_obj = parent_svg;
      left_offset = parent_svg.style.padding.left + this.style.margin.left;
      if (this.title != null) {
        this.title_obj = parent_svg.obj.append('text').text(this.title).attr('class', 'title').attr('transform', 'translate(0,' + (parent_svg.style.padding.top + this.style.margin.top) + ')');
      }
      this.obj = parent_svg.obj.append('g');
      this.obj.attr('class', 'nhcontext');
      if (this.title != null) {
        this.obj.attr('transform', 'translate(' + left_offset + ',' + (parent_svg.style.padding.top + this.style.margin.top + this.style.title_height) + ')');
      } else {
        this.obj.attr('transform', 'translate(' + left_offset + ',' + (parent_svg.style.padding.top + this.style.margin.top) + ')');
      }
      this.style.dimensions.width = parent_svg.style.dimensions.width - ((parent_svg.style.padding.left + parent_svg.style.padding.right) + (this.style.margin.left + this.style.margin.right));
      this.obj.attr('width', this.style.dimensions.width);
      this.axes.x.min = parent_svg.data.extent.start;
      this.axes.x.max = parent_svg.data.extent.end;
      this.axes.x.scale = nh_graphs.time.scale().domain([this.axes.x.min, this.axes.x.max]).range([left_offset, this.style.dimensions.width]);
      this.graph.init(this);
      if ((this.title != null) && !this.graph.style.axis.x.hide) {
        this.style.dimensions.height += this.graph.style.dimensions.height + (this.graph.style.axis.x.size.height * 2) + this.style.title_height;
      } else {
        this.style.dimensions.height += this.graph.style.dimensions.height;
      }
      parent_svg.style.dimensions.height += this.style.dimensions.height + (this.style.margin.top + this.style.margin.bottom);
      this.graph.drawables.brush = this.graph.obj.append('g').attr('class', 'brush-container');
      self = this;
      this.brush = nh_graphs.svg.brush().x(this.graph.axes.x.scale).on("brush", function(context) {
        if (context == null) {
          context = self;
        }
        return self.handle_brush(self, context);
      });
      this.graph.drawables.brush.append("g").attr("class", "x brush").call(this.brush).selectAll("rect").attr("y", 0).attr("height", this.graph.style.dimensions.height);
      self = this;
      window.addEventListener('context_resize', function(event) {
        return self.handle_resize(self, parent_svg, event);
      });
    } else {
      throw new Error('Context init being called before SVG initialised');
    }
  };

  NHContext.prototype.draw = function(parent_svg) {
    this.graph.draw(this);
  };

  return NHContext;

})(NHGraphLib);

if (!window.NH) {
  window.NH = {};
}

window.NH.NHContext = NHContext;

var NHFocus,
  bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

NHFocus = (function() {
  function NHFocus() {
    this.redraw = bind(this.redraw, this);
    this.draw = bind(this.draw, this);
    this.init = bind(this.init, this);
    var self;
    this.style = {
      spacing: 20,
      margin: {
        top: 0,
        left: 0,
        right: 0,
        bottom: 0
      },
      padding: {
        top: 20,
        left: 0,
        right: 0,
        bottom: 20
      },
      dimensions: {
        height: 0,
        width: 0
      },
      title_height: 70
    };
    this.graphs = new Array();
    this.tables = new Array();
    this.axes = {
      x: {
        scale: null,
        axis: null,
        min: 0,
        max: 0
      },
      y: {
        scale: null,
        axis: null,
        min: 0,
        max: 0
      }
    };
    this.parent_obj = null;
    this.title = null;
    this.title_obj = null;
    self = this;
  }

  NHFocus.prototype.handle_resize = function(self, event) {
    var d, new_date, ref;
    self.style.dimensions.width = self.parent_obj.style.dimensions.width - ((self.parent_obj.style.padding.left + self.parent_obj.style.padding.right) + (self.style.margin.left + self.style.margin.right));
    self.obj.attr('width', self.style.dimensions.width);
    if ((ref = self.axes.x.scale) != null) {
      ref.range()[1] = self.style.dimensions.width;
    }
    if (self.parent_obj.options.mobile.is_mob) {
      if (window.innerWidth > window.innerHeight) {
        new_date = new Date(self.axes.x.max);
        d = new_date.getDate() - self.parent_obj.options.mobile.date_range.landscape;
        new_date.setDate(d);
        return self.redraw([new_date, self.axes.x.max]);
      } else {
        new_date = new Date(self.axes.x.max);
        d = new_date.getDate() - self.parent_obj.options.mobile.date_range.portrait;
        new_date.setDate(d);
        return self.redraw([new_date, self.axes.x.max]);
      }
    } else {
      return self.redraw([self.axes.x.min, self.axes.x.max]);
    }
  };

  NHFocus.prototype.init = function(parent_svg) {
    var final, graph, h_mb, h_mn_pt, h_mt, i, j, len, len1, pl_ml, ref, ref1, self, table, top_offset;
    if (parent_svg != null) {
      this.parent_obj = parent_svg;
      if (this.title != null) {
        this.title_obj = this.parent_obj.obj.append('text').text(this.title).attr('class', 'title');
        if (parent_svg.context != null) {
          h_mb = parent_svg.context.style.dimensions.height + parent_svg.context.style.margin.bottom;
          h_mn_pt = h_mb + parent_svg.style.padding.top;
          final = h_mn_pt + this.style.margin.top;
          this.title_obj.attr('transform', 'translate(0,' + final + ')');
        } else {
          h_mt = parent_svg.style.padding.top + this.style.margin.top;
          this.title_obj.attr('transform', 'translate(0,' + h_mt + ')');
        }
      }
      this.obj = parent_svg.obj.append('g');
      this.obj.attr('class', 'nhfocus');
      top_offset = parent_svg.style.padding.top + this.style.margin.top;
      if (this.title != null) {
        top_offset += this.style.title_height;
      }
      if (parent_svg.context != null) {
        pl_ml = parent_svg.style.padding.left + this.style.margin.left;
        h_mb = parent_svg.context.style.dimensions.height + parent_svg.context.style.margin.bottom;
        final = h_mb + top_offset;
        this.obj.attr('transform', 'translate(' + pl_ml + ',' + final + ')');
      } else {
        this.obj.attr('transform', 'translate(' + (parent_svg.style.padding.left + this.style.margin.left) + ',' + top_offset + ')');
      }
      this.style.dimensions.width = parent_svg.style.dimensions.width - ((parent_svg.style.padding.left + parent_svg.style.padding.right) + (this.style.margin.left + this.style.margin.right));
      this.obj.attr('width', this.style.dimensions.width);
      this.axes.x.min = parent_svg.data.extent.start;
      this.axes.x.max = parent_svg.data.extent.end;
      ref = this.graphs;
      for (i = 0, len = ref.length; i < len; i++) {
        graph = ref[i];
        graph.init(this);
        this.style.dimensions.height += graph.style.dimensions.height + this.style.spacing;
      }
      ref1 = this.tables;
      for (j = 0, len1 = ref1.length; j < len1; j++) {
        table = ref1[j];
        table.init(this);
      }
      if (this.title != null) {
        this.style.dimensions.height += this.style.title_height;
      }
      parent_svg.style.dimensions.height += this.style.dimensions.height + (this.style.margin.top + this.style.margin.bottom);
      self = this;
      return window.addEventListener('focus_resize', function(event) {
        return self.handle_resize(self, event);
      });
    } else {
      throw new Error('Focus init being called before SVG initialised');
    }
  };

  NHFocus.prototype.draw = function(parent_svg) {
    var graph, i, j, len, len1, ref, ref1, table;
    ref = this.graphs;
    for (i = 0, len = ref.length; i < len; i++) {
      graph = ref[i];
      graph.draw(this);
    }
    ref1 = this.tables;
    for (j = 0, len1 = ref1.length; j < len1; j++) {
      table = ref1[j];
      table.draw(this);
    }
  };

  NHFocus.prototype.redraw = function(extent) {
    var graph, i, j, len, len1, ref, ref1, table;
    ref = this.graphs;
    for (i = 0, len = ref.length; i < len; i++) {
      graph = ref[i];
      graph.axes.x.scale.domain([extent[0], extent[1]]);
      graph.axes.x.axis.ticks(this.style.dimensions.width / 100);
      graph.axes.x.scale.range([0, this.style.dimensions.width - graph.style.label_width]);
      graph.redraw(this);
    }
    ref1 = this.tables;
    for (j = 0, len1 = ref1.length; j < len1; j++) {
      table = ref1[j];
      table.range = extent;
      table.redraw(this);
    }
  };

  return NHFocus;

})();

if (!window.NH) {
  window.NH = {};
}

window.NH.NHFocus = NHFocus;

var NHGraph,
  bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

Array.prototype.min = function() {
  return Math.min.apply(null, this);
};

NHGraph = (function(superClass) {
  extend(NHGraph, superClass);

  function NHGraph() {
    this.redraw = bind(this.redraw, this);
    this.draw = bind(this.draw, this);
    this.init = bind(this.init, this);
    this.axes = {
      x: {
        scale: null,
        axis: null,
        min: 0,
        max: 0,
        obj: null
      },
      y: {
        scale: null,
        axis: null,
        min: 0,
        max: 0,
        obj: null,
        ranged_extent: null
      },
      obj: null
    };
    this.style = {
      dimensions: {
        height: 200,
        width: 0
      },
      margin: {
        top: 0,
        right: 0,
        bottom: 0,
        left: 0
      },
      padding: {
        top: 0,
        right: 0,
        bottom: 0,
        left: 0
      },
      axis: {
        step: 0,
        x: {
          hide: false,
          size: null
        },
        y: {
          hide: false,
          size: null
        }
      },
      data_style: '',
      norm_style: '',
      axis_label_font_size: 12,
      axis_label_line_height: 1.2,
      axis_label_text_height: 10,
      axis_label_text_padding: 50,
      label_text_height: 18,
      label_width: 100,
      range: {
        cap: {
          height: 2,
          width: 9
        },
        width: 2
      },
      range_padding: 1
    };
    this.options = {
      keys: new Array(),
      label: null,
      measurement: '',
      normal: {
        min: 0,
        max: 0,
        diff: 0
      }
    };
    this.drawables = {
      area: null,
      graph_object: null,
      data: null,
      initial_values: null,
      ranged_values: null,
      background: {
        obj: null,
        data: null
      },
      brush: null
    };
    this.obj = null;
    this.parent_obj = null;
  }

  NHGraph.prototype.show_popup = function(string, x, y) {
    var cp;
    cp = document.getElementById('chart_popup');
    cp.innerHTML = string;
    cp.style.top = y + 'px';
    cp.style.left = x + 'px';
    return cp.classList.remove('hidden');
  };

  NHGraph.prototype.hide_popup = function() {
    var cp;
    cp = document.getElementById('chart_popup');
    return cp.classList.add('hidden');
  };

  NHGraph.prototype.rangify_graph = function(self, event) {
    var d0, d1;
    if (event.srcElement.checked) {
      d0 = self.axes.y.ranged_extent[0] - self.style.range_padding;
      d1 = self.axes.y.ranged_extent[1] + self.style.range_padding;
      self.axes.y.scale.domain([(d0 > 0 ? d0 : 0), d1]);
    } else {
      self.axes.y.scale.domain([self.axes.y.min, self.axes.y.max]);
    }
    self.redraw(self.parent_obj);
    self.axes.y.obj.selectAll('.tick line').filter(function(d) {
      if (self.style.axis.step < 1) {
        if (!(d % 1 === 0)) {
          return d;
        }
      }
    }).attr('class', 'y-minor-tick');
  };

  NHGraph.prototype.resize_graph = function(self, event) {
    var ref;
    self.style.dimensions.width = self.parent_obj.style.dimensions.width - ((self.parent_obj.style.padding.left + self.parent_obj.style.padding.right) + (self.style.margin.left + self.style.margin.right)) - this.style.label_width;
    self.obj.attr('width', self.style.dimensions.width);
    if ((ref = self.axes.x.scale) != null) {
      ref.range()[1] = self.style.dimensions.width;
    }
    return self.redraw(self.parent_obj);
  };

  NHGraph.prototype.init = function(parent_obj) {
    var adjusted_line, j, key, left_offset, len, line_self, ob, rangify, ref, self, tick_font_size, tick_line_height, top_offset, values, y_label;
    this.parent_obj = parent_obj;
    this.obj = parent_obj.obj.append('g');
    this.obj.attr('class', 'nhgraph');
    this.style.dimensions.width = parent_obj.style.dimensions.width - ((parent_obj.style.padding.left + parent_obj.style.padding.right) + (this.style.margin.left + this.style.margin.right)) - this.style.label_width;
    this.obj.attr('width', this.style.dimensions.width);
    left_offset = parent_obj.style.padding.left + this.style.margin.left;
    top_offset = parent_obj.style.dimensions.height + this.style.margin.top;
    this.drawables.background.obj = this.obj.append('g').attr('class', 'background');
    this.axes.obj = this.obj.append('g').attr('class', 'axes');
    this.drawables.data = this.obj.append('g').attr('class', 'data');
    this.axes.x.min = parent_obj.axes.x.min;
    this.axes.x.max = parent_obj.axes.x.max;
    this.axes.x.scale = nh_graphs.time.scale().domain([this.axes.x.min, this.axes.x.max]).range([left_offset, this.style.dimensions.width]);
    this.axes.x.axis = nh_graphs.svg.axis().scale(this.axes.x.scale).orient("top").ticks(this.style.dimensions.width / 100);
    if (!this.style.axis.x.hide) {
      this.axes.x.obj = this.axes.obj.append("g").attr("class", "x axis").call(this.axes.x.axis);
      line_self = this;
      tick_font_size = line_self.style.axis_label_font_size;
      tick_line_height = line_self.style.axis_label_line_height;
      adjusted_line = Math.round(((tick_font_size * tick_line_height) * 10) / 10);
      this.axes.obj.selectAll(".x.axis g text").each(function(d) {
        var el, i, j, len, top_lines, tspan, word, words;
        el = nh_graphs.select(this);
        words = line_self.date_to_string(d).split(" ");
        el.text("");
        for (i = j = 0, len = words.length; j < len; i = ++j) {
          word = words[i];
          tspan = el.append("tspan").text(word);
          tspan.attr("style", "font-size: " + tick_font_size + "px;");
          if (i > 0) {
            tspan.attr("x", 0).attr("dy", adjusted_line);
          }
        }
        top_lines = ((words.length - 1) * adjusted_line) + tick_font_size;
        return el.attr("y", "-" + Math.round((top_lines * 10) / 10));
      });
      this.style.axis.x.size = this.axes.x.obj[0][0].getBBox();
      this.style.dimensions.height -= this.style.axis.x.size.height;
    }
    this.obj.attr('height', this.style.dimensions.height);
    this.obj.append("defs").append("clipPath").attr("class", "clip").attr('id', this.options.keys.join('-') + '-clip').append("rect").attr("width", this.style.dimensions.width).attr("height", this.style.dimensions.height).attr("y", top_offset).attr("x", left_offset);
    this.axes.y.scale = nh_graphs.scale.linear().domain([this.axes.y.min, this.axes.y.max]).range([top_offset + this.style.dimensions.height, top_offset]);
    self = this;
    this.axes.y.axis = nh_graphs.svg.axis().scale(this.axes.y.scale).orient('left').tickFormat(this.style.axis.step > 0 ? nh_graphs.format(",." + this.style.axis.step + "f") : nh_graphs.format("d")).tickSubdivide(this.style.axis.step);
    if (!this.style.axis.y.hide) {
      this.axes.y.obj = this.axes.obj.append('g').attr('class', 'y axis').call(this.axes.y.axis);
      this.style.axis.y.size = this.axes.y.obj[0][0].getBBox();
    }
    if (self.options.keys.length > 1) {
      values = [];
      ref = self.parent_obj.parent_obj.data.raw;
      for (j = 0, len = ref.length; j < len; j++) {
        ob = ref[j];
        values.push((function() {
          var k, len1, ref1, results;
          ref1 = self.options.keys;
          results = [];
          for (k = 0, len1 = ref1.length; k < len1; k++) {
            key = ref1[k];
            results.push(ob[key]);
          }
          return results;
        })());
      }
      this.axes.y.ranged_extent = nh_graphs.extent(values.concat.apply([], values));
    } else {
      this.axes.y.ranged_extent = nh_graphs.extent(self.parent_obj.parent_obj.data.raw, function(d) {
        return d[self.options.keys[0]];
      });
    }
    if (this.options.label != null) {
      y_label = this.axes.y.scale(this.axes.y.min) - (this.style.label_text_height * (this.options.keys.length + 1));
      this.drawables.background.obj.append('text').text(this.options.label).attr({
        'x': this.style.dimensions.width + this.style.label_text_height,
        'y': y_label,
        'class': 'label'
      });
      self = this;
      this.drawables.background.obj.selectAll('text.measurement').data(this.options.keys).enter().append('text').text(function(d, i) {
        var raw;
        raw = self.parent_obj.parent_obj.data.raw;
        if (i !== self.options.keys.length - 1) {
          return raw[self.parent_obj.parent_obj.data.raw.length - 1][d];
        } else {
          return raw[self.parent_obj.parent_obj.data.raw.length - 1][d] + '' + self.options.measurement;
        }
      }).attr({
        'x': self.style.dimensions.width + self.style.label_text_height,
        'y': function(d, i) {
          return self.axes.y.scale(self.axes.y.min) - (self.style.label_text_height * (self.options.keys.length - i));
        },
        'class': 'measurement'
      });
    }
    window.addEventListener('graph_resize', function(event) {
      return self.resize_graph(self, event);
    });
    rangify = self.parent_obj.parent_obj.options.controls.rangify;
    if (rangify != null) {
      rangify.addEventListener('click', function(event) {
        return self.rangify_graph(self, event);
      });
    }
  };

  NHGraph.prototype.draw = function(parent_obj) {
    var background_object, j, len, ref, self;
    self = this;
    if (self.drawables.background.data != null) {
      ref = self.drawables.background.data;
      for (j = 0, len = ref.length; j < len; j++) {
        background_object = ref[j];
        self.drawables.background.obj.selectAll(".range").data(self.drawables.background.data).enter().append("rect").attr({
          "class": function(d) {
            return d["class"] + ' range';
          },
          x: self.axes.x.scale(self.axes.x.scale.domain()[0]),
          y: function(d) {
            return self.axes.y.scale(d.e) - 1;
          },
          width: self.style.dimensions.width,
          "clip-path": "url(#" + self.options.keys.join('-') + '-clip' + ")",
          height: function(d) {
            return self.axes.y.scale(d.s) - (self.axes.y.scale(d.e) - 1);
          }
        });
      }
    }
    self.drawables.background.obj.selectAll('.normal').data([self.options.normal]).enter().append("rect").attr({
      'class': 'normal',
      'y': function(d) {
        return self.axes.y.scale(d.max);
      },
      'x': self.axes.x.scale(self.axes.x.scale.domain()[0]),
      'width': self.style.dimensions.width,
      'clip-path': 'url(#' + self.options.keys.join('-') + '-clip' + ')',
      'height': function(d) {
        return self.axes.y.scale(d.min) - (self.axes.y.scale(d.max));
      }
    });
    self.drawables.background.obj.selectAll(".grid.vertical").data(self.axes.x.scale.ticks()).enter().append("line").attr({
      "class": "vertical grid",
      x1: function(d) {
        return self.axes.x.scale(d);
      },
      x2: function(d) {
        return self.axes.x.scale(d);
      },
      y1: self.axes.y.scale.range()[1],
      y2: self.axes.y.scale.range()[0]
    });
    self.drawables.background.obj.selectAll(".grid.horizontal").data(self.axes.y.scale.ticks()).enter().append("line").attr({
      "class": "horizontal grid",
      x1: self.axes.x.scale(self.axes.x.scale.domain()[0]),
      x2: self.axes.x.scale(self.axes.x.scale.domain()[1]),
      y1: function(d) {
        return self.axes.y.scale(d);
      },
      y2: function(d) {
        return self.axes.y.scale(d);
      }
    });
    switch (self.style.data_style) {
      case 'stepped':
      case 'linear':
        self.drawables.area = nh_graphs.svg.line().interpolate(self.style.data_style === 'stepped' ? "step-after" : "linear").defined(function(d) {
          if (d.none_values === "[]") {
            return d;
          }
        }).x(function(d) {
          return self.axes.x.scale(self.date_from_string(d.date_terminated));
        }).y(function(d) {
          return self.axes.y.scale(d[self.options.keys[0]]);
        });
        if (self.parent_obj.parent_obj.data.raw.length > 1) {
          self.drawables.data.append("path").datum(self.parent_obj.parent_obj.data.raw).attr("d", self.drawables.area).attr("clip-path", "url(#" + self.options.keys.join('-') + '-clip' + ")").attr("class", "path");
        }
        self.drawables.data.selectAll(".point").data(self.parent_obj.parent_obj.data.raw.filter(function(d) {
          if (d.none_values === "[]") {
            return d;
          }
        })).enter().append("circle").attr("cx", function(d) {
          return self.axes.x.scale(self.date_from_string(d.date_terminated));
        }).attr("cy", function(d) {
          return self.axes.y.scale(d[self.options.keys[0]]);
        }).attr("r", 3).attr("class", "point").attr("clip-path", "url(#" + self.options.keys.join('-') + '-clip' + ")").on('mouseover', function(d) {
          return self.show_popup(d[self.options.keys[0]], event.pageX, event.pageY);
        }).on('mouseout', function(d) {
          return self.hide_popup();
        });
        return self.drawables.data.selectAll(".empty_point").data(self.parent_obj.parent_obj.data.raw.filter(function(d) {
          if (d.none_values !== "[]") {
            return d;
          }
        })).enter().append("circle").attr("cx", function(d) {
          return self.axes.x.scale(self.date_from_string(d.date_terminated));
        }).attr("cy", function(d) {
          return self.axes.y.scale(self.axes.y.scale.domain()[1] / 2);
        }).attr("r", 3).attr("class", "empty_point").attr("clip-path", "url(#" + self.options.keys.join('-') + '-clip' + ")").on('mouseover', function(d) {
          return self.show_popup('Partial observation', event.pageX, event.pageY);
        }).on('mouseout', function(d) {
          return self.hide_popup();
        });
      case 'range':
        if (self.options.keys.length === 2) {
          self.drawables.data.selectAll(".range.top").data(self.parent_obj.parent_obj.data.raw.filter(function(d) {
            if (d[self.options.keys[0]]) {
              return d;
            }
          })).enter().append("rect").attr({
            'y': function(d) {
              return self.axes.y.scale(d[self.options.keys[0]]);
            },
            'x': function(d) {
              return self.axes.x.scale(self.date_from_string(d.date_terminated)) - (self.style.range.cap.width / 2) + 1;
            },
            'height': self.style.range.cap.height,
            'width': self.style.range.cap.width,
            'class': 'range top',
            'clip-path': 'url(#' + self.options.keys.join('-') + '-clip' + ')'
          }).on('mouseover', function(d) {
            var k, key, len1, ref1, string_to_use;
            string_to_use = '';
            ref1 = self.options.keys;
            for (k = 0, len1 = ref1.length; k < len1; k++) {
              key = ref1[k];
              string_to_use += key + ': ' + d[key] + '<br>';
            }
            return self.show_popup('<p>' + string_to_use + '</p>', event.pageX, event.pageY);
          }).on('mouseout', function(d) {
            return self.hide_popup();
          });
          self.drawables.data.selectAll(".range.bottom").data(self.parent_obj.parent_obj.data.raw.filter(function(d) {
            if (d[self.options.keys[1]]) {
              return d;
            }
          })).enter().append("rect").attr({
            'y': function(d) {
              return self.axes.y.scale(d[self.options.keys[1]]);
            },
            'x': function(d) {
              return self.axes.x.scale(self.date_from_string(d.date_terminated)) - (self.style.range.cap.width / 2) + 1;
            },
            'height': self.style.range.cap.height,
            'width': self.style.range.cap.width,
            'class': 'range bottom',
            'clip-path': 'url(#' + self.options.keys.join('-') + '-clip' + ')'
          }).on('mouseover', function(d) {
            var k, key, len1, ref1, string_to_use;
            string_to_use = '';
            ref1 = self.options.keys;
            for (k = 0, len1 = ref1.length; k < len1; k++) {
              key = ref1[k];
              string_to_use += key + ': ' + d[key] + '<br>';
            }
            return self.show_popup('<p>' + string_to_use + '</p>', event.pageX, event.pageY);
          }).on('mouseout', function(d) {
            return self.hide_popup();
          });
          return self.drawables.data.selectAll(".range.extent").data(self.parent_obj.parent_obj.data.raw.filter(function(d) {
            if (d[self.options.keys[0]] && d[self.options.keys[1]]) {
              return d;
            }
          })).enter().append("rect").attr({
            'y': function(d) {
              return self.axes.y.scale(d[self.options.keys[0]]);
            },
            'x': function(d) {
              return self.axes.x.scale(self.date_from_string(d.date_terminated));
            },
            'height': function(d) {
              return self.axes.y.scale(d[self.options.keys[1]]) - self.axes.y.scale(d[self.options.keys[0]]);
            },
            'width': self.style.range.width,
            'class': 'range extent',
            'clip-path': 'url(#' + self.options.keys.join('-') + '-clip' + ')'
          }).on('mouseover', function(d) {
            var k, key, len1, ref1, string_to_use;
            string_to_use = '';
            ref1 = self.options.keys;
            for (k = 0, len1 = ref1.length; k < len1; k++) {
              key = ref1[k];
              string_to_use += key + ': ' + d[key] + '<br>';
            }
            return self.show_popup('<p>' + string_to_use + '</p>', event.pageX, event.pageY);
          }).on('mouseout', function(d) {
            return self.hide_popup();
          });
        } else {
          throw new Error('Cannot plot ranged graph with ' + self.options.keys.length + 'data points');
        }
      case 'star':
        return console.log('star');
      case 'pie':
        return console.log('pie');
      case 'sparkline':
        return console.log('sparkline');
      default:
        throw new Error('no graph style defined');
    }
  };

  NHGraph.prototype.redraw = function(parent_obj) {
    var adjusted_line, self, tick_font_size, tick_line_height;
    self = this;
    self.axes.obj.select('.x.axis').call(self.axes.x.axis);
    self.axes.obj.select('.y.axis').call(self.axes.y.axis);
    tick_font_size = self.style.axis_label_font_size;
    tick_line_height = self.style.axis_label_line_height;
    adjusted_line = tick_font_size * tick_line_height;
    this.axes.obj.selectAll(".x.axis g text").each(function(d) {
      var el, i, j, len, top_lines, tspan, word, words;
      el = nh_graphs.select(this);
      words = self.date_to_string(d).split(" ");
      el.text("");
      for (i = j = 0, len = words.length; j < len; i = ++j) {
        word = words[i];
        tspan = el.append("tspan").text(word);
        tspan.attr("style", "font-size: " + tick_font_size + "px;");
        if (i > 0) {
          tspan.attr("x", 0).attr("dy", adjusted_line);
        }
      }
      top_lines = ((words.length - 1) * adjusted_line) + tick_font_size;
      return el.attr("y", "-" + Math.round((top_lines * 10) / 10));
    });
    self.drawables.background.obj.selectAll('.range').attr('width', self.axes.x.scale.range()[1]).attr({
      'y': function(d) {
        return self.axes.y.scale(d.e) - 1;
      }
    }).attr({
      'height': function(d) {
        return self.axes.y.scale(d.s) - (self.axes.y.scale(d.e) - 1);
      }
    });
    self.drawables.background.obj.selectAll('.normal').attr({
      'width': self.axes.x.scale.range()[1],
      'y': function(d) {
        return self.axes.y.scale(d.max);
      },
      'height': function(d) {
        return self.axes.y.scale(d.min) - (self.axes.y.scale(d.max));
      }
    });
    self.drawables.background.obj.selectAll('.label').attr({
      'x': self.axes.x.scale.range()[1] + self.style.label_text_height
    });
    self.drawables.background.obj.selectAll('.measurement').attr({
      'x': self.axes.x.scale.range()[1] + self.style.label_text_height
    });
    self.drawables.background.obj.selectAll(".grid.vertical").data(self.axes.x.scale.ticks()).attr('x1', function(d) {
      return self.axes.x.scale(d);
    }).attr('x2', function(d) {
      return self.axes.x.scale(d);
    });
    self.drawables.background.obj.selectAll('.grid.horizontal').data(self.axes.y.scale.ticks()).attr('x2', self.axes.x.scale.range()[1]).attr('y1', function(d) {
      return self.axes.y.scale(d);
    }).attr('y2', function(d) {
      return self.axes.y.scale(d);
    });
    self.obj.selectAll('.clip').selectAll('rect').attr('width', self.axes.x.scale.range()[1]);
    switch (self.style.data_style) {
      case 'stepped':
      case 'linear':
        self.drawables.data.selectAll('.path').attr("d", self.drawables.area);
        self.drawables.data.selectAll('.point').attr('cx', function(d) {
          return self.axes.x.scale(self.date_from_string(d.date_terminated));
        }).attr('cy', function(d) {
          return self.axes.y.scale(d[self.options.keys[0]]);
        });
        break;
      case 'range':
        self.drawables.data.selectAll('.range.top').attr('x', function(d) {
          return self.axes.x.scale(self.date_from_string(d.date_terminated)) - (self.style.range.cap.width / 2) + 1;
        }).attr({
          'y': function(d) {
            return self.axes.y.scale(d[self.options.keys[0]]);
          }
        });
        self.drawables.data.selectAll('.range.bottom').attr('x', function(d) {
          return self.axes.x.scale(self.date_from_string(d.date_terminated)) - (self.style.range.cap.width / 2) + 1;
        }).attr({
          'y': function(d) {
            return self.axes.y.scale(d[self.options.keys[1]]);
          }
        });
        self.drawables.data.selectAll('.range.extent').attr('x', function(d) {
          return self.axes.x.scale(self.date_from_string(d.date_terminated));
        }).attr({
          'y': function(d) {
            return self.axes.y.scale(d[self.options.keys[0]]);
          }
        }).attr({
          'height': function(d) {
            return self.axes.y.scale(d[self.options.keys[1]]) - self.axes.y.scale(d[self.options.keys[0]]);
          }
        });
        break;
      case 'star':
        console.log('star');
        break;
      case 'pie':
        console.log('pie');
        break;
      case 'sparkline':
        console.log('sparkline');
        break;
      default:
        throw new Error('no graph style defined');
    }
  };

  return NHGraph;

})(NHGraphLib);

if (!window.NH) {
  window.NH = {};
}

window.NH.NHGraph = NHGraph;

var NHTable,
  bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

NHTable = (function(superClass) {
  extend(NHTable, superClass);

  function NHTable() {
    this.redraw = bind(this.redraw, this);
    this.draw = bind(this.draw, this);
    this.init = bind(this.init, this);
    this.range = null;
    this.keys = new Array();
    this.obj = null;
    this.header_row = null;
    this.data_rows = null;
    this.title = null;
    this.title_obj = null;
    this.data = null;
  }

  NHTable.prototype.init = function(parent_obj) {
    var header, i, key, len, ref;
    this.parent_obj = parent_obj;
    this.data = this.parent_obj.parent_obj.data.raw.concat();
    this.data.reverse();
    if (this.title != null) {
      this.title_obj = nh_graphs.select(this.parent_obj.parent_obj.el).append('h3').html(this.title);
    }
    this.obj = nh_graphs.select(parent_obj.parent_obj.el).append('table');
    this.obj.attr('class', 'nhtable');
    this.range = [parent_obj.axes.x.min, parent_obj.axes.x.max];
    header = ['Date'];
    ref = this.keys;
    for (i = 0, len = ref.length; i < len; i++) {
      key = ref[i];
      header.push(key['title']);
    }
    this.header_row = this.obj.append('thead').append('tr');
    this.header_row.selectAll('th').data(header).enter().append('th').text(function(d) {
      return d;
    });
    this.data_rows = this.obj.append('tbody');
  };

  NHTable.prototype.draw = function(parent_obj) {
    var i, key, keys, len, ref, self;
    self = this;
    keys = ['date_terminated'];
    ref = self.keys;
    for (i = 0, len = ref.length; i < len; i++) {
      key = ref[i];
      keys.push(key['key']);
    }
    self.data_rows.selectAll('tr').data(function() {
      var data, data_map, data_to_use;
      data_map = self.data.map(function(row) {
        if (self.date_from_string(row['date_terminated']) >= self.range[0] && self.date_from_string(row['date_terminated']) <= self.range[1]) {
          return keys.map(function(column) {
            return {
              column: column,
              value: row[column]
            };
          });
        }
      });
      data_to_use = (function() {
        var j, len1, results;
        results = [];
        for (j = 0, len1 = data_map.length; j < len1; j++) {
          data = data_map[j];
          if (data != null) {
            results.push(data);
          }
        }
        return results;
      })();
      return data_to_use;
    }).enter().append('tr').selectAll('td').data(function(d) {
      return d;
    }).enter().append('td').html(function(d) {
      var data, date_rotate;
      data = d.value;
      if (d.column === 'date_terminated') {
        data = self.date_to_string(self.date_from_string(data), false);
        date_rotate = data.split(' ');
        if (date_rotate.length === 1) {
          data = date_rotate[0];
        }
        data = date_rotate[1] + ' ' + date_rotate[0];
      }
      return data;
    });
  };

  NHTable.prototype.redraw = function(parent_obj) {
    var i, key, keys, len, ref, self;
    self = this;
    keys = ['date_terminated'];
    ref = self.keys;
    for (i = 0, len = ref.length; i < len; i++) {
      key = ref[i];
      keys.push(key['key']);
    }
    self.data_rows.selectAll('tr').remove();
    self.data_rows.selectAll('tr').data(function() {
      var data, data_map, data_to_use;
      data_map = self.data.map(function(row) {
        if (self.date_from_string(row['date_terminated']) >= self.range[0] && self.date_from_string(row['date_terminated']) <= self.range[1]) {
          return keys.map(function(column) {
            return {
              column: column,
              value: row[column]
            };
          });
        }
      });
      data_to_use = (function() {
        var j, len1, results;
        results = [];
        for (j = 0, len1 = data_map.length; j < len1; j++) {
          data = data_map[j];
          if (data != null) {
            results.push(data);
          }
        }
        return results;
      })();
      return data_to_use;
    }).enter().append('tr').selectAll('td').data(function(d) {
      return d;
    }).enter().append('td').html(function(d) {
      return d.value;
    });
  };

  return NHTable;

})(NHGraphLib);

if (!window.NH) {
  window.NH = {};
}

window.NH.NHTable = NHTable;
