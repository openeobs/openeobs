'use strict';

/*global
    openerp, $
 */

(function () {
    var _t = openerp._t;
    openerp.Tour.register({
        id: 'olap_tutorial',
        name: "Tutorial demonstrating the features of the NEWS Analysis OLAP tool",
        path: '/web',
        mode: 'tour',
        steps: [
            {
                title:     _t("NEWS Observation Analysis Tutorial"),
                content: _t("This tutorial shows the options available in the tool and guides you through a typical use case."),
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Start Here"),
                content: _t("Click here to access the analysis panel"),
                element:   "span.oe_menu_text:contains('NEWS Analysis')",
                placement: 'bottom'
            },
            //{
            //    title:     _t("Overview"),
            //    content: _t(""),
            //    popover:   { next: _t("Continue"), end: _t("Exit") }
            //},
            {
                title:     _t("Select your measures"),
                content: _t("Add or remove measures by clicking the items in this dropdown. <br/>Click <strong>Continue</strong> when done."),
                element:   "ul.dropdown-menu.graph_measure_selection",
                placement: 'top',
                popover:   { next: _t("Continue"), end: _t("Exit") }
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
                waitFor: ".btn[data-mode='row'].active",
                title:     _t("Swap Axes"),
                content: _t("This will swap the axes over. Try it now then click <strong>Continue</strong>"),
                element:   ".btn[data-choice='swap_axis']",
                placement: 'top',
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Expand All"),
                content: _t("You can click here to expand all measures (if they have been collapsed by clicking the '-' button)"),
                element:   ".btn[data-choice='swap_axis']",
                placement: 'top',
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Refresh Data"),
                content: _t("You can click here to update the data in the current view"),
                element:   ".btn[data-choice='swap_axis']",
                placement: 'top',
                popover:   { next: _t("Continue"), end: _t("Exit") }
            },
            {
                title:     _t("Export Dataset"),
                content: _t("You can click here to download the dataset as a CSV"),
                element:   ".btn[data-choice='swap_axis']",
                placement: 'top',
                popover:   { next: _t("Continue"), end: _t("Exit") }
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
                content: _t("When you are happy with your selection, click here to save it to your dashboard."),
                element:   ".oe_searchview_dashboard",
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
                waitNot: "input[placeholder='Title of new dashboard item']",
                title:     _t("Click Here"),
                content: _t("To view your new selection inside your dashboard"),
                element:  "span.oe_menu_text:contains('My Dashboard')",
                placement: 'bottom'
            },
        ]
    });
}());