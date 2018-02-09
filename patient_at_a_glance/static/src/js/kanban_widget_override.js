openerp.patient_at_a_glance = function(instance, local) {
    instance.web_kanban.KanbanRecord.include({
        on_card_clicked: function() {
            if (this.$el.children('.patient')) {
                this.do_action({
                    'type': 'ir.actions.act_window',
                    'views': [[false, 'form']],
                    'res_model': 'nh.clinical.patient.in_detail',
                    'res_id': this.record.patient_in_detail.raw_value[0]
                })
            }
            this._super()
        }
    })
}