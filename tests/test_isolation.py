from __future__ import with_statement
import urllib2

from dingus import Dingus, patch


class WhenPatchingObjects:
    @patch('urllib2.urlopen')
    def should_replace_object_with_dingus(self):
        assert isinstance(urllib2.urlopen, Dingus)

    def should_restore_object_after_patched_function_exits(self):
        @patch('urllib2.urlopen')
        def patch_urllib2():
            pass
        patch_urllib2()
        assert not isinstance(urllib2.urlopen, Dingus)

    def should_be_usable_as_context_manager(self):
        with patch('urllib2.urlopen'):
            assert isinstance(urllib2.urlopen, Dingus)
        assert not isinstance(urllib2.urlopen, Dingus)

    def should_be_able_to_provide_dingus(self):
        my_dingus = Dingus()
        with patch('urllib2.urlopen', my_dingus):
            assert urllib2.urlopen is my_dingus

