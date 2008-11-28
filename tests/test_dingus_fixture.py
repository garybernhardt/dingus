import sys
import new

from dingus import DingusFixture, Dingus


class WhenRunningFixtureOnAModule(object):
    def setup(self):
        self.module = self._create_fake_module()
        self.class_under_test = self._create_class_under_test()
        self.fixture_class = self._create_fixture_class()

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

    def _create_fixture_class(self):
        class FixtureClass(DingusFixture(self.class_under_test)):
            pass
        return FixtureClass

    def teardown(self):
        del sys.modules[self.module.__name__]


class WhenCallingSetupFunction(WhenRunningFixtureOnAModule):
    def should_replace_module_attributes(self):
        self.fixture_class().setup()
        assert isinstance(self.module.value, Dingus)


class WhenCallingTeardownFunction(WhenRunningFixtureOnAModule):
    def setup(self):
        super(WhenCallingTeardownFunction, self).setup()
        self.fixture_object = self.fixture_class()
        self.original_module_dict = self.module.__dict__.copy()
        self.fixture_object.setup()
        self.fixture_object.teardown()

    def should_restore_module_attributes(self):
        assert self.module.value is 'value'

    def should_leave_globals_as_they_were_before_fixture(self):
        assert self.module.__dict__ == self.original_module_dict

