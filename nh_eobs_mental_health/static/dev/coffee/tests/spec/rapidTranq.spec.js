function getRapidTranqButton(){
    return document.getElementById('toggle-rapid-tranq');
}

function pressRapidTranqButton(){
    var toggleButton = getRapidTranqButton();
    var clickEvent = document.createEvent('CustomEvent');
    clickEvent.initCustomEvent('click', false, true, false);
    toggleButton.dispatchEvent(clickEvent);
}

function setRapidTranqButtonValue(value){
    var button = getRapidTranqButton();
    button.setAttribute('data-state-to-set', value);
}

function confirmRapidTranqChange(){
    var popup = document.getElementById('rapid_tranq_check');
    var submitButton = popup.getElementsByTagName('a')[1];
    var clickEvent = document.createEvent('CustomEvent');
    clickEvent.initCustomEvent('click', false, true, false);
    submitButton.dispatchEvent(clickEvent);
}

describe("Rapid Tranquilisation Button", function(){
    var patient;
    beforeEach(function(){
        var bodyEl = document.getElementsByTagName("body")[0];
        var test = document.getElementById("test");
        if (test != null) {
            test.parentNode.removeChild(test);
        }
        var testArea = document.createElement("div");
        testArea.setAttribute("id", "test");
        testArea.style.height = "500px";
        testArea.innerHTML = '<a class="patientInfo" href="#" id="obsButton">' +
                '<h3 class="name"><strong>Test Patient</strong></h3></a>' +
                '<button id="take-observation">Take Observation</button>' +
                "<button id=\"toggle-rapid-tranq\" class=\"full-width big dont-do-it\" data-state-to-set=\"true\">Start Rapid Tranquilisation</button>" +
                '<ul id="obsMenu"><li><a>Obs one</a></li><li><a>Obs two</a></li></ul>' +
                '<select name="chart_select" id="chart_select">' +
                '<option value="ews" selected="selected">NEWS</option>' +
                '<option value="neuro">Neurological observation</option>' +
                '</select>' +
                '<ul class="two-col tabs">' +
                '<li><a href="#graph-content" class="selected tab">Graph</a></li>' +
                '<li><a href="#table-content" class="tab">Table</a></li>' +
                '</ul>' +
                '<div id="graph-content" data-id="1">' +
                '<div id="controls">' +
                '<div id="start">' +
                '<h4>Start date</h4>' +
                '<label for="start_date">' +
                'Date: <input type="date" name="start_date" id="start_date"/>' +
                '</label>' +
                '<label for="start_time">' +
                'Time: <input type="time" name="start_time" id="start_time"/>' +
                '</label>' +
                '</div>' +
                '<div id="end">' +
                '<h4>End date</h4>' +
                '<label for="end_date">' +
                'Date: <input type="date" name="end_date" id="end_date"/>' +
                '</label>' +
                '<label for="end_time">' +
                'Time: <input type="time" name="end_time" id="end_time"/>' +
                '</label>' +
                '</div>' +
                '<div id="range">' +
                '<label for="rangify">' +
                '<h4>Ranged values</h4> <input type="checkbox" name="rangify" id="rangify"/>' +
                '</label>' +
                '</div>' +
                '</div>' +
                '<div id="chart"></div>' +
                '</div>' +
                '<div id="table-content"></div>';
        bodyEl.appendChild(testArea);
        var dialogs = document.getElementsByClassName("dialog");
        for(var i = 0; i < dialogs.length; i++){
            var dialog = dialogs[i];
            dialog.parentNode.removeChild(dialog);
        }
        var covers = document.getElementsByClassName("cover");
        for(var j = 0; j < covers.length; j++){
            var cover = covers[j];
            cover.parentNode.removeChild(cover);
        }
        patient = new window.NH.NHMobilePatient();
    });

    afterEach(function () {
        var test = document.getElementById("test");
        if (test != null) {
            test.parentNode.removeChild(test);
        }
        if(patient != null){
            patient = null;
        }
        var fullScreenModals = document.getElementsByClassName("full-modal");
        for(var i = 0; i < fullScreenModals.length; i++){
            var modal = fullScreenModals[i];
            modal.parentNode.removeChild(modal);
        }
    });

    it("adds event listener to Rapid Tranquilisation Button on init", function(){
        spyOn(NHMobilePatientMentalHealth.prototype, 'checkRapidTranqStatus');
        pressRapidTranqButton();
        expect(NHMobilePatientMentalHealth.prototype.checkRapidTranqStatus).toHaveBeenCalled();
    });
    describe("Pressing Rapid Tranquilisation Button", function(){
        beforeEach(function(){
            setRapidTranqButtonValue('true');
            spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
            spyOn(NHMobilePatientMentalHealth.prototype, 'checkRapidTranqStatus').and.callThrough();
            spyOn(NHMobilePatientMentalHealth.prototype, 'process_request').and.callFake(function(){
                var request = NHMobilePatientMentalHealth.prototype.process_request.calls.mostRecent().args[1];
                var promise = new Promise();
                var returnedResponse = null;
                if(request.indexOf('?check=true') > -1){
                    returnedResponse = new NHMobileData({
                        status: 'success',
                        title: 'Confirm Action',
                        description: 'Confirm you want to set patient\'s rapid tranquilisation status to true',
                        data: {
                            rapid_tranq: true
                        }
                    });
                }else {
                    returnedResponse = new NHMobileData({
                        status: 'fail',
                        title: 'Action already taken',
                        description: 'The patient\'s rapid tranquilisation status has already been set to false, please reload your page',
                        data: {
                            rapid_tranq: false
                        }
                    });
                }
                promise.complete(returnedResponse);
                return promise;
            });
        });
        afterEach(function(){
           cleanUp();
        });
        it("Shows confirmation message if able to change status", function(){
            pressRapidTranqButton();
            expect(NHMobilePatientMentalHealth.prototype.process_request).toHaveBeenCalled();
            expect(NHMobilePatientMentalHealth.prototype.process_request.calls.mostRecent().args[0]).toBe('GET');
            expect(NHMobilePatientMentalHealth.prototype.process_request.calls.mostRecent().args[1]).toBe('http://localhost:8069/mobile/patient/1/rapid_tranq?check=true');
            expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
            expect(NHModal.prototype.create_dialog.calls.mostRecent().args[4][0]).toBe("<a href=\"#\" data-action=\"close\" data-target=\"rapid_tranq_check\">Cancel</a>");
            expect(NHModal.prototype.create_dialog.calls.mostRecent().args[4][1]).toBe("<a href=\"#\" data-action=\"confirm_submit\" data-target=\"rapid_tranq_check\">Confirm</a>");
        });
        it("Shows warning message if status has been changed by another user", function(){
            setRapidTranqButtonValue('false');
            pressRapidTranqButton();
            expect(NHMobilePatientMentalHealth.prototype.process_request).toHaveBeenCalled();
            expect(NHMobilePatientMentalHealth.prototype.process_request.calls.mostRecent().args[0]).toBe('GET');
            expect(NHMobilePatientMentalHealth.prototype.process_request.calls.mostRecent().args[1]).toBe('http://localhost:8069/mobile/patient/1/rapid_tranq?check=false');
            expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
            expect(NHModal.prototype.create_dialog.calls.mostRecent().args[4][0]).toBe("<a href=\"#\" data-action=\"close_reload\" data-target=\"rapid_tranq_check\">Reload</a>");
        });
    });
    describe("Reloading page after being shown warning message", function(){
        beforeEach(function(){
           setRapidTranqButtonValue('true');
           spyOn(NHModal.prototype, 'reloadPage');
           spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
           spyOn(NHMobilePatientMentalHealth.prototype, 'process_request').and.callFake(function(){
                var promise = new Promise();
                var returnedResponse = new NHMobileData({
                    status: 'fail',
                    title: 'Action already taken',
                    description: 'The patient\'s rapid tranquilisation status has already been set to false, please reload your page',
                    data: {
                        rapid_tranq: false
                    }
                });
                promise.complete(returnedResponse);
                return promise;
            });
        });

        afterEach(function(){
           cleanUp();
        });

        it("Reloads page when pressing \"Reload\" button", function(){
            pressRapidTranqButton();
            var popup = document.getElementById('rapid_tranq_check');
            var closeButton = popup.getElementsByTagName('a')[0];
            var clickEvent = document.createEvent('CustomEvent');
            clickEvent.initCustomEvent('click', false, true, false);
            closeButton.dispatchEvent(clickEvent);
            expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
            expect(NHModal.prototype.reloadPage).toHaveBeenCalled();
        });
        it("Reloads page when pressing greyed out background for button", function(){
            pressRapidTranqButton();
            var cover = document.getElementsByClassName('cover')[0];
            var clickEvent = document.createEvent('CustomEvent');
            clickEvent.initCustomEvent('click', false, true, false);
            cover.dispatchEvent(clickEvent);
            expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
            expect(NHModal.prototype.reloadPage).toHaveBeenCalled();
        });
    });
    describe("Changing Rapid Tranquilisation status after confirming", function(){
        beforeEach(function(){
           setRapidTranqButtonValue('true');
           spyOn(NHMobilePatientMentalHealth.prototype, 'submitRapidTranqChange').and.callThrough();
           spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
           spyOn(NHModal.prototype, 'close_modal').and.callThrough();
           spyOn(NHMobilePatientMentalHealth.prototype, 'process_request').and.callFake(function(){
                var verb = NHMobilePatientMentalHealth.prototype.process_request.calls.mostRecent().args[0];
                var data = NHMobilePatientMentalHealth.prototype.process_request.calls.mostRecent().args[2];
                var promise = new Promise();
                var returnedResponse = new NHMobileData({
                    status: 'success',
                    title: '',
                    description: '',
                    data: {
                        rapid_tranq: false
                    }
                });
                if(verb === 'POST') {
                    if(data === '?check=true'){
                        returnedResponse.data.rapid_tranq = true;
                    }
                }
                promise.complete(returnedResponse);
                return promise;
            });
        });

        afterEach(function(){
           cleanUp();
        });

        it("Calls the server to change the status", function(){
            pressRapidTranqButton();
            confirmRapidTranqChange();
            expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
            expect(NHMobilePatientMentalHealth.prototype.submitRapidTranqChange).toHaveBeenCalled();
            expect(NHModal.prototype.close_modal).toHaveBeenCalled();
        });
        it("Changes Rapid Tranquilisation from inactive to active", function(){
            setRapidTranqButtonValue('true');
            pressRapidTranqButton();
            confirmRapidTranqChange();
            expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
            expect(NHMobilePatientMentalHealth.prototype.submitRapidTranqChange).toHaveBeenCalled();
            expect(NHModal.prototype.close_modal).toHaveBeenCalled();
            var toggleButton = getRapidTranqButton();
            expect(toggleButton.innerText).toBe('Stop Rapid Tranquilisation');
            expect(toggleButton.getAttribute('data-state-to-set')).toBe('false');
            expect(toggleButton.classList.contains('white-on-black')).toBe(true);
        });
        it("Changes Rapid Tranquilisation from active to inactive", function(){
            setRapidTranqButtonValue('false');
            pressRapidTranqButton();
            confirmRapidTranqChange();
            expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
            expect(NHMobilePatientMentalHealth.prototype.submitRapidTranqChange).toHaveBeenCalled();
            expect(NHModal.prototype.close_modal).toHaveBeenCalled();
            var toggleButton = getRapidTranqButton();
            expect(toggleButton.innerText).toBe('Start Rapid Tranquilisation');
            expect(toggleButton.getAttribute('data-state-to-set')).toBe('true');
            expect(toggleButton.classList.contains('dont-do-it')).toBe(true);
        });
    });
});