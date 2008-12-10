import operator
from functools import partial

from nose.tools import assert_raises

from dingus import Dingus


class WhenCreatingNewDingus:
    def setup(self):
        self.dingus = Dingus()

    def should_not_have_any_recorded_calls(self):
        assert not self.dingus.calls()

    def should_have_a_name(self):
        assert self.dingus.__name__ == 'dingus_%i' % id(self.dingus)


class WhenCallingDingusAsFunction:
    def setup(self):
        self.dingus = Dingus()
        self.dingus('arg', kwarg=None)

    def should_record_call(self):
        assert self.dingus.calls()

    def should_have_exactly_one_call(self):
        assert self.dingus.calls().one()

    def should_record_args(self):
        assert self.dingus.calls.one().args == ('arg',)

    def should_record_kwargs(self):
        assert self.dingus.calls.one().kwargs == {'kwarg': None}


class WhenCallingAttributeChild:
    def setup(self):
        self.parent = Dingus()
        self.child = self.parent.child
        self.child('arg', kwarg=None)

    def should_record_call_on_child(self):
        assert self.child.calls.one()

    def should_record_call_on_parent(self):
        assert self.parent.calls('child').one()

    def should_record_args(self):
        assert self.parent.calls('child').one().args == ('arg',)

    def should_record_kwargs(self):
        assert self.parent.calls('child').one().kwargs == {'kwarg': None}


class WhenCallingAttributeGrandchild:
    def setup(self):
        self.grandparent = Dingus()
        self.parent = self.grandparent.parent
        self.child = self.parent.child
        self.child('arg', kwarg=None)

    def should_record_call_on_grandparent(self):
        assert self.grandparent.calls('parent.child').one()

    def should_record_call_on_parent(self):
        assert self.parent.calls('child').one()


class WhenCallingAttributesOfReturnedValues:
    def setup(self):
        self.grandparent = Dingus()
        self.parent = self.grandparent()
        self.child = self.parent.child
        self.child('arg', kwarg=None)

    def should_record_call_on_grandparent(self):
        assert self.grandparent.calls('()').one()

    def should_record_child_call_on_child(self):
        assert self.child.calls('()').one()

    def should_record_child_call_on_parent(self):
        assert self.parent.calls('child').one()

    def should_record_child_call_on_grandparent(self):
        assert self.grandparent.calls('().child').one()


class WhenCallingItemChild:
    def should_record_call(self):
        parent = Dingus()
        parent['child']()
        assert parent.calls('[child]').one()


class WhenCallingItemGrandchild:
    def should_record_call_on_grandparent(self):
        grandparent = Dingus()
        grandparent['parent']['child']()
        assert grandparent.calls('[parent][child]')


class WhenCallingListItemOfDingus:
    def setup(self):
        self.parent = Dingus()
        self.child = self.parent[0]
        self.child()

    def should_record_call_on_parent(self):
        assert self.parent.calls('[0]').one()

    def should_record_call_on_child(self):
        assert self.child.calls('()').one()


class WhenAccessingMagicAttributes:
    def should_raise_attribute_error_for_pyobjc_object(self):
        # PyObjC uses __pyobjc_object__ to get an ObjC object from a Python
        # object. Returning a Mock will cause a crash.
        assert_raises(AttributeError, lambda: Dingus().__pyobjc_object__)


class WhenApplyingBinaryOperators:
    operator_names = ['add', 'and_', 'div', 'lshift', 'mod', 'mul', 'or_',
                      'pow', 'rshift', 'sub', 'xor']

    def assert_returns_new_dingus(self, op):
        left, right = Dingus.many(2)
        result = op(left, right)
        assert result is not left and result is not right

    def should_always_return_new_dingus(self):
        for operator_name in self.operator_names:
            op = getattr(operator, operator_name)
            yield self.assert_returns_new_dingus, op


class WhenComputingLength:
    def should_be_one(self):
        assert len(Dingus()) == 1


class WhenAccessingReturnValueBeforeCalling:
    def setup(self):
        self.dingus = Dingus()

    def should_have_return_value_before_calling(self):
        assert self.dingus.return_value

    def should_return_same_return_value_that_existed_before_calling(self):
        original_return_value = self.dingus.return_value
        return_value = self.dingus()
        assert return_value is original_return_value

    def should_have_same_return_value_before_and_after_calling(self):
        original_return_value = self.dingus.return_value
        self.dingus()
        assert self.dingus.return_value is original_return_value


class WhenSettingReturnValue:
    def setup(self):
        self.dingus = Dingus()
        self.return_value = 5
        self.dingus.return_value = self.return_value

    def should_return_assigned_return_value(self):
        assert self.dingus() is self.return_value

    def should_have_same_return_value_after_calling(self):
        self.dingus()
        assert self.dingus.return_value is self.return_value


class WhenSettingAttributes:
    def setup(self):
        self.dingus = Dingus()
        self.attr = Dingus()
        self.dingus.attr = self.attr

    def should_remember_attr(self):
        assert self.dingus.attr is self.attr

    def should_not_return_attributes_as_items(self):
        assert self.dingus['attr'] is not self.attr

    def should_return_distinct_dinguses_for_different_attributes(self):
        assert self.dingus['attr'] is not self.dingus['attr2']


class WhenAccessingItems:
    def should_log_access(self):
        dingus = Dingus()
        dingus['item']
        assert dingus.calls('__getitem__', 'item').one()

    def should_log_access_after_initial_item_read(self):
        dingus = Dingus()
        for _ in range(2):
            dingus['item']
        assert len(dingus.calls('__getitem__', 'item')) == 2


class WhenSettingItems:
    def setup(self):
        self.dingus = Dingus()
        self.item = Dingus()
        self.dingus['item'] = self.item

    def should_remember_item(self):
        assert self.dingus['item'] is self.item

    def should_log_access(self):
        assert self.dingus.calls('__setitem__', 'item', self.item).one()

    def should_not_return_items_as_attributes(self):
        assert self.dingus.item is not self.item

    def should_return_distinct_dinguses_for_different_items(self):
        assert self.dingus['item'] is not self.dingus['item2']


class WhenNothingIsSet:
    def setup(self):
        self.attribute_name = 'attr'
        self.dingus = Dingus()

    def should_be_able_to_access_attributes_that_dont_exist(self):
        assert isinstance(getattr(self.dingus, self.attribute_name), Dingus)

    def should_get_same_attribute_on_every_access(self):
        get_attr = lambda: getattr(self.dingus, self.attribute_name)
        assert get_attr() is get_attr()

    def should_be_able_to_acces_items_that_dont_exist(self):
        assert isinstance(self.dingus[self.attribute_name], Dingus)

    def should_get_same_item_on_every_access(self):
        get_item = lambda: self.dingus[self.attribute_name]
        assert get_item() is get_item()

    def should_have_attributes_that_have_not_been_set(self):
        assert hasattr(self.dingus, self.attribute_name)


class WhenSpecifyingAttributesViaKeywordArguments:
    def should_set_specified_attributes(self):
        attr = Dingus()
        object_with_attr = Dingus(attr=attr)
        assert object_with_attr.attr is attr


class WhenCallingInitMethod:
    def should_record_call(self):
        dingus = Dingus()
        dingus.__init__()
        assert dingus.calls('__init__').one()


class WhenCreatingMultipleDinguses:
    def should_return_a_dingus_when_asked_for_one(self):
        assert len(Dingus.many(1)) == 1

    def should_return_two_dinguses_when_asked_for_two(self):
        assert len(Dingus.many(2)) == 2

    def should_return_dingus_instances_when_asked_for_multiple(self):
        assert all(isinstance(dingus, Dingus) for dingus in Dingus.many(2))

    def should_return_dinguses_in_tuple(self):
        assert isinstance(Dingus.many(2), tuple)

    def should_return_nothing_when_asked_for_zero_dinguses(self):
        assert not Dingus.many(0)

