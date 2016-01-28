openerp.testing.section('nh_eobs.Logout - auto logout feature', function (test) {

    test("'click' event listener",
        {asserts: 1},
        function(instance) {

            instance.web_kanban(instance);
            instance.nh_eobs(instance);
            var log = sinon.spy(instance.nh_eobs.Logout, 'reset');

            var body_el;
            body_el = document.getElementsByTagName('body')[0];
            test_area = document.createElement('div');
            body_el.appendChild(test_area);
            $(test_area).click();

            ok(log.called, "should be called by 'click' event");
            instance.nh_eobs.Logout.reset.restore();
        }
    );

    test("nh_eobs.Logout - initial values",
        {asserts: 2},
        function(instance) {

            instance.web_kanban(instance);
            instance.nh_eobs(instance);
            var log = instance.nh_eobs.Logout;

            equal(log.default, 1200000, "defaults to 20 minute interval");
            ok(log.ref, "timer should be set");
        }
    );

    test("nh_eobs.Logout - reset()",
        {asserts: 3},
        function(instance) {

            instance.web_kanban(instance);
            instance.nh_eobs(instance);
            var spy = sinon.spy(window, 'setTimeout');
            var log = instance.nh_eobs.Logout;

            log.reset();

            ok(spy.called, 'should call window.setTimeout');
            equal(spy.args[0][1], 1190000, 'should set timeout with default time 1200000 - 10000');
            equal(typeof log.ref, 'number', "logout.timer should contain id of setTimeout");

            window.setTimeout.restore();
            if (log.ref) window.clearTimeout(log.ref)
        }
    );

    test("nh_eobs.Logout - reset(15000)",
        {asserts: 3},
        function(instance) {

            instance.web_kanban(instance);
            instance.nh_eobs(instance);
            var spy = sinon.spy(window, 'setTimeout');
            var log = instance.nh_eobs.Logout;

            log.reset(15000);

            ok(spy.called, 'should call window.setTimeout');
            equal(spy.args[0][1], 5000, 'should setTimeout with interval of 5000');
            equal(typeof log.ref, 'number', "logout.timer should contain id of setInterval");

            window.setTimeout.restore();
            if (log.ref) window.clearTimeout(log.ref)
        }
    );

    test("nh_eobs.Logout - displays logout warning and sets new 10s timeout",
        {asserts: 3},
        function(instance) {
            var clock = sinon.useFakeTimers();
            var step = $.Deferred();

            instance.web_kanban(instance);
            instance.nh_eobs(instance);
            var spy = sinon.spy(window, 'setTimeout');
            var log = instance.nh_eobs.Logout;
            log.reset(15000);

            clock.tick(6000);
            ok($(".ui-notify:contains('inactivity')"), "Should display warning notification");
            equal(typeof log.ref, 'number', "logout.timer should contain id of setInterval");
            equal(spy.args[1][1], 10000, 'should setTimeout with interval of 10,500');

            window.setTimeout.restore();
            if (log.ref) window.clearTimeout(log.ref);
            clock.restore();
            return step.resolve()
        }
    );

    test("nh_eobs.Logout - calls openerp.session.logout()",
        {asserts: 2},
        function(instance) {

            instance.web_kanban(instance);
            instance.nh_eobs(instance);
            var spy = sinon.spy(openerp.session, 'logout');
            var log = instance.nh_eobs.Logout;

            log.reset(100);

            ok(spy.called, 'should call openerp.session.logout()');

            openerp.session.restore();
            if (log.ref) window.clearInterval(log.timer)
        }
    );
});