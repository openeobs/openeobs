openerp.nh_eobs = function (instance) {

    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    // Used to store reference to parent modal so can be refreshed by child
    // modals on save/discard when allocating
    var modal_view = null;

    // regex to sort out Odoo's timestamp format (used by graphs)
    var date_regex = new RegExp('([0-9][0-9][0-9][0-9])-([0-9][0-9])-([0-9][0-9]) ([0-9][0-9]):([0-9][0-9]):([0-9][0-9])');

    // Refresh interval and kiosk mode interval defaults, used by ViewManager
    // and KanBanView to set timeout (and to store internal timer refs)
    instance.nh_eobs.defaults = {
        refresh: {
            'Acuity Board': {
                'kanban': 30000,
                'list': 30000
            },
            'Patients by Ward': {
                'list': 30000
            }
        },
        kiosk: {
            interval: 15000
        },
        logout: 1200000 //Inactivity auto-logout time (20mins)
    };

    // Function to get the user groups the user belongs to and add it to the
    // session object for use by tutorials menu
    (function () {
        var model = new instance.web.Model('res.users');
        model.call('get_groups_string', [], {}).done(function (user_groups) {
            instance.session.user_groups = user_groups;
        });
    }());

    // Auto logout object - reset() sets timeout interval with provided interval
    // or default value. Displays notification 10 seconds before timeout then
    // logs out unless reset has been called again.
    instance.nh_eobs.Logout = {
        ref: null, // Used to store the timeout reference if set
        reset: function (time) {
            var self = this,
                interval = instance.nh_eobs.defaults.logout;

            // When called by mouse click time param is passed event object
            if (typeof time !== 'number') {
                time = null;
            }
            if (typeof this.ref === 'number') {
                window.clearTimeout(this.ref);
            }
            this.ref = window.setTimeout(
                function () {
                    instance.web.notification.warn(
                        'Logging Out',
                        'You are about to be logged out due to inactivity. ' +
                        'Close this notification to continue your session.',
                        true
                    ).element.find('.ui-notify-close').click(
                        // Required as click event not propagated to window.
                        instance.nh_eobs.Logout.reset.bind(instance.nh_eobs.Logout)
                    );
                    self.ref = window.setTimeout(function () {
                        instance.session.session_logout()
                            .done(function () {
                                location.reload();
                                console.log('Logged out due to inactivity');
                            });
                    }, 10000);
                },
                (time || interval) - 10000
            );
        }
    };

    // Set initial countdown
    instance.nh_eobs.Logout.reset();

    // Sets click event listener for logout.reset() function
    window.addEventListener('click', instance.nh_eobs.Logout.reset.bind(instance.nh_eobs.Logout));

    // ? Redundant - Ref to nh_open_form in poc management is commented out
    //instance.web.NHTreeView = instance.web.TreeView.extend({
    //
    //    activate: function (id) {
    //        var self = this;
    //        if ('nh_open_form' in this.dataset.context) {
    //            var form_id = this.dataset.context['nh_open_form'];
    //            return self.do_action({
    //                type: 'ir.actions.act_window',
    //                res_model: self.dataset.model,
    //                res_id: id,
    //                views: [[form_id, 'form']],
    //                target: 'current',
    //                view_id: form_id,
    //                context: this.dataset.context
    //            });
    //        }
    //        return this._super(id);
    //    }
    //});
    //
    //instance.web.views.add('tree', 'instance.web.NHTreeView');

    //If the provided widget is our customized 'act_button' one, it will
    //render the button differently. Notice the 'active' and 'inactive' values.
    //It uses a different template to render the button too. Check the XML
    //file to find the corresponding template.
    instance.nh_eobs.Button = instance.web.list.Column.extend({
        format: function (row_data, options) {
            options = options || {};
            var attrs = {};
            if (options.process_modifiers !== false) {
                attrs = this.modifiers_for(row_data);
            }
            if (attrs.invisible) {
                return '';
            }
            if (this.widget == 'act_button') {
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
            else {
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

        start: function() {
            var self = this;
            this._super();

            var environmentModel = new instance.web.Model("nh.clinical.environment");

            environmentModel.call("get_eobs_version").then(function(eobsVersion) {
                    var text = 'LiveObs version ' + eobsVersion;
                    self.$el.find('#liveobs_about_link').text(text);
                }
            );
        },

        // Modified version of on_menu_ default to show tutorials menu relevant
        // to user (WI-2237)
        on_menu_tutorials: function () {
            var self = this;
            self.rpc("/web/webclient/version_info", {}).done(function (res) {
                var tours = instance.Tour.tours,
                    context = {
                        tours: []
                    },
                    user_status = instance.session.user_groups;

                // Create array of tours appropriate to user status
                for (var prop in tours) {
                    if (tours[prop].users) {
                        var auth_users = tours[prop].users;
                        var include = false;

                        // User status is usually a single string
                        if (user_status.length == 1) {
                            if (auth_users.indexOf(user_status[0]) !== -1) {
                                include = true
                            }
                        }
                        // Sometimes a user belongs to more than one group
                        else {
                            for (var i = 0; i < user_status.length; i++) {
                                if (auth_users.indexOf(user_status[i]) !== -1) {
                                    include = true
                                }
                            }
                        }
                        if (include) context.tours.push(tours[prop])
                    }
                };

                var $tuts = $(QWeb.render("UserMenu.tutorials", context));

                new instance.web.Dialog(this, {
                    size: 'large',
                    dialogClass: 'oe_act_window',
                    title: _t("Tutorials")
                }, $tuts).open();
            });
        },

        //Customizing the help menu link to open the Neova Health website.
        on_menu_help: function () {
            window.open('http://www.neovahealth.co.uk', '_blank');
        },

        // Hide the support menu item and odoo messaging button
        do_update: function () {
            this._super();
            $('li.odoo_support_contact').hide();
            $('ul.oe_systray').hide()
        }

        //2 changes:
        // - openerp.web.bus.trigger('resize') call removed - ?why
        // - $('li.odoo_support_contact').hide() - remove menu item
        //do_update: function () {
        //    var self = this;
        //    var fct = function () {
        //        var $avatar = self.$el.find('.oe_topbar_avatar');
        //        $avatar.attr('src', $avatar.data('default-src'));
        //        if (!self.session.uid)
        //            return;
        //        var func = new instance.web.Model("res.users").get_func("read");
        //        return self.alive(func(self.session.uid, ["name", "company_id"])).then(function (res) {
        //            var topbar_name = res.name;
        //            if (instance.session.debug)
        //                topbar_name = _.str.sprintf("%s (%s)", topbar_name, instance.session.db);
        //            if (res.company_id[0] > 1)
        //                topbar_name = _.str.sprintf("%s (%s)", topbar_name, res.company_id[1]);
        //            self.$el.find('.oe_topbar_name').text(topbar_name);
        //            if (!instance.session.debug) {
        //                topbar_name = _.str.sprintf("%s (%s)", topbar_name, instance.session.db);
        //            }
        //            var avatar_src = self.session.url('/web/binary/image', {
        //                model: 'res.users',
        //                field: 'image_small',
        //                id: self.session.uid
        //            });
        //            $avatar.attr('src', avatar_src);
        //
        //        });
        //    };
        //    this.update_promise = this.update_promise.then(fct, fct);
        //    $('li.odoo_support_contact').hide();
        //}
    });


    instance.web.ViewManager.include({
        // Sets timeout if action and view_type exist in defaults.refresh object
        // Timeout recalls same method which reloads the view
        switch_mode: function (view_type, no_store, view_options) {

            var action = null;
            if (this.action) {
                action = this.action.name
            }

            var defaults = instance.nh_eobs.defaults.refresh;
            var self = this;

            window.clearTimeout(instance.nh_eobs.defaults.refresh._timer);

            if (defaults[action] && defaults[action][view_type]) {
                instance.nh_eobs.defaults.refresh._timer = window.setTimeout(
                    function () {
                        self.switch_mode(view_type, no_store, view_options)
                    }, defaults[action][view_type]
                )
            }

            // Clear kiosk interval timer.
            if (view_type !== 'kanban' &&
                instance.nh_eobs.defaults.kiosk._timer) {
                window.clearInterval(instance.nh_eobs.defaults.kiosk._timer);
                instance.nh_eobs.defaults.kiosk._timer = null
            }

            return this._super(view_type, no_store, view_options);
        },

        //'nh.clinical.allocating' views will be opened in edit mode by default.
        //would be read mode otherwise.
        do_create_view: function (view_type) {
            if (this.dataset.model === 'nh.clinical.allocating') {
                this.views[view_type].options.initial_mode = 'edit';
            }
            return this._super(view_type);
        }
    });

    //Expands groups in list view by clicking headers
    //Removes the checkboxes on the list view opened by all the listed actions.
    //Removes the 'Import' option for the 'Patients' action.
    instance.web.ListView.include({

        //Method to expand groups in list view by clicking headers if not open
        reload_content: function () {
            var self = this;
            this._super().done(function () {
                if (self.grouped) {
                    window.setTimeout(function () {
                        var groups = $(".oe_group_header");
                        var open = $(".oe_group_header .ui-icon-triangle-1-s").length;
                        if (groups.length && !open) {
                            groups.click();
                        }
                    }, 250)
                }
            })
        },
        init: function (parent, dataset, view_id, options) {
            if (options.action) {
                if (
                    [   'Doctors',
                        'Spells',
                        'Hospital Wards',
                        'Device Categories',
                        'Acuity Board',
                        'Patients by Ward',
                        'Overdue Tasks',
                        'Doctor Tasks',
                        'Device Types',
                        'Devices',
                        'O2 Targets',
                        'User Management',
                        'Recently Discharged',
                        'Recently Transferred',
                        'Patients without bed',
                        'Wardboard',
                        'Active Points of Care',
                        'Inactive Points of Care'
                    ].indexOf(options.action.name) > -1) {
                    options.selectable = false;
                };
                if (
                    [   'Patients',
                        'Patient Visits',
                        'Locations'
                    ].indexOf(options.action.name) == -1) {
                    options.import_enabled = false;
                };
            }
            ;
            this._super.apply(this, [parent, dataset, view_id, options]);
        },
        //select_record: function (index, view) {
        //    // called when selecting the row
        //
        //    view = view || index == null ? 'form' : 'form';
        //    this.dataset.index = index;
        //    if (this.fields_view.name != "NH Clinical Placement Tree View") {
        //        _.delay(_.bind(function () {
        //            this.do_switch_view(view);
        //        }, this));
        //    }
        //},
        load_list: function (data) {
            this._super(data);
            //if its Postural Blood Pressure Tree view then render it's customized template
            if (this.model == 'nh.clinical.patient.observation.pbp') {
                this.$el.html(QWeb.render('ListViewPBP', this));
            }
        }
    });

    //Gender widget for list view that shows male/female icons depending on the
    //field value
    instance.nh_eobs.GenderWidget = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            if (row_data.sex.value == 'M') {
                return QWeb.render('nh_genderCell', {
                    'widget': this,
                    'prefix': instance.session.prefix,
                    'male': true,
                    'female': false,
                });
            } else if (row_data.sex.value == 'F') {
                return QWeb.render('nh_genderCell', {
                    'widget': this,
                    'prefix': instance.session.prefix,
                    'male': false,
                    'female': true,
                });
            } else {
                return 'Not Given';
            }
        }
    });
    instance.web.list.columns.add('field.nh_gender', 'instance.nh_eobs.GenderWidget');

    //Score Trend widget for list view that shows arrow icons depending on the
    //field value
    instance.nh_eobs.ScoreTrendWidget = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            if (row_data.ews_trend_string.value == 'up') {
                return QWeb.render('nh_trendCell', {
                    'widget': this,
                    'prefix': instance.session.prefix,
                    'up': true,
                    'down': false,
                    'same': false
                });
            } else if (row_data.ews_trend_string.value == 'down') {
                return QWeb.render('nh_trendCell', {
                    'widget': this,
                    'prefix': instance.session.prefix,
                    'up': false,
                    'down': true,
                    'same': false
                });
            } else if (row_data.ews_trend_string.value == 'same') {
                return QWeb.render('nh_trendCell', {
                    'widget': this,
                    'prefix': instance.session.prefix,
                    'up': false,
                    'down': false,
                    'same': true
                });
            } else if (row_data.ews_score_string.value == 'none') {
                return "Waiting 1st Observation";
            } else return row_data.ews_score_string.value;
        }
    });
    instance.web.list.columns.add('field.nh_scoretrend', 'instance.nh_eobs.ScoreTrendWidget');

    // Refreshes list view after confirming placement
    instance.nh_eobs.WidgetButton = instance.web.form.WidgetButton.extend({
        on_click: function () {
            this._super();
            // Hack to refresh list view after confirming placement
            if (this.string == "Confirm Placement") {
                window.setTimeout(function () {
                    var button = $("li.active:contains('Patients without bed')");
                    if ($(".ui-dialog").length == 0 &&
                        button.length &&
                        $(".oe_view_manager_view_list").css('display') != 'none'
                    ) {
                        button.click();
                    }
                }, 250);
            }
        }
    });
    instance.web.form.tags.add('button', 'instance.nh_eobs.WidgetButton');

    //NEWS observations Graph widget
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
            this.ranged = true;
            this.refused = false;
            this.partial_type = 'dot';
        },
        set_value: function (value_) {
            this.set({'value': value_});
            this.render_chart();
        },
        render_chart: function () {
            this.model = new instance.web.Model('nh.eobs.api');
            this.o2targetModel = new instance.web.Model('nh.clinical.patient.o2target');
            this.o2levelModel = new instance.web.Model('nh.clinical.o2level');
            this.wardboard_model = new instance.web.Model('nh.clinical.wardboard');
            var vid = this.view.dataset.context.active_id;
            var self = this;

            $('.modal-dialog .paged_form_view_header #o2_target_header').remove();
            this.o2targetModel.call('get_last', [this.view.datarecord.id]).done(function (o2targetRecords) {
                var o2levelid = o2targetRecords
                if (o2levelid) {
                    self.o2levelModel.call('read', [o2levelid], {context: self.view.dataset.context}).done(function (o2levelRecords) {
                        var name = o2levelRecords.name;
                        $('.modal-dialog .paged_form_view_header').append('<li id="o2_target_header"><strong class="target-right">Patient O2 Saturation Target Range: </strong><span>' + name + '%</span></li>')
                    });
                }
            });

            var recData = this.model.call('get_activities_for_spell', [this.view.dataset.ids[this.view.dataset.index], 'ews'], {context: this.view.dataset.context}).done(function (records) {
                var svg = new window.NH.NHGraphLib('#chart');

                $(svg.el).html('');
                if (records.length > 0) {
                    var obs = records.reverse();

                    obs.forEach(function (d) {
                        if (d.body_temperature) {
                            d.body_temperature = parseFloat(d.body_temperature.toFixed(1));
                        }

                        if (d.partial_reason === 'refused' && self.refused || d.is_partial && self.partial_type === 'character'){
                            d.score = false;
                        }


                        var date_els = d.date_terminated.match(date_regex);
                        var dt = new Date(date_els[1], (parseInt(date_els[2]) - 1), date_els[3], date_els[4], date_els[5], date_els[6], 0);
                        var days = ["Sun", "Mon", "Tues", "Wed", "Thu", "Fri", "Sat"];
                        d.date_terminated = days[dt.getDay()] + " " + +dt.getDate() + '/' + ('0' + (dt.getMonth() + 1)).slice(-2) + "/" + ('0' + (dt.getFullYear())).slice(-2) + " " + ('0' + (dt.getHours())).slice(-2) + ":" + ('0' + (dt.getMinutes())).slice(-2);

                        d.oxygen_administration_device = 'No';
                        if (d.flow_rate && d.flow_rate > -1 || d.concentration && d.concentration > -1 || d.oxygen_administration_flag) {
                            plotO2 = true;
                            d.inspired_oxygen = "";
                            if (d.device_id) {
                                d.inspired_oxygen += "Device: " + d.device_id[1] + "<br>";
                            }
                            if (d.flow_rate && d.flow_rate > -1) {
                                d.inspired_oxygen += "Flow: " + d.flow_rate + " l/m<br>";
                            }
                            if (d.concentration && d.concentration > -1) {
                                d.inspired_oxygen += "Concentration: " + d.concentration + "%<br>";
                            }
                            if (d.cpap_peep && d.cpap_peep > -1) {
                                d.inspired_oxygen += "CPAP PEEP: " + d.cpap_peep + "<br>";
                            } else if (d.niv_backup && d.niv_backup > -1) {
                                d.inspired_oxygen += "NIV Backup Rate: " + d.niv_backup + "<br>";
                                d.inspired_oxygen += "NIV EPAP: " + d.niv_epap + "<br>";
                                d.inspired_oxygen += "NIV IPAP: " + d.niv_ipap + "<br>";
                            }
                            if (d.oxygen_administration_flag) {
                                d.oxygen_administration_device = 'Yes';
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
                    resp_rate_graph.axes.y.max = 40;
                    resp_rate_graph.options.normal.min = 12;
                    resp_rate_graph.options.normal.max = 20;
                    resp_rate_graph.style.dimensions.height = 250;
                    resp_rate_graph.style.data_style = 'linear';
                    resp_rate_graph.style.label_width = 60;
                    resp_rate_graph.drawables.background.data = [
                        {"class": "red", s: 0, e: 9},
                        {"class": "green", s: 9, e: 12},
                        {"class": "amber", s: 21, e: 25},
                        {"class": "red", s: 25, e: 60}
                    ];

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
                    oxy_graph.drawables.background.data = [
                        {"class": "red", s: 0, e: 92},
                        {"class": "amber", s: 92, e: 94},
                        {"class": "green", s: 94, e: 96},
                    ];

                    var temp_graph = new window.NH.NHGraph();
                    temp_graph.options.keys = ['body_temperature'];
                    temp_graph.options.label = 'Temp';
                    temp_graph.options.measurement = '°C';
                    temp_graph.axes.y.min = 25;
                    temp_graph.axes.y.max = 45;
                    temp_graph.style.axis.step = 1;
                    temp_graph.options.normal.min = 36.1;
                    temp_graph.options.normal.max = 38.1;
                    temp_graph.style.dimensions.height = 200;
                    temp_graph.style.axis.x.hide = true;
                    temp_graph.style.data_style = 'linear';
                    temp_graph.style.label_width = 60;
                    temp_graph.style.range_padding = 1;
                    temp_graph.drawables.background.data = [
                        {"class": "red", s: 0, e: 35},
                        {"class": "amber", s: 35, e: 35.1},
                        {"class": "green", s: 35.1, e: 36.0},
                        {"class": "green", s: 38.1, e: 39.1},
                        {"class": "amber", s: 39.1, e: 50},
                    ];

                    var pulse_graph = new window.NH.NHGraph();
                    pulse_graph.options.keys = ['pulse_rate'];
                    pulse_graph.options.label = 'HR';
                    pulse_graph.options.measurement = '/min';
                    pulse_graph.axes.y.min = 25;
                    pulse_graph.axes.y.max = 200;
                    pulse_graph.options.normal.min = 50;
                    pulse_graph.options.normal.max = 91;
                    pulse_graph.style.dimensions.height = 200;
                    pulse_graph.style.axis.x.hide = true;
                    pulse_graph.style.data_style = 'linear';
                    pulse_graph.style.label_width = 60;
                    pulse_graph.drawables.background.data = [
                        {"class": "red", s: 0, e: 40},
                        {"class": "amber", s: 40, e: 41},
                        {"class": "green", s: 41, e: 50},
                        {"class": "green", s: 91, e: 111},
                        {"class": "amber", s: 111, e: 131},
                        {"class": "red", s: 131, e: 200}
                    ];

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
                    bp_graph.drawables.background.data = [
                        {"class": "red", s: 0, e: 91},
                        {"class": "amber", s: 91, e: 101},
                        {"class": "green", s: 101, e: 111},
                        {"class": "red", s: 220, e: 260}
                    ];

                    var score_graph = new window.NH.NHGraph();
                    score_graph.options.keys = ['score'];
                    score_graph.options.plot_partial = true;
                    score_graph.style.dimensions.height = 200;
                    score_graph.style.data_style = 'stepped';
                    score_graph.style.padding.bottom = 10;
                    score_graph.axes.y.min = 0;
                    score_graph.axes.y.max = 22;
                    score_graph.drawables.background.data = [
                        {"class": "green", s: 1, e: 4},
                        {"class": "amber", s: 4, e: 6},
                        {"class": "red", s: 6, e: 22}
                    ];
                    score_graph.style.label_width = 60;


                    var tabular_obs = new window.NH.NHTable();
                    tabular_obs.keys = [
                        {key: 'avpu_text', title: 'AVPU'},
                        {
                            key: 'oxygen_administration_device',
                            title: 'On Supplemental O2'
                        },
                        {key: 'inspired_oxygen', title: 'Inspired Oxygen'}
                    ];
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
                    svg.options.controls.rangify.checked = self.ranged;
                    svg.options.ranged = self.ranged;
                    svg.options.refused = self.refused;
                    svg.options.partial_type = self.partial_type;
                    svg.data.raw = obs;
                    svg.init();
                    svg.draw();

                    svg.options.controls.rangify.addEventListener(
                        'click',
                        function () {
                            self.ranged = svg.options.controls.rangify.checked
                        }
                    );
                } else {
                    $(svg.el).html('<p>No data available for this patient</p>');
                    //d3.select(svg.el).append("text").text("No data available for this patient");
                }
            });
        },
    });
    instance.web.form.widgets.add('nh_ewschart', 'instance.nh_eobs.EwsChartWidget');

    // probably not needed
    instance.nh_eobs.PrescribeWidget = instance.web.form.AbstractField.extend({
        template: 'nh_prescribe',
        className: 'nh_prescribe',

        init: function (field_manager, node) {
            this._super(field_manager, node);
            this.model = new instance.web.Model('ir.config_parameter');
            var self = this;
            var recData = this.model.call('search', [[['key', '=', 'nh.eobs.prescribe.url']]], {context: this.view.dataset.context}).done(function (records) {
                if (records.length > 0) {
                    var recData2 = self.model.call('read', [records[0], ['value']], {context: self.view.dataset.context}).done(function (record) {
                        if (record) {
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

    instance.web.FormView.include({

        //'nh.clinical.allocating' Form view handling. Saves the values and closes
        //the window. Would save without closing otherwise.
        on_button_save: function (e) {
            if (this.dataset.model === 'nh.clinical.allocating') {
                var self = this;
                $(e.target).attr("disabled", true);
                return this.save().done(function (result) {
                    self.trigger("save", result);
                    self.reload();
                    self.ViewManager.ActionManager.$el.parent().parent().find('.modal-header .close').click();
                }).always(function () {
                    $(e.target).attr("disabled", false);
                    // Should this close the allocation modal?
                    self.$el.parents('.modal').find('.close').click();
                    if (modal_view != undefined) {
                        modal_view.reinitialize();
                    }
                });
            } else {
                return this._super(e);
            }
        },

        //Cancel button closes without saving. Would just cancel the edition and
        //go back to read mode otherwise (if I'm not mistaken...)
        on_button_cancel: function (e) {
            if (this.dataset.model === 'nh.clinical.allocating') {
                var self = this;
                if (this.can_be_discarded()) {
                    this.to_view_mode();
                    $.when.apply(null, this.render_value_defs).then(function () {
                        self.trigger('load_record', self.datarecord);
                    });
                    this.to_edit_mode();
                }
                this.trigger('on_button_cancel');
                self.$el.parents('.modal').find('.close').click();
                if (modal_view != undefined) {
                    modal_view.reinitialize();
                }
                return false;
            } else {
                return this._super(e);
            }
        },

        //The nh.clinical.allocating object is linked to the Staff Allocation
        //features and this change allows us to have a pop up window that loops
        //through all the records in the same way the full screen form view do
        //and saves the values when going forwards or backwards with the pager
        //widget. For any other object the behaviour remains the default.
        can_be_discarded: function () {
            // Hack to save if on the patient allocation stuff
            if (this.model !== 'nh.clinical.allocating') {
                return this._super();
            }

            if (this.view_id) {
                this.save();
            }
            return true;
        }
    });


    //Kanban view visual customizations (coloured backgrounds for the patient
    //board columns). Manages the refresh timer for the Kanban board too.
    instance.nh_eobs.KanbanView = instance.web_kanban.KanbanView.extend({

        // Kiosk mode view rotation.
        init: function (parent, dataset, view_id, options) {
            var self = this;
            this._super(parent, dataset, view_id, options);

            this.has_been_loaded.done(function () {

                var kiosk = instance.nh_eobs.defaults.kiosk;

                if (self.options.action.name == "Kiosk Board" ||
                    self.options.action.name == "Kiosk Workload NEWS" ||
                    self.options.action.name == "Kiosk Workload Other Tasks") {

                    // Hide the side menu
                    $(".oe_leftbar").attr("style", "");
                    $(".oe_leftbar").addClass("nh_eobs_hide");
                    $(".oe_searchview").hide();

                    kiosk._active = true;

                    if (kiosk._timer) {
                        clearInterval(kiosk._timer);
                    }

                    kiosk._timer = window.setInterval(function () {
                        if (kiosk._button == null) {
                            kiosk._button = $('span.oe_menu_text:contains(Kiosk Workload NEWS)');
                        } else if (kiosk._button.text().indexOf('Kiosk Patients Board') > 0) {
                            kiosk._button = $('span.oe_menu_text:contains(Kiosk Workload NEWS)');
                        } else if (kiosk._button.text().indexOf('Kiosk Workload NEWS') > 0) {
                            kiosk._button = $('span.oe_menu_text:contains(Kiosk Workload Other Tasks)');
                        } else {
                            kiosk._button = $('span.oe_menu_text:contains(Kiosk Patients Board)');
                        }
                        if (kiosk._active) {
                            kiosk._button.click();
                        }
                    }, kiosk.interval);
                }
                else {
                    kiosk._active = false;

                    if (kiosk._timer) {
                        clearInterval(kiosk._timer);
                    }
                    $(".oe_leftbar").addClass("nh_eobs_show");
                    $(".oe_searchview").show();
                }
            })
        },

        // Add clinical_risk classes to kanban columns for colour coding
        on_groups_started: function () {

            if (this.group_by == 'clinical_risk') {

                var cols = this.$el.find('td.oe_kanban_column');
                var heads = this.$el.find('td.oe_kanban_group_header');
                var titles = this.$el.find('span.oe_kanban_group_title_vertical');
                var cards = this.$el.find('div.oe_kanban_card');

                var class_map = {
                    "No Score Yet": "none",
                    "High Risk": "high",
                    "Medium Risk": "medium",
                    "Low Risk": "low",
                    "No Risk": "no"
                };
                for (i = 0; i < heads.length; i++) {
                    column_string = $(titles[i]).text().trim();
                    col_class = 'nhclinical_kanban_column_clinical_risk_' + class_map[column_string];
                    $(heads[i]).addClass(col_class);
                    $(cols[i]).addClass(col_class);
                }
                for (i = 0; i < cards.length; i++) {
                    $(cards[i]).addClass("nhclinical_kanban_card_clinical_risk");
                }
            }
            this._super();
        }
    });
    instance.web.views.add('kanban', 'instance.nh_eobs.KanbanView');

    //Most of the code is the default Odoo just copied over. Has a change to
    //manage the Menu hiding when the user is logged in in Kiosk mode.
    instance.web.Menu.include({
        open_menu: function (id) {
            var kiosk = instance.nh_eobs.defaults.kiosk;
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
            if (!kiosk._active) {
                this.$secondary_menus.parent('.oe_leftbar').toggle(!!$sub_menu.children().length);
            }

            // Activate current menu item and show parents
            this.$secondary_menus.find('.active').removeClass('active');

            if ($main_menu !== $clicked_menu) {
                if (!kiosk._active) {
                    $clicked_menu.parents().show();
                }
                if ($clicked_menu.is('.oe_menu_toggler')) {
                    $clicked_menu.toggleClass('oe_menu_opened').siblings('.oe_secondary_submenu:first').toggle();
                } else {
                    $clicked_menu.parent().addClass('active');
                }
            }
            // add a tooltip to cropped menu items
            this.$secondary_menus.find('.oe_secondary_submenu li a span').each(function () {
                $(this).tooltip(this.scrollWidth > this.clientWidth ? {
                    title: $(this).text().trim(),
                    placement: 'right'
                } : 'destroy');
            });
        }
    });
    // Function to handle the time to next observation
    // Displays (overdue)? [0-9]* days [0-2][0-9]:[0-5][0-9]
    // Takes the date string returned by Odoo
    //var nh_date_diff_to_string = function(date1, date2){
    //    var time_diff = (date1.getTime() - date2.getTime()) / 1000;
    //    var string_to_return = ' ';
    //    if(time_diff < 0){
    //        string_to_return += 'overdue: ';
    //        time_diff = Math.abs(time_diff);
    //    }
    //    var days = Math.floor(time_diff/86400);
    //    time_diff -= days * 86400;
    //    var hours = Math.floor(time_diff/3600);
    //    time_diff -= hours * 3600;
    //    var mins = Math.floor(time_diff/60);
    //    if(days > 0){
    //        var term = 'day';
    //        if(days > 1){
    //            term += 's';
    //        }
    //        string_to_return += days + ' ' + term + ' ';
    //    }
    //    string_to_return += ('0' + hours).slice(-2) +':'+ ('0' + mins).slice(-2);
    //    return string_to_return;
    //};

    // Taken from odoo (web/static/src/js/formats.js)
    var normalize_format = function (format) {
        return Date.normalizeFormat(instance.web.strip_raw_chars(format));
    };


    //Adds the 'nhc_datetime' widget to the list of field widgets to remove the
    //seconds from the display format. Everything else is default Odoo code.

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
                return value_if_empty === undefined ? '' : value_if_empty;
        }
        var l10n = instance.web._t.database.parameters;
        switch (descriptor.widget || descriptor.type || (descriptor.field && descriptor.field.type)) {
            case 'id':
                return value.toString();
            case 'integer':
                return instance.web.insert_thousand_seps(
                    _.str.sprintf('%d', value));
            case 'float':
                var digits = descriptor.digits ? descriptor.digits : [69, 2];
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
                if (min == 60) {
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
                if (descriptor.string == "Starting Date") {
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
            case 'selection':
            case 'statusbar':
                // Each choice is [value, label]
                if (_.isArray(value)) {
                    value = value[0]
                }
                var result = _(descriptor.selection).detect(function (choice) {
                    return choice[0] === value;
                });
                if (result) {
                    return result[1];
                }
                return;
            case 'boolean':
                if (descriptor.string == "Oxygen Administration Flag") {
                    return "Set (2 score)";
                }
                return value;
            case 'nhc_datetime':
                if (typeof(value) == "string")
                    value = instance.web.auto_str_to_date(value);
                return value.toString(normalize_format('%d/%m/%y')
                    + ' ' + normalize_format('%H:%M'));
            default:
                return value;
        }
    };


    // Override of the do_action implementation in web.View so it actually gets record ids [WI-577]
    instance.web.View.include({
        do_execute_action: function (action_data, dataset, record_id, on_closed) {
            if ((['nh.clinical.allocating', 'nh.clinical.wardboard'].indexOf(dataset.model) < 0) || (typeof(this.fields_view.type) !== 'undefined' && this.fields_view.type !== 'tree') || action_data.type !== 'action') {
                return this._super(action_data, dataset, record_id, on_closed);
            }

            var self = this;
            var result_handler = function () {
                if (on_closed) {
                    on_closed.apply(null, arguments);
                }
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
                        _.object(_.reject(_.pairs(dataset.get_context().eval()), function (pair) {
                            return pair[0].match('^(?:(?:default_|search_default_).+|.+_view_ref|group_by|group_by_no_leaf|active_id|active_ids)$') !== null;
                        }))
                    );
                    ncontext.add(action_data.context || {});
                    ncontext.add({active_model: dataset.model});

                    // Add records from self.records._proxies
                    var active_ids_to_send = [];
                    var active_records_to_send = [];
                    if (dataset.model === 'nh.clinical.wardboard') {
                        if (self.records.length == 0 && typeof(self.records._proxies) == 'object') {
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
                        } else if (self.records.length > 0) {
                            for (var i = 0; i < self.records.length; i++) {
                                var rec = self.records.records[i];
                                active_ids_to_send.push(rec.attributes.id);
                                active_records_to_send.push(rec.attributes);
                            }
                        } else {
                            if (record_id) {
                                active_ids_to_send.push(record_id)
                            }
                        }
                    } else {
                        for (var j = 0; j < self.records.records.length; j++) {
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

                    //var title_to_use = 'Observation Chart'
                    if (self.dataset.model == 'nh.clinical.allocating.user') {
                        title_to_use = 'Shift Management';
                    }

                    modal_view = self.ViewManager;

                    var pop = new instance.nh_eobs.PagedFormOpenPopup(action);
                    pop.show_element(
                        action.res_model,
                        action.res_id,
                        action.context,
                        {
                            title: action.display_name,
                            view_id: action.view_id[0],
                            readonly: true,
                            active_id: record_id,
                            active_index: active_ids_to_send.indexOf(record_id),
                            active_ids: active_ids_to_send,
                            active_records: active_records_to_send,
                        }
                    );

                } else {
                    self.do_action({"type": "ir.actions.act_window_close"});
                    return result_handler();
                }
            };

            if (action_data.special === 'cancel') {
                return handler({"type": "ir.actions.act_window_close"});
            } else if (action_data.type == "object") {
                var args = [[record_id]];
                if (action_data.args) {
                    try {
                        // Warning: quotes and double quotes problem due to json and xml clash
                        // Maybe we should force escaping in xml or do a better parse of the args array
                        var additional_args = JSON.parse(action_data.args.replace(/'/g, '"'));
                        args = args.concat(additional_args);
                    } catch (e) {
                        console.error("Could not JSON.parse arguments", action_data.args);
                    }
                }
                args.push(context);
                return dataset.call_button(action_data.name, args).then(handler).then(function () {
                    if (instance.webclient) {
                        instance.webclient.menu.do_reload_needaction();
                    }
                });
            } else if (action_data.type == "action") {

                var active_ids_to_send = []
                if (self.records.length == 0 && typeof(self.records._proxies) == 'object') {
                    for (key in self.records._proxies) {
                        if (self.records._proxies.hasOwnProperty(key)) {
                            for (var i = 0; i < self.records._proxies[key].records.length; i++) {
                                var rec = self.records._proxies[key].records[i];
                                active_ids_to_send.push(rec.attributes.id);
                            }
                            //active_ids_to_send = self.records._proxies[key].records;
                        }
                    }
                    if (active_ids_to_send.length < 1) {
                        active_ids_to_send.push(record_id)
                    }
                } else if (self.records.length > 0) {
                    for (var i = 0; i < self.records.length; i++) {
                        var rec = self.records.records[i];
                        active_ids_to_send.push(rec.attributes.id);
                    }
                } else {
                    if (record_id) {
                        active_ids_to_send.push(record_id)
                    }
                }


                return this.rpc('/web/action/load', {
                    action_id: action_data.name,
                    context: _.extend(instance.web.pyeval.eval('context', context), {
                        'active_model': dataset.model,
                        'ids': active_ids_to_send,
                        'id': record_id
                    }),
                    do_not_eval: true
                }).then(handler);
            } else {
                return dataset.exec_workflow(record_id, action_data.name).then(handler);
            }
        },
    });

    instance.nh_eobs.PagedFormOpenViewManager = instance.web.ViewManager.extend({
        template: "PagedFormOpenViewManager",

    });

    instance.nh_eobs.PagedFormOpenViewManager2 = instance.web.ViewManager.extend({
        template: "PagedFormOpenViewManager2",

    });

    //Custom PopPup widget that allows to loop through all the available records
    //with the pager widget.
    instance.nh_eobs.PagedFormOpenPopup = instance.web.form.FormOpenPopup.extend({
        init_popup: function (model, row_id, domain, context, options) {
            this.row_id = row_id;
            this.model = model;
            this.domain = domain || [];
            this.context = context || {};
            this.ids = options.active_ids;
            this.options = options;
            _.defaults(this.options, {});
        },
        init_dataset: function () {
            var self = this;
            this.created_elements = [];
            ids = this.ids;
            index = this.index;
            this.dataset = new instance.web.ProxyDataSet(this, this.model, this.context);
            if (ids) {
                this.dataset.ids = ids;
            }
            this.dataset.read_function = this.options.read_function;
            this.dataset.create_function = function (data, options, sup) {
                var fct = self.options.create_function || sup;
                return fct.call(this, data, options).done(function (r) {
                    self.trigger('create_completed saved', r);
                    self.created_elements.push(r);
                });
            };
            this.dataset.write_function = function (id, data, options, sup) {
                var fct = self.options.write_function || sup;
                return fct.call(this, id, data, options).done(function (r) {
                    self.trigger('write_completed saved', r);
                });
            };
            this.dataset.parent_view = this.options.parent_view;
            this.dataset.child_name = this.options.child_name;
        },
        setup_form_view: function () {
            var self = this;
            if (this.options.active_index > 0) {
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

    // Reporting stuff...
    instance.web.ActionManager = instance.web.ActionManager.extend({
        ir_actions_action_nh_clinical_download_report: function (action, options) {
            if (!this.dialog) {
                options.on_close();
            }
            this.dialog_stop();
            var c = instance.webclient.crashmanager;
            this.session.get_file({
                url: '/web/binary/saveas_ajax',
                data: {
                    data: JSON.stringify({
                        model: 'ir.attachment',
                        id: (action.id || ''),
                        field: 'datas',
                        filename_field: 'datas_fname',
                        data: '',
                        context: this.session.user_context
                    })
                },
                complete: instance.web.unblockUI,
                error: c.rpc_error.bind(c)
            });


            //instance.webclient.action_manager.ir_actions_report_xml(action, options);
            return $.when();
        }
    });

    // List view handling. Prevents disabling of cell button on clicking NEWS
    // Chart or NEWS table buttons. Only changes are what is commented out.
    instance.web.ListView.List.include({
        init: function (group, opts) {
            var self = this;
            this._super(group, opts);
            if (this.dataset.model === 'nh.clinical.allocating') {
                this.$current = $('<tbody>')
                    .delegate('td.oe_list_field_cell button', 'click', function (e) {
                        e.stopPropagation();
                        var $target = $(e.currentTarget),
                            field = $target.closest('td').data('field'),
                            $row = $target.closest('tr'),
                            record_id = self.row_id($row);

                        if ($target.attr('disabled')) {
                            return;
                        }
                        $(self).trigger('action', [field.toString(), record_id, function (id) {
                            return self.reload_record(self.records.get(id));
                        }]);
                    })
            }
            if (this.dataset.model === 'nh.clinical.wardboard') {
                this.$current = $('<tbody>')
                    .undelegate('td.oe_list_field_cell button', 'click')
                    .delegate('td.oe_list_field_cell button', 'click', function (e) {
                        e.stopPropagation();
                        var $target = $(e.currentTarget),
                            field = $target.closest('td').data('field'),
                            $row = $target.closest('tr'),
                            record_id = self.row_id($row);

                        if ($target.attr('disabled')) {
                            return;
                        }
                        $(self).trigger('action', [field.toString(), record_id, function (id) {
                            return self.reload_record(self.records.get(id));
                        }]);
                    }).delegate('tr', 'click', function (e) {
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

    // Adding date format dropdown to CSV import options (WI-2119)
    // setTimeout = temp fix as import.js not loading before nh_eobs.js
    window.setTimeout(function () {

        var _lt = instance.web._lt,
            _t = instance.web._t;

        instance.web.DataImport.include({
            opts: [
                {name: 'dateformat', label: _lt("Date format:"), value: 'YMD'},
                {name: 'encoding', label: _lt("Encoding:"), value: 'utf-8'},
                {name: 'separator', label: _lt("Separator:"), value: ','},
                {name: 'quoting', label: _lt("Quoting:"), value: '"'}
            ],
            start: function () {
                var self = this;
                this.setup_encoding_picker();
                this.setup_separator_picker();
                this.setup_dateformat_picker(); // Add call to custom method

                return $.when(
                    this._super(),
                    this.Import.call('create', [{
                        'res_model': this.res_model
                    }]).done(function (id) {
                        self.id = id;
                        self.$('input[name=import_id]').val(id);
                    })
                )
            },

            // Modified version of setup_seperator_picker
            setup_dateformat_picker: function () {
                this.$('input.oe_import_dateformat').select2({
                    width: '160px',
                    query: function (q) {
                        var suggestions = [
                            {id: 'YMD', text: _t('Year Month Day')},
                            {id: 'DMY', text: _t('Day Month Year')},
                            {id: 'MDY', text: _t('Month Day Year')}
                        ];
                        if (q.term) {
                            suggestions.unshift({id: q.term, text: q.term});
                        }
                        q.callback({results: suggestions});
                    },
                    initSelection: function (e, c) {
                        return c({id: 'YMD', text: _t('Year Month Day')});
                    },
                    // Removes search box from drop down
                    minimumResultsForSearch: Infinity
                });
            }
        })
    },2000);

    // Over ride default year range in date picker to show years up to 115 ago
    $.datepicker.setDefaults({yearRange: '-115:+0'});

    instance.web.DateTimeWidget.include({
        on_picker_select: function(text, instance_) {
            var date = this.picker('getDate');
            this.$input
                .val(date ? this.format_client(date) : '')
                .change()
                .focus();

            // If datepicker is being used for date of birth
            if (this.$input.attr('name') === 'dob') {

                // Calculate age from date selected
                var agems = Date.now() - date.getTime();
                var age = Math.abs(new Date(agems).getUTCFullYear() - 1970);

                // Add an age div after the picker or change the text if already
                // present
                if (!document.getElementById('age')) {
                    $(this.$el).after('<div id="age" style="display:inline;margin-left:20px;">' + age + ' years old</div>');
                }
                else {
                    $('#age').text(age + ' years old')
                }
            }
        }
    })

    instance.web.StaleDataExceptionHandler = instance.web.Dialog.extend(instance.web.ExceptionHandler, {
        init: function(parent, error) {
            this._super(parent);
            this.error = error;
        },
        display: function() {
            var self = this;
            error = this.error;
            error.data.message = error.data.arguments[0];

            new instance.web.Dialog(this, {
                size: 'medium',
                title: error.data.arguments[1],
                buttons: [
                    {text: "Reload Page",
                     click: function() {
                        location.reload();
                    }}
                ],
            }, QWeb.render('CrashManager.warning', {error: error})).open();
        }
    });

    instance.web.crash_manager_registry.add('openerp.addons.nh_eobs.exceptions.StaleDataException', 'instance.web.StaleDataExceptionHandler');
}