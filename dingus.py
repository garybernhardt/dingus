# This library was written by Gary Bernhardt and is licensed under the BSD
# license. It grew out of an old version of the mock library by Michael Foord
# available at http://www.voidspace.org.uk/python/mock.html.


import sys
import new


def DingusTestCase(class_under_test):
    class TestCase(object):
        def setup(self):
            module_name = class_under_test.__module__
            self._dingus_module = sys.modules[module_name]
            self._dingus_replace_module_globals(self._dingus_module,
                                                class_under_test)

        def teardown(self):
            self._dingus_restore_module(self._dingus_module)

        def _dingus_wipe_module(self, module):
            old_module_dict = module.__dict__.copy()
            module.__dict__.clear()
            module.__dict__.update(__builtins__)
            module.__dict__['__dingused_dict__'] = old_module_dict


        def _dingus_replace_module_globals(self, module, class_under_test):
            module_keys = set(module.__dict__.iterkeys())
            builtin_keys = set(__builtins__.iterkeys())

            test_class_name = class_under_test.__name__
            replaced_keys = (module_keys -
                             builtin_keys -
                             set([test_class_name]))
            self._dingus_wipe_module(module)
            for key in replaced_keys:
                module.__dict__[key] = Dingus()
            module.__dict__[test_class_name] = class_under_test

        def _dingus_restore_module(self, module):
            old_module_dict = module.__dict__['__dingused_dict__']
            module.__dict__.clear()
            module.__dict__.update(old_module_dict)


    TestCase.__name__ = '%sDingusTestCase' % class_under_test.__module__
    return TestCase



# These sentinels are used for argument defaults because the user might want
# to pass in None, which is different in some cases than passing nothing.
class NoReturnValue(object):
    pass
class NoArgument(object):
    pass


class DontCare(object):
    pass


class Call(tuple):
    def __new__(cls, name, args, kwargs, return_value):
        return tuple.__new__(cls, (name, args, kwargs, return_value))

    def __init__(self, *args):
        self.name = self[0]
        self.args = self[1]
        self.kwargs = self[2]
        self.return_value = self[3]


class CallList(list):
    @staticmethod
    def _match_args(call, args):
        if not args:
            return True
        elif len(args) != len(call.args):
            return False
        else:
            return all(args[i] in (DontCare, call.args[i])
                       for i in range(len(call.args)))

    def one(self):
        assert len(self) == 1
        return self[0]

    def __call__(self, name=NoArgument, *args, **kwargs):
        return CallList([call for call in self
                         if (name is NoArgument or name == call.name)
                         and self._match_args(call, args)
                         and (not kwargs or kwargs == call.kwargs)])


class Dingus(object):
    def __init__(self, name=None, **kwargs):
        self._parent = None
        self.reset()
        self.__name__ = 'dingus_%i' % id(self) if name is None else name

        for attr_name, attr_value in kwargs.iteritems():
            setattr(self, attr_name, attr_value)

        self._replace_init_method()

    @classmethod
    def many(cls, count):
        return tuple(cls() for _ in range(count))

    def _fake_init(self, *args, **kwargs):
        return self.__getattr__('__init__')(*args, **kwargs)

    def _replace_init_method(self):
        self.__init__ = self._fake_init

    def _create_child(self, name):
        child = Dingus(name)
        child._parent = self
        return child

    def reset(self):
        self._return_value = NoReturnValue
        self.calls = CallList()
        self._children = {}

    def _get_return_value(self):
        if self._return_value is NoReturnValue:
            self._return_value = self._create_child('()')
        return self._return_value

    def _set_return_value(self, value):
        self._return_value = value

    return_value = property(_get_return_value, _set_return_value)

    def __call__(self, *args, **kwargs):
        if self.return_value is NoReturnValue:
            self.return_value = self._create_child('()')

        self._log_call_in_parent(self.__name__,
                                 args,
                                 kwargs,
                                 self.return_value)
        self._log_call('()', args, kwargs, self.return_value)

        return self.return_value

    def _log_call_in_parent(self, name, args, kwargs, return_value):
        parent = self._parent
        if parent is None:
            return

        parent._log_call(name, args, kwargs, return_value)

        if parent.__name__ is not None:
            separator = ('' if (name.startswith('()') or name.startswith('['))
                         else '.')
            name = parent.__name__ + separator + name
            parent._log_call_in_parent(name, args, kwargs, return_value)

    def _log_call(self, name, args, kwargs, return_value):
        self.calls.append(Call(name, args, kwargs, return_value))

    def _should_ignore_attribute(self, name):
        return name == '__pyobjc_object__'

    def __getattr__(self, name):
        if self._should_ignore_attribute(name):
            raise AttributeError(name)

        if name not in self._children:
            self._children[name] = self._create_child(name)

        return self._children[name]

    def __getitem__(self, index):
        child_name = '[%s]' % index
        return_value = self._children.setdefault(
            child_name, self._create_child('[%s]' % index))
        self._log_call('__getitem__', (index,), {}, return_value)
        return return_value

    def __setitem__(self, index, value):
        child_name = '[%s]' % index
        self._log_call('__setitem__', (index, value), {}, None)
        self._children[child_name] = value

    def _create_operator(name):
        def operator_fn(self, other):
            if name not in self._children:
                self._children[name] = self._create_child(name)
            return self._children[name]
        operator_fn.__name__ = name
        return operator_fn

    def _operators():
        operator_names = ['add', 'and', 'div', 'lshift', 'mod', 'mul', 'or',
                          'pow', 'rshift', 'sub', 'xor']
        reverse_operator_names = ['r%s' % name for name in operator_names]
        for operator_name in operator_names + reverse_operator_names:
            operator_fn_name = '__%s__' % operator_name
            yield operator_fn_name

    # Define each operator
    for operator_fn_name in _operators():
        exec('%s = _create_operator("%s")' % (operator_fn_name,
                                              operator_fn_name))

    def __str__(self):
        return '<Dingus %s>' % self.__name__
    __repr__ = __str__

    def __len__(self):
        return 1


def exception_raiser(exception):
    def raise_exception(*args, **kwargs):
        raise exception
    return raise_exception

