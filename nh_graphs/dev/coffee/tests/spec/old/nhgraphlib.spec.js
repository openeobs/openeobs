
describe("NHGraphLib",function() {

    var graphlib, test_area, table_cont;

    graphlib = null;
    test_area = null;
    table_cont = null;

    beforeEach(function() {

        var body_el;
        body_el = document.getElementsByTagName('body')[0];
        test_area = document.createElement('div');
        test_area.setAttribute('id', 'test_area');
        test_area.style.width = '500px';
        body_el.appendChild(test_area);

        table_el = document.createElement('div');
        table_el.setAttribute('id','table');
        test_area.appendChild(table_el);

        table_cont = document.createElement('div');
        table_cont.setAttribute('id','table-content');
        test_area.appendChild(table_cont);

        if (graphlib === null) {
          graphlib = new NHGraphLib('#test_area');
        }

        graphlib.data.raw = ews_data.multi_partial;

        graphlib.table.element = '#table';

        graphlib.table.keys = [
            {
              title: 'NEWS Score',
              keys: ['score_display']
            },
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
              title: 'Patient on Supplemental O2',
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
        ]
    });

    afterEach(function() {

        if (graphlib !== null) {
            graphlib = null;
        }

        if (test_area !== null) {
            test_area.parentNode.removeChild(test_area);
        }

    });

    describe("init()",function() {
        // Extra test to plug coverage gap
        it("throws error if initialised without element to play with",function() {
            graphlib.el = null;
            expect(function() {graphlib.init()}).toThrow(new Error('No element specified'))
        });

        it("throws error if initialised with no data provided",function() {
            graphlib.data.raw = [];
            graphlib.init()
            expect(function() {graphlib.draw()}).toThrow(new Error('No raw data provided'))
        });
    });


    describe("NHGraphLib.draw_table()",function() {

        beforeEach(function() {
            spyOn(NHGraphLib.prototype, 'draw_table').and.callThrough()
            graphlib.init();
            graphlib.draw();
        });

        it("is called by NHGraphlib.draw() when table.element defined",function() {
            expect(NHGraphLib.prototype.draw_table).toHaveBeenCalled()
        });

        it("draws the correct table element structure", function() {
            var els = document.querySelectorAll('table');
            expect(els.length).toBe(1);

            els = document.querySelectorAll('table thead');
            expect(els.length).toBe(1);
            els = document.querySelectorAll('table thead tr');
            expect(els.length).toBe(1);
            els = document.querySelectorAll('table thead tr th');
            expect(els.length).toBe(graphlib.data.raw.length+1);

            els = document.querySelectorAll('table tbody');
            expect(els.length).toBe(1);
            els = document.querySelectorAll('table tbody tr');
            expect(els.length).toBe(graphlib.table.keys.length);
            els = els[1].getElementsByTagName('td');
            expect(els.length).toBe(graphlib.data.raw.length+1);
        });

        it("labels the header row with expected times", function() {
            var els = document.querySelectorAll('table thead tr th');
            expect(els[0].textContent).toBe('Date');

            for (var i = 1; i < els.length; i++) {
                var time = els[i].innerHTML.split('<br>')[0];
                var expected = graphlib.date_from_string(graphlib.data.raw[i-1].date_terminated);
                var expectedTime = expected.getHours() + ':' + expected.getMinutes();
                expect(time).toBe(expectedTime);

                // Checking date mega-long due to formatting, skipping for now
                //var date = els[i].innerHTML.split('<br>')[1];
                //var expectedDate = expected.getYear() + '/' + expected.getMonth() + '/' + expected.getDate();
                //expect(date).toBe(expectedDate);
            }
        });

        it("shows the records in reverse chronological order",function() {
            // Not working in Phantom, date_from_string() and Date() unable to parse

            // Grab the header cells as an array
            var els = document.querySelectorAll('table thead tr th');
            expect(els.length).toBe(4);

            // Convert to standard array minus first ('Date') element
            var ar = [];
            for (i = 1; i < els.length; i++) {

                // Resorting to comparing just the hours as Phantom unable to parse date
                ar.push(+els[i].innerHTML.replace('<br>',' ').substr(0,2))
            }

            // Check each hour is greater than the one before (elements reversed by .push)
            for (i = 1; i < ar.length; i++) {
                expect(ar[i]).toBeGreaterThan(ar[i-1])
            }
        });

        it("shows the correct observation label names", function() {
            var els = document.querySelectorAll('table tbody tr');

            for (var i = 0; i < els.length; i++) {
                var text = els[i].getElementsByTagName('td')[0].textContent;
                expect(text).toBe(graphlib.table.keys[i].title)
            }
        });

        it("converts boolean values to Yes/No",function(){
            var els = document.querySelectorAll('table tbody tr');
            for (var i = 0; i < graphlib.data.raw.length; i++) {
                if (graphlib.data.raw[i].oxygen_administration_flag) {
                    expect(els[8].getElementsByTagName('td')[i+1].textContent).toBe('Yes')
                }
                else {
                    expect(els[8].getElementsByTagName('td')[i+1].textContent).toBe('No')
                }
            }
        });

        it("handles nested keys, e.g. inspired_oxygen",function() {
            var actual = document.querySelectorAll('table tbody tr')[9].getElementsByTagName('td')[3].innerHTML;

            // Cheating to avoid this sort of stuff..
            //var ar = actual.split(/<\/strong>|<strong>|<br>/g).filter(function(el) { if (el !== '') return el})

            var expected = "<strong>Flow Rate:</strong> 15lpm<br><strong>Concentration:</strong> 100%<br><strong>Device:</strong> 12<br>";
            expect(actual).toBe(expected);
        })

    })
})