describe('NHMobileShare', function() {
    var mobile, test_area;
    var patient_info_data = [
        {
            'full_name': 'Test Patient',
            'gender': 'M',
            'dob': '1988-01-12 00:00',
            'location': 'Bed 1',
            'parent_location': 'Ward 1',
            'ews_score': 1,
            'other_identifier': '012345678',
            'patient_identifier': 'NHS012345678',
            'activities': [
                {
                    'display_name': 'NEWS Observation',
                    'id': 1,
                    'time': 'Overdue: 00:10 hours'
                },
                {
                    'display_name': 'Inform Medical Team',
                    'id': 2,
                    'time': ''
                }
            ]
        }
    ];

    beforeEach(function () {
        // set up the DOM for test
        var body_el = document.getElementsByTagName('body')[0];
        var test = document.getElementById('test');
        if (test != null) {
            test.parentNode.removeChild(test);
        }
        test_area = document.createElement('div');
        test_area.setAttribute('id', 'test');
        test_area.style.height = '500px';
        test_area.innerHTML = '<div class="header">' +
            '<div class="header-main block">' +
            '<img src="/mobile/src/img/logo.png" class="logo">' +
            '<ul class="header-meta">' +
            '<li><a href="#" class="button share">Share</a></li>' +
            '<li class="logout"><a href="/mobile/logout/" class="button back">Logout</a></li>' +
            '</ul></div>' +
            '<ul class="header-menu two-col">' +
            '<li><a href="/mobile/tasks/" id="taskNavItem" class="selected">Tasks</a></li>' +
            '<li><a href="/mobile/patients/" id="patientNavItem">My Patients</a></li>' +
            '</ul></div>'+
            '<div class="content">'+
            '<ul class="tasklist">'+
            '<li>' +
            '<input type="checkbox" name="patient_share_74" class="patient_share_checkbox"/>'+
            '<a href="/mobile/patient/74" class="level-none block">' +
            '<div class="task-meta">' +
            '<div class="task-right">' +
            '<p class="aside">overdue: 17:01 hours</p>' +
            ' </div>' +
            '<div class="task-left">' +
            '<strong>Rodriguez, Audrina </strong> ( <i class="icon-none-arrow"></i>)<br>' +
            ' <em>Bed 05,Ward A</em>' +
            '</div>' +
            '</div>' +
            '<div class="task-meta">' +
            '<p class="taskInfo"><br></p>' +
            '</div>' +
            '</a>' +
            '</li><li>' +
            '<input type="checkbox" name="patient_share_73" class="patient_share_checkbox"/>'+
            '<a href="/mobile/patient/73" class="level-none block">' +
            '<div class="task-meta">' +
            '<div class="task-right">' +
            '<p class="aside">overdue: 17:01 hours</p>' +
            '</div>' +
            ' <div class="task-left">' +
            '<strong>Kreiger, Concha </strong> ( <i class="icon-none-arrow"></i>)<br>' +
            '<em>Bed 06,Ward A</em>' +
            '</div>' +
            '</div>' +
            '<div class="task-meta">' +
            '<p class="taskInfo"><br></p>' +
            '</div>' +
            '</a>' +
            '</li><li>' +
            '<input type="checkbox" name="patient_share_73" class="patient_share_checkbox"/>'+
            '<a href="/mobile/patient/75" class="level-none block">' +
            '<div class="task-meta">' +
            '<div class="task-right">' +
            '<p class="aside">overdue: 17:01 hours</p>' +
            '</div>' +
            '<div class="task-left">' +
            '<strong>Stokes, Josue </strong> ( <i class="icon-none-arrow"></i>)<br>' +
            '<em>Bed 07,Ward A</em>' +
            '</div>' +
            '</div>' +
            '<div class="task-meta">' +
            '<p class="taskInfo"><br></p>' +
            '</div>' +
            '</a>' +
            '</li><li>' +
            '<input type="checkbox" name="patient_share_76" class="patient_share_checkbox"/>'+
            '<a href="/mobile/patient/76" class="level-two block">' +
            '<div class="task-meta">' +
            '<div class="task-right">' +
            '<p class="aside">overdue: 16:15 hours</p>' +
            '</div>' +
            '<div class="task-left">' +
            '<strong>Crooks, Montgomery </strong> (5 <i class="icon-first-arrow"></i>)<br>' +
            '<em>Bed 09,Ward A</em>' +
            '</div>' +
            '</div>' +
            '<div class="task-meta">' +
            '<p class="taskInfo"><br></p>' +
            '</div>' +
            '</a>' +
            '</li>'+
            '</ul>' +
            '</div>';
        body_el.appendChild(test_area);
        if (mobile == null) {
            trigger_button = test_area.getElementsByClassName('share')[0];
            mobile = new NHMobileShare(trigger_button);
        }
    });

    afterEach(function () {
        if (mobile != null) {
            mobile = null;
        }
        var test = document.getElementById('test');
        if (test != null) {
            test.parentNode.removeChild(test);
        }
//        var covers = document.getElementsByClassName('cover');
//        var dialog = document.getElementById('patient_share');
        var body = document.getElementsByTagName('body')[0];
//        for (var i = 0; i < covers.length; i++) {
//            var cover = covers[i];
//            body.removeChild(cover);
//        }
//        if (dialog) {
//            body.removeChild(dialog);
//        }
    });

    it('Creates a click event listener on share button', function(){
    	spyOn(NHMobileShare.prototype, 'share_button_click');
    	var share_button = test_area.getElementsByClassName('share')[0];
    	// fire a click event at the scan button
    	var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        share_button.dispatchEvent(click_event);
    	// test is fires the appropriate function
    	expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
    });

    it('All checkboxes are hidden on initial load', function(){
        var checkboxes = document.getElementsByClassName('patient_share_checkbox');
        for(var i = 0; i < checkboxes.length; i++){
            var checkbox = checkboxes[i];
            expect(window.getComputedStyle(checkbox).display).toBe('none');
        }
    });

    it('On pressing share button the checkboxes are shown', function(){
        spyOn(NHMobileShare.prototype, 'share_button_click').andCallThrough();
    	var share_button = test_area.getElementsByClassName('share')[0];
    	// fire a click event at the scan button
    	var click_event = document.createEvent('CustomEvent');
        click_event.initCustomEvent('click', false, true, false);
        share_button.dispatchEvent(click_event);
    	// test is fires the appropriate function
    	expect(NHMobileShare.prototype.share_button_click).toHaveBeenCalled();
        var list = document.getElementsByClassName('tasklist')[0];
        var list_items = list.getElementsByTagName('li');
        for(var j = 0; j < list_items.length; j++){
            var list_item = list_items[j];
            expect(list_item.classList.contains('patient_share_active')).toBe(true);
            var list_item_link = list_item.getElementsByClassName('block')[0];
            var checkbox = list_item.getElementsByClassName('patient_share_checkbox')[0];
            expect(window.getComputedStyle(checkbox).display).toBe('block');
        }
    });

    it('On pressing share button the list of available nurses is fetched', function(){
       expect(false).toBe(true);
    });

});