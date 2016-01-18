/**
 * Acuity Board
 * Automated QA tours
 * Created by Jon on 12/01/16.
 */

'use strict';

/*global
    openerp, $
 */

(function () {
    var _t = openerp._t,
        assert = openerp.Tour.helpers.assert,
        capitalise = openerp.Tour.helpers.capitalise,
        wm = openerp.Tour.users.wm;
    openerp.Tour.register({
        id: 'acuity_board_kanban',
        name: "Describe acuity board kanban view (" + wm + ")",
        path: '/web?debug=',
        user: wm,
        mode: 'test',
        steps: [
            {
                title:     _t("User logged in"),
                element:   ".oe_topbar_name:contains('" + wm + "')"
            },
            {
                title: _t('No score kanban column'),
                waitFor: ".nhclinical_kanban_column_clinical_risk_none",
                onload: function () {
                    // Check cards are ordered by bed number
                    var cards = $(".nhclinical_kanban_column_clinical_risk_none .oe_kanban_content div:contains('Bed')");
                    for (var i = 0; i < cards.length - 1; i++) {
                        var first = +cards[i].textContent.substr(4, 2),
                            second = +cards[i+1].textContent.substr(4, 2);
                        assert(first < second, "Cards are ordered by bed number");
                    }

                    // Check cards all have an appropriate score for column
                    cards = $(".nhclinical_kanban_column_clinical_risk_none .oe_kanban_content div:contains('Score')");
                    cards.each(function (el) {
                        var score = cards[el].textContent;
                        assert(score.indexOf('NA'), "Patient has appropriate score for column")
                    })
                }
            },
            {
                title: _t('Column is unique'),
                waitNot: ".oe_kanban_column.nhclinical_kanban_column_clinical_risk_none:eq(1)"
            },
            {
                title: _t('No risk kanban column'),
                waitFor: ".oe_kanban_column.nhclinical_kanban_column_clinical_risk_no",
                onload: function () {
                    var cards = $(".nhclinical_kanban_column_clinical_risk_no .oe_kanban_content div:contains('Bed')");
                    for (var i = 0; i < cards.length - 1; i++) {
                        var first = +cards[i].textContent.substr(4, 2),
                            second = +cards[i+1].textContent.substr(4, 2);
                        assert(first < second, "Cards are ordered by bed number");
                    }

                    // Check cards all have an appropriate score for column
                    cards = $(".nhclinical_kanban_column_clinical_risk_no .oe_kanban_content div:contains('Score')");
                    cards.each(function (el) {
                        var score = +cards[el].textContent.substr(7,9);
                        assert(score === 0, "Patient has NEWS score of 0")
                    })
                }
            },
            {
                title: _t('Column is unique'),
                waitNot: ".oe_kanban_column.nhclinical_kanban_column_clinical_risk_no:eq(1)"
            },
            {
                title: _t('Low risk kanban column'),
                waitFor: ".oe_kanban_column.nhclinical_kanban_column_clinical_risk_low",
                onload: function () {
                    var cards = $(".nhclinical_kanban_column_clinical_risk_low .oe_kanban_content div:contains('Bed')");
                    for (var i = 0; i < cards.length - 1; i++) {
                        var first = +cards[i].textContent.substr(4, 2),
                            second = +cards[i+1].textContent.substr(4, 2);
                        assert(first < second, "Cards are ordered by bed number");
                    }
                    // Check cards all have an appropriate score for column
                    cards = $(".nhclinical_kanban_column_clinical_risk_low .oe_kanban_content div:contains('Score')");
                    cards.each(function (el) {
                        var score = +cards[el].textContent.substr(7,9);
                        assert(5 > score > 0, "Patient has appropriate score for column")
                    })
                }
            },
            {
                title: _t('Column is unique'),
                waitNot: ".oe_kanban_column.nhclinical_kanban_column_clinical_risk_low:eq(1)"
            },
            {
                title: _t('Medium risk kanban column'),
                waitFor: ".oe_kanban_column.nhclinical_kanban_column_clinical_risk_medium",
                onload: function () {
                    var cards = $(".nhclinical_kanban_column_clinical_risk_medium .oe_kanban_content div:contains('Bed')");
                    for (var i = 0; i < cards.length - 1; i++) {
                        var first = +cards[i].textContent.substr(4, 2),
                            second = +cards[i+1].textContent.substr(4, 2);
                        assert(first < second, "Cards are ordered by bed number");
                    }
                    // Check cards all have an appropriate score for column
                    cards = $(".nhclinical_kanban_column_clinical_risk_medium .oe_kanban_content div:contains('Score')");
                    cards.each(function (el) {
                        var score = +cards[el].textContent.substr(7,9);
                        assert(10 > score >= 5, "Patient has appropriate score for column")
                    })
                }
            },
            {
                title: _t('Column is unique'),
                waitNot: ".oe_kanban_column.nhclinical_kanban_column_clinical_risk_medium:eq(1)"
            },
            {
                title: _t('High risk kanban column'),
                waitFor: ".oe_kanban_column.nhclinical_kanban_column_clinical_risk_high",
                onload: function () {
                    var cards = $(".nhclinical_kanban_column_clinical_risk_high .oe_kanban_content div:contains('Bed')");
                    for (var i = 0; i < cards.length - 1; i++) {
                        var first = +cards[i].textContent.substr(4, 2),
                            second = +cards[i+1].textContent.substr(4, 2);
                        assert(first < second, "Cards are ordered by bed number");
                    }
                    // Check cards all have an appropriate score for column
                    cards = $(".nhclinical_kanban_column_clinical_risk_high .oe_kanban_content div:contains('Score')");
                    cards.each(function (el) {
                        var score = +cards[el].textContent.substr(7,9);
                        assert(score >= 10, "Patient has appropriate score for column")
                    })
                }
            },
            {
                title: _t('Column is unique'),
                waitNot: ".oe_kanban_column.nhclinical_kanban_column_clinical_risk_high:eq(1)"
            },
            {
                title: _t('Check there are no duplicate bed cards'),
                waitFor: "div.oe_kanban_card",
                onload: function () {
                    // Function to check each card only appears once, works but
                    // could be refactored
                    var beds = $("div.oe_kanban_card .oe_kanban_content div:contains('Bed')");
                    for (var i = 0; i < beds.length; i++) {
                        var count = 0,
                            bed = beds[i].textContent;
                        for (var j = 0; j < beds.length; j++) {
                            if (bed === beds[j].textContent) count ++
                        }
                        assert(count===1, "Each card should only appear once on board");
                    }
                }
            },
            {
                // Necessary final step in case assert in previous step fails
                title: _t('All checks passed'),
                waitFor: ".oe_topbar_name:contains('Winifred')"
            }
        ]
    });
    openerp.Tour.register({
        id: 'acuity_board_list',
        name: "Describe acuity board list view (" + wm +")",
        path: '/web?debug=',
        user: wm,
        mode: 'test',
        steps: [
            {
                title:     _t("User logged in"),
                waitFor:   ".oe_topbar_name:contains('" + capitalise(wm) + "')"
            },
            {
                title:     _t("Switch to list view"),
                element:   "a[data-view-type='list']"
            },
            {
                title: _t('It shows the no score group'),
                waitFor: "tr.oe_group_header:contains('No Score Yet')"
            },
            {
                title: _t('It shows the no risk group'),
                waitFor: "tr.oe_group_header:contains('No Risk')"
            },
            {
                title: _t('It shows the low risk group'),
                waitFor: "tr.oe_group_header:contains('Low Risk')"
            },
            {
                title: _t('It shows the medium risk group'),
                waitFor: "tr.oe_group_header:contains('Medium Risk')"
            },
            {
                title: _t('It shows the high risk group'),
                waitFor: "tr.oe_group_header:contains('High Risk')"
            },
            {
                title: _t('It shows the patient record cells expanded'),
                waitFor: "tr[data-id]"
            },
            //{
            //    title: _t("It doesn't show patients the user is not responsible for"),
            //    waitNot: "tr[data-id] td[data-field='full_name']:contains('James')"
            //},
            {
                title: _t('It only shows patients that have an active recurrent scheduling pattern'),
                onload: function () {
                    var freqs = $("tr[data-id] td[data-field='frequency']");
                    freqs.each(function (el) {
                        assert(freqs[el].textContent !== '', 'All patient records should have a NEWS frequency')
                    })
                }
            },
            {
                title: _t('shows the patients name'),
                waitFor: "tr[data-id]:eq(0) td[data-field='full_name']"
            },
            {
                title: _t('shows current location'),
                waitFor: "tr[data-id]:eq(0) td[data-field='location']"
            },
            {
                title: _t('shows the patients sex'),
                waitFor: "tr[data-id]:eq(0) td[data-field='sex']"
            },
            {
                title: _t('shows the patients latest NEWS score'),
                waitFor: "tr[data-id]:eq(0) td[data-field='ews_score_string']"
            },
            {
                title: _t('shows the patients latest NEWS trend'),
                waitFor: "tr[data-id]:eq(0) td[data-field='ews_trend_string']",
                onload: function () {
                    var src = $("tr[data-id]:eq(0) img[alt='Score Trend']").attr('src'),
                        act = '/src/img/icons/level-up.png';
                    src = src.slice(-act.length);
                    assert(src === act, 'img src path should match expected');
                }
            },
            {
                title: _t('shows the time to next observation'),
                waitFor: "tr[data-id]:eq(0) td[data-field='next_diff']"
            },
            {
                title: _t('shows the patients NEWS frequency'),
                waitFor: "tr[data-id]:eq(0) td[data-field='frequency']"
            },
            {
                title: _t('has button to open NEWS chart'),
                waitFor: "tr[data-id]:eq(0) button[title='Chart']",
                onload: function () {
                    var src = $("tr[data-id]:eq(0) img[alt='Chart']").attr('src'),
                        act = '/src/img/icons/chart.png';
                    src = src.slice(-act.length);
                    assert(src === act, 'path should match expected');
                }
            },
            {
                title: _t('has button to open observation list'),
                waitFor: "tr[data-id]:eq(0) button[title='EWS']",
                onload: function () {
                    var src = $("tr[data-id]:eq(0) img[alt='EWS']").attr('src'),
                        act = '/src/img/icons/observation.png';
                    src = src.slice(-act.length);
                    assert(src === act, 'img src path should match expected');
                }
            },
            {
                title: _t('it worked')
            }
        ]
    });
}());