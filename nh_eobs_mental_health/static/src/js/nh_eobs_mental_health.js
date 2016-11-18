openerp.nh_eobs_mental_health = function (instance) {
    //Kanban view visual customizations (coloured backgrounds for the patient
    //board columns). Manages the refresh timer for the Kanban board too.
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
}