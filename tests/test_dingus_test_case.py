import sys
import new

from dingus import DingusTestCase, Dingus


class WhenRunningTestCaseOnAModule(object):
    def setup(self):
        self.module = self._create_fake_module()
        self.class_under_test = self._create_class_under_test()
        self.test_case_class = self._create_test_case_class()

    def _create_fake_module(self):
        module = new.module('test_module')
        module.value = 'value'
        sys.modules[module.__name__] = module
        return module

    def _create_class_under_test(self):
        class ClassThatWouldBeUnderTest:
            pass
        ClassThatWouldBeUnderTest.__module__ = self.module.__name__
        self.module.ClassThatWouldBeUnderTest = ClassThatWouldBeUnderTest
        return ClassThatWouldBeUnderTest

    def _create_test_case_class(self):
        class TestCaseClass(DingusTestCase(self.class_under_test)):
            pass
        return TestCaseClass

    def teardown(self):
        del sys.modules[self.module.__name__]


class WhenCallingSetupFunction(WhenRunningTestCaseOnAModule):
    def setup(self):
        super(WhenCallingSetupFunction, self).setup()
        self.test_case_instance = self.test_case_class()
        self.test_case_instance.setup()

    def teardown(self):
        self.test_case_instance.teardown()
        super(WhenCallingSetupFunction, self).teardown()

    def should_replace_module_attributes(self):
        assert isinstance(self.module.value, Dingus)

    def should_leave_class_under_test_intact(self):
        assert self.module.ClassThatWouldBeUnderTest is self.class_under_test


class WhenCallingTeardownFunction(WhenRunningTestCaseOnAModule):
    def setup(self):
        super(WhenCallingTeardownFunction, self).setup()
        self.test_case_object = self.test_case_class()
        self.original_module_dict = self.module.__dict__.copy()
        self.test_case_object.setup()
        self.test_case_object.teardown()

    def should_restore_module_attributes(self):
        assert self.module.value is 'value'

    def should_leave_globals_as_they_were_before_dingusing(self):
        assert self.module.__dict__ == self.original_module_dict

