from nose.tools import assert_raises

from dingus import Call, CallList, DontCare


class WhenEmpty:
    def setup(self):
        self.calls = CallList()

    def should_be_false_in_boolean_context(self):
        assert not self.calls

    def should_not_have_one_element(self):
        assert_raises(AssertionError, self.calls.one)


class WhenPopulatedWithACall:
    def setup(self):
        self.calls = CallList()
        self.calls.append(Call('test name',
                               'test args',
                               'test kwargs',
                               'test return_value'))

    def should_be_true_in_boolean_context(self):
        assert self.calls

    def should_have_exactly_one_call(self):
        assert self.calls.one()

    def should_not_return_call_when_querying_for_wrong_name(self):
        assert not self.calls(name='wrong name')

    def should_not_return_call_when_querying_for_wrong_args(self):
        assert not self.calls(args='wrong args')

    def should_not_return_call_when_querying_for_wrong_kwargs(self):
        assert not self.calls(kwargs=dict(wrong_key='wrong_value'))


class WhenPopulatedWithTwoCalls:
    def setup(self):
        self.calls = CallList()
        self.calls.append(Call('name1', ('arg1',), {'kwarg1': 1}, 'return 1'))
        self.calls.append(Call('name2', ('arg2',), {'kwarg2': 2}, 'return 2'))

    def should_not_have_one_element(self):
        assert_raises(AssertionError, self.calls.one)

    def should_filter_on_name(self):
        assert self.calls('name1').one()

    def should_filter_on_args(self):
        assert self.calls(args=('arg1',)).one()


class WhenCallsDifferInAllWays:
    def setup(self):
        self.calls = CallList()
        for name in ('name1', 'name2'):
            for args in (('arg1',), ('arg2',)):
                for kwargs in ({'kwarg1': 1}, {'kwarg2': 2}):
                    call = Call(name, args, kwargs, 'return value')
                    self.calls.append(call)
        self.call_count = len(self.calls)

    def should_filter_on_name(self):
        assert len(self.calls('name1')) == self.call_count / 2

    def should_filter_on_args(self):
        assert len(self.calls(args=('arg1',))) == self.call_count / 2

    def should_filter_on_kwargs(self):
        assert len(self.calls(kwargs={'kwarg1': 1})) == self.call_count / 2


class WhenCallsHaveMultipleArguments:
    def setup(self):
        self.calls = CallList()
        for arg1 in (1, 2):
            for arg2 in (1, 2):
                self.calls.append(Call('name',
                                       (arg1, arg2),
                                       {},
                                       'return_value'))
        self.call_count = len(self.calls)

    def should_be_able_to_ignore_all_arguments(self):
        assert len(self.calls(args=(DontCare, DontCare))) == self.call_count

    def should_be_able_to_ignore_first_argument(self):
        assert len(self.calls(args=(1, DontCare))) == self.call_count / 2

    def should_be_able_to_ignore_second_argument(self):
        assert len(self.calls(args=(DontCare, 1))) == self.call_count / 2

    def should_be_able_to_specify_both_arguments(self):
        assert len(self.calls(args=(1, 1))) == self.call_count / 4

