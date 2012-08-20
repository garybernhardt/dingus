from dingus import assert_call, Dingus
from nose.tools import raises


class AssertCallTest(object):

    def setup(self):
        self.ding = Dingus('ding')

class WhenCallsExists(AssertCallTest):

    def should_not_raise_any_error_simple_call(self):
        self.ding.foo()

        assert_call(self.ding, 'foo')

    def should_not_raise_any_error_with_args(self):
        self.ding.foo('bar')

        assert_call(self.ding, 'foo')
        assert_call(self.ding, 'foo', 'bar')
        
    def should_not_raise_any_error_with_args_and_kwargs(self):
        self.ding.foo('bar', qux=1)

        assert_call(self.ding, 'foo')
        assert_call(self.ding, 'foo', 'bar')
        assert_call(self.ding, 'foo', 'bar', qux=1)

class WhenThereIsNoCallsForTheMatchedArgs(AssertCallTest):

    @raises(AssertionError)
    def should_raise_an_assertion_error(self):
        assert_call(self.ding, 'foo')
        
    @raises(AssertionError)
    def should_raise_an_assertion_error_other_method_call(self):
        self.ding.bar()
        assert_call(self.ding, 'foo')

    @raises(AssertionError)
    def should_raise_an_assertion_error_with_args(self):
        self.ding.foo()

        assert_call(self.ding, 'foo', 'bar')

    @raises(AssertionError)
    def should_raise_an_assertion_error_with_args_and_kargs(self):
        self.ding.foo('bar')

        assert_call(self.ding, 'foo', 'bar', qux=1)

    def should_show_a_friendly_error_message(self):
        try:
            assert_call(self.ding, 'foo')
        except AssertionError, e:
            self._assert_message(e.message, 'foo', (), {})

    def should_show_a_friendly_error_message_with_call_to_other_method(self):
        self.ding.bar()
        try:
            assert_call(self.ding, 'foo')
        except AssertionError, e:
            self._assert_message(e.message, 'foo', (), {})

    def _assert_message(self, message, method, args, kwargs):
            expected, recorded_calls = message.split('\n')
            assert "Expected a call to method: '%s', args: %s, kwargs: %s, " % (method, args, kwargs)  + \
                   "dingus: %s" % self.ding == \
                    expected
            if not self.ding.calls:
                assert "No calls recorded" == recorded_calls
            else:
                assert "Recorded calls:\n%s" == recorded_calls
