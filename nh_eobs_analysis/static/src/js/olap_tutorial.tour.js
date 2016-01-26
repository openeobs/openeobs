'use strict';

/*global
    openerp, $
 */

(function () {
    var _t = openerp._t,
        combo = '<div class="popover tour fade top in"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div><nav class="popover-navigation"><button class="btn btn-sm btn-default" data-role="next">Continue</button> <small> <span class="text-muted"> or </span><button class="btn-link" data-role="end" style="float: none; padding: 0">Exit</button></small></nav></div>';
    openerp.Tour.register({
        id: 'olap_tutorial',
        name: "Tutorial demonstrating the features of the NEWS Analysis OLAP tool",
        path: '/web?debug=',
        mode: 'tour',
        steps: [
            {
                title:     _t("NEWS Observation Analysis Tutorial"),
                content: _t("This tutorial shows the options available in the tool and guides you through a typical use case."),
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Start Here"),
                content: _t("Click to open the analysis panel"),
                element:   "span.oe_menu_text:contains('NEWS Analysis')",
                placement: 'bottom'
            },
            {
                title:     _t("Choose Dimensions"),
                content: _t("Use the group-by buttons to quickly select the dimensions you want to view. <br/>Click <strong>Continue</strong> when done."),
                element:   "dt:contains('Group By')",
                placement: 'left',
                popover:   { next: _t("Continue"), end: _t("Exit") },
                template: combo
            },
            {
                title:     _t("Specify Dimensions"),
                content: _t("Use the <span class='fa fa-plus-square' style='display:inline;'</span> and <span class='fa fa-minus-square' style='display:inline;'</span> buttons to further specify dimensions.<br/>Click <strong>Continue</strong> when done."),
                element:   "span.fa.fa-minus-square.web_graph_click",
                placement: 'top',
                popover:   { next: _t("Continue"), end: _t("Exit") },
                template: combo
            },
            {
                title:     _t("Select your measures"),
                content: _t("Add or remove measures by clicking the items in this dropdown. <br/>Click <strong>Continue</strong> when done."),
                element:   ".dropdown-toggle:contains('Measures')",
                placement: 'top',
                popover:   { next: _t("Continue"), end: _t("Exit") },
                template: combo
            },
            {
                title:     _t("Heatmap"),
                content: _t("Click here to view your selection as a heatmap"),
                element:   ".btn[data-mode='both']",
                placement: 'top'
            },
            {
                waitFor: ".btn[data-mode='both'].active",
                title:     _t("Heatmap Rows"),
                content: _t("Click here to view your selection as a heatmap by row"),
                element:   ".btn[data-mode='row']",
                placement: 'top'
            },
            {
                waitFor: ".btn[data-mode='row'].active",
                title:     _t("Heatmap Columns"),
                content: _t("Click here to view your selection as a heatmap by columns"),
                element:   ".btn[data-mode='col']",
                placement: 'top'
            },
            {
                waitFor: ".btn[data-mode='col'].active",
                title:     _t("Swap Axes"),
                content: _t("This will swap the axes over. Try it now then click <strong>Continue</strong>"),
                element:   ".btn[data-choice='swap_axis']",
                placement: 'top',
                popover:   { next: _t("Continue"), end: _t("Exit") },
                template: combo
            },
            {
                title:     _t("Expand All"),
                content: _t('You can click here to expand all measures (e.g. if one has been collapsed by clicking the <span class="fa fa-minus-square web_graph_click" style="margin-left: 0px;"</span> button)'),
                element:   ".btn[data-choice='expand_all']",
                placement: 'top',
                popover:   { next: _t("Continue"), end: _t("Exit") },
                template: combo
            },
            {
                title:     _t("Refresh Data"),
                content: _t("You can click here to update the data in the current view. "),
                element:   ".btn[data-choice='update_values']",
                placement: 'top',
                popover:   { next: _t("Continue"), end: _t("Exit") },
                template: combo
            },
            {
                title:     _t("Export Dataset"),
                content: _t("You can click here to download the dataset as a CSV"),
                element:   ".btn[data-choice='export_data']",
                placement: 'top',
                popover:   { next: _t("Continue"), end: _t("Exit") },
                template: combo
            },
            {
                title:     _t("View as Bar Chart"),
                content: _t("Click here to view the dataset as a bar chart"),
                element:   ".btn[data-mode='bar']",
                placement: 'top'
            },
            {
                waitFor: ".btn[data-mode='bar'].active",
                title:     _t("View as Line Graph"),
                content: _t("Click here to view the dataset as a line graph. Depends on appropriate data having been selected"),
                element:   ".btn[data-mode='line']",
                placement: 'top'
            },
            {
                waitFor: ".btn[data-mode='line'].active",
                title:     _t("View as Pie Chart"),
                content: _t("Click here to view the dataset as a pie chart. Depends on appropriate data having been selected"),
                element:   ".btn[data-mode='pie']",
                placement: 'top'
            },
            {
                waitFor: ".btn[data-mode='pie'].active",
                title:     _t("Save Dashboard"),
                content: _t("When you are happy with your selection, click here to save it to your personal dashboard."),
                element:   "h4:contains('Add to Dashboard')",
                placement: 'bottom'
            },
            {
                waitFor: "select:contains('My Dashboard')",
                title:     _t("Enter Name"),
                content: _t("Choose a descriptive name for your view. Then click <strong>Add</strong> to confirm."),
                element:  "input[placeholder='Title of new dashboard item']",
                placement: 'bottom'
            },
            {
                waitNot: ".oe_searchview_dashboard.oe_opened",
                waitFor: ".ui-notify-message:contains('Filter added to dashboard'):hidden",
                title:     _t("Click Here"),
                content: _t("To view the newly added selection inside your dashboard"),
                element:  "span.oe_menu_text:contains('My Dashboard')",
                placement: 'bottom'
            },
            {
                title:     _t("Here it is"),
                content: _t("Your analysis has been saved to your dashboard."),
                element:  ".oe_action",
                placement: 'top',
                popover:   { next: _t("Continue"), end: _t("Exit") },
                template:   combo
            },
            {
                title:     _t("Customise your Dashboard"),
                content: _t("You can rearrange your analyses using this button. Try it now."),
                element:  "span:contains('Change Layout')",
                placement: 'bottom'
            },
            {
                title:     _t("Select a Layout"),
                content: _t("Click any layout preference from above"),
                element:  ".oe_dashboard_layout_selector ul li:eq(2)",
                placement: 'bottom'
            },
            {
                waitNot: ".modal",
                title:     _t("Reset Dashboard"),
                content: _t("This resets your dashboard and remove all saved views. Caution: Cannot be undone."),
                element: "span:contains('Reset')",
                placement: 'bottom',
                popover:   { next: _t("Continue"), end: _t("Exit") },
                template:   combo
            },
            {
                title:     _t("End of Tutorial"),
                content: _t("This concludes the analysis tutorial"),
                popover:   { next: _t("Exit") }
            }
        ]
    });
}());