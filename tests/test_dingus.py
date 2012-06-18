import operator
import pickle
import copy

from nose.tools import assert_raises

from dingus import Dingus, patch


class WhenCreatingNewDingus(object):
    def setup(self):
        self.dingus = Dingus()

    def should_not_have_any_recorded_calls(self):
        assert not self.dingus.calls()

    def should_have_a_name(self):
        assert self.dingus.__name__ == 'dingus_%i' % id(self.dingus)


class WhenCreatingNewDingusWithAName(object):
    def setup(self):
        self.dingus = Dingus('something')

    def should_have_a_name(self):
        assert self.dingus.__name__ == 'something'

    def should_include_name_in_repr(self):
        assert repr(self.dingus) == '<Dingus something>'

    def should_include_attribute_name_in_childrens_repr(self):
        assert repr(self.dingus.child) == '<Dingus something.child>'

    def should_include_attribute_name_in_repr_of_children_from_calling(self):
        assert repr(self.dingus()) == '<Dingus something()>'

    def should_include_attribute_name_in_repr_of_children_from_indexing(self):
        assert repr(self.dingus()['5']) == '<Dingus something()[5]>'


class WhenCallingDingusAsFunction(object):
    def setup(self):
        self.dingus = Dingus()
        self.dingus('arg', kwarg=None)

    def should_record_call(self):
        assert self.dingus.calls()

    def should_have_exactly_one_call(self):
        assert self.dingus.calls().one()

    def should_have_once_method_as_alias_for_one_method(self):
        assert self.dingus.calls().once()

    def should_record_args(self):
        assert self.dingus.calls.one().args == ('arg',)

    def should_record_kwargs(self):
        assert self.dingus.calls.one().kwargs == {'kwarg': None}


class WhenCallingAttributeChild(object):
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


class WhenCallingAttributeGrandchild(object):
    def setup(self):
        self.grandparent = Dingus()
        self.parent = self.grandparent.parent
        self.child = self.parent.child
        self.child('arg', kwarg=None)

    def should_not_record_call_on_grandparent(self):
        assert not self.grandparent.calls('parent.child')

    def should_record_call_on_parent(self):
        assert self.parent.calls('child').one()


class WhenCallingAttributesOfReturnedValues(object):
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

    def should_not_record_child_call_on_grandparent(self):
        assert not self.grandparent.calls('().child')


class WhenCallingItemChild(object):
    def should_record_call(self):
        parent = Dingus()
        parent['child']()
        assert parent.calls('[child]').one()


class WhenCallingListItemOfDingus(object):
    def setup(self):
        self.parent = Dingus()
        self.child = self.parent[0]
        self.child()

    def should_record_call_on_parent(self):
        assert self.parent.calls('[0]').one()

    def should_record_call_on_child(self):
        assert self.child.calls('()').one()


class WhenAccessingMagicAttributes(object):
    def should_raise_attribute_error_for_pyobjc_object(self):
        # PyObjC uses __pyobjc_object__ to get an ObjC object from a Python
        # object. Returning a Mock will cause a crash.
        assert_raises(AttributeError, lambda: Dingus().__pyobjc_object__)

    def should_raise_attribute_error_for_getnewargs(self):
        # Pickle uses __getnewargs__ to pickle a new-style object.
        assert_raises(AttributeError, lambda: Dingus().__getnewargs__)


INFIX_OPERATORS = ['add', 'and_', 'div', 'lshift', 'mod', 'mul', 'or_',
                   'pow', 'rshift', 'sub', 'xor']


class WhenApplyingInfixOperators(object):
    def __init__(self):
        self.operators = [getattr(operator, operator_name)
                          for operator_name in INFIX_OPERATORS]

    def assert_returns_new_dingus(self, op):
        left, right = Dingus.many(2)
        result = op(left, right)
        assert result is not left and result is not right

    def should_always_return_new_dingus(self):
        for operator in self.operators:
            yield self.assert_returns_new_dingus, operator

    def should_record_call(self):
        for operator in self.operators:
            left, right = Dingus.many(2)
            operator(left, right)
            operator_name_without_mangling = operator.__name__.replace('_', '')
            magic_method_name = '__%s__' % operator_name_without_mangling
            yield assert_call_was_logged, left, magic_method_name, right


class WhenApplyingAugmentedOperators(object):
    AUGMENTED_OPERATORS = ['i%s' % operator_name.replace('_', '')
                           for operator_name in INFIX_OPERATORS]

    def __init__(self):
        self.operators = [getattr(operator, operator_name)
                          for operator_name in self.AUGMENTED_OPERATORS]

    def assert_returns_same_dingus(self, op):
        left, right = Dingus.many(2)
        result = op(left, right)
        assert result is left

    def should_always_return_same_dingus(self):
        for operator in self.operators:
            yield self.assert_returns_same_dingus, operator

    def should_record_call(self):
        for operator in self.operators:
            left, right = Dingus.many(2)
            operator(left, right)
            magic_method_name = '__%s__' % operator.__name__
            yield assert_call_was_logged, left, magic_method_name, right


def assert_call_was_logged(dingus, method_name, *args):
    assert dingus.calls(method_name, *args).once()


class WhenComputingLength(object):
    def should_be_one(self):
        assert len(Dingus()) == 1


class WhenIterating(object):
    def should_return_one_dingus(self):
        assert len(list(Dingus())) == 1

    def should_return_dinguses(self):
        assert isinstance(list(Dingus())[0], Dingus)


class WhenAccessingReturnValueBeforeCallingi(object):
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


class WhenSettingReturnValue(object):
    def setup(self):
        self.dingus = Dingus()
        self.return_value = 5
        self.dingus.return_value = self.return_value

    def should_return_assigned_return_value(self):
        assert self.dingus() is self.return_value

    def should_have_same_return_value_after_calling(self):
        self.dingus()
        assert self.dingus.return_value is self.return_value


class WhenSettingAttributes(object):
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


class WhenDeletingAttributes(object):
    def should_record_deletion(self):
        dingus = Dingus()
        del dingus.foo
        assert dingus.calls('__delattr__', 'foo').once()


class WhenAccessingItems(object):
    def should_log_access(self):
        dingus = Dingus()
        dingus['item']
        assert dingus.calls('__getitem__', 'item').one()

    def should_log_access_after_initial_item_read(self):
        dingus = Dingus()
        for _ in range(2):
            dingus['item']
        assert len(dingus.calls('__getitem__', 'item')) == 2

    def should_accept_tuples_as_item_name(self):
        dingus = Dingus()
        assert dingus[('x', 'y')]


class WhenSettingItems(object):
    def setup(self):
        self.dingus = Dingus()
        self.item = Dingus()
        self.dingus['item'] = self.item

    def should_remember_item(self):
        assert self.dingus['item'] is self.item

    def should_remember_item_even_if_its_value_is_None(self):
        self.dingus['item'] = None
        assert self.dingus['item'] is None

    def should_log_access(self):
        assert self.dingus.calls('__setitem__', 'item', self.item).one()

    def should_not_return_items_as_attributes(self):
        assert self.dingus.item is not self.item

    def should_return_distinct_dinguses_for_different_items(self):
        assert self.dingus['item'] is not self.dingus['item2']
    
    def should_accept_tuples_as_item_name(self):
        dingus = Dingus()
        dingus[('x', 'y')] = 'foo'
        assert dingus[('x', 'y')] == 'foo'


class WhenNothingIsSet(object):
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


class WhenSpecifyingAttributesViaKeywordArguments(object):
    def should_set_specified_attributes(self):
        attr = Dingus()
        object_with_attr = Dingus(attr=attr)
        assert object_with_attr.attr is attr


class WhenSpecifyingMethodReturnValuesViaKeywordArguments(object):
    def should_define_methods_returning_specified_values(self):
        result = Dingus()
        object_with_result = Dingus(method__returns=result)
        assert object_with_result.method() is result

    def should_record_calls_on_children(self):
        result = Dingus()
        object_with_result = Dingus(method__returns=result)
        object_with_result.method()
        assert object_with_result.calls('method')


class WhenCallingInitMethod(object):
    def should_record_call(self):
        dingus = Dingus()
        dingus.__init__()
        assert dingus.calls('__init__').one()


class WhenCreatingMultipleDinguses(object):
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

class WhenPicklingDingus(object):
    def setup(self):
        self.dingus = Dingus("something")

        # interact before pickling
        self.dingus('arg', kwarg=None)
        self.dingus.child.function_with_return_value.return_value = 'RETURN'
        self.dingus.child('arg', kwarg=None)
        
        self.dump_str = pickle.dumps(self.dingus, pickle.HIGHEST_PROTOCOL)
        del self.dingus        
        self.unpickled_dingus = pickle.loads(self.dump_str)

    def should_remember_name(self):
        assert self.unpickled_dingus.__name__ == 'something'
    
    def should_remember_called_functions(self):
        assert self.unpickled_dingus.calls('()').one().args == ('arg',) 

    def should_remember_child_calls(self):
        assert self.unpickled_dingus.calls("child").one().args == ('arg',)

    def should_remember_child_functions_return_value(self):
        assert self.unpickled_dingus.child.function_with_return_value() == 'RETURN'

    def should_have_replaced_init(self):
        assert self.unpickled_dingus.__init__ == self.unpickled_dingus._fake_init
        assert self.unpickled_dingus.child.__init__ == self.unpickled_dingus.child._fake_init


class WhenDingusIsSubclassed(object):
    def should_return_subclass_instances_instead_of_dinguses(self):
        class MyDingus(Dingus):
            pass

        dingus = MyDingus()
        assert isinstance(dingus.foo, MyDingus)


class WhenDingusIsDeepCopied(object):
    def should_retain_attributes(self):
        dingus = Dingus(foo=1)
        assert copy.deepcopy(dingus).foo == 1

    def should_be_independent_of_original_dingus(self):
        dingus = Dingus()
        copied_dingus = copy.deepcopy(dingus)
        copied_dingus.frob()
        assert copied_dingus.calls('frob').once()
        assert not dingus.calls('frob')

class WhenUsedAsAContextManager(object):
    def should_not_raise_an_exception(self):
        with Dingus():
            pass

    def should_be_able_to_return_something(self):
        open = Dingus()
        open().__enter__().read.return_value = "some data"
        with open('foo') as h:
            data_that_was_read = h.read()

        assert data_that_was_read == "some data"

    def _raiser(self, exc, dingus):
        def callable():
            with dingus:
                raise exc
        return callable

    def should_not_consume_exceptions_from_context(self):
        dingus = Dingus()
        assert_raises(KeyError, self._raiser(KeyError, dingus))

    def should_be_able_to_consume_an_arbitrary_exception(self):
        dingus = Dingus(consumed_context_manager_exceptions=(EOFError,))
        self._raiser(EOFError, dingus)()
        assert_raises(KeyError, self._raiser(KeyError, dingus))

    def should_be_able_to_consume_multiple_exceptions(self):
        dingus = Dingus(consumed_context_manager_exceptions=(
            NameError, NotImplementedError))
        self._raiser(NameError, dingus)()
        self._raiser(NotImplementedError, dingus)()
        assert_raises(KeyError, self._raiser(KeyError, dingus))

    def should_be_able_to_manually_consume_exceptions(self):
        dingus = Dingus(consumed_context_manager_exceptions=(EOFError,))
        self._raiser(EOFError, dingus)()
        assert_raises(KeyError, self._raiser(KeyError, dingus))

