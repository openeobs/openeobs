describe('NHGraphLib - Table', function(){
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
        respiration_rate: 18,
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



    it('draws the table', function(){

        var tabular_obs = new NHTable();
        tabular_obs.keys = [{key:'avpu_text', title: 'AVPU'}, {key:'oxygen_administration_flag', title: 'On Supplemental O2'}];
        tabular_obs.title = 'Tabular values';
        var focus = new NHFocus();
        focus.tables.push(tabular_obs);
        graphlib.focus = focus;
        graphlib.init();

        spyOn(graphlib, 'draw').andCallThrough();
        graphlib.draw();
        expect(graphlib.draw).toHaveBeenCalled();

        // check that title is there
        var title_el = test.getElementsByTagName('h3');
        expect(title_el.length).toBe(1);
        title_el = title_el[0];
        expect(title_el.textContent).toBe('Tabular values');

        // check that table is there and is properly coded
        var table_el = test.getElementsByClassName('nhtable');
        expect(table_el.length).toBe(1);
        table_el = table_el[0];

        var thead_el = table_el.getElementsByTagName('thead');
        expect(thead_el.length).toBe(1);
        thead_el = thead_el[0];

        var tbody_el = table_el.getElementsByTagName('tbody');
        expect(tbody_el.length).toBe(1);
        tbody_el = tbody_el[0];

        // check that table has correct headers
        var thead_tr = thead_el.getElementsByTagName('tr');
        expect(thead_tr.length).toBe(1);
        thead_tr = thead_tr[0];
        expect(thead_tr.childNodes.length).toBe(3);
        expect(thead_tr.childNodes[0].textContent).toBe('Date');
        expect(thead_tr.childNodes[1].textContent).toBe('AVPU');
        expect(thead_tr.childNodes[2].textContent).toBe('On Supplemental O2');

        //  check that is has correct amount of rows and proper values
        var tbody_tr = tbody_el.getElementsByTagName('tr');
        expect(tbody_tr.length).toBe(1);
        tbody_tr = tbody_tr[0];
        expect(tbody_tr.childNodes.length).toBe(3);
        expect(tbody_tr.childNodes[0].textContent).toBe('2014-12-01 16:16:53');
        expect(tbody_tr.childNodes[1].textContent).toBe('A');
        expect(tbody_tr.childNodes[2].textContent).toBe('false');

    });

    it('draws the table with two sets of data', function(){
        graphlib.data.raw.push(more_data);


        var tabular_obs = new NHTable();
        tabular_obs.keys = [{key:'avpu_text', title: 'AVPU'}, {key:'oxygen_administration_flag', title: 'On Supplemental O2'}, {key:'pulse_rate', title: 'Pulse Rate'}];
        tabular_obs.title = 'Tabular values';
        var focus = new NHFocus();
        focus.tables.push(tabular_obs);
        graphlib.focus = focus;
        graphlib.init();

        spyOn(graphlib, 'draw').andCallThrough();
        graphlib.draw();
        expect(graphlib.draw).toHaveBeenCalled();

        // check that title is there
        var title_el = test.getElementsByTagName('h3');
        expect(title_el.length).toBe(1);
        title_el = title_el[0];
        expect(title_el.textContent).toBe('Tabular values');

        // check that table is there and is properly coded
        var table_el = test.getElementsByClassName('nhtable');
        expect(table_el.length).toBe(1);
        table_el = table_el[0];

        var thead_el = table_el.getElementsByTagName('thead');
        expect(thead_el.length).toBe(1);
        thead_el = thead_el[0];

        var tbody_el = table_el.getElementsByTagName('tbody');
        expect(tbody_el.length).toBe(1);
        tbody_el = tbody_el[0];

        // check that table has correct headers
        var thead_tr = thead_el.getElementsByTagName('tr');
        expect(thead_tr.length).toBe(1);
        thead_tr = thead_tr[0];
        expect(thead_tr.childNodes.length).toBe(4);
        expect(thead_tr.childNodes[0].textContent).toBe('Date');
        expect(thead_tr.childNodes[1].textContent).toBe('AVPU');
        expect(thead_tr.childNodes[2].textContent).toBe('On Supplemental O2')
        expect(thead_tr.childNodes[3].textContent).toBe('Pulse Rate');

        //  check that is has correct amount of rows and proper values
        var tbody_tr = tbody_el.getElementsByTagName('tr');
        expect(tbody_tr.length).toBe(2);
        var tbody_tr_two = tbody_tr[1];
        tbody_tr = tbody_tr[0];
        expect(tbody_tr.childNodes.length).toBe(4);
        expect(tbody_tr.childNodes[0].textContent).toBe('2014-12-01 16:16:53');
        expect(tbody_tr.childNodes[1].textContent).toBe('A');
        expect(tbody_tr.childNodes[2].textContent).toBe('false');
        expect(tbody_tr.childNodes[3].textContent).toBe('80');

        expect(tbody_tr_two.childNodes.length).toBe(4);
        expect(tbody_tr_two.childNodes[0].textContent).toBe('2014-12-01 17:16:53');
        expect(tbody_tr_two.childNodes[1].textContent).toBe('V');
        expect(tbody_tr_two.childNodes[2].textContent).toBe('false');
        expect(tbody_tr_two.childNodes[3].textContent).toBe('81');

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