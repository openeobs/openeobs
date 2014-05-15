openerp.t4clinical_ui = function (instance) {

    var QWeb = instance.web.qweb;
    var timing, timing2, timing3;
    var refresh_placement = false;
    var refresh_active_poc = false;
    var _t = instance.web._t;

    instance.web.T4TreeView = instance.web.TreeView.extend({

        activate: function (id) {
            var self = this;
            if ('t4_open_form' in this.dataset.context) {
                var form_id = this.dataset.context['t4_open_form'];
                return self.do_action({
                    type: 'ir.actions.act_window',
                    res_model: self.dataset.model,
                    res_id: id,
                    views: [[form_id, 'form']],
                    target: 'current',
                    view_id: form_id,
                    context: this.dataset.context
                });
            }
            return this._super(id);
        }
    });

    instance.web.views.add('tree', 'instance.web.T4TreeView');

    instance.t4clinical_ui.Button = instance.web.list.Column.extend({
        format: function (row_data, options) {
            options = options || {};
            var attrs = {};
            if (options.process_modifiers !== false) {
                attrs = this.modifiers_for(row_data);
            }
            if (attrs.invisible) { return ''; }
            if (this.widget == 'act_button'){
                return QWeb.render('t4.ListView.row.act_button', {
                    widget: this,
                    prefix: instance.session.prefix,
                    active: row_data.active.value,
                    inactive: !row_data.active.value,
                    disabled: attrs.readonly
                        || isNaN(row_data.id.value)
                        || instance.web.BufferedDataSet.virtual_id_regex.test(row_data.id.value)
                })
            }
            else{
                return QWeb.render('t4.ListView.row.button', {
                    widget: this,
                    prefix: instance.session.prefix,
                    disabled: attrs.readonly
                        || isNaN(row_data.id.value)
                        || instance.web.BufferedDataSet.virtual_id_regex.test(row_data.id.value)
                })
            }
        }
    });

    instance.web.list.columns.add('button', 'instance.t4clinical_ui.Button');

    instance.web.UserMenu.include({
        on_menu_help: function() {
            window.open('http://www.tactix4.net', '_blank');
        },
        do_update: function(){
            var self = this;
            var fct = function() {
                var $avatar = self.$el.find('.oe_topbar_avatar');
                $avatar.attr('src', $avatar.data('default-src'));
                if (!self.session.uid)
                    return;
                var func = new instance.web.Model("res.users").get_func("read");
                return self.alive(func(self.session.uid, ["name", "company_id"])).then(function(res) {
                    var topbar_name = res.name;
                    if(instance.session.debug)
                        topbar_name = _.str.sprintf("%s (%s)", topbar_name, instance.session.db);
                    if(res.company_id[0] > 1)
                        topbar_name = _.str.sprintf("%s (%s)", topbar_name, res.company_id[1]);
                    self.$el.find('.oe_topbar_name').text(topbar_name);
                    if (!instance.session.debug) {
                        topbar_name = _.str.sprintf("%s (%s)", topbar_name, instance.session.db);
                    }
                    var avatar_src = self.session.url('/web/binary/image', {model:'res.users', field: 'image_small', id: self.session.uid});
                    $avatar.attr('src', avatar_src);
                });
            };
            this.update_promise = this.update_promise.then(fct, fct);
        },
    });

    instance.web.ListView.include({
        init: function(parent, dataset, view_id, options) {

            if (options.action){
                if (options.action.name == "Patient Placements" || options.action.name == "Wardboard" || options.action.name == "Active Points of Care" || options.action.name == "Inactive Points of Care"){
                    options.selectable = false;
                };
                if (options.action.name == "Wardboard"){
                    if (typeof(timing) != 'undefined'){
                        clearInterval(timing);
                    }
                    timing = window.setInterval(function(){
                        var button =  $("a:contains('Wardboard')");
                        if ($(".ui-dialog").length == 0 && button.parent('li').hasClass('oe_active') && $(".oe_view_manager_view_list").css('display') != 'none'){
                            button.click();
                        }
                    }, 300000);
                }
                else if (options.action.name == "Patient Placements"){
                    if (typeof(timing2) != 'undefined'){
                        clearInterval(timing2);
                    }
                    timing2 = window.setInterval(function(){
                        var button =  $("a:contains('Patient Placements')");
                        if ($(".ui-dialog").length == 0 && $(".oe_view_manager_view_list").css('display') != 'none'){
                            if (refresh_placement){
                                button.click();
                                refresh_placement = false;
                            }
                        }
                    }, 10);
                }
                else if (options.action.name == "Active Points of Care" || options.action.name == "Inactive Points of Care"){
                    if (typeof(timing3) != 'undefined'){
                        clearInterval(timing3);
                    }
                    timing3 = window.setInterval(function(){
                        if (options.action.name == "Active Points of Care"){
                            var button =  $("a:contains('Active Points of Care')");
                        } else {
                            var button =  $("a:contains('Inactive Points of Care')");
                        }
                        if (refresh_active_poc){
                            button.click();
                            refresh_active_poc = false;
                        }
                    }, 10);
                }
                else{
                    if (typeof(timing) != 'undefined'){
                        clearInterval(timing);
                    }
                    if (typeof(timing2) != 'undefined'){
                        clearInterval(timing2);
                    }
                    if (typeof(timing3) != 'undefined'){
                        clearInterval(timing3);
                    }
                }
            };
            this._super.apply(this, [parent, dataset, view_id, options]);

        },

        select_record: function (index, view) {
            view = view || index == null ? 'form' : 'form';
            this.dataset.index = index;
            if (this.fields_view.name != "T4 Clinical patient placement activity Tree View"){
                _.delay(_.bind(function () {
                    this.do_switch_view(view);
                }, this));
            }
        },

        do_button_action: function (name, id, callback) {
            this.handle_button(name, id, callback);
            if (name == "activate_deactivate"){
                refresh_active_poc = true;
            }
        },

    });

    instance.t4clinical_ui.T4Many2One = instance.web.form.FieldMany2One.extend({
        get_search_result: function(search_val) {
            var self = this;

            var dataset = new instance.web.DataSet(this, this.field.relation, self.build_context());
            var blacklist = this.get_search_blacklist();
            this.last_query = search_val;

            return this.orderer.add(dataset.name_search(
                    search_val, new instance.web.CompoundDomain(self.build_domain(), [["id", "not in", blacklist]]),
                    'ilike', this.limit + 1, self.build_context())).then(function(data) {
                self.last_search = data;
                // possible selections for the m2o
                var values = _.map(data, function(x) {
                    x[1] = x[1].split("\n")[0];
                    return {
                        label: _.str.escapeHTML(x[1]),
                        value: x[1],
                        name: x[1],
                        id: x[0],
                    };
                });

                // search more... if more results that max
                if (values.length > self.limit) {
                    values = values.slice(0, self.limit);
                    values.push({
                        label: _t("Search More..."),
                        action: function() {
                            dataset.name_search(search_val, self.build_domain(), 'ilike', false).done(function(data) {
                                self._search_create_popup("search", data);
                            });
                        },
                        classname: 'oe_m2o_dropdown_option'
                    });
                }

                return values;
            });
        }
    });

    instance.web.form.widgets.add('t4_many2one', 'instance.t4clinical_ui.T4Many2One');

    instance.t4clinical_ui.GenderWidget = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            if (row_data.sex.value == 'M'){
                return QWeb.render('t4_genderCell', {
                    'widget': this,
                    'prefix': instance.session.prefix,
                    'male': true,
                    'female': false,
                });
            } else if (row_data.sex.value == 'F'){
                return QWeb.render('t4_genderCell', {
                    'widget': this,
                    'prefix': instance.session.prefix,
                    'male': false,
                    'female': true,
                });
            } else {
                return 'Not Given';
            };
        },
    });

    instance.web.list.columns.add('field.t4_gender', 'instance.t4clinical_ui.GenderWidget');

    instance.t4clinical_ui.ScoreTrendWidget = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            if (row_data.ews_trend_string.value == 'up'){
                return QWeb.render('t4_trendCell', {
                    'widget': this,
                    'prefix': instance.session.prefix,
                    'up': true,
                    'down': false,
                    'same': false,
                });
            } else if (row_data.ews_trend_string.value == 'down') {
                return QWeb.render('t4_trendCell', {
                    'widget': this,
                    'prefix': instance.session.prefix,
                    'up': false,
                    'down': true,
                    'same': false,
                });
            } else if (row_data.ews_trend_string.value == 'same'){
                return QWeb.render('t4_trendCell', {
                    'widget': this,
                    'prefix': instance.session.prefix,
                    'up': false,
                    'down': false,
                    'same': true,
                });
            } else {
                return row_data.ews_trend_string.value;
                if (row_data.ews_score_string.value !== 'none'){
                    return "Initial Value";
                }
                return "Waiting 1st Observation";
            };
        },
    });

    instance.web.list.columns.add('field.t4_scoretrend', 'instance.t4clinical_ui.ScoreTrendWidget');

    instance.t4clinical_ui.WidgetButton = instance.web.form.WidgetButton.extend({
        on_click: function() {
            var self = this;
            this.force_disabled = true;
            this.check_disable();
            this.execute_action().always(function() {
                self.force_disabled = false;
                self.check_disable();
            });
            if (this.string == "Confirm Placement"){
                refresh_placement = true;
                console.log(this);
            }
        },
    });
    instance.web.form.tags.add('button', 'instance.t4clinical_ui.WidgetButton');
}