/* istanbul ignore next */
var NHTable,
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

NHTable = (function (superClass) {
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

    NHTable.prototype.init = function (parent_obj) {
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
        this.header_row.selectAll('th').data(header).enter().append('th').text(function (d) {
            return d;
        });
        this.data_rows = this.obj.append('tbody');
    };

    NHTable.prototype.draw = function (parent_obj) {
        var i, key, keys, len, ref, self;
        self = this;
        keys = ['date_terminated'];
        ref = self.keys;
        for (i = 0, len = ref.length; i < len; i++) {
            key = ref[i];
            keys.push(key['key']);
        }
        self.data_rows.selectAll('tr').data(function () {
            var data, data_map, data_to_use;
            data_map = self.data.map(function (row) {
                if (self.date_from_string(row['date_terminated']) >= self.range[0] && self.date_from_string(row['date_terminated']) <= self.range[1]) {
                    return keys.map(function (column) {
                        return {
                            column: column,
                            value: row[column]
                        };
                    });
                }
            });
            data_to_use = (function () {
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
        }).enter().append('tr').selectAll('td').data(function (d) {
            return d;
        }).enter().append('td').html(function (d) {
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

    NHTable.prototype.redraw = function (parent_obj) {
        var i, key, keys, len, ref, self;
        self = this;
        keys = ['date_terminated'];
        ref = self.keys;
        for (i = 0, len = ref.length; i < len; i++) {
            key = ref[i];
            keys.push(key['key']);
        }
        self.data_rows.selectAll('tr').remove();
        self.data_rows.selectAll('tr').data(function () {
            var data, data_map, data_to_use;
            data_map = self.data.map(function (row) {
                if (self.date_from_string(row['date_terminated']) >= self.range[0] && self.date_from_string(row['date_terminated']) <= self.range[1]) {
                    return keys.map(function (column) {
                        return {
                            column: column,
                            value: row[column]
                        };
                    });
                }
            });
            data_to_use = (function () {
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
        }).enter().append('tr').selectAll('td').data(function (d) {
            return d;
        }).enter().append('td').html(function (d) {
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

    return NHTable;

})(NHGraphLib);


/* istanbul ignore if */

if (!window.NH) {
    window.NH = {};
}

window.NH.NHTable = NHTable;
