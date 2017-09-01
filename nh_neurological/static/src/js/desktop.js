openerp.nh_neurological = function (instance) {

    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.nh_neurological.NeuroChartWidget = instance.web.form.AbstractField.extend({
        template: 'neuro_chart',
        className: 'neuro_chart',

        init: function (field_manager, node) {
            this._super(field_manager, node);
            this.dataset = new instance.web.form.One2ManyDataSet(this, this.field.relation);
            this.dataset.o2m = this;
            this.dataset.parent_view = this.view;
            this.dataset.child_name = this.name;
            this.ranged = true;
            this.refused = false;
            this.partial_type = 'dot';
        },
        start: function () {
            this._super();
            this.model = new instance.web.Model('nh.eobs.api');
            this.model.call('get_activities_for_spell', [this.view.dataset.ids[this.view.dataset.index], 'neurological'], {context: this.view.dataset.context}).done(function (records) {
                var obs = records.reverse();
                if (obs.length > 0) {
                    var settings = {
                        chart_element: 'neuro_chart'
                    }
                    drawNeurologicalChart(settings, obs);
                } else {
                    $('#neuro_chart').html('<p>No data available for this patient</p>');
                }
            });
        },
    });
    instance.web.form.widgets.add('neuro_chart', 'instance.nh_neurological.NeuroChartWidget');
}