# This library was written by Gary Bernhardt and is licensed under the BSD
# license. It grew out of an old version of the mock library by Michael Foord
# available at http://www.voidspace.org.uk/python/mock.html.


import sys
import new


def DingusTestCase(object_under_test, exclude=None):
    exclude = [] if exclude is None else exclude

    def get_names_under_test():
        module = sys.modules[object_under_test.__module__]
        for name, value in module.__dict__.iteritems():
            if value is object_under_test or name in exclude:
                yield name

    class TestCase(object):
        def setup(self):
            module_name = object_under_test.__module__
            self._dingus_module = sys.modules[module_name]
            self._dingus_replace_module_globals(self._dingus_module)

        def teardown(self):
            self._dingus_restore_module(self._dingus_module)

        def _dingus_replace_module_globals(self, module):
            old_module_dict = module.__dict__.copy()
            module_keys = set(module.__dict__.iterkeys())

            replaced_keys = (module_keys -
                             set(['__builtins__', '__builtin__']) -
                             set(names_under_test))
            for key in replaced_keys:
                module.__dict__[key] = Dingus()
            module.__dict__['__dingused_dict__'] = old_module_dict

        def _dingus_restore_module(self, module):
            old_module_dict = module.__dict__['__dingused_dict__']
            module.__dict__.clear()
            module.__dict__.update(old_module_dict)

    names_under_test = list(get_names_under_test())
    TestCase.__name__ = '%s_DingusTestCase' % '_'.join(names_under_test)
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
        
    def __getnewargs__(self):
        return (self.name, self.args, self.kwargs, self.return_value)


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
        if len(self) == 1:
            return self[0]
        else:
            return None

    def once(self):
        return self.one()

    def __call__(self, name=NoArgument, *args, **kwargs):
        return CallList([call for call in self
                         if (name is NoArgument or name == call.name)
                         and self._match_args(call, args)
                         and (not kwargs or kwargs == call.kwargs)])


def returner(return_value):
    return Dingus(return_value=return_value)


class Dingus(object):
    def __init__(self, name=None, full_name=None, **kwargs):
        self._parent = None
        self.reset()
        name = 'dingus_%i' % id(self) if name is None else name
        full_name = name if full_name is None else full_name
        self._short_name = name
        self._full_name = full_name
        self.__name__ = name
        self._full_name = full_name

        for attr_name, attr_value in kwargs.iteritems():
            if attr_name.endswith('__returns'):
                attr_name = attr_name.replace('__returns', '')
                setattr(self, attr_name, lambda *args, **kwargs: attr_value)
            else:
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
        separator = ('' if (name.startswith('()') or name.startswith('['))
                     else '.')
        full_name = self._full_name + separator + name
        child = Dingus(name, full_name)
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
        self._log_call('()', args, kwargs, self.return_value)
        if self._parent:
            self._parent._log_call(self._short_name,
                                   args,
                                   kwargs,
                                   self.return_value)

        return self.return_value

    def _log_call(self, name, args, kwargs, return_value):
        self.calls.append(Call(name, args, kwargs, return_value))

    def _should_ignore_attribute(self, name):
        return name in ['__pyobjc_object__', '__getnewargs__']
    
    def __getstate__(self):
        # Python cannot pickle a instancemethod
        # http://bugs.python.org/issue558238
        return [ (attr, value) for attr, value in self.__dict__.items() if attr != "__init__"]
    
    def __setstate__(self, state):
        self.__dict__.update(state)
        self._replace_init_method()

    def _existing_or_new_child(self, child_name, default_value=NoArgument):
        if child_name not in self._children:
            value = (self._create_child(child_name)
                     if default_value is NoArgument
                     else default_value)
            self._children[child_name] = value

        return self._children[child_name]

    def _remove_child_if_exists(self, child_name):
        if child_name in self._children:
            del self._children[child_name]

    def __getattr__(self, name):
        if self._should_ignore_attribute(name):
            raise AttributeError(name)
        return self._existing_or_new_child(name)

    def __getitem__(self, index):
        child_name = '[%s]' % (index,)
        return_value = self._existing_or_new_child(child_name)
        self._log_call('__getitem__', (index,), {}, return_value)
        return return_value

    def __setitem__(self, index, value):
        child_name = '[%s]' % (index,)
        self._log_call('__setitem__', (index, value), {}, None)
        self._remove_child_if_exists(child_name)
        self._existing_or_new_child(child_name, value)

    def _create_operator(name):
        def operator_fn(self, other):
            return self._existing_or_new_child(name)
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
        return '<Dingus %s>' % self._full_name
    __repr__ = __str__

    def __len__(self):
        return 1

    def __iter__(self):
        return iter([self._existing_or_new_child('__iter__')])


def exception_raiser(exception):
    def raise_exception(*args, **kwargs):
        raise exception
    return raise_exception

