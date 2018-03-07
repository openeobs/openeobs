openerp.nh_clinical = function(instance){

    instance.web.form.SelectCreatePopup.include({
        setup_search_view: function(search_defaults) {
            var self = this;
            if(self.options.title.indexOf("Nursing Staff for new shift") > -1){
                self.options.no_create = true;
            }
            self._super(search_defaults);
        },
    });

    /*
    Fixes a bug that means create, edit, and delete attributes on the tree
    element are not respected. This was causing delete icons to be shown in
    the reallocation wizard which we did not want. An attempt to fix this bug
    has already been made by others but was not accepted into the code base.

    https://code.launchpad.net/~openerp-dev/openerp-web/trunk-bug-1179839-bth

    They identified Many2ManyListView's override of `is_action_enabled` as the
    problem. It always returns `true` instead of inspecting the attributes in
    the view.

    To fix this we need to call the original implementation and cut out
    Many2ManyListView's override but I couldn't not find a way to call super
    of super with Odoo's inheritance mechanism. The result is a dirty fix
    which is a copy-paste of the parent implementation which can be found at
    `openerp/addons/web/static/src/js/views.js:1576`.
     */
    instance.web.form.Many2ManyListView.include({
        is_action_enabled: function(action) {
            var attrs = this.fields_view.arch.attrs;
            return (action in attrs) ? JSON.parse(attrs[action]) : true;
        }
    })
};