openerp.nh_food_and_fluid = function (instance) {

    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.nh_food_and_fluid.FoodFluidTableWidget = instance.web.form.AbstractField.extend({
        template: 'food_fluid_table',
        className: 'food_fluid_table',

        init: function (fieldManager, node) {
            this._super(fieldManager, node);
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
            var spellModel = new instance.web.Model('nh.clinical.spell');
            var apiModel = new instance.web.Model('nh.eobs.api');
            var context = this.view.dataset.context;
            spellModel.call('read', [this.view.dataset.ids[this.view.dataset.index]], {context: context}).done(function(spellRecord){
                var patientId = spellRecord.patient_id[0];
                apiModel.call('get_activities_for_patient', [patientId, 'food_fluid'], {context: context}).done(function (records) {
                    var obs = records.reverse();
                    if (obs.length > 0) {
                        $('.modal-dialog').addClass('food_fluid_modal');
                        var settings = {
                            table_element: 'table-content',
                            desktop: true
                        };
                        drawFood_fluidTable(settings, obs);
                    } else {
                        $('#table-content').html('<p>No data available for this patient</p>');
                    }
                });
            });
        },
    });
    instance.web.form.widgets.add('food_fluid_table', 'instance.nh_food_and_fluid.FoodFluidTableWidget');
};