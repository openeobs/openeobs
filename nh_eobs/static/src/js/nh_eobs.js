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
                if (options.action.name == "Hospital Wards" || options.action.name == "Device Categories" || options.action.name == "Patients Board" || options.action.name == "Overdue Tasks" || options.action.name == "Doctor Tasks" || options.action.name == "Device Types" || options.action.name == "Devices" || options.action.name == "O2 Targets" || options.action.name == "User Management" || options.action.name == "Recently Discharged" || options.action.name == "Recently Transferred" || options.action.name == "Patients without bed" || options.action.name == "Wardboard" || options.action.name == "Active Points of Care" || options.action.name == "Inactive Points of Care"){
                    options.selectable = false;
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
            view = view || index == null ? 'form' : 'form';
            this.dataset.index = index;
            if (this.fields_view.name != "NH Clinical Placement Tree View"){
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

        load_list: function(data) {
            this._super(data);
            if (this.model == 'nh.clinical.patient.observation.pbp'){
                this.$el.html(QWeb.render('ListViewPBP', this));
            }
        }

    });

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
            if ((this.field_manager.ViewManager.dataset.model == "nh.clinical.wardboard") && this.string == "Print Report"){
                // Do some shit
                // Old stuff below...
                this.model = new instance.web.Model("nh.clinical.wardboard");
                var attachment_id = this.model.call('print_report',[[this.view.datarecord.id]], {context: this.view.dataset.context}).done(function(response){
                    if (response[0]){
                        var dataToSend = {"data":'{"data": null, "model":"ir.attachment","field":"datas","filename_field":"datas_fname","id":'+response[0]+', "context": '+JSON.stringify(response[1])+'}'}
                        var options = {url: '/web/binary/saveas_ajax', data: dataToSend};
                        openerp.instances.instance0.session.get_file(options);
                    }
                });
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
        start: function() {
        	this._super();
            this.model = new instance.web.Model('nh.eobs.api');
            var vid = this.view.dataset.context.active_id;
        	var self = this;


            if(typeof(this.view.dataset.context.printing) !== "undefined" && this.view.dataset.context.printing === "true"){
                printing = true;
            }

            var recData = this.model.call('get_activities_for_spell',[this.view.dataset.ids[0],'ews'], {context: this.view.dataset.context}).done(function(records){
                var svg = new window.NH.NHGraphLib('#chart');
                if(records.length > 0){
                    var obs = records.reverse();

                    records.forEach(function(d){
                        d.body_temperature = d.body_temperature.toFixed(1);
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
                    d3.select(svg.el).append("text").text("No data available for this patient");
                }
            });
        }
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
                if(records.length > 0){
                    /*records.forEach(function(d){
                        d.date_started = svg.startParse(d.date_terminated);
                        d.score = d.blood_sugar;
                        d.blood_sugar_null = false;
                    });*/

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
                if(records.length > 0){


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
        }
    });

    instance.web.views.add('form', 'instance.nh_eobs.FormView');

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
}