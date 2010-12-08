========
DINGUSES
========

A dingus is sort of like a mock object. The main difference is that you don't
set up expectations ahead of time. You just run your code, using a dingus in
place of another object or class, and it will record what happens to it. Then,
once your code has been exercised, you can make assertions about what it did
to the dingus.

A new dingus is created from the Dingus class. You can give dinguses names,
which helps with debugging your tests, especially when there are multiple
dinguses in play.

    >>> from dingus import Dingus
    >>> d = Dingus('root')
    >>> d
    <Dingus root>

Accessing any attribute of a dingus will return a new dingus.

    >>> d.something
    <Dingus root.something>

There are a few exceptions for special dingus methods. We'll see some in a
bit.

A dingus can also be called like a function or method. It doesn't care how
many arguments you give it or what those arguments are. Calls to a dingus will
always return the same object, regardless of the arguments.

    >>> d()
    <Dingus root()>
    >>> d('argument')
    <Dingus root()>
    >>> d(55)
    <Dingus root()>

========================
RECORDING AND ASSERTIONS
========================

At any time we can get a list of calls that have been made to a dingus. Each
entry in the call list contains:

* the name of the method called (or "()" if the dingus itself was called)
* The arguments, or () if none
* The keyword argumnets, or {} if none
* The value that was returned to the caller

Here is a list of the calls we've made to d so far:

    >>> from pprint import pprint
    >>> pprint(d.calls)
    [('()', (), {}, <Dingus root()>),
     ('()', ('argument',), {}, <Dingus root()>),
     ('()', (55,), {}, <Dingus root()>)]

You can filter calls by name, arguments, and keyword arguments:

    >>> pprint(d.calls('()', 55))
    [('()', (55,), {}, <Dingus root()>)]

If you don't care about a particular argument's value, you can use the value
DontCare when filtering:

    >>> from dingus import DontCare
    >>> pprint(d.calls('()', DontCare))
    [('()', ('argument',), {}, <Dingus root()>),
     ('()', (55,), {}, <Dingus root()>)]

Dinguses can do more than just have attributes accessed and be called. They
support many Python operators. The goal is to allow, and record, any
interaction:

    >>> d = Dingus('root')
    >>> (2 ** d.something)['hello']() / 100 * 'foo'
    <Dingus root.something.__rpow__[hello]().__div__.__mul__>

(Hopefully your real-world dingus recordings won't look like this!)

========
PATCHING
========

Dingus provides a context manager for patching objects during tests. For
example:

    >>> from dingus import patch
    >>> import urllib2
    >>> with patch('urllib2.urlopen'):
    ...     print urllib2.urlopen.__class__
    <class 'dingus.Dingus'>
    >>> print urllib2.urlopen.__class__
    <type 'function'>

You can also use this as a decorator on your test methods:

    >>> @patch('urllib2.urlopen')
    ... def test_something(self):
    ...     pass
    ...

===============
DANGEROUS MAGIC
===============

Dingus can also automatically replace a module's globals when running tests.
This allows you to write fully isolated unit tests. See
examples/urllib2/test\_urllib2.py for an example. The author no longer
recommends this feature, as it can encourage very brittle tests. You should
feel the pain of manually mocking dependencies; the pain will tell you when a
class collaborates with too many others.

