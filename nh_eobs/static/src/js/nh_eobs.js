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

    /*instance.web.form.widgets.add('button', 'instance.nh_eobs.WidgetButton');

    instance.nh_eobs.WidgetButton = instance.web.form.WidgetButton.extend({
        execute_action: function() {
            var self = this;

            if ((this.field_manager.ViewManager.process_model == "nh.clinical.wardboard") && this.string == "Print Report"){
                // Do some shit
                // Old stuff below...
                this.model = new instance.web.Model("nh.clinical.wardboard");
                var attachment_id = this.model.call('print_report',[[this.view.datarecord.id]], {context: this.view.dataset.context}).done(function(response){
                    if (response[0]){
                        var dataToSend = {"data":'{"data": null, "model":"ir.attachment","field":"datas","filename_field":"datas_fname","id":'+response[0]+', "context": '+JSON.stringify(response[1])+'}'}
                        var options = {url: '/web/binary/saveas_ajax', data: dataToSend};
                        openerp.instances.instance0.session.get_file(options);
                        //return this.session.url('/web/binary/saveas', {model: 'ir.attachment', field: 'datas', filename_field: 'datas_fname', id: attachment['id']});
                    }
                });
            }
            this._super();
        },
    });   */

//    instance.web.form.tags = new instance.web.Registry({
//        'button' : 'instance.web.form.WidgetButton',
//    });

    instance.web.ListView.include({
        init: function(parent, dataset, view_id, options) {

            if (options.action){
                if (options.action.name == "Device Categories" || options.action.name == "Patients Board" || options.action.name == "Overdue Tasks" || options.action.name == "Doctor Tasks" || options.action.name == "Device Types" || options.action.name == "Devices" || options.action.name == "O2 Targets" || options.action.name == "User Management" || options.action.name == "Recently Discharged Patients" || options.action.name == "Patients without bed" || options.action.name == "Wardboard" || options.action.name == "Active Points of Care" || options.action.name == "Inactive Points of Care"){
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
                        //return this.session.url('/web/binary/saveas', {model: 'ir.attachment', field: 'datas', filename_field: 'datas_fname', id: attachment['id']});
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
        	var self = this;

            var svg = graph_lib.svg,
                focus = graph_lib.focus,
                context = graph_lib.context;
            svg.focusOnly = false;

            if(typeof(this.view.dataset.context.printing) !== "undefined" && this.view.dataset.context.printing === "true"){
                printing = true;
                graph_lib.svg.printing = true;
            }

            if(printing){
                $(".oe_form_sheetbg").attr({"style": "display: inline; background : none;"});

                $(".oe_form_sheet.oe_form_sheet_width").attr({"style" : "display : inline-block;"});

                $(".oe_form_group>.oe_form_group_row:first-child").append($(".oe_form_group>.oe_form_group_row:last-child td:first-child"));
                $(".oe_form_group>.oe_form_group_row:last-child").remove();
                $(".oe_form_group>.oe_form_group_row td").attr({"style" : "width: 33%;"});

                $(".oe_title label").remove();
                $(".oe_title h1:first-child").attr({"style" : "display: inline;"});
                $(".oe_title h1:first-child .oe_form_field").attr({"style" : "float: left; width: auto;"});
                $(".oe_title h1:last-child span").attr({"style": "width: auto;"});
            }
            focus.graphs = null;
            focus.graphs = new Array();
            focus.tables = null;
            focus.tables = new Array();

            this.model = new instance.web.Model('nh.eobs.api');

            var vid = this.view.dataset.context.active_id;
            var plotO2 = false;
            //var start_date = new Date();
            //var end_date = new Date();
            //var start_string = start_date.getFullYear()+"-"+("0"+(start_date.getMonth()+1)).slice(-2)+"-"+("0"+start_date.getDate()).slice(-2)+" "+("0"+start_date.getHours()).slice(-2)+":"+("0"+start_date.getMinutes()).slice(-2)+":"+("0"+start_date.getSeconds()).slice(-2)
            //var end_string = end_date.getFullYear()+"-"+("0"+(end_date.getMonth()+1)).slice(-2)+"-"+("0"+end_date.getDate()).slice(-2)+" "+("0"+end_date.getHours()).slice(-2)+":"+("0"+end_date.getMinutes()).slice(-2)+":"+("0"+end_date.getSeconds()).slice(-2)

            var recData = this.model.call('get_activities_for_spell',[this.view.dataset.ids[0],'ews'], {context: this.view.dataset.context}).done(function(records){
                if(records.length > 0){
                    records = records.reverse();
                    context.earliestDate = svg.startParse(records[0].date_terminated);
                    context.now = svg.startParse(records[records.length-1].date_terminated);

                    context.scoreRange = [  {"class": "green",s: 0,e: 5},
                                {"class": "amber",s: 5,e: 7},
                                {"class": "red",s: 7,e: 18} ];
                    records.forEach(function(d){
                        d.date_started = svg.startParse(d.date_terminated);
                        d.body_temperature = d.body_temperature.toFixed(1);
                        if (d.flow_rate > -1){
                            plotO2 = true;
                            d.inspired_oxygen = "";
                            d.inspired_oxygen += "Flow: " + d.flow_rate + "l/hr<br>";
                            d.inspired_oxygen += "Concentration: " + d.concentration + "%<br>";
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

                    svg.data = records;
                    focus.graphs.push({key: "respiration_rate",label: "RR",measurement: "/min",max: 60,min: 0,normMax: 20,normMin: 12});
                    focus.graphs.push({key: "indirect_oxymetry_spo2",label: "Spo2",measurement: "%",max: 100,min: 70,normMax: 100,normMin: 96});
                    focus.graphs.push({key: "body_temperature",label: "Temp",measurement: "°C",max: 50,min: 15,normMax: 37.1,normMin: 35});
                    focus.graphs.push({key: "pulse_rate",label: "HR",measurement: "/min",max: 200,min: 30,normMax: 100,normMin: 50});
                    focus.graphs.push({key: "blood_pressure",label: "BP",measurement: "mmHg",max: 260,min: 30,normMax: 150,normMin: 50});
                    focus.tables.push({
                        key: "avpu_text",
                        label: "AVPU"
                    });
                    focus.tables.push({
                        key: "indirect_oxymetry_spo2_label",
                        label: "Oxygen saturation"
                    });
                    graph_lib.initGraph(18);
                    if (plotO2==true){
                        focus.tables.push({key:"inspired_oxygen", label:"Inspired oxygen"});
                    }
                    graph_lib.initTable();
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
                    /*printing = false;
                    graph_lib.svg.printing = false;*/

                }else{
                    d3.select(svg.el).append("text").text("No data available for this patient");
                }
            });
        },
    });

    instance.web.form.widgets.add('nh_ewschart', 'instance.nh_eobs.EwsChartWidget');

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

            var svg = graph_lib.svg,
                focus = graph_lib.focus,
                context = graph_lib.context;

            focus.graphs = null;
            focus.graphs = new Array();
            focus.tables = null;
            focus.tables = new Array();

            var vid = this.view.dataset.context.active_id;
            //var start_date = new Date(0);
            //var end_date = new Date();
            this.model = new instance.web.Model('nh.eobs.api');
            //var start_string = start_date.getFullYear()+"-"+("0"+(start_date.getMonth()+1)).slice(-2)+"-"+("0"+start_date.getDate()).slice(-2)+" "+("0"+start_date.getHours()).slice(-2)+":"+("0"+start_date.getMinutes()).slice(-2)+":"+("0"+start_date.getSeconds()).slice(-2)
            //var end_string = end_date.getFullYear()+"-"+("0"+(end_date.getMonth()+1)).slice(-2)+"-"+("0"+end_date.getDate()).slice(-2)+" "+("0"+end_date.getHours()).slice(-2)+":"+("0"+end_date.getMinutes()).slice(-2)+":"+("0"+end_date.getSeconds()).slice(-2)

            var recData = this.model.call('get_activities_for_spell',[this.view.dataset.ids[0],'blood_sugar'], {context: this.view.dataset.context}).done(function(records){
                if(records.length > 0){
                    //records = records.reverse();
                    context.earliestDate = svg.startParse(records[0].date_terminated);
                    context.now = svg.startParse(records[records.length-1].date_terminated);
                    context.scoreRange = [];

                    records.forEach(function(d){
                        d.date_started = svg.startParse(d.date_terminated);
                        d.score = d.blood_sugar;
                        d.blood_sugar_null = false;
                    });

                    svg.data = records;
                    svg.focusOnly = true;
                    svg.el = '#focusChart'
                    focus.graphs.push({key: "blood_sugar",label: "BS",measurement: "mmol/L",max: 8,min: 0,normMax: 7,normMin: 4});
                    graph_lib.initGraph(18);
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

            var svg = graph_lib.svg,
                focus = graph_lib.focus,
                context = graph_lib.context;

            focus.graphs = null;
            focus.graphs = new Array();
            focus.tables = null;
            focus.tables = new Array();

            var vid = this.view.dataset.context.active_id;
            var height = this.view.dataset.context.height;
            //var start_date = new Date(0);
            //var end_date = new Date();
            this.model = new instance.web.Model('nh.eobs.api');
            //var start_string = start_date.getFullYear()+"-"+("0"+(start_date.getMonth()+1)).slice(-2)+"-"+("0"+start_date.getDate()).slice(-2)+" "+("0"+start_date.getHours()).slice(-2)+":"+("0"+start_date.getMinutes()).slice(-2)+":"+("0"+start_date.getSeconds()).slice(-2)
            //var end_string = end_date.getFullYear()+"-"+("0"+(end_date.getMonth()+1)).slice(-2)+"-"+("0"+end_date.getDate()).slice(-2)+" "+("0"+end_date.getHours()).slice(-2)+":"+("0"+end_date.getMinutes()).slice(-2)+":"+("0"+end_date.getSeconds()).slice(-2)

            var recData = this.model.call('get_activities_for_spell',[this.view.dataset.ids[0],'weight'], {context: this.view.dataset.context}).done(function(records){
                if(records.length > 0){
                    //records = records.reverse();
                    context.earliestDate = svg.startParse(records[0].date_terminated);
                    context.now = svg.startParse(records[records.length-1].date_terminated);
                    context.scoreRange = [];

                    records.forEach(function(d){
                        d.date_started = svg.startParse(d.date_terminated);
                        d.score = d.weight;
                        d.weight_null = false;
                    });

                    var wmin = (18*(height*height)).toFixed(0);
                    var wmax = (25*(height*height)).toFixed(0);
                    var wmax2 = (50*(height*height)).toFixed(0);

                    svg.data = records;
                    svg.focusOnly = true;
                    svg.el = '#focusChart'
                    focus.graphs.push({key: "weight",label: "W",measurement: "kg",max: wmax2,min: 2,normMax: wmax,normMin: wmin});
                    graph_lib.initGraph(18);
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