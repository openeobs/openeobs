var logout_time = 1200000;

openerp.nh_eobs = function (instance) {

    var QWeb = instance.web.qweb;
    var printing = false;
    var timing, timing2, timing3, timing4, timing5;
    var refresh_placement = false;
    var refresh_active_poc = false;
    var wardboard_refreshed = false;
    var _t = instance.web._t;
    var logout_timeout, session;
    var wardboard_groups_opened = false;
    var kiosk_mode = false;
    var kiosk_t;
    var ranged_chart = null;
    // regex to sort out Odoo's idiotic timestamp format
    var date_regex = new RegExp('([0-9][0-9][0-9][0-9])-([0-9][0-9])-([0-9][0-9]) ([0-9][0-9]):([0-9][0-9]):([0-9][0-9])');

    instance.web.NHTreeView = instance.web.TreeView.extend({

        activate: function (id) {
            var self = this;
            if ('nh_open_form' in this.dataset.context) {
                var form_id = this.dataset.context['nh_open_form'];
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

    instance.web.views.add('tree', 'instance.web.NHTreeView');

    instance.nh_eobs.Button = instance.web.list.Column.extend({
        format: function (row_data, options) {
            options = options || {};
            var attrs = {};
            if (options.process_modifiers !== false) {
                attrs = this.modifiers_for(row_data);
            }
            if (attrs.invisible) { return ''; }
            if (this.widget == 'act_button'){
                return QWeb.render('nh.ListView.row.act_button', {
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
                return QWeb.render('nh.ListView.row.button', {
                    widget: this,
                    prefix: instance.session.prefix,
                    disabled: attrs.readonly
                        || isNaN(row_data.id.value)
                        || instance.web.BufferedDataSet.virtual_id_regex.test(row_data.id.value)
                })
            }
        }
    });

    instance.web.list.columns.add('button', 'instance.nh_eobs.Button');

    instance.web.UserMenu.include({
        on_menu_help: function() {
            window.open('http://www.neovahealth.co.uk', '_blank');
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
                if (['Doctors','Spells','Hospital Wards','Device Categories','Patients Board','Overdue Tasks','Doctor Tasks','Device Types','Devices','O2 Targets','User Management','Recently Discharged','Recently Transferred','Patients without bed','Wardboard','Active Points of Care','Inactive Points of Care'].indexOf(options.action.name) > -1){
                    options.selectable = false;
                };
                if ('Patients' != options.action.name){
                    options.import_enabled = false;
                };
                if (typeof(timing5) != 'undefined'){
                    clearInterval(timing5);
                }
                wardboard_groups_opened = false;
                if (options.action.name == "Patients Board"){
                    if (typeof(timing) != 'undefined'){
                        clearInterval(timing);
                    }
                    timing = window.setInterval(function(){
                        var button =  $("a:contains('Patients Board')");
                        if ($(".ui-dialog").length == 0 && button.parent('li').hasClass('oe_active') && $(".oe_view_manager_view_list").css('display') != 'none'){
                            wardboard_refreshed = true;
                            button.click();
                        }
                    }, 300000);
                    timing5 = window.setInterval(function(){
                        var groups =  $(".oe_group_header");
                        if (!wardboard_groups_opened && groups){
                            wardboard_groups_opened = true;
                            groups.click();
                        }
                    }, 700);
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

            if (!wardboard_refreshed){
                if (typeof(logout_timeout) != 'undefined'){
                    clearInterval(logout_timeout);
                }
                session = this.session;
                logout_timeout = window.setInterval(function(){
                    session.session_logout().done(function(){
                        location.reload();
                    });
                }, logout_time);
            } else {
                wardboard_refreshed = false;
            }

        },

        select_record: function (index, view) {
            // called when selecting the row

            view = view || index == null ? 'form' : 'form';
            this.dataset.index = index;
            if (this.fields_view.name != "NH Clinical Placement Tree View"){
                _.delay(_.bind(function () {
                    this.do_switch_view(view);
                }, this));
            }
        },

        do_button_action: function (name, id, callback) {
            // called when pressing a button on row
            this.handle_button(name, id, callback);
            if (name == "switch_active_status"){
                refresh_active_poc = true;
            }
        },

        load_list: function(data) {
            this._super(data);
            if (this.model == 'nh.clinical.patient.observation.pbp'){
                this.$el.html(QWeb.render('ListViewPBP', this));
            }
        }

    });

    //instance.web.ListView.List.include({
    //    row_clicked: function(e, view){
    //        if()
    //    }
    //})

    instance.nh_eobs.NHMany2One = instance.web.form.FieldMany2One.extend({
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

    instance.web.form.widgets.add('nh_many2one', 'instance.nh_eobs.NHMany2One');

    instance.nh_eobs.GenderWidget = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            if (row_data.sex.value == 'M'){
                return QWeb.render('nh_genderCell', {
                    'widget': this,
                    'prefix': instance.session.prefix,
                    'male': true,
                    'female': false,
                });
            } else if (row_data.sex.value == 'F'){
                return QWeb.render('nh_genderCell', {
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

    instance.web.list.columns.add('field.nh_gender', 'instance.nh_eobs.GenderWidget');

    instance.nh_eobs.ScoreTrendWidget = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            if (row_data.ews_trend_string.value == 'up'){
                return QWeb.render('nh_trendCell', {
                    'widget': this,
                    'prefix': instance.session.prefix,
                    'up': true,
                    'down': false,
                    'same': false,
                });
            } else if (row_data.ews_trend_string.value == 'down') {
                return QWeb.render('nh_trendCell', {
                    'widget': this,
                    'prefix': instance.session.prefix,
                    'up': false,
                    'down': true,
                    'same': false,
                });
            } else if (row_data.ews_trend_string.value == 'same'){
                return QWeb.render('nh_trendCell', {
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

    instance.web.list.columns.add('field.nh_scoretrend', 'instance.nh_eobs.ScoreTrendWidget');

    instance.nh_eobs.WidgetButton = instance.web.form.WidgetButton.extend({
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
    instance.web.form.tags.add('button', 'instance.nh_eobs.WidgetButton');

    instance.nh_eobs.EwsChartWidget = instance.web.form.AbstractField.extend({
        template: 'nh_ewschart',
        className: 'nh_ewschart',

        init: function (field_manager, node) {
            console.log("EWSCHART INIT");
        	this._super(field_manager, node);
            this.dataset = new instance.web.form.One2ManyDataSet(this, this.field.relation);
            this.dataset.o2m = this;
            this.dataset.parent_view = this.view;
            this.dataset.child_name = this.name;
            var self = this
        },
        set_value: function(value_){
            this.set({'value': value_});
            $('#rangify').on('mouseup', function(e){
               if($('#rangify').attr('checked')){
                   ranged_chart = false;
               }else{
                   ranged_chart = true;
               }
            });
            this.render_chart();
        },
        render_chart: function(){
            this.model = new instance.web.Model('nh.eobs.api');
            this.wardboard_model = new instance.web.Model('nh.clinical.wardboard');
            var vid = this.view.dataset.context.active_id;
        	var self = this;




            if(typeof(this.view.dataset.context.printing) !== "undefined" && this.view.dataset.context.printing === "true"){
                printing = true;
            }

            var recData = this.model.call('get_activities_for_spell',[this.view.dataset.ids[this.view.dataset.index],'ews'], {context: this.view.dataset.context}).done(function(records){
                var svg = new window.NH.NHGraphLib('#chart');

                $(svg.el).html('');
                if(records.length > 0){
                    var obs = records.reverse();

                    obs.forEach(function(d){
                        d.body_temperature = d.body_temperature.toFixed(1);

                        var date_els = d.date_terminated.match(date_regex);
                        var dt = new Date(date_els[1], (parseInt(date_els[2])-1), date_els[3], date_els[4], date_els[5], date_els[6], 0);
                        var days = ["Sun", "Mon", "Tues", "Wed", "Thu", "Fri", "Sat"];
                        d.date_terminated = days[dt.getDay()] + " " + +dt.getDate() + '/' + ('0'+(dt.getMonth() + 1)).slice(-2) + "/" + ('0'+(dt.getFullYear())).slice(-2) + " " + ('0'+(dt.getHours())).slice(-2) + ":" + ('0'+(dt.getMinutes())).slice(-2);


                        if (d.flow_rate > -1){
                            plotO2 = true;
                            d.inspired_oxygen = "";
                            if(d.flow_rate > -1){
                                d.inspired_oxygen += "Flow: " + d.flow_rate + "l/hr<br>";
                            }
                            if(d.inspired_oxygen > -1){
                                d.inspired_oxygen += "Concentration: " + d.concentration + "%<br>";
                            }
                            if(d.cpap_peep > -1){
                                d.inspired_oxygen += "CPAP PEEP: " + d.cpap_peep + "<br>";
                            }else if(d.niv_backup > -1){
                                d.inspired_oxygen += "NIV Backup Rate: " + d.niv_backup + "<br>";
                                d.inspired_oxygen += "NIV EPAP: " + d.niv_epap + "<br>";
                                d.inspired_oxygen += "NIV IPAP: " + d.niv_ipap + "<br>";
                            }
                        }
                        if (d.indirect_oxymetry_spo2) {
                            d.indirect_oxymetry_spo2_label = d.indirect_oxymetry_spo2 + "%";
                        }
                    });

                    var resp_rate_graph = new window.NH.NHGraph();
                    resp_rate_graph.options.keys = ['respiration_rate'];
                    resp_rate_graph.options.label = 'RR';
                    resp_rate_graph.options.measurement = '/min';
                    resp_rate_graph.axes.y.min = 0;
                    resp_rate_graph.axes.y.max = 60;
                    resp_rate_graph.options.normal.min = 12;
                    resp_rate_graph.options.normal.max = 20;
                    resp_rate_graph.style.dimensions.height = 250;
                    resp_rate_graph.style.data_style = 'linear';
                    resp_rate_graph.style.label_width = 60;

                    var oxy_graph = new window.NH.NHGraph()
                    oxy_graph.options.keys = ['indirect_oxymetry_spo2'];
                    oxy_graph.options.label = 'Spo2';
                    oxy_graph.options.measurement = '%';
                    oxy_graph.axes.y.min = 70;
                    oxy_graph.axes.y.max = 100;
                    oxy_graph.options.normal.min = 96;
                    oxy_graph.options.normal.max = 100;
                    oxy_graph.style.dimensions.height = 200;
                    oxy_graph.style.axis.x.hide = true;
                    oxy_graph.style.data_style = 'linear';
                    oxy_graph.style.label_width = 60;

                    var temp_graph = new window.NH.NHGraph();
                    temp_graph.options.keys = ['body_temperature'];
                    temp_graph.options.label = 'Temp';
                    temp_graph.options.measurement = '°C';
                    temp_graph.axes.y.min = 15;
                    temp_graph.axes.y.max = 50;
                    temp_graph.options.normal.min = 35;
                    temp_graph.options.normal.max = 37.1;
                    temp_graph.style.dimensions.height = 200;
                    temp_graph.style.axis.x.hide = true;
                    temp_graph.style.data_style = 'linear';
                    temp_graph.style.label_width = 60;

                    var pulse_graph = new window.NH.NHGraph();
                    pulse_graph.options.keys = ['pulse_rate'];
                    pulse_graph.options.label = 'HR';
                    pulse_graph.options.measurement = '/min';
                    pulse_graph.axes.y.min = 30;
                    pulse_graph.axes.y.max = 200;
                    pulse_graph.options.normal.min = 50;
                    pulse_graph.options.normal.max = 100;
                    pulse_graph.style.dimensions.height = 200;
                    pulse_graph.style.axis.x.hide = true;
                    pulse_graph.style.data_style = 'linear';
                    pulse_graph.style.label_width = 60;

                    var bp_graph = new window.NH.NHGraph();
                    bp_graph.options.keys = ['blood_pressure_systolic', 'blood_pressure_diastolic'];
                    bp_graph.options.label = 'BP';
                    bp_graph.options.measurement = 'mmHg';
                    bp_graph.axes.y.min = 30;
                    bp_graph.axes.y.max = 260;
                    bp_graph.options.normal.min = 150;
                    bp_graph.options.normal.max = 151;
                    bp_graph.style.dimensions.height = 200;
                    bp_graph.style.axis.x.hide = true;
                    bp_graph.style.data_style = 'range';
                    bp_graph.style.label_width = 60;

                    var score_graph = new window.NH.NHGraph();
                    score_graph.options.keys = ['score'];
                    score_graph.style.dimensions.height = 200;
                    score_graph.style.data_style = 'stepped';
                    score_graph.axes.y.min = 0;
                    score_graph.axes.y.max = 22;
                    score_graph.drawables.background.data =  [
                        {"class": "green",s: 1, e: 4},
                        {"class": "amber",s: 4,e: 6},
                        {"class": "red",s: 6,e: 22}
                    ];
                    score_graph.style.label_width = 60;


                    var tabular_obs = new window.NH.NHTable();
                    tabular_obs.keys = [{key:'avpu_text', title: 'AVPU'}, {key:'oxygen_administration_flag', title: 'On Supplemental O2'}, {key:'inspired_oxygen', title: 'Inspired Oxygen'}];
                    tabular_obs.title = 'Tabular values';
                    var focus = new window.NH.NHFocus();
                    var context = new window.NH.NHContext();
                    focus.graphs.push(resp_rate_graph);
                    focus.graphs.push(oxy_graph);
                    focus.graphs.push(temp_graph);
                    focus.graphs.push(pulse_graph);
                    focus.graphs.push(bp_graph);
                    focus.tables.push(tabular_obs);
                    focus.title = 'Individual values';
                    focus.style.padding.right = 0;
                    context.graph = score_graph;
                    context.title = 'NEWS Score';
                    svg.focus = focus;
                    svg.context = context;
                    svg.options.controls.rangify = document.getElementById('rangify');
                    svg.data.raw = obs;
                    svg.init();
                    svg.draw();
                    if(ranged_chart == null){
                        if($('#rangify:checked').length < 1){
                            $('#rangify').click();
                        }else{
                            $('#rangify').click();
                            $('#rangify').click();
                        }
                    }else{
                        if(ranged_chart){
                            if($('#rangify:checked').length < 1){
                                $('#rangify').click();
                            }else{
                                $('#rangify').click();
                                $('#rangify').click();
                            }
                        }else{
                            if($('#rangify:checked').length < 1){
                                $('#rangify').click();
                                $('#rangify').click();
                            }else{
                                $('#rangify').click();
                            }
                        }
                    }


                    if(printing){
                        if (typeof(timing4) != 'undefined'){
                            clearInterval(timing4);
                        }
                        timing4 = window.setInterval(function(){
                            if (printing){
                                window.print();
                                printing = false;
                                graph_lib.svg.printing = false;
                                clearInterval(timing4);
                            }
                        }, 1000);
                    }

                }else{
                    $(svg.el).html('<p>No data available for this patient</p>');
                    //d3.select(svg.el).append("text").text("No data available for this patient");
                }
            });
        },
    });

    instance.web.form.widgets.add('nh_ewschart', 'instance.nh_eobs.EwsChartWidget');

    instance.nh_eobs.PrescribeWidget = instance.web.form.AbstractField.extend({
        template: 'nh_prescribe',
        className: 'nh_prescribe',

        init: function (field_manager, node) {
        	this._super(field_manager, node);
        	this.model = new instance.web.Model('ir.config_parameter');
        	var self = this;
        	var recData = this.model.call('search',[[['key', '=', 'nh.eobs.prescribe.url']]], {context: this.view.dataset.context}).done(function(records){
        	    if(records.length > 0){
        	        var recData2 = self.model.call('read',[records[0],['value']], {context: self.view.dataset.context}).done(function(record){
        	            if(record){
        	                self.url = record.value;
        	                self.$el.html(QWeb.render('nh_prescribe', {
                                url: encodeURI(decodeURI(self.url))
                            }));
        	            }
        	        });
        	    }
        	});
        }
    });

    instance.web.form.widgets.add('nh_prescribe', 'instance.nh_eobs.PrescribeWidget');

    instance.nh_eobs.BloodSugarChartWidget = instance.web.form.AbstractField.extend({
        template: 'nh_bschart',
        className: 'nh_ewschart',


        init: function (field_manager, node) {
            console.log("SUGARCHART INIT");
        	this._super(field_manager, node);
            this.dataset = new instance.web.form.One2ManyDataSet(this, this.field.relation);
            this.dataset.o2m = this;
            this.dataset.parent_view = this.view;
            this.dataset.child_name = this.name;
            var self = this
        },
        start: function() {
        	this._super();
        	var self = this;

            var vid = this.view.dataset.context.active_id;
            this.model = new instance.web.Model('nh.eobs.api');

            var recData = this.model.call('get_activities_for_spell',[this.view.dataset.ids[0],'blood_sugar'], {context: this.view.dataset.context}).done(function(records){
                var svg = new window.NH.NHGraphLib('#chart');

                var obs = records.reverse();
                if(obs.length > 0){
                    /*records.forEach(function(d){
                        d.date_started = svg.startParse(d.date_terminated);
                        d.score = d.blood_sugar;
                        d.blood_sugar_null = false;
                    });*/

                    obs.forEach(function(d){
                        var date_els = d.date_terminated.match(date_regex);
                        var dt = new Date(date_els[1], (parseInt(date_els[2])-1), date_els[3], date_els[4], date_els[5], date_els[6], 0);
                        var days = ["Sun", "Mon", "Tues", "Wed", "Thu", "Fri", "Sat"];
                        d.date_terminated = days[dt.getDay()] + " " + +dt.getDate() + '/' + ('0'+(dt.getMonth() + 1)).slice(-2) + "/" + ('0'+(dt.getFullYear())).slice(-2) + " " + ('0'+(dt.getHours())).slice(-2) + ":" + ('0'+(dt.getMinutes())).slice(-2);
                    });

                    var bs_graph = new window.NH.NHGraph();
                    bs_graph.options.keys = ['blood_sugar'];
                    bs_graph.options.label = 'BS';
                    bs_graph.options.measurement = 'mmol/L';
                    bs_graph.axes.y.min = 0;
                    bs_graph.axes.y.max = 8;
                    bs_graph.options.normal.min = 4;
                    bs_graph.options.normal.max = 7;
                    bs_graph.style.dimensions.height = 250;
                    bs_graph.style.data_style = 'linear';
                    bs_graph.style.label_width = 60;


                    var focus = new window.NH.NHFocus();
                    focus.graphs.push(bs_graph);
                    focus.style.padding.right = 0;
                    focus.style.margin.top = 80;
                    svg.focus = focus;
                    svg.data.raw = obs;
                    svg.init();
                    svg.draw();


                }else{
                    d3.select(svg.el).append("text").text("No data available for this patient");
                }
            });
        },
    });

    instance.web.form.widgets.add('nh_bschart', 'instance.nh_eobs.BloodSugarChartWidget');

    instance.nh_eobs.WeightChartWidget = instance.web.form.AbstractField.extend({
        template: 'nh_weightchart',
        className: 'nh_ewschart',


        init: function (field_manager, node) {
            console.log("WEIGHTCHART INIT");
        	this._super(field_manager, node);
            this.dataset = new instance.web.form.One2ManyDataSet(this, this.field.relation);
            this.dataset.o2m = this;
            this.dataset.parent_view = this.view;
            this.dataset.child_name = this.name;
            var self = this
        },
        start: function() {
        	this._super();
        	var self = this;


            var vid = this.view.dataset.context.active_id;
            var height = this.view.dataset.context.height;
            this.model = new instance.web.Model('nh.eobs.api');

            var recData = this.model.call('get_activities_for_spell',[this.view.dataset.ids[0],'weight'], {context: this.view.dataset.context}).done(function(records){
                var svg = new window.NH.NHGraphLib('#chart');
                var obs = records.reverse();
                if(obs.length > 0){

                    obs.forEach(function(d){
                        var date_els = d.date_terminated.match(date_regex);
                        var dt = new Date(date_els[1], (parseInt(date_els[2])-1), date_els[3], date_els[4], date_els[5], date_els[6], 0);
                        var days = ["Sun", "Mon", "Tues", "Wed", "Thu", "Fri", "Sat"];
                        d.date_terminated = days[dt.getDay()] + " " + +dt.getDate() + '/' + ('0'+(dt.getMonth() + 1)).slice(-2) + "/" + ('0'+(dt.getFullYear())).slice(-2) + " " + ('0'+(dt.getHours())).slice(-2) + ":" + ('0'+(dt.getMinutes())).slice(-2);
                    });

                    var wmin = (18*(height*height)).toFixed(0);
                    var wmax = (25*(height*height)).toFixed(0);
                    var wmax2 = (50*(height*height)).toFixed(0);


                    var bs_graph = new window.NH.NHGraph();
                    bs_graph.options.keys = ['weight'];
                    bs_graph.options.label = 'W';
                    bs_graph.options.measurement = 'kg';
                    bs_graph.axes.y.min = 2;
                    bs_graph.axes.y.max = wmax2;
                    bs_graph.options.normal.min = wmin;
                    bs_graph.options.normal.max = wmax;
                    bs_graph.style.dimensions.height = 250;
                    bs_graph.style.data_style = 'linear';
                    bs_graph.style.label_width = 60;


                    var focus = new window.NH.NHFocus();
                    focus.graphs.push(bs_graph);
                    focus.style.padding.right = 0;
                    focus.style.margin.top = 80;
                    svg.focus = focus;
                    svg.data.raw = obs;
                    svg.init();
                    svg.draw();



                }else{
                    d3.select(svg.el).append("text").text("No data available for this patient");
                }
            });
        },
    });

    instance.web.form.widgets.add('nh_weightchart', 'instance.nh_eobs.WeightChartWidget');

    instance.nh_eobs.FormView = instance.web.FormView.extend({
        init: function(parent, dataset, view_id, options) {
            this._super(parent, dataset, view_id, options);
            if (typeof(logout_timeout) != 'undefined'){
                clearInterval(logout_timeout);
            }
            session = this.session;
            logout_timeout = window.setInterval(function(){
                session.session_logout().done(function(){
                    location.reload();
                });
            }, logout_time);
        },
    });

    instance.web.views.add('form', 'instance.nh_eobs.FormView');

    instance.web.FormView.include({
         can_be_discarded: function() {
             // Hack to save if on the patient allocation stuff
            if(this.model !== 'nh.clinical.allocating.user'){
                return this._super();
            }

            if(this.view_id){
                this.save();
            }


            //if (this.$el.is('.oe_form_dirty')) {
            //    if (!confirm(_t("Warning, the record has been modified, your changes will be discarded.\n\nAre you sure you want to leave this page ?"))) {
            //        return false;
            //    }
            //    this.$el.removeClass('oe_form_dirty');
            //}
            return true;
        },
    })

    instance.nh_eobs.KanbanView = instance.web_kanban.KanbanView.extend({
    	
    	on_groups_started: function() {
           if (this.group_by == 'clinical_risk'){
           	var cols = this.$el.find('td.oe_kanban_column');
           	var heads = this.$el.find('td.oe_kanban_group_header');
           	var titles = this.$el.find('span.oe_kanban_group_title_vertical');
           	var cards = this.$el.find('div.oe_kanban_card');
           	console.log($(cards));
            	class_map = {"No Score Yet": "none", "High Risk": "high", "Medium Risk": "medium", "Low Risk": "low", "No Risk": "no"}
            	for (i=0; i < heads.length; i++){
            		column_string = $(titles[i]).text().trim();
            		console.log(column_string);
            		col_class ='nhclinical_kanban_column_clinical_risk_' + class_map[column_string];
            		$(heads[i]).addClass(col_class);
            		$(cols[i]).addClass(col_class);
            	}
            	for (i=0; i < cards.length; i++){
            		$(cards[i]).addClass("nhclinical_kanban_card_clinical_risk");
            	}
            	
            }    		
    		this._super();
    		if (this.options.action.name == "Kiosk Board" || this.options.action.name == "Kiosk Workload"){
                $(".oe_leftbar").attr("style", "");
                $(".oe_leftbar").addClass("nh_eobs_hide");
                $(".oe_searchview").hide();
                kiosk_mode = true;
                if (typeof(kiosk_t) != 'undefined'){
                    clearInterval(kiosk_t);
                }
                kiosk_t = window.setInterval(function(){
                    var button =  $('li:not(.active) .oe_menu_leaf');
                    if (kiosk_mode){
                        button.click();
                    }
                }, 15000);
            }
            else{
                kiosk_mode = false;
                if (typeof(kiosk_t) != 'undefined'){
                    clearInterval(kiosk_t);
                }
                $(".oe_leftbar").addClass("nh_eobs_show");
                $(".oe_searchview").show();
            }
    	}
    });

    instance.web.views.add('kanban', 'instance.nh_eobs.KanbanView');

    instance.web.Menu.include({
        open_menu: function (id) {
            this.current_menu = id;
            this.session.active_id = id;
            var $clicked_menu, $sub_menu, $main_menu;
            $clicked_menu = this.$el.add(this.$secondary_menus).find('a[data-menu=' + id + ']');
            this.trigger('open_menu', id, $clicked_menu);

            if (this.$secondary_menus.has($clicked_menu).length) {
                $sub_menu = $clicked_menu.parents('.oe_secondary_menu');
                $main_menu = this.$el.find('a[data-menu=' + $sub_menu.data('menu-parent') + ']');
            } else {
                $sub_menu = this.$secondary_menus.find('.oe_secondary_menu[data-menu-parent=' + $clicked_menu.attr('data-menu') + ']');
                $main_menu = $clicked_menu;
            }

            // Activate current main menu
            this.$el.find('.active').removeClass('active');
            $main_menu.parent().addClass('active');

            // Show current sub menu
            this.$secondary_menus.find('.oe_secondary_menu').hide();
            $sub_menu.show();

            // Hide/Show the leftbar menu depending of the presence of sub-items
            if (! kiosk_mode){
                this.$secondary_menus.parent('.oe_leftbar').toggle(!!$sub_menu.children().length);
            }

            // Activate current menu item and show parents
            this.$secondary_menus.find('.active').removeClass('active');

            if ($main_menu !== $clicked_menu) {
                if (! kiosk_mode){
                    $clicked_menu.parents().show();
                }
                if ($clicked_menu.is('.oe_menu_toggler')) {
                    $clicked_menu.toggleClass('oe_menu_opened').siblings('.oe_secondary_submenu:first').toggle();
                } else {
                    $clicked_menu.parent().addClass('active');
                }
            }
            // add a tooltip to cropped menu items
            this.$secondary_menus.find('.oe_secondary_submenu li a span').each(function() {
                $(this).tooltip(this.scrollWidth > this.clientWidth ? {title: $(this).text().trim(), placement: 'right'} :'destroy');
           });
        }
    });

    var normalize_format = function (format) {
        return Date.normalizeFormat(instance.web.strip_raw_chars(format));
    };

    instance.web.format_value = function (value, descriptor, value_if_empty) {
        // If NaN value, display as with a `false` (empty cell)
        if (typeof value === 'number' && isNaN(value)) {
            value = false;
        }
        //noinspection FallthroughInSwitchStatementJS
        switch (value) {
            case '':
                if (descriptor.type === 'char') {
                    return '';
                }
                console.warn('Field', descriptor, 'had an empty string as value, treating as false...');
            case false:
            case Infinity:
            case -Infinity:
                return value_if_empty === undefined ?  '' : value_if_empty;
        }
        var l10n = instance.web._t.database.parameters;
        switch (descriptor.widget || descriptor.type || (descriptor.field && descriptor.field.type)) {
            case 'id':
                return value.toString();
            case 'integer':
                return instance.web.insert_thousand_seps(
                    _.str.sprintf('%d', value));
            case 'float':
                var digits = descriptor.digits ? descriptor.digits : [69,2];
                digits = typeof digits === "string" ? py.eval(digits) : digits;
                var precision = digits[1];
                var formatted = _.str.sprintf('%.' + precision + 'f', value).split('.');
                formatted[0] = instance.web.insert_thousand_seps(formatted[0]);
                return formatted.join(l10n.decimal_point);
            case 'float_time':
                var pattern = '%02d:%02d';
                if (value < 0) {
                    value = Math.abs(value);
                    pattern = '-' + pattern;
                }
                var hour = Math.floor(value);
                var min = Math.round((value % 1) * 60);
                if (min == 60){
                    min = 0;
                    hour = hour + 1;
                }
                return _.str.sprintf(pattern, hour, min);
            case 'many2one':
                // name_get value format
                return value[1] ? value[1].split("\n")[0] : value[1];
            case 'one2many':
            case 'many2many':
                if (typeof value === 'string') {
                    return value;
                }
                return _.str.sprintf(instance.web._t("(%d records)"), value.length);
            case 'datetime':
                if (typeof(value) == "string")
                    value = instance.web.auto_str_to_date(value);
                if (descriptor.string == "Starting Date"){
                    s = value.toString(normalize_format(l10n.date_format)
                            + ' ' + normalize_format(l10n.time_format));
                    return s.substring(0, s.length - 3);
                }
                return value.toString(normalize_format(l10n.date_format)
                            + ' ' + normalize_format(l10n.time_format));
            case 'date':
                if (typeof(value) == "string")
                    value = instance.web.auto_str_to_date(value);
                return value.toString(normalize_format(l10n.date_format));
            case 'time':
                if (typeof(value) == "string")
                    value = instance.web.auto_str_to_date(value);
                return value.toString(normalize_format(l10n.time_format));
            case 'selection': case 'statusbar':
                // Each choice is [value, label]
                if(_.isArray(value)) {
                     value = value[0]
                }
                var result = _(descriptor.selection).detect(function (choice) {
                    return choice[0] === value;
                });
                if (result) { return result[1]; }
                return;
            case 'boolean':
                if (descriptor.string == "Oxygen Administration Flag"){
                    return "Set (2 score)";
                }
                return value;
            case 'nhc_datetime':
                if (typeof(value) == "string")
                    value = instance.web.auto_str_to_date(value);
                s = value.toString(normalize_format(l10n.date_format)
                            + ' ' + normalize_format(l10n.time_format));
                return s.substring(0, s.length - 3);
            default:
                return value;
        }
    };


    // Override of the do_action implementation in web.View so it actually gets record ids [WI-577]
    instance.web.View.include({
        do_execute_action: function (action_data, dataset, record_id, on_closed) {
            if((['nh.clinical.allocating.user', 'nh.clinical.wardboard'].indexOf(dataset.model) < 0) || (typeof(this.fields_view.type) !== 'undefined' && this.fields_view.type !== 'tree') || action_data.type !== 'action'){
                return this._super(action_data, dataset, record_id, on_closed);
            }

            var self = this;
            var result_handler = function () {
                if (on_closed) { on_closed.apply(null, arguments); }
                if (self.getParent() && self.getParent().on_action_executed) {
                    return self.getParent().on_action_executed.apply(null, arguments);
                }
            };
            var context = new instance.web.CompoundContext(dataset.get_context(), action_data.context || {});

            // response handler
            var handler = function (action) {
                if (action && action.constructor == Object) {
                    // filter out context keys that are specific to the current action.
                    // Wrong default_* and search_default_* values will no give the expected result
                    // Wrong group_by values will simply fail and forbid rendering of the destination view
                    var ncontext = new instance.web.CompoundContext(
                        _.object(_.reject(_.pairs(dataset.get_context().eval()), function(pair) {
                          return pair[0].match('^(?:(?:default_|search_default_).+|.+_view_ref|group_by|group_by_no_leaf|active_id|active_ids)$') !== null;
                        }))
                    );
                    ncontext.add(action_data.context || {});
                    ncontext.add({active_model: dataset.model});

                    // Add records from self.records._proxies
                    var active_ids_to_send = [];
                    var active_records_to_send = [];
                    if (dataset.model === 'nh.clinical.wardboard') {
                        if (typeof(self.records._proxies) == 'object') {
                            for (key in self.records._proxies) {
                                if (self.records._proxies.hasOwnProperty(key)) {
                                    for (var i = 0; i < self.records._proxies[key].records.length; i++) {
                                        var rec = self.records._proxies[key].records[i];
                                        active_ids_to_send.push(rec.attributes.id);
                                        active_records_to_send.push(rec.attributes);
                                    }
                                    //active_ids_to_send = self.records._proxies[key].records;
                                }
                            }
                        } else {
                            if (record_id) {
                                active_ids_to_send = [record_id]
                            }
                        }
                    } else {
                        for (var j=0; j<self.records.records.length;j++){
                            var rec = self.records.records[j];
                            active_ids_to_send.push(rec.attributes.id);
                            active_records_to_send.push(rec.attributes);
                        }
                    }


                    if (record_id) {
                        ncontext.add({
                            index: active_ids_to_send.indexOf(record_id),
                            active_ids: active_ids_to_send,
                            active_recs: active_records_to_send,
                        });
                    }
                    ncontext.add(action.context || {});
                    action.context = ncontext;
                    //return self.do_action(action, {
                    //    on_close: result_handler,
                    //});

                    self.dataset.index = active_ids_to_send.indexOf(record_id);
                    self.dataset.ids = active_ids_to_send;
                    self.dataset.records = active_records_to_send;

                    var title_to_use = 'Patient Chart'
                    if(self.dataset.model == 'nh.clinical.allocating.user'){
                        title_to_use = 'User Allocation';
                    }


                    var pop = new instance.nh_eobs.PagedFormOpenPopup(action);
                    pop.show_element(
                            action.res_model,
                            action.res_id,
                            action.context,
                            {
                                title: _t(title_to_use),
                                view_id: action.view_id[0],
                                readonly: true,
                                active_id: record_id,
                                active_index: active_ids_to_send.indexOf(record_id),
                                active_ids: active_ids_to_send,
                                active_records: active_records_to_send,
                            }
                    );

                } else {
                    self.do_action({"type":"ir.actions.act_window_close"});
                    return result_handler();
                }
            };

            if (action_data.special === 'cancel') {
                return handler({"type":"ir.actions.act_window_close"});
            } else if (action_data.type=="object") {
                var args = [[record_id]];
                if (action_data.args) {
                    try {
                        // Warning: quotes and double quotes problem due to json and xml clash
                        // Maybe we should force escaping in xml or do a better parse of the args array
                        var additional_args = JSON.parse(action_data.args.replace(/'/g, '"'));
                        args = args.concat(additional_args);
                    } catch(e) {
                        console.error("Could not JSON.parse arguments", action_data.args);
                    }
                }
                args.push(context);
                return dataset.call_button(action_data.name, args).then(handler).then(function () {
                    if (instance.webclient) {
                        instance.webclient.menu.do_reload_needaction();
                    }
                });
            } else if (action_data.type=="action") {

                var active_ids_to_send = []
                    if(typeof(self.records._proxies) == 'object'){
                        for(key in self.records._proxies){
                            if(self.records._proxies.hasOwnProperty(key)){
                                for(var i = 0; i < self.records._proxies[key].records.length; i++){
                                    var rec = self.records._proxies[key].records[i];
                                    active_ids_to_send.push(rec.attributes.id);
                                }
                                //active_ids_to_send = self.records._proxies[key].records;
                            }
                        }
                    }else{
                        if(record_id){
                            active_ids_to_send = [record_id]
                        }
                    }




                return this.rpc('/web/action/load', {
                    action_id: action_data.name,
                    context: _.extend(instance.web.pyeval.eval('context', context), {'active_model': dataset.model, 'ids': active_ids_to_send, 'id': record_id}),
                    do_not_eval: true
                }).then(handler);
            } else  {
                return dataset.exec_workflow(record_id, action_data.name).then(handler);
            }
        },
    });

    instance.nh_eobs.PagedFormOpenViewManager = instance.web.ViewManager.extend({
        template: "PagedFormOpenViewManager",

    })

    instance.nh_eobs.PagedFormOpenViewManager2 = instance.web.ViewManager.extend({
        template: "PagedFormOpenViewManager2",

    })

    instance.nh_eobs.PagedFormOpenPopup = instance.web.form.FormOpenPopup.extend({
         init_popup: function(model, row_id, domain, context, options) {
            this.row_id = row_id;
            this.model = model;
            this.domain = domain || [];
            this.context = context || {};
            this.ids = options.active_ids;
            this.options = options;
            _.defaults(this.options, {
            });
        },
        init_dataset: function() {
            var self = this;
            this.created_elements = [];
            ids = this.ids;
            index = this.index;
            this.dataset = new instance.web.ProxyDataSet(this, this.model, this.context);
            if(ids){
                this.dataset.ids = ids;
            }
            this.dataset.read_function = this.options.read_function;
            this.dataset.create_function = function(data, options, sup) {
                var fct = self.options.create_function || sup;
                return fct.call(this, data, options).done(function(r) {
                    self.trigger('create_completed saved', r);
                    self.created_elements.push(r);
                });
            };
            this.dataset.write_function = function(id, data, options, sup) {
                var fct = self.options.write_function || sup;
                return fct.call(this, id, data, options).done(function(r) {
                    self.trigger('write_completed saved', r);
                });
            };
            this.dataset.parent_view = this.options.parent_view;
            this.dataset.child_name = this.options.child_name;
        },
        setup_form_view: function() {
            var self = this;
            if (this.options.active_index) {
                //this.dataset.ids = [this.row_id];
                this.dataset.index = this.options.active_index;
            } else {
                this.dataset.index = 0;
            }
            var options = _.clone(self.options.form_view_options) || {};
            if (this.row_id !== null) {
                options.initial_mode = this.options.readonly ? "view" : "edit";
            }
            _.extend(options, {
                $buttons: this.$buttonpane,
            });
            if (this.dataset.model === 'nh.clinical.wardboard') {
                this.viewmanager = new instance.nh_eobs.PagedFormOpenViewManager(this, this.dataset, [[this.options.view_id, "form"]], {});
            } else {
                this.viewmanager = new instance.nh_eobs.PagedFormOpenViewManager2(this, this.dataset, [[this.options.view_id, "form"]], {});
            }
            this.viewmanager.appendTo(this.$el.find('.oe_popup_form'));

        },
    });

    instance.web.ActionManager = instance.web.ActionManager.extend({
        ir_actions_action_nh_clinical_download_report: function(action, options){
            if(!this.dialog){
                options.on_close();
            }
            this.dialog_stop();
            var c = instance.webclient.crashmanager;
            this.session.get_file({
                url: '/web/binary/saveas_ajax',
                data: {data: JSON.stringify({
                    model: 'ir.attachment',
                    id: (action.id || ''),
                    field: 'datas',
                    filename_field: 'datas_fname',
                    data: '',
                    context: this.session.user_context
                })},
                complete: instance.web.unblockUI,
                error: c.rpc_error.bind(c)
            });


            //instance.webclient.action_manager.ir_actions_report_xml(action, options);
            return $.when();
        }
    });

    instance.web.ViewManager.include({
        do_create_view: function(view_type){
            if (this.dataset.model === 'nh.clinical.allocating.user'){
                this.views[view_type].options.initial_mode = 'edit';
            }
            return this._super(view_type);
        }
    });

    instance.web.FormView.include({
        on_button_save: function(e) {
            if (this.dataset.model === 'nh.clinical.allocating.user'){
                var self = this;
                $(e.target).attr("disabled", true);
                return this.save().done(function(result) {
                    self.trigger("save", result);
                    self.reload();
                }).always(function(){
                   $(e.target).attr("disabled", false)
                });
            } else {
                return this._super(e);
            }
        },
        on_button_cancel: function(e) {
            if (this.dataset.model === 'nh.clinical.allocating.user'){
                var self = this;
                if (this.can_be_discarded()) {
                    this.to_view_mode();
                    $.when.apply(null, this.render_value_defs).then(function(){
                        self.trigger('load_record', self.datarecord);
                    });
                    this.to_edit_mode();
                }
                this.trigger('on_button_cancel');
                return false;
            } else {
                return this._super(e);
            }
        }
    });

    instance.web.ListView.List.include({
       init: function (group, opts) {
           var self = this;
           this._super(group, opts);
           if (this.dataset.model === 'nh.clinical.allocating.user' || this.dataset.model === 'nh.clinical.wardboard'){
               this.$current = $('<tbody>')
                    .delegate('input[readonly=readonly]', 'click', function (e) {
                        e.preventDefault();
                    })
                    .delegate('th.oe_list_record_selector', 'click', function (e) {
                        e.stopPropagation();
                        var selection = self.get_selection();
                        var checked = $(e.currentTarget).find('input').prop('checked');
                        $(self).trigger(
                                'selected', [selection.ids, selection.records, ! checked]);
                    })
                    .delegate('td.oe_list_record_delete button', 'click', function (e) {
                        e.stopPropagation();
                        var $row = $(e.target).closest('tr');
                        $(self).trigger('deleted', [[self.row_id($row)]]);
                    })
                    .delegate('td.oe_list_field_cell button', 'click', function (e) {
                        e.stopPropagation();
                        var $target = $(e.currentTarget),
                              field = $target.closest('td').data('field'),
                               $row = $target.closest('tr'),
                          record_id = self.row_id($row);

                        if ($target.attr('disabled')) {
                            return;
                        }
                        //$target.attr('disabled', 'disabled');

                        $(self).trigger('action', [field.toString(), record_id, function (id) {
                            //$target.removeAttr('disabled');
                            return self.reload_record(self.records.get(id));
                        }]);
                    })
                    .delegate('a', 'click', function (e) {
                        e.stopPropagation();
                    })
                    .delegate('tr', 'click', function (e) {
                        var row_id = self.row_id(e.currentTarget);
                        if (row_id) {
                            e.stopPropagation();
                            if (!self.dataset.select_id(row_id)) {
                                throw new Error(_t("Could not find id in dataset"));
                            }
                            self.row_clicked(e);
                        }
                    });
           }
       }
    });
}