from dingus import DingusTestCase, DontCare
import urllib2
from urllib2 import urlopen


# We want to unit test the urlopen function. It's very small (as you can see
# by looking at the source at ${PYTHON_INSTALL}/lib/python2.5/urllib2.py
#
# (This example assumes Python 2.5. Hopefully it also works for your version.)
#
# Dingus allows us to test urlopen without actually touching the network, or
# any other classes and functions at all. When we define the test class, we
# inherit from "DingusTestCase(urlopen)". DingusTestCase will define setup and
# teardown method that replace every object in urllib2 with a dingus
# (except urlopen, which is the "object under test". It does this by looking
# at the module that urlopen was defined in, making a backup copy of its
# contents, then replacing everything with a dingus. So, instead of making
# network connections as it usually would, urlopen will be making calls into
# the dinguses, which will record the calls so that we can make assertions
# about them later.
class WhenOpeningURLs(DingusTestCase(urlopen)):
    def setup(self):
        # We have to call DingusTestCase's setup method so that it can
        # modify the urllib2 module's contents.
        super(WhenOpeningURLs, self).setup()

        # We set up the object under test here by calling urlopen with a URL.
        self.url = 'http://www.example.com'
        self.opened_url = urlopen(self.url)

    # First, we expect urlopen to try to open the URL.
    def should_open_provided_url(self):
        # Normally urlopen would use a prexisting "opener" object that would
        # touch the network, disk, etc., but DingusTestCase has replaced it
        # with a dingus. We first grab that _opener object so we can make
        # assertions about it.
        opener = urllib2._opener

        # We want to assert that urlopen should call "open" on the opener,
        # passing the URL we gave it. "open" also takes another argument, but
        # we don't care about that for this test. We pass in DontCare for
        # things we don't care about, and the dingus will ignore that argument
        # for the purposes of this assertion.
        #     assert opener.calls('open', self.url, DontCare, DontCare).once()
        # However, since we want this test to work across all Python versions,
        # and the opener.open() call differs between them, we'll use a
        # slightly more complex method to only check the first argument of the
        # open() call.
        assert opener.calls('open').once().args[0] == self.url

        # Note that we never told the _opener dingus that it should have an
        # "open" method. A dingus has *all* methods - it will try to allow
        # anything to be done to it.

    def should_return_opened_url(self):
        # Now we want to assert that the opened object is returned to the
        # caller. The line of code from urllib2 that we're testing is:
        #     return _opener.open(url, data)
        # We need to make sure that urlopen returned the result of that. We do
        # that by accessing _opener.open.return_value. _opener.open is the
        # dingus that replaced the original _opener.open method. The
        # return_value is a special attribute of all dinguses that gets
        # returned when the dingus is called as a function.
        assert self.opened_url is urllib2._opener.open.return_value

    # We could also define a teardown method for this test class, but that's
    # rarely needed when writing fully isolated tests like this one.
    # DingusTestCase does define a teardown method, though - it reverses the
    # changes it made to the module under test, removing the dinguses and
    # restoring the module's original contents. This class inherited it, so we
    # don't have to call it manually.

