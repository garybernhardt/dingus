from dingus import Call


class WhenInstantiated:
    def setup(self):
        self.call = Call('test name',
                         'test args',
                         'test kwargs',
                         'test return_value')

    def should_have_name(self):
        assert self.call.name == 'test name'

    def should_have_args(self):
        assert self.call.args == 'test args'

    def should_have_kwargs(self):
        assert self.call.kwargs == 'test kwargs'

    def should_have_return_value(self):
        assert self.call.return_value == 'test return_value'

