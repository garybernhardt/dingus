from nose.tools import assert_raises
from nose.tools import raises

from dingus import exception_raiser


class WhenCalled:
    def setup(self):
        exception = ValueError()
        self.raise_exception = exception_raiser(exception)

    def should_raise_provided_exception(self):
        assert_raises(ValueError, self.raise_exception)

    def should_take_args(self):
        assert_raises(ValueError, self.raise_exception, 1)

    def should_take_kwargs(self):
        assert_raises(ValueError, self.raise_exception, kwarg=1)

