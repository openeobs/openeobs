describe('NHGraphLib - Graph', function(){
    var graphlib, test, table_el, table_container;
    var data = [{
        __last_update: "2014-12-01 16:16:53",
        activity_id: [700, "NEWS Observation"],
        avpu_text: "A",
        blood_pressure_diastolic: 80,
        blood_pressure_systolic: 120,
        body_temperature: 40,
        clinical_risk: "Medium",
        concentration: false,
        cpap_peep: false,
        create_date: "2014-12-01 13:15:13",
        create_uid: [1, "Administrator"],
        date_started: "2014-12-01 16:16:42",
        date_terminated: "2014-12-01 16:16:53",
        device_id: false,
        display_name: "False",
        flow_rate: false,
        frequency: 240,
        id: 83,
        indirect_oxymetry_spo2: 90,
        is_partial: false,
        mews_score: 0,
        name: false,
        niv_backup: false,
        niv_epap: false,
        niv_ipap: false,
        none_values: "[]",
        null_values: "['niv_epap', 'concentration', 'flow_rate', 'cpap_peep', 'niv_ipap', 'niv_backup']",
        order_by: false,
        oxygen_administration_flag: false,
        partial_reason: false,
        patient_id: [11, "Littel, Alfreda"],
        pulse_rate: 80,
        respiration_rate: 18,
        score: 5,
        state: "completed",
        terminate_uid: [19, "Nadine Bullock"],
        three_in_one: true,
        write_date: "2014-12-01 16:16:53",
        write_uid: [1, "Administrator"]
    }];

    var more_data = {
        __last_update: "2014-12-01 17:16:53",
        activity_id: [700, "NEWS Observation"],
        avpu_text: "V",
        blood_pressure_diastolic: 90,
        blood_pressure_systolic: 130,
        body_temperature: 41,
        clinical_risk: "Medium",
        concentration: false,
        cpap_peep: false,
        create_date: "2014-12-01 14:15:13",
        create_uid: [1, "Administrator"],
        date_started: "2014-12-01 17:16:42",
        date_terminated: "2014-12-01 17:16:53",
        device_id: false,
        display_name: "False",
        flow_rate: false,
        frequency: 240,
        id: 83,
        indirect_oxymetry_spo2: 91,
        is_partial: false,
        mews_score: 0,
        name: false,
        niv_backup: false,
        niv_epap: false,
        niv_ipap: false,
        none_values: "[]",
        null_values: "['niv_epap', 'concentration', 'flow_rate', 'cpap_peep', 'niv_ipap', 'niv_backup']",
        order_by: false,
        oxygen_administration_flag: false,
        partial_reason: false,
        patient_id: [11, "Littel, Alfreda"],
        pulse_rate: 81,
        respiration_rate: 25,
        score: 5,
        state: "completed",
        terminate_uid: [19, "Nadine Bullock"],
        three_in_one: true,
        write_date: "2014-12-01 17:16:53",
        write_uid: [1, "Administrator"]
    };

    beforeEach(function () {
        var body_el = document.getElementsByTagName('body')[0];
        test = document.createElement('div');
        test.setAttribute('id', 'test');
        body_el.appendChild(test);
        if(graphlib == null){
            graphlib = new NHGraphLib('#test');
        }
        body_el.appendChild(test);
        graphlib.data.raw = data;
    });



    it('Draws a table with a single dataset', function(){

        var bp_graph, context, focus, obs, oxy_graph, pulse_graph, resp_rate_graph, score_graph, svg, tabular_obs, temp_graph;
        resp_rate_graph = new NHGraph();
        resp_rate_graph.options.keys = ['respiration_rate'];
        resp_rate_graph.options.label = 'RR';
        resp_rate_graph.options.measurement = '/min';
        resp_rate_graph.axes.y.min = 0;
        resp_rate_graph.axes.y.max = 60;
        resp_rate_graph.options.normal.min = 12;
        resp_rate_graph.options.normal.max = 20;
        resp_rate_graph.style.dimensions.height = 250;
        resp_rate_graph.style.data_style = 'linear';
        resp_rate_graph.style.label_width = 60;

        oxy_graph = new NHGraph();
        oxy_graph.options.keys = ['indirect_oxymetry_spo2'];
        oxy_graph.options.label = 'Spo2';
        oxy_graph.options.measurement = '%';
        oxy_graph.axes.y.min = 70;
        oxy_graph.axes.y.max = 100;
        oxy_graph.options.normal.min = 96;
        oxy_graph.options.normal.max = 100;
        oxy_graph.style.dimensions.height = 200;
        oxy_graph.style.axis.x.hide = true;
        oxy_graph.style.data_style = 'linear';
        oxy_graph.style.label_width = 60;

        bp_graph = new NHGraph();
        bp_graph.options.keys = ['blood_pressure_systolic', 'blood_pressure_diastolic'];
        bp_graph.options.label = 'BP';
        bp_graph.options.measurement = 'mmHg';
        bp_graph.axes.y.min = 30;
        bp_graph.axes.y.max = 260;
        bp_graph.options.normal.min = 150;
        bp_graph.options.normal.max = 151;
        bp_graph.style.dimensions.height = 200;
        bp_graph.style.axis.x.hide = true;
        bp_graph.style.data_style = 'range';
        bp_graph.style.label_width = 60;

        focus = new NHFocus();
        focus.graphs.push(resp_rate_graph);
        focus.graphs.push(oxy_graph);
        focus.graphs.push(bp_graph);

        focus.title = 'Individual values';
        focus.style.padding.right = 0;
        graphlib.focus = focus;
        graphlib.init();

        spyOn(graphlib, 'draw').andCallThrough();
        graphlib.draw();
        expect(graphlib.draw).toHaveBeenCalled();

        // check that title is there
        var focus_el = test.getElementsByClassName('nhfocus');
        expect(focus_el.length).toBe(1);
        focus_el = focus_el[0];
        expect(focus_el.childNodes.length).toBe(3);
        var resp_g = focus_el.childNodes[0];
        var oxy_g = focus_el.childNodes[1];
        var bp_g = focus_el.childNodes[2];

        // Resp Rate Graph - Groups
        var resp_a = resp_g.getElementsByClassName('axes');
        expect(resp_a.length).toBe(1);
        resp_a = resp_a[0];

        var resp_b = resp_g.getElementsByClassName('background');
        expect(resp_b.length).toBe(1);
        resp_b = resp_b[0];

        var resp_c = resp_g.getElementsByTagName('defs');
        expect(resp_c.length).toBe(1);
        resp_c = resp_c[0];

        var resp_d = resp_g.getElementsByClassName('data');
        expect(resp_d.length).toBe(1);
        resp_d = resp_d[0];

        // Resp Rate Graph - Background
        var resp_l = resp_b.getElementsByClassName('label');
        expect(resp_l.length).toBe(1);
        resp_l = resp_l[0];
        expect(resp_l.textContent).toBe('RR');

        var resp_m = resp_b.getElementsByClassName('measurement');
        expect(resp_m.length).toBe(1);
        resp_m = resp_m[0];
        expect(resp_m.textContent).toBe('18 /min');

        var resp_n = resp_b.getElementsByClassName('normal');
        expect(resp_n.length).toBe(1);
        resp_n = resp_n[0];
        expect(resp_n.getAttribute('clip-path')).toBe('url(#respiration_rate-clip)');

        var resp_vg = resp_b.getElementsByClassName('vertical');
        expect(resp_vg.length).toNotBe(0);

        var resp_hg = resp_b.getElementsByClassName('horizontal');
        expect(resp_hg.length).toNotBe(0);

        // Resp Rate Graph - Axes
        var resp_ax = resp_a.getElementsByClassName('x');
        expect(resp_ax.length).toBe(1);
        resp_ax = resp_ax[0];
        expect(resp_ax.childNodes.length).toNotBe(0);

        var resp_axp = resp_ax.getElementsByClassName('domain');
        expect(resp_axp.length).toBe(1);

        var resp_axt = resp_ax.getElementsByClassName('tick');
        expect(resp_axt.length).toNotBe(0);

        var resp_ay = resp_a.getElementsByClassName('y');
        expect(resp_ay.length).toBe(1);
        resp_ay = resp_ay[0];
        expect(resp_ay.childNodes.length).toNotBe(0);

        var resp_ayp = resp_ay.getElementsByClassName('domain');
        expect(resp_ayp.length).toBe(1);

        var resp_ayt = resp_ay.getElementsByClassName('tick');
        expect(resp_ayt.length).toNotBe(0);

        // Resp Rate Graph - Data
        var resp_dc = resp_d.getElementsByClassName('point');
        expect(resp_dc.length).toBe(1);
        resp_dc = resp_dc[0];
        expect(resp_dc.tagName).toBe('circle');
        expect(resp_dc.getAttribute('clip-path')).toBe('url(#respiration_rate-clip)');

        // Resp Rate Graph - Clip Path
        // var resp_ccp = resp_c.getElementsByTagName('clippath'); // can't use due to stupid webkit bug that means can't select clippath elements
        var resp_ccp = resp_c.getElementsByClassName('clip');
        expect(resp_ccp.length).toBe(1);
        resp_ccp = resp_ccp[0];
        expect(resp_ccp.getAttribute('id')).toBe('respiration_rate-clip');
        var resp_cr = resp_ccp.getElementsByTagName('rect');
        expect(resp_cr.length).toBe(1);



        // Oxygen Graph - Groups
        var oxy_a = oxy_g.getElementsByClassName('axes');
        expect(oxy_a.length).toBe(1);
        oxy_a = oxy_a[0];

        var oxy_b = oxy_g.getElementsByClassName('background');
        expect(oxy_b.length).toBe(1);
        oxy_b = oxy_b[0];

        var oxy_c = oxy_g.getElementsByTagName('defs');
        expect(oxy_c.length).toBe(1);
        oxy_c = oxy_c[0];

        var oxy_d = oxy_g.getElementsByClassName('data');
        expect(oxy_d.length).toBe(1);
        oxy_d = oxy_d[0];

        // Oxygen Graph - Background
        var oxy_l = oxy_b.getElementsByClassName('label');
        expect(oxy_l.length).toBe(1);
        oxy_l = oxy_l[0];
        expect(oxy_l.textContent).toBe('Spo2');

        var oxy_m = oxy_b.getElementsByClassName('measurement');
        expect(oxy_m.length).toBe(1);
        oxy_m = oxy_m[0];
        expect(oxy_m.textContent).toBe('90 %');

        var oxy_n = oxy_b.getElementsByClassName('normal');
        expect(oxy_n.length).toBe(1);
        oxy_n = oxy_n[0];
        expect(oxy_n.getAttribute('clip-path')).toBe('url(#indirect_oxymetry_spo2-clip)');

        var oxy_vg = oxy_b.getElementsByClassName('vertical');
        expect(oxy_vg.length).toNotBe(0);

        var oxy_hg = oxy_b.getElementsByClassName('horizontal');
        expect(oxy_hg.length).toNotBe(0);

        // Oxygen Graph - Axes
        var oxy_ax = oxy_a.getElementsByClassName('x');
        expect(oxy_ax.length).toBe(0);

        var oxy_ay = oxy_a.getElementsByClassName('y');
        expect(oxy_ay.length).toBe(1);
        oxy_ay = oxy_ay[0];
        expect(oxy_ay.childNodes.length).toNotBe(0);

        var oxy_ayp = oxy_ay.getElementsByClassName('domain');
        expect(oxy_ayp.length).toBe(1);

        var oxy_ayt = oxy_ay.getElementsByClassName('tick');
        expect(oxy_ayt.length).toNotBe(0);

        // Oxygen Graph - Data
        var oxy_dc = oxy_d.getElementsByClassName('point');
        expect(oxy_dc.length).toBe(1);
        oxy_dc = oxy_dc[0];
        expect(oxy_dc.tagName).toBe('circle');
        expect(oxy_dc.getAttribute('clip-path')).toBe('url(#indirect_oxymetry_spo2-clip)');

        // Oxygen Graph - Clip Path
        var oxy_ccp = oxy_c.getElementsByClassName('clip');
        expect(oxy_ccp.length).toBe(1);
        oxy_ccp = oxy_ccp[0];
        expect(oxy_ccp.getAttribute('id')).toBe('indirect_oxymetry_spo2-clip');
        var oxy_cr = oxy_ccp.getElementsByTagName('rect');
        expect(oxy_cr.length).toBe(1);


        // BP Graph - Groups
        var bp_a = bp_g.getElementsByClassName('axes');
        expect(bp_a.length).toBe(1);
        bp_a = bp_a[0];

        var bp_b = bp_g.getElementsByClassName('background');
        expect(bp_b.length).toBe(1);
        bp_b = bp_b[0];

        var bp_c = bp_g.getElementsByTagName('defs');
        expect(bp_c.length).toBe(1);
        bp_c = bp_c[0];

        var bp_d = bp_g.getElementsByClassName('data');
        expect(bp_d.length).toBe(1);
        bp_d = bp_d[0];

        // BP Graph - Background
        var bp_l = bp_b.getElementsByClassName('label');
        expect(bp_l.length).toBe(1);
        bp_l = bp_l[0];
        expect(bp_l.textContent).toBe('BP');

        var bp_m = bp_b.getElementsByClassName('measurement');
        expect(bp_m.length).toBe(2);
        var bp_mt = bp_m[0];
        var bp_mb = bp_m[1];
        expect(bp_mt.textContent).toBe('120');
        expect(bp_mb.textContent).toBe('80 mmHg');

        var bp_n = bp_b.getElementsByClassName('normal');
        expect(bp_n.length).toBe(1);
        bp_n = bp_n[0];
        expect(bp_n.getAttribute('clip-path')).toBe('url(#blood_pressure_systolic-blood_pressure_diastolic-clip)');

        var bp_vg = bp_b.getElementsByClassName('vertical');
        expect(bp_vg.length).toNotBe(0);

        var bp_hg = bp_b.getElementsByClassName('horizontal');
        expect(bp_hg.length).toNotBe(0);

        // BP Graph - Axes
        var bp_ax = bp_a.getElementsByClassName('x');
        expect(bp_ax.length).toBe(0);

        var bp_ay = bp_a.getElementsByClassName('y');
        expect(bp_ay.length).toBe(1);
        bp_ay = bp_ay[0];
        expect(bp_ay.childNodes.length).toNotBe(0);

        var bp_ayp = bp_ay.getElementsByClassName('domain');
        expect(bp_ayp.length).toBe(1);

        var bp_ayt = bp_ay.getElementsByClassName('tick');
        expect(bp_ayt.length).toNotBe(0);

        // BP Graph - Data
        var bp_dt = bp_d.getElementsByClassName('top');
        expect(bp_dt.length).toBe(1);
        bp_dt = bp_dt[0];
        expect(bp_dt.tagName).toBe('rect');
        expect(bp_dt.getAttribute('clip-path')).toBe('url(#blood_pressure_systolic-blood_pressure_diastolic-clip)');

        var bp_db = bp_d.getElementsByClassName('bottom');
        expect(bp_db.length).toBe(1);
        bp_db = bp_db[0];
        expect(bp_db.tagName).toBe('rect');
        expect(bp_db.getAttribute('clip-path')).toBe('url(#blood_pressure_systolic-blood_pressure_diastolic-clip)');

        var bp_de = bp_d.getElementsByClassName('extent');
        expect(bp_de.length).toBe(1);
        bp_de = bp_de[0];
        expect(bp_de.tagName).toBe('rect');
        expect(bp_de.getAttribute('clip-path')).toBe('url(#blood_pressure_systolic-blood_pressure_diastolic-clip)');


        // Oxygen Graph - Clip Path
        var bp_ccp = bp_c.getElementsByClassName('clip');
        expect(bp_ccp.length).toBe(1);
        bp_ccp = bp_ccp[0];
        expect(bp_ccp.getAttribute('id')).toBe('blood_pressure_systolic-blood_pressure_diastolic-clip');
        var bp_cr = bp_ccp.getElementsByTagName('rect');
        expect(bp_cr.length).toBe(1);


    });


    it('Draws a table with two datasets', function(){

        graphlib.data.raw.push(more_data);
        var bp_graph, context, focus, obs, oxy_graph, pulse_graph, resp_rate_graph, score_graph, svg, tabular_obs, temp_graph;
        resp_rate_graph = new NHGraph();
        resp_rate_graph.options.keys = ['respiration_rate'];
        resp_rate_graph.options.label = 'RR';
        resp_rate_graph.options.measurement = '/min';
        resp_rate_graph.axes.y.min = 0;
        resp_rate_graph.axes.y.max = 60;
        resp_rate_graph.options.normal.min = 12;
        resp_rate_graph.options.normal.max = 20;
        resp_rate_graph.style.dimensions.height = 250;
        resp_rate_graph.style.data_style = 'linear';
        resp_rate_graph.style.label_width = 60;

        oxy_graph = new NHGraph();
        oxy_graph.options.keys = ['indirect_oxymetry_spo2'];
        oxy_graph.options.label = 'Spo2';
        oxy_graph.options.measurement = '%';
        oxy_graph.axes.y.min = 70;
        oxy_graph.axes.y.max = 100;
        oxy_graph.options.normal.min = 96;
        oxy_graph.options.normal.max = 100;
        oxy_graph.style.dimensions.height = 200;
        oxy_graph.style.axis.x.hide = true;
        oxy_graph.style.data_style = 'linear';
        oxy_graph.style.label_width = 60;

        bp_graph = new NHGraph();
        bp_graph.options.keys = ['blood_pressure_systolic', 'blood_pressure_diastolic'];
        bp_graph.options.label = 'BP';
        bp_graph.options.measurement = 'mmHg';
        bp_graph.axes.y.min = 30;
        bp_graph.axes.y.max = 260;
        bp_graph.options.normal.min = 150;
        bp_graph.options.normal.max = 151;
        bp_graph.style.dimensions.height = 200;
        bp_graph.style.axis.x.hide = true;
        bp_graph.style.data_style = 'range';
        bp_graph.style.label_width = 60;

        focus = new NHFocus();
        focus.graphs.push(resp_rate_graph);
        focus.graphs.push(oxy_graph);
        focus.graphs.push(bp_graph);

        focus.title = 'Individual values';
        focus.style.padding.right = 0;
        graphlib.focus = focus;
        graphlib.init();

        spyOn(graphlib, 'draw').andCallThrough();
        graphlib.draw();
        expect(graphlib.draw).toHaveBeenCalled();

        // check that title is there
        var focus_el = test.getElementsByClassName('nhfocus');
        expect(focus_el.length).toBe(1);
        focus_el = focus_el[0];
        expect(focus_el.childNodes.length).toBe(3);
        var resp_g = focus_el.childNodes[0];
        var oxy_g = focus_el.childNodes[1];
        var bp_g = focus_el.childNodes[2];

        // Resp Rate Graph - Groups
        var resp_a = resp_g.getElementsByClassName('axes');
        expect(resp_a.length).toBe(1);
        resp_a = resp_a[0];

        var resp_b = resp_g.getElementsByClassName('background');
        expect(resp_b.length).toBe(1);
        resp_b = resp_b[0];

        var resp_c = resp_g.getElementsByTagName('defs');
        expect(resp_c.length).toBe(1);
        resp_c = resp_c[0];

        var resp_d = resp_g.getElementsByClassName('data');
        expect(resp_d.length).toBe(1);
        resp_d = resp_d[0];

        // Resp Rate Graph - Background
        var resp_l = resp_b.getElementsByClassName('label');
        expect(resp_l.length).toBe(1);
        resp_l = resp_l[0];
        expect(resp_l.textContent).toBe('RR');

        var resp_m = resp_b.getElementsByClassName('measurement');
        expect(resp_m.length).toBe(1);
        resp_m = resp_m[0];
        expect(resp_m.textContent).toBe('25 /min');

        var resp_n = resp_b.getElementsByClassName('normal');
        expect(resp_n.length).toBe(1);
        resp_n = resp_n[0];
        expect(resp_n.getAttribute('clip-path')).toBe('url(#respiration_rate-clip)');

        var resp_vg = resp_b.getElementsByClassName('vertical');
        expect(resp_vg.length).toNotBe(0);

        var resp_hg = resp_b.getElementsByClassName('horizontal');
        expect(resp_hg.length).toNotBe(0);

        // Resp Rate Graph - Axes
        var resp_ax = resp_a.getElementsByClassName('x');
        expect(resp_ax.length).toBe(1);
        resp_ax = resp_ax[0];
        expect(resp_ax.childNodes.length).toNotBe(0);

        var resp_axp = resp_ax.getElementsByClassName('domain');
        expect(resp_axp.length).toBe(1);

        var resp_axt = resp_ax.getElementsByClassName('tick');
        expect(resp_axt.length).toNotBe(0);

        var resp_ay = resp_a.getElementsByClassName('y');
        expect(resp_ay.length).toBe(1);
        resp_ay = resp_ay[0];
        expect(resp_ay.childNodes.length).toNotBe(0);

        var resp_ayp = resp_ay.getElementsByClassName('domain');
        expect(resp_ayp.length).toBe(1);

        var resp_ayt = resp_ay.getElementsByClassName('tick');
        expect(resp_ayt.length).toNotBe(0);

        // Resp Rate Graph - Data
        var resp_dc = resp_d.getElementsByClassName('point');
        expect(resp_dc.length).toBe(2);
        expect(resp_dc[0].tagName).toBe('circle');
        expect(resp_dc[0].getAttribute('clip-path')).toBe('url(#respiration_rate-clip)');
        expect(resp_dc[1].tagName).toBe('circle');
        expect(resp_dc[1].getAttribute('clip-path')).toBe('url(#respiration_rate-clip)');

        var resp_dl = resp_d.getElementsByClassName('path');
        expect(resp_dl.length).toBe(1);
        expect(resp_dl[0].tagName).toBe('path');
        expect(resp_dl[0].getAttribute('clip-path')).toBe('url(#respiration_rate-clip)');

        // Resp Rate Graph - Clip Path
        // var resp_ccp = resp_c.getElementsByTagName('clippath'); // can't use due to stupid webkit bug that means can't select clippath elements
        var resp_ccp = resp_c.getElementsByClassName('clip');
        expect(resp_ccp.length).toBe(1);
        resp_ccp = resp_ccp[0];
        expect(resp_ccp.getAttribute('id')).toBe('respiration_rate-clip');
        var resp_cr = resp_ccp.getElementsByTagName('rect');
        expect(resp_cr.length).toBe(1);



        // Oxygen Graph - Groups
        var oxy_a = oxy_g.getElementsByClassName('axes');
        expect(oxy_a.length).toBe(1);
        oxy_a = oxy_a[0];

        var oxy_b = oxy_g.getElementsByClassName('background');
        expect(oxy_b.length).toBe(1);
        oxy_b = oxy_b[0];

        var oxy_c = oxy_g.getElementsByTagName('defs');
        expect(oxy_c.length).toBe(1);
        oxy_c = oxy_c[0];

        var oxy_d = oxy_g.getElementsByClassName('data');
        expect(oxy_d.length).toBe(1);
        oxy_d = oxy_d[0];

        // Oxygen Graph - Background
        var oxy_l = oxy_b.getElementsByClassName('label');
        expect(oxy_l.length).toBe(1);
        oxy_l = oxy_l[0];
        expect(oxy_l.textContent).toBe('Spo2');

        var oxy_m = oxy_b.getElementsByClassName('measurement');
        expect(oxy_m.length).toBe(1);
        oxy_m = oxy_m[0];
        expect(oxy_m.textContent).toBe('91 %');

        var oxy_n = oxy_b.getElementsByClassName('normal');
        expect(oxy_n.length).toBe(1);
        oxy_n = oxy_n[0];
        expect(oxy_n.getAttribute('clip-path')).toBe('url(#indirect_oxymetry_spo2-clip)');

        var oxy_vg = oxy_b.getElementsByClassName('vertical');
        expect(oxy_vg.length).toNotBe(0);

        var oxy_hg = oxy_b.getElementsByClassName('horizontal');
        expect(oxy_hg.length).toNotBe(0);

        // Oxygen Graph - Axes
        var oxy_ax = oxy_a.getElementsByClassName('x');
        expect(oxy_ax.length).toBe(0);

        var oxy_ay = oxy_a.getElementsByClassName('y');
        expect(oxy_ay.length).toBe(1);
        oxy_ay = oxy_ay[0];
        expect(oxy_ay.childNodes.length).toNotBe(0);

        var oxy_ayp = oxy_ay.getElementsByClassName('domain');
        expect(oxy_ayp.length).toBe(1);

        var oxy_ayt = oxy_ay.getElementsByClassName('tick');
        expect(oxy_ayt.length).toNotBe(0);

        // Oxygen Graph - Data
        var oxy_dc = oxy_d.getElementsByClassName('point');
        expect(oxy_dc.length).toBe(2);
        expect(oxy_dc[0].tagName).toBe('circle');
        expect(oxy_dc[0].getAttribute('clip-path')).toBe('url(#indirect_oxymetry_spo2-clip)');
        expect(oxy_dc[1].tagName).toBe('circle');
        expect(oxy_dc[1].getAttribute('clip-path')).toBe('url(#indirect_oxymetry_spo2-clip)');

        var oxy_dl = oxy_d.getElementsByClassName('path');
        expect(oxy_dl.length).toBe(1);
        expect(oxy_dl[0].tagName).toBe('path');
        expect(oxy_dl[0].getAttribute('clip-path')).toBe('url(#indirect_oxymetry_spo2-clip)');

        // Oxygen Graph - Clip Path
        var oxy_ccp = oxy_c.getElementsByClassName('clip');
        expect(oxy_ccp.length).toBe(1);
        oxy_ccp = oxy_ccp[0];
        expect(oxy_ccp.getAttribute('id')).toBe('indirect_oxymetry_spo2-clip');
        var oxy_cr = oxy_ccp.getElementsByTagName('rect');
        expect(oxy_cr.length).toBe(1);


        // BP Graph - Groups
        var bp_a = bp_g.getElementsByClassName('axes');
        expect(bp_a.length).toBe(1);
        bp_a = bp_a[0];

        var bp_b = bp_g.getElementsByClassName('background');
        expect(bp_b.length).toBe(1);
        bp_b = bp_b[0];

        var bp_c = bp_g.getElementsByTagName('defs');
        expect(bp_c.length).toBe(1);
        bp_c = bp_c[0];

        var bp_d = bp_g.getElementsByClassName('data');
        expect(bp_d.length).toBe(1);
        bp_d = bp_d[0];

        // BP Graph - Background
        var bp_l = bp_b.getElementsByClassName('label');
        expect(bp_l.length).toBe(1);
        bp_l = bp_l[0];
        expect(bp_l.textContent).toBe('BP');

        var bp_m = bp_b.getElementsByClassName('measurement');
        expect(bp_m.length).toBe(2);
        var bp_mt = bp_m[0];
        var bp_mb = bp_m[1];
        expect(bp_mt.textContent).toBe('130');
        expect(bp_mb.textContent).toBe('90 mmHg');

        var bp_n = bp_b.getElementsByClassName('normal');
        expect(bp_n.length).toBe(1);
        bp_n = bp_n[0];
        expect(bp_n.getAttribute('clip-path')).toBe('url(#blood_pressure_systolic-blood_pressure_diastolic-clip)');

        var bp_vg = bp_b.getElementsByClassName('vertical');
        expect(bp_vg.length).toNotBe(0);

        var bp_hg = bp_b.getElementsByClassName('horizontal');
        expect(bp_hg.length).toNotBe(0);

        // BP Graph - Axes
        var bp_ax = bp_a.getElementsByClassName('x');
        expect(bp_ax.length).toBe(0);

        var bp_ay = bp_a.getElementsByClassName('y');
        expect(bp_ay.length).toBe(1);
        bp_ay = bp_ay[0];
        expect(bp_ay.childNodes.length).toNotBe(0);

        var bp_ayp = bp_ay.getElementsByClassName('domain');
        expect(bp_ayp.length).toBe(1);

        var bp_ayt = bp_ay.getElementsByClassName('tick');
        expect(bp_ayt.length).toNotBe(0);

        // BP Graph - Data
        var bp_dt = bp_d.getElementsByClassName('top');
        expect(bp_dt.length).toBe(2);
        expect(bp_dt[0].tagName).toBe('rect');
        expect(bp_dt[0].getAttribute('clip-path')).toBe('url(#blood_pressure_systolic-blood_pressure_diastolic-clip)');
        expect(bp_dt[1].tagName).toBe('rect');
        expect(bp_dt[1].getAttribute('clip-path')).toBe('url(#blood_pressure_systolic-blood_pressure_diastolic-clip)');

        var bp_db = bp_d.getElementsByClassName('bottom');
        expect(bp_db.length).toBe(2);
        expect(bp_db[0].tagName).toBe('rect');
        expect(bp_db[0].getAttribute('clip-path')).toBe('url(#blood_pressure_systolic-blood_pressure_diastolic-clip)');
        expect(bp_db[1].tagName).toBe('rect');
        expect(bp_db[1].getAttribute('clip-path')).toBe('url(#blood_pressure_systolic-blood_pressure_diastolic-clip)');

        var bp_de = bp_d.getElementsByClassName('extent');
        expect(bp_de.length).toBe(2);
        expect(bp_de[0].tagName).toBe('rect');
        expect(bp_de[0].getAttribute('clip-path')).toBe('url(#blood_pressure_systolic-blood_pressure_diastolic-clip)');
        expect(bp_de[1].tagName).toBe('rect');
        expect(bp_de[1].getAttribute('clip-path')).toBe('url(#blood_pressure_systolic-blood_pressure_diastolic-clip)');


        // Oxygen Graph - Clip Path
        var bp_ccp = bp_c.getElementsByClassName('clip');
        expect(bp_ccp.length).toBe(1);
        bp_ccp = bp_ccp[0];
        expect(bp_ccp.getAttribute('id')).toBe('blood_pressure_systolic-blood_pressure_diastolic-clip');
        var bp_cr = bp_ccp.getElementsByTagName('rect');
        expect(bp_cr.length).toBe(1);


    });



    afterEach(function () {
        if (graphlib != null) {
            graphlib = null;
        }
        if(test != null){
            test.parentNode.removeChild(test);
        }
        if(table_el != null){
            table_el.parentNode.removeChild(table_el);
        }
        var popup = document.getElementById('chart_popup');
        if(popup != null){
            popup.parentNode.removeChild(popup);
        }
        if(table_container != null){
            table_container.parentNode.removeChild(table_container);
        }
    });

});