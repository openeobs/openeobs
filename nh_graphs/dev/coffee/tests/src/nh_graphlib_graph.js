
/* istanbul ignore next */
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
      plot_partial: true,
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

  NHGraph.prototype.rangify_graph = function(self, ranged) {
    var d0, d1;
    if (ranged) {
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
    self.redraw(self.parent_obj);
  };

  NHGraph.prototype.init = function(parent_obj) {
    var adjusted_line, d0, d1, dom, j, k, key, left_offset, len, len1, line_self, ob, ref, ref1, scaleNot, scaleRanged, self, tick_font_size, tick_line_height, top_offset, values, y_label;
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
    this.obj.append("defs").append("clipPath").attr("class", "clip").attr('id', this.options.keys.join('-') + '-clip').append("rect").attr("width", this.style.dimensions.width).attr("height", this.style.dimensions.height + 3).attr("y", top_offset).attr("x", left_offset);
    self = this;
    if (self.options.keys.length > 1) {
      values = [];
      ref = self.options.keys;
      for (j = 0, len = ref.length; j < len; j++) {
        key = ref[j];
        ref1 = self.parent_obj.parent_obj.data.raw;
        for (k = 0, len1 = ref1.length; k < len1; k++) {
          ob = ref1[k];
          if (typeof ob[key] === 'number') {
            values.push(ob[key]);
          } else {
            values.push(null);
          }
        }
      }
      this.axes.y.ranged_extent = nh_graphs.extent(values.concat.apply([], values));
    } else {
      this.axes.y.ranged_extent = nh_graphs.extent(self.parent_obj.parent_obj.data.raw, function(d) {
        if (typeof d[self.options.keys[0]] === 'number') {
          return d[self.options.keys[0]];
        } else {
          return null;
        }
      });
    }
    d0 = self.axes.y.ranged_extent[0] - self.style.range_padding;
    d1 = self.axes.y.ranged_extent[1] + self.style.range_padding;
    dom = [(d0 > 0 ? d0 : 0), d1];
    scaleRanged = nh_graphs.scale.linear().domain(dom).range([top_offset + this.style.dimensions.height, top_offset]);
    scaleNot = nh_graphs.scale.linear().domain([self.axes.y.min, self.axes.y.max]).range([top_offset + this.style.dimensions.height, top_offset]);
    if (this.parent_obj.parent_obj.options.ranged) {
      this.axes.y.scale = scaleRanged;
    } else {
      this.axes.y.scale = scaleNot;
    }
    this.axes.y.axis = nh_graphs.svg.axis().scale(this.axes.y.scale).orient('left').tickFormat(this.style.axis.step > 0 ? nh_graphs.format(",." + this.style.axis.step + "f") : nh_graphs.format("d")).tickSubdivide(this.style.axis.step);
    if (!this.style.axis.y.hide) {
      this.axes.y.obj = this.axes.obj.append('g').attr('class', 'y axis').call(this.axes.y.axis);
      this.style.axis.y.size = this.axes.y.obj[0][0].getBBox();
    }
    if (this.options.label != null) {
      y_label = scaleNot(this.axes.y.min) - (this.style.label_text_height * (this.options.keys.length + 1));
      this.drawables.background.obj.append('text').text(this.options.label).attr({
        'x': this.style.dimensions.width + this.style.label_text_height,
        'y': y_label,
        'class': 'label'
      });
      this.drawables.background.obj.selectAll('text.measurement').data(this.options.keys).enter().append('text').text(function(d, i) {
        var raw;
        raw = self.parent_obj.parent_obj.data.raw;
        if (i !== self.options.keys.length - 1) {
          if (raw[raw.length - 1][d] !== false) {
            return raw[raw.length - 1][d];
          } else {
            return 'NA';
          }
        } else {
          if (raw[raw.length - 1][d] !== false) {
            return raw[raw.length - 1][d] + '' + self.options.measurement;
          } else {
            return 'NA';
          }
        }
      }).attr({
        'x': self.style.dimensions.width + self.style.label_text_height,
        'y': function(d, i) {
          return scaleNot(self.axes.y.min) - (self.style.label_text_height * (self.options.keys.length - i));
        },
        'class': 'measurement'
      });
    }
    (function(self) {
      var max, min, valid, yMax, yMin;
      valid = true;
      if ((self.options.normal.min != null) && (self.options.normal.max != null)) {
        min = self.options.normal.min;
        max = self.options.normal.max;
        yMin = self.axes.y.min;
        yMax = self.axes.y.max;
        if (isNaN(min) || isNaN(max)) {
          valid = false;
        } else {
          if (min > yMax || min < yMin || min > max) {
            valid = false;
          }
          if (max < yMin || max > yMax || max < min) {
            valid = false;
          }
        }
      } else {
        valid = false;
      }
      if (!valid) {
        console.log('Invalid normal range defined');
        self.options.normal.min = 0;
        return self.options.normal.max = 0;
      }
    })(this);
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
          var key, none_vals, partial;
          none_vals = d.none_values;
          key = self.options.keys[0];
          partial = self.options.plot_partial;
          if (none_vals !== "[]" && d[key] !== false && partial) {
            return d;
          }
        })).enter().append("circle").attr("cx", function(d) {
          return self.axes.x.scale(self.date_from_string(d.date_terminated));
        }).attr("cy", function(d) {
          return self.axes.y.scale(d[self.options.keys[0]]);
        }).attr("r", 3).attr("class", "empty_point").attr("clip-path", "url(#" + self.options.keys.join('-') + '-clip' + ")").on('mouseover', function(d) {
          return self.show_popup('Partial observation: ' + d[self.options.keys[0]], event.pageX, event.pageY);
        }).on('mouseout', function(d) {
          return self.hide_popup();
        });
      case 'range':
        if (self.options.keys.length === 2) {
          self.drawables.data.selectAll(".range.top").data(self.parent_obj.parent_obj.data.raw.filter(function(d) {
            if (d.none_values === "[]" && d[self.options.keys[0]]) {
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
              string_to_use += key.replace(/_/g, ' ') + ': ' + d[key] + '<br>';
            }
            return self.show_popup('<p>' + string_to_use + '</p>', event.pageX, event.pageY);
          }).on('mouseout', function(d) {
            return self.hide_popup();
          });
          self.drawables.data.selectAll(".range.bottom").data(self.parent_obj.parent_obj.data.raw.filter(function(d) {
            if (d.none_values === "[]" && d[self.options.keys[1]]) {
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
              string_to_use += key.replace(/_/g, ' ') + ': ' + d[key] + '<br>';
            }
            return self.show_popup('<p>' + string_to_use + '</p>', event.pageX, event.pageY);
          }).on('mouseout', function(d) {
            return self.hide_popup();
          });
          self.drawables.data.selectAll(".range.extent").data(self.parent_obj.parent_obj.data.raw.filter(function(d) {
            var bottom, top;
            top = d[self.options.keys[0]];
            bottom = d[self.options.keys[1]];
            if (d.none_values === "[]" && top && bottom) {
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
              string_to_use += key.replace(/_/g, ' ') + ': ' + d[key] + '<br>';
            }
            return self.show_popup('<p>' + string_to_use + '</p>', event.pageX, event.pageY);
          }).on('mouseout', function(d) {
            return self.hide_popup();
          });
          self.drawables.data.selectAll(".range.top.empty_point").data(self.parent_obj.parent_obj.data.raw.filter(function(d) {
            var key, none_vals, partial;
            none_vals = d.none_values;
            key = self.options.keys[0];
            partial = self.options.plot_partial;
            if (none_vals !== "[]" && d[key] !== false && partial) {
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
            'class': 'range top empty_point',
            'clip-path': 'url(#' + self.options.keys.join('-') + '-clip' + ')'
          }).on('mouseover', function(d) {
            var k, key, len1, ref1, string_to_use;
            string_to_use = 'Partial Observation:<br>';
            ref1 = self.options.keys;
            for (k = 0, len1 = ref1.length; k < len1; k++) {
              key = ref1[k];
              string_to_use += key.replace(/_/g, ' ') + ': ' + d[key] + '<br>';
            }
            return self.show_popup('<p>' + string_to_use + '</p>', event.pageX, event.pageY);
          }).on('mouseout', function(d) {
            return self.hide_popup();
          });
          self.drawables.data.selectAll(".range.bottom.empty_point").data(self.parent_obj.parent_obj.data.raw.filter(function(d) {
            var key, none_vals, partial;
            none_vals = d.none_values;
            key = self.options.keys[1];
            partial = self.options.plot_partial;
            if (none_vals !== "[]" && d[key] !== false && partial) {
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
            'class': 'range bottom empty_point',
            'clip-path': 'url(#' + self.options.keys.join('-') + '-clip' + ')'
          }).on('mouseover', function(d) {
            var k, key, len1, ref1, string_to_use;
            string_to_use = 'Partial Observation:<br>';
            ref1 = self.options.keys;
            for (k = 0, len1 = ref1.length; k < len1; k++) {
              key = ref1[k];
              string_to_use += key.replace(/_/g, ' ') + ': ' + d[key] + '<br>';
            }
            return self.show_popup('<p>' + string_to_use + '</p>', event.pageX, event.pageY);
          }).on('mouseout', function(d) {
            return self.hide_popup();
          });
          return self.drawables.data.selectAll(".range.extent.empty_point").data(self.parent_obj.parent_obj.data.raw.filter(function(d) {
            var bottom, keys_valid, none_vals, partial, top;
            partial = self.options.plot_partial;
            top = d[self.options.keys[0]];
            bottom = d[self.options.keys[1]];
            none_vals = d.none_values;
            keys_valid = top !== false && bottom !== false;
            if (none_vals !== "[]" && keys_valid && partial) {
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
            'class': 'range extent empty_point',
            'clip-path': 'url(#' + self.options.keys.join('-') + '-clip' + ')'
          }).on('mouseover', function(d) {
            var k, key, len1, ref1, string_to_use;
            string_to_use = 'Partial Observation<br>';
            ref1 = self.options.keys;
            for (k = 0, len1 = ref1.length; k < len1; k++) {
              key = ref1[k];
              string_to_use += key.replace(/_/g, ' ') + ': ' + d[key] + '<br>';
            }
            return self.show_popup('<p>' + string_to_use + '</p>', event.pageX, event.pageY);
          }).on('mouseout', function(d) {
            return self.hide_popup();
          });
        } else {
          throw new Error('Cannot plot ranged graph with ' + self.options.keys.length + ' data point(s)');
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
        self.drawables.data.selectAll('.empty_point').attr('cx', function(d) {
          return self.axes.x.scale(self.date_from_string(d.date_terminated));
        }).attr("cy", function(d) {
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


/* istanbul ignore if */

if (!window.NH) {
  window.NH = {};
}

window.NH.NHGraph = NHGraph;
