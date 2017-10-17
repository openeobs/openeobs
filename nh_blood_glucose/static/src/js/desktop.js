openerp.nh_blood_glucose = function (instance) {

    //Blood Glucose Observations Graph widget
    instance.nh_eobs.BloodGlucoseChartWidget = instance.web.form.AbstractField.extend({
        template: "nh_blood_glucose_chart",
        className: "nh_blood_glucose_chart",


        init: function (fieldManager, node) {
            this._super(fieldManager, node);
            this.dataset = new instance.web.form.One2ManyDataSet(this, this.field.relation);
            this.dataset.o2m = this;
            this.dataset.parent_view = this.view;
            this.dataset.child_name = this.name;
        },
        start: function () {
            this._super();
            this.model = new instance.web.Model("nh.eobs.api");
            this.model.call("get_activities_for_spell", [this.view.dataset.ids[0], "blood_glucose"], {context: this.view.dataset.context}).done(function (records) {
                var obs = records.reverse();
                if (obs.length > 0) {
                    var settings = {
                        chart_element: "blood_glucose_chart"
                    };
                    drawBlood_glucoseChart(settings, obs);
                } else {
                    $("#blood_glucose_chart").html("<p>No data available for this patient</p>");
                }
            });
        }
    });
    instance.web.form.widgets.add("nh_blood_glucose_chart", "instance.nh_eobs.BloodGlucoseChartWidget");
}