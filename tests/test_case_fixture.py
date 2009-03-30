atomic_value = 'foo'

callable_value_with_wrong_name = lambda: None
callable_value_with_wrong_name.__name__ = 'wrong'

class ClassUnderTest:
    pass
