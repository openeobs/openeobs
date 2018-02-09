// This override allows the
openerp.patient = function(instance, local) {
    instance.web_kanban.KanbanRecord.include({
        on_card_clicked: function() {
            if (this.$el.children('.patient')) {
                this.do_action('patient.in_detail')
            }
            this._super()
        }
    })
}