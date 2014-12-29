describe('NHGraphLib - Card Table', function(){
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
    beforeEach(function () {
        var body_el = document.getElementsByTagName('body')[0];
        test = document.createElement('div');
        test.setAttribute('id', 'test');
        body_el.appendChild(test);
        if(graphlib == null){
            graphlib = new NHGraphLib('#test');
        }

        table_container = document.createElement('div');
        table_container.setAttribute('id', 'table-content');
        body_el.appendChild(table_container);

        table_el = document.createElement('div');
        table_el.setAttribute('id', 'table');
        body_el.appendChild(table_el);



        graphlib.table.element = '#table';
        graphlib.table.keys = [
            {
                title: 'Respiration Rate',
                keys: ['respiration_rate']
            },
            {
                title: 'O2 Saturation',
                keys: ['indirect_oxymetry_spo2']
            },
            {
                title: 'Body Temperature',
                keys: ['body_temperature']
            },
            {
                title: 'Blood Pressure Systolic',
                keys: ['blood_pressure_systolic']
            },
            {
                title: 'Blood Pressure Diastolic',
                keys: ['blood_pressure_diastolic']
            },
            {
                title: 'Pulse Rate',
                keys: ['pulse_rate']
            },
            {
                title: 'AVPU',
                keys: ['avpu_text']
            },
            {
                title: 'Patient on Supplmental O2',
                keys: ['oxygen_administration_flag']
            },
            {
                title: 'Inspired Oxygen',
                keys: [
                    {
                        title: 'Flow Rate',
                        keys: ['flow_rate']
                    },
                    {
                        title: 'Concentration',
                        keys: ['concentration']
                    },
                    {
                        title: 'Device',
                        keys: ['device_id']
                    },
                    {
                        title: 'CPAP PEEP',
                        keys: ['cpap_peep']
                    },
                    {
                        title: 'NIV iPAP',
                        keys: ['niv_ipap']
                    },
                    {
                        title: 'NIV ePAP',
                        keys: ['niv_epap']
                    },
                    {
                        title: 'NIV Backup Rate',
                        keys: ['niv_backup']
                    }
                ]
            }
        ];
        graphlib.data.raw = data;
    });



    it('draws the table', function(){
        spyOn(graphlib, 'init').andCallThrough();
        spyOn(graphlib, 'draw').andCallThrough();
        spyOn(graphlib, 'draw_table').andCallThrough();
        graphlib.init();
        expect(graphlib.init).toHaveBeenCalled();

        graphlib.draw();
        expect(graphlib.draw).toHaveBeenCalled();
        expect(graphlib.draw_table).toHaveBeenCalled();
        // see if svg element is there
        var svg = test.getElementsByTagName('svg');
        expect(svg.length).toBe(1);
        svg = svg[0];
        svg_height = svg.getAttribute('height');
        svg_width = svg.getAttribute('width');
        expect(svg_height).toBe('0');
        expect(svg_width).toBe(test.clientWidth.toString());
        expect(svg.hasChildNodes()).toBe(false);

        // see if popup element is there
        var popup = document.getElementById('chart_popup');
        expect(popup.classList.contains('hidden')).toBe(true)

        // see if table is there
        var table = document.getElementById('table');
        expect(typeof(table)).toBe('object');

        // see if cards are there
        expect(table_container.hasChildNodes()).toBe(true);
        var cards = document.getElementsByClassName('card');
        expect(cards.length).toBe(1);
        cards = cards[0];
        var card_title = cards.getElementsByTagName('h3');
        expect(card_title.length).toBe(1);
        card_title = card_title[0];
        expect(card_title.textContent).toBe('16:16 01/12/2014');
        var card_table = cards.getElementsByTagName('table');
        expect(card_table.length).toBe(2); // there's a table inside the main table
        card_table = card_table[0];
        expect(card_table.hasChildNodes()).toBe(true);
        expect(card_table.getElementsByTagName('tr').length).toBe(9);
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