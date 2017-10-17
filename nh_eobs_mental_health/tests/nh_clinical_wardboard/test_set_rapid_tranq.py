# -*- coding: utf-8 -*-
from openerp.addons.nh_eobs.exceptions import StaleDataException
from openerp.tests.common import TransactionCase


start_called = False
complete_called = False
toggle_rapid_tranq_called = False


class TestSetRapidTranq(TransactionCase):

    def setUp(self):
        super(TestSetRapidTranq, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)
        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.rapid_tranq_model = self.env['nh.clinical.pme.rapid_tranq']

        self.wardboard = self.wardboard_model.browse(self.spell.id)

    def call_test(self, set_value=True, existing_value=False):
        if existing_value is True:
            # Manually start rapid tranq.
            rapid_tranq_activity = self.test_utils\
                .create_activity_rapid_tranq()
            rapid_tranq = rapid_tranq_activity.data_ref
            rapid_tranq_activity.state = 'started'
            rapid_tranq.spell.rapid_tranq = True
            self.assertTrue(self.spell.rapid_tranq)
        else:
            self.assertFalse(self.spell.rapid_tranq)

        self.wardboard.set_rapid_tranq(set_value)

    def test_toggle_rapid_tranq_does_not_raise_when_started(self):
        self.call_test()

    def test_toggle_rapid_tranq_does_not_raise_when_stopped(self):
        self.call_test(set_value=False, existing_value=True)

    def test_toggle_rapid_tranq_raises_when_already_started(self):
        with self.assertRaises(StaleDataException):
            self.call_test(existing_value=True)

    def test_toggle_rapid_tranq_raises_when_already_stopped(self):
        with self.assertRaises(StaleDataException):
            self.call_test(set_value=False)

    def test_toggle_rapid_tranq_not_called_when_already_started(self):
        global toggle_rapid_tranq_called
        toggle_rapid_tranq_called = False

        def mock_toggle_rapid_tranq(*args, **kwargs):
            global toggle_rapid_tranq_called
            toggle_rapid_tranq_called = True
            return mock_toggle_rapid_tranq.origin(*args, **kwargs)

        self.rapid_tranq_model._patch_method('toggle_rapid_tranq',
                                             mock_toggle_rapid_tranq)
        try:
            self.call_test(existing_value=True)
        except StaleDataException:
            pass
        finally:
            self.rapid_tranq_model._revert_method('toggle_rapid_tranq')

        # Assert truthy and boolean.
        self.assertIs(toggle_rapid_tranq_called, False)

    def test_toggle_rapid_tranq_not_called_when_already_stopped(self):
        global toggle_rapid_tranq_called
        toggle_rapid_tranq_called = False

        def mock_toggle_rapid_tranq(*args, **kwargs):
            global toggle_rapid_tranq_called
            toggle_rapid_tranq_called = True
            return mock_toggle_rapid_tranq.origin(*args, **kwargs)

        self.rapid_tranq_model._patch_method('toggle_rapid_tranq',
                                             mock_toggle_rapid_tranq)
        try:
            self.call_test(set_value=False, existing_value=False)
        except StaleDataException:
            pass
        finally:
            self.rapid_tranq_model._revert_method('toggle_rapid_tranq')

        # Assert truthy and boolean.
        self.assertIs(toggle_rapid_tranq_called, False)

    def test_toggle_rapid_tranq_called_when_started(self):
        global toggle_rapid_tranq_called
        toggle_rapid_tranq_called = False

        def mock_toggle_rapid_tranq(*args, **kwargs):
            global toggle_rapid_tranq_called
            toggle_rapid_tranq_called = True
            return mock_toggle_rapid_tranq.origin(*args, **kwargs)

        self.rapid_tranq_model._patch_method('toggle_rapid_tranq',
                                             mock_toggle_rapid_tranq)
        try:
            self.call_test()
        finally:
            self.rapid_tranq_model._revert_method('toggle_rapid_tranq')

        # Assert truthy and boolean.
        self.assertIs(toggle_rapid_tranq_called, True)

    def test_toggle_rapid_tranq_called_when_stopped(self):
        global toggle_rapid_tranq_called
        toggle_rapid_tranq_called = False

        def mock_toggle_rapid_tranq(*args, **kwargs):
            global toggle_rapid_tranq_called
            toggle_rapid_tranq_called = True
            return mock_toggle_rapid_tranq.origin(*args, **kwargs)

        self.rapid_tranq_model._patch_method('toggle_rapid_tranq',
                                             mock_toggle_rapid_tranq)
        try:
            self.call_test(set_value=False, existing_value=True)
        finally:
            self.rapid_tranq_model._revert_method('toggle_rapid_tranq')

        # Assert truthy and boolean.
        self.assertIs(toggle_rapid_tranq_called, True)

    def test_calls_start_on_rapid_tranq_when_started(self):
        global start_called
        start_called = False

        def mock_start(*args, **kwargs):
            global start_called
            start_called = True
            return mock_start.origin(*args, **kwargs)

        self.rapid_tranq_model._patch_method('start', mock_start)

        try:
            self.call_test(set_value=True, existing_value=False)
        finally:
            self.rapid_tranq_model._revert_method('start')

        self.assertIs(start_called, True)  # Assert truthy and boolean.

    def test_calls_complete_on_rapid_tranq_when_stopped(self):
        global complete_called
        complete_called = False

        def mock_complete(*args, **kwargs):
            global complete_called
            complete_called = True
            return mock_complete.origin(*args, **kwargs)

        self.rapid_tranq_model._patch_method('complete', mock_complete)

        try:
            self.call_test(set_value=False, existing_value=True)
        finally:
            self.rapid_tranq_model._revert_method('complete')

        self.assertIs(complete_called, True)  # Assert truthy and boolean.

    def test_does_not_call_start_on_rapid_tranq_when_already_started(self):
        global start_called
        start_called = False

        def mock_start(*args, **kwargs):
            global start_called
            start_called = True
            return mock_start.origin(*args, **kwargs)

        self.rapid_tranq_model._patch_method('start', mock_start)

        try:
            self.call_test(existing_value=True)
        except StaleDataException:
            pass
        finally:
            self.rapid_tranq_model._revert_method('start')

        self.assertIs(start_called, False)  # Assert truthy and boolean.

    def test_does_not_call_complete_on_rapid_tranq_when_already_stopped(self):
        global complete_called
        complete_called = False

        def mock_complete(*args, **kwargs):
            global complete_called
            complete_called = True
            return mock_complete.origin(*args, **kwargs)

        self.rapid_tranq_model._patch_method('complete', mock_complete)

        try:
            self.call_test(set_value=False, existing_value=False)
        except StaleDataException:
            pass
        finally:
            self.rapid_tranq_model._revert_method('complete')

        self.assertIs(complete_called, False)  # Assert truthy and boolean.
