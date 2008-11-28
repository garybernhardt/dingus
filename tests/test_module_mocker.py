import sys
import new

from dingus import ModuleMocker, Mock


class WhenMockingAModule(object):
    def setup(self):
        self.module = self._create_fake_module()
        self.class_under_test = self._create_class_under_test()
        self.mocking_class = self._create_mocking_class()

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

    def _create_mocking_class(self):
        class MockingClass(ModuleMocker(self.class_under_test)):
            pass
        return MockingClass

    def teardown(self):
        del sys.modules[self.module.__name__]


class WhenCallingSetupFunction(WhenMockingAModule):
    def should_mock_module_attributes(self):
        self.mocking_class().setup()
        assert isinstance(self.module.value, Mock)


class WhenCallingTeardownFunction(WhenMockingAModule):
    def setup(self):
        super(WhenCallingTeardownFunction, self).setup()
        self.mocking_object = self.mocking_class()
        self.original_module_dict = self.mocking_object.__dict__.copy()
        self.mocking_object.setup()
        self.mocking_object.teardown()

    def should_unmock_module_attributes(self):
        assert self.module.value is 'value'

    def should_leave_globals_as_they_were_before_mock(self):
        assert self.mocking_object.__dict__ == self.original_module_dict

