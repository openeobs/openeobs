openerp.nh_eobs_analysis = function (instance) {

    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.board.AddToDashboard.include({
        add_dashboard: function () {

            // Get measures array from pivot table class
            var formView = this.__parentedParent.__parentedParent.__parentedChildren[2];
            var graph = formView.__parentedChildren[0];

            var measures = graph.pivot.measures.map(function (el) {
                return el.field;
            });

            var self = this;
            if (!this.view.view_manager.action || !this.$el.find("select").val()) {
                this.do_warn(_t("Can't find dashboard action"));
                return;
            }
            var data = this.view.build_search_data();
            var context = new instance.web.CompoundContext(this.view.dataset.get_context() || []);
            var domain = new instance.web.CompoundDomain(this.view.dataset.get_domain() || []);
            _.each(data.contexts, context.add, context);
            _.each(data.domains, domain.add, domain);

            context.add({
                heatmap_mode: graph.heatmap_mode,
                mode: graph.mode,
                measures: measures,
                group_by: instance.web.pyeval.eval('groupbys', data.groupbys || [])
            });

            var c = instance.web.pyeval.eval('context', context);
            for (var k in c) {
                if (c.hasOwnProperty(k) && /^search_default_/.test(k)) {
                    delete c[k];
                }
            }
            // TODO: replace this 6.1 workaround by attribute on <action/>
            c.dashboard_merge_domains_contexts = false;
            var d = instance.web.pyeval.eval('domain', domain);

            this.rpc('/board/add_to_dashboard', {
                menu_id: this.$el.find("select").val(),
                action_id: this.view.view_manager.action.id,
                context_to_save: c,
                domain: d,
                view_mode: this.view.view_manager.active_view,
                name: this.$el.find("input").val()
            }).done(function (r) {
                if (r === false) {
                    self.do_warn(_t("Could not add filter to dashboard"));
                } else {
                    self.$el.toggleClass('oe_opened');
                    self.do_notify(_t("Filter added to dashboard"), '');
                }
            });
        }
    });


    // Graph widget
    instance.web_graph.Graph.include({
        init: function (parent, model, domain, options) {
            this._super(parent, model, domain, options);
            if (options.context.measures) {
                this.pivot_options.measures = options.context.measures;
                this.heatmap_mode = options.context.heatmap_mode;
                this.mode = options.context.mode;
            }
        },
        add_measures_to_options: function() {
            var sorted_measures = ['__count', 'on_time', 'not_on_time', 'minutes_early', 'delay', 'trend_up', 'trend_same', 'trend_down'];
            this.measure_list.sort(function(a, b){
                var keyA = sorted_measures.indexOf(a.field),
                    keyB = sorted_measures.indexOf(b.field);
                // Compare the 2 dates
                if(keyA < keyB) return -1;
                if(keyA > keyB) return 1;
                return 0;
            });
            this.$('.graph_measure_selection').append(
            _.map(this.measure_list, function (measure) {
                return $('<li>').append($('<a>').attr('data-choice', measure.field)
                                         .attr('href', '#')
                                         .text(measure.string));
            }));
        },
        header_cell_clicked: function (event) {
            event.preventDefault();
            event.stopPropagation();
            var id = event.target.getAttribute('data-id'),
                header = this.pivot.get_header(id),
                self = this;

            if (header.expanded) {
                if (header.root === this.pivot.rows) {
                    this.fold_row(header, event);
                } else {
                    this.fold_col(header);
                }
                return;
            }
            if (header.path.length < header.root.groupby.length) {
                this.$row_clicked = $(event.target).closest('tr');
                this.expand(id);
                return;
            }
            if (!this.groupby_fields.length) {
                return;
            }

            var fields = _.map(this.groupby_fields, function (field) {
                    return {id: field.field, value: field.string, type:self.fields[field.field.split(':')[0]].type};
            });
            var sorted_fields = ['clinical_risk', 'previous_risk', 'score', 'previous_score', 'ward_id', 'location_str', 'staff_type', 'user_id', 'date_terminated', 'date_scheduled', 'type']

            fields.sort(function(a, b){
                var keyA = sorted_fields.indexOf(a.id),
                    keyB = sorted_fields.indexOf(b.id);
                // Compare the 2 dates
                if(keyA < keyB) return -1;
                if(keyA > keyB) return 1;
                return 0;
            });

            if (this.dropdown) {
                this.dropdown.remove();
            }
            this.dropdown = $(QWeb.render('field_selection', {fields:fields, header_id:id}));
            $(event.target).after(this.dropdown);
            this.dropdown.css({
                position:'absolute',
                left:event.originalEvent.layerX,
            });
            this.$('.field-selection').next('.dropdown-menu').first().toggle();
        },

        build_rows: function (headers, raw) {
            var self = this,
                pivot = this.pivot,
                m, i, j, k, cell, row;

            var rows = [];
            var cells, pivot_cells, values;

            var nbr_of_rows = headers.length;
            var col_headers = pivot.get_cols_leaves();

            for (i = 0; i < nbr_of_rows; i++) {
                row = headers[i];
                cells = [];
                pivot_cells = [];
                for (j = 0; j < pivot.cells.length; j++) {
                    if (pivot.cells[j].x == row.id || pivot.cells[j].y == row.id) {
                        pivot_cells.push(pivot.cells[j]);
                    }
                }

                for (j = 0; j < col_headers.length; j++) {
                    values = undefined;
                    for (k = 0; k < pivot_cells.length; k++) {
                        if (pivot_cells[k].x == col_headers[j].id || pivot_cells[k].y == col_headers[j].id) {
                            values = pivot_cells[k].values;
                            break;
                        }
                    }
                    if (!values) { values = new Array(pivot.measures.length);}
                    for (m = 0; m < pivot.measures.length; m++) {
                        // Added or 0 to prevent make_cell being called with undefined value (WI-2102)
                        cells.push(self.make_cell(row,col_headers[j],values[m] || 0, m, raw));
                    }
                }
                if (col_headers.length > 1) {
                    var totals = pivot.get_total(row);
                    for (m = 0; m < pivot.measures.length; m++) {
                        cell = self.make_cell(row, pivot.cols.headers[0], totals[m], m, raw);
                        cell.is_bold = 'true';
                        cells.push(cell);
                    }
                }
                rows.push({
                    id: row.id,
                    indent: row.path.length,
                    title: row.title,
                    expanded: row.expanded,
                    cells: cells,
                });
            }

            return rows;
        }
    });
}