openerp.patient = function(instance, local) {
    var QWeb = instance.web.qweb;

    local.PatientAtAGlanceWidget = instance.Widget.extend({
        start: function() {
            this.$el.append(QWeb.render('PatientAtAGlance'))
        }
    })

    local.PatientInDetailWidget = instance.Widget.extend({
        start: function() {
            var patientAtAGlanceWidget = new local.PatientAtAGlanceWidget(this)
            return patientAtAGlanceWidget.appendTo(this.$el)
        }
    })

    instance.web.client_actions.add('patient.in_detail', 'instance.patient.PatientInDetailWidget')
}
