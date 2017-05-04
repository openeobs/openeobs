openerp.nh_eobs_mental_health = function (instance) {

    var QWeb = instance.web.qweb;
    //Kanban view visual customizations (coloured backgrounds for the patient
    //board columns). Manages the refresh timer for the Kanban board too.
    instance.nh_eobs_mental_health.RapidTranqWidget = instance.web.list.Column.extend({
        _format: function (rowData, options) {
            if (rowData.rapid_tranq.value === true) {
                return QWeb.render('nh_rapid_tranq_cell', {
                    'widget': this,
                    'prefix': instance.session.prefix
                });
            } else {
                return '';
            }
        }
    });
    instance.web.list.columns.add('field.nh_rapid_tranq', 'instance.nh_eobs_mental_health.RapidTranqWidget');

    instance.web.ListView.include({
        style_for: function(record){
            var style = this._super(record);
            if(record.attributes.rapid_tranq === true){
                style += ' border-top: 1px solid black; border-bottom: 1px solid black;';
            }
            return style;
        }
    });

    instance.nh_eobs.KanbanView.include({

        // Add clinical_risk classes to kanban columns for colour coding
        on_groups_started: function () {

            if (this.group_by == 'acuity_index') {

                var cols = this.$el.find('td.oe_kanban_column');
                var heads = this.$el.find('td.oe_kanban_group_header');
                var titles = this.$el.find('span.oe_kanban_group_title_vertical');
                var cards = this.$el.find('div.oe_kanban_card');

                var class_map = {
                    "New Pt / Obs Restart": "none",
                    "High Risk": "high",
                    "Medium Risk": "medium",
                    "Low Risk": "low",
                    "No Risk": "no",
                    "Obs Stop": "none",
                    "Refused": "none"
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

    instance.nh_eobs.EwsChartWidget.include({
        init: function (field_manager, node) {
            this._super(field_manager, node);
            this.refused = true;
            this.partial_type = 'character';
        }
    });

    instance.web_kanban.KanbanGroup.include({
        init: function (parent, records, group, dataset) {
        var self = this;
        this._super(parent);
        this.$has_been_started = $.Deferred();
        this.view = parent;
        this.group = group;
        this.dataset = dataset;
        this.dataset_offset = 0;
        this.aggregates = {};
        this.value = this.title = null;
        if (this.group) {
            this.value = group.get('value');
            this.title = group.get('value');
            if (this.value instanceof Array) {
                this.title = this.value[1];
                this.value = this.value[0];
            }
            var field = this.view.group_by_field;
            if (!_.isEmpty(field)) {
                try {
                    this.title = instance.web.format_value(group.get('value'), field, false);
                } catch(e) {}
            }
            _.each(this.view.aggregates, function(value, key) {
                self.aggregates[value] = instance.web.format_value(group.get('aggregates')[key], {type: 'float'});
            });
        }

        if (this.title === false) {
            this.title = _t('Undefined');
            this.undefined_title = true;
        }
        var key = this.view.group_by + '-' + this.value;
        this.view.state.groups[key] = {
            folded: group ? group.get('folded') : false
        };
        this.state = this.view.state.groups[key];
        this.$records = null;

        this.records = [];
        this.$has_been_started.done(function() {
            self.do_add_records(records);
        });
    },
    });
}