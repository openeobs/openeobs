openerp.nh_eobs_analysis = function (instance) {

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
        }
    });
}