/* istanbul ignore next */
var NHContext,
    bind = function (fn, me) {
        return function () {
            return fn.apply(me, arguments);
        };
    },
    extend = function (child, parent) {
        for (var key in parent) {
            if (hasProp.call(parent, key)) child[key] = parent[key];
        }
        function ctor() {
            this.constructor = child;
        }

        ctor.prototype = parent.prototype;
        child.prototype = new ctor();
        child.__super__ = parent.prototype;
        return child;
    },
    hasProp = {}.hasOwnProperty;

NHContext = (function (superClass) {
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

    NHContext.prototype.handle_resize = function (self, parent_svg, event) {
        var d, new_date, ref, ref1, ref2, ref3, ref4;
        if (!event.handled) {
            self.style.dimensions.width = self.parent_obj.style.dimensions.width - ((self.parent_obj.style.padding.left + self.parent_obj.style.padding.right) + (self.style.margin.left + self.style.margin.right));
            self.obj.attr('width', self.style.dimensions.width);
            if ((ref = self.axes.x.scale) != null) {
                ref.range()[1] = self.style.dimensions.width;
            }
            self.graph.resize_graph(self.graph, event);
            self.parent_obj.focus.handle_resize(self.parent_obj.focus, event);
            if (self.parent_obj.options.mobile.is_mob) {
                new_date = new Date(self.axes.x.max);
                if (self.parent_obj.is_landscape()) {
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
            event.handled = true;
        }
    };

    NHContext.prototype.handle_brush = function (self, context) {
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

    NHContext.prototype.init = function (parent_svg) {
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
            this.brush = nh_graphs.svg.brush().x(this.graph.axes.x.scale).on("brush", function (context) {
                if (context == null) {
                    context = self;
                }
                return self.handle_brush(self, context);
            });
            this.graph.drawables.brush.append("g").attr("class", "x brush").call(this.brush).selectAll("rect").attr("y", 0).attr("height", this.graph.style.dimensions.height);
            self = this;
        } else {
            throw new Error('Context init being called before SVG initialised');
        }
    };

    NHContext.prototype.draw = function (parent_svg) {
        this.graph.draw(this);
    };

    return NHContext;

})(NHGraphLib);


/* istanbul ignore if */

if (!window.NH) {
    window.NH = {};
}

window.NH.NHContext = NHContext;
