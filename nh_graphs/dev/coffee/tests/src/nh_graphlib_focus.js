/* istanbul ignore next */
var NHFocus,
    bind = function (fn, me) {
        return function () {
            return fn.apply(me, arguments);
        };
    };

NHFocus = (function () {
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

    NHFocus.prototype.handle_resize = function (self, event) {
        var d, new_date, ref;
        if (!event.handled) {
            self.style.dimensions.width = self.parent_obj.style.dimensions.width - ((self.parent_obj.style.padding.left + self.parent_obj.style.padding.right) + (self.style.margin.left + self.style.margin.right));
            self.obj.attr('width', self.style.dimensions.width);
            if ((ref = self.axes.x.scale) != null) {
                ref.range()[1] = self.style.dimensions.width;
            }
            if (self.parent_obj.options.mobile.is_mob) {
                if (self.parent_obj.is_landscape()) {
                    new_date = new Date(self.axes.x.max);
                    d = new_date.getDate() - self.parent_obj.options.mobile.date_range.landscape;
                    new_date.setDate(d);
                    self.redraw([new_date, self.axes.x.max]);
                } else {
                    new_date = new Date(self.axes.x.max);
                    d = new_date.getDate() - self.parent_obj.options.mobile.date_range.portrait;
                    new_date.setDate(d);
                    self.redraw([new_date, self.axes.x.max]);
                }
            } else {
                self.redraw([self.axes.x.min, self.axes.x.max]);
            }
            event.handled = true;
        }
    };

    NHFocus.prototype.init = function (parent_svg) {
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
            return self = this;
        } else {
            throw new Error('Focus init being called before SVG initialised');
        }
    };

    NHFocus.prototype.draw = function (parent_svg) {
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

    NHFocus.prototype.redraw = function (extent) {
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


/* istanbul ignore if */

if (!window.NH) {
    window.NH = {};
}

window.NH.NHFocus = NHFocus;
