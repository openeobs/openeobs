openerp.nh_weight = function (instance) {

    instance.nh_eobs.WeightChartWidget = instance.web.form.AbstractField.extend({
        template: 'nh_weightchart',
        className: 'nh_weightchart',


        init: function (field_manager, node) {
            this._super(field_manager, node);
            this.dataset = new instance.web.form.One2ManyDataSet(this, this.field.relation);
            this.dataset.o2m = this;
            this.dataset.parent_view = this.view;
            this.dataset.child_name = this.name;
        },
        start: function () {
            this._super();
            this.model = new instance.web.Model('nh.eobs.api');
            this.model.call('get_activities_for_spell', [this.view.dataset.ids[0], 'weight'], {context: this.view.dataset.context}).done(function (records) {
                var obs = records.reverse();
                if (obs.length > 0) {
                    var settings = {
                        chart_element: 'weight_chart'
                    };
                    drawWeightChart(settings, obs);
                } else {
                    $("#weight_chart").html("<p>No data available for this patient</p>");
                }
            });
        },
    });

    instance.web.form.widgets.add('nh_weightchart', 'instance.nh_eobs.WeightChartWidget');
}