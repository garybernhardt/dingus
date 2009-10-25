from dingus import Dingus, returner


class WhenCreatingReturner:
    def should_return_given_value(self):
        return_value = Dingus()
        r = returner(return_value)
        assert r() == return_value

