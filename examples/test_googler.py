from dingus import Dingus, DingusFixture, DontCare
import googler
from googler import Googler


class WhenCreatingRequest(DingusFixture(Googler)):
    def setup(self):
        super(WhenCreatingRequest, self).setup()
        self.query_term = 'query term'
        self.googler = Googler([self.query_term])

    def should_use_google_search_url(self):
        query_url = 'http://www.google.com/search?q=%s' % self.query_term
        assert googler.urllib2.calls('Request', query_url)


class WhenCreatingRequestWithTwoTerms(DingusFixture(Googler)):
    def setup(self):
        super(WhenCreatingRequestWithTwoTerms, self).setup()
        self.terms = ['term1', 'term2']
        self.googler = Googler(self.terms)

    def should_combine_terms_in_search_url(self):
        query_string = '+'.join(self.terms)
        query_url = 'http://www.google.com/search?q=%s' % query_string
        assert googler.urllib2.calls('Request', query_url)


class WhenSendingRequest(DingusFixture(Googler)):
    def setup(self):
        super(WhenSendingRequest, self).setup()
        self.request = googler.urllib2.Request.return_value
        Googler(['query term'])

    def should_connect_to_google(self):
        assert googler.urllib2.calls('urlopen', self.request)

    def should_add_fake_user_agent_to_evade_filters(self):
        call = self.request.calls('add_header',
                                  'User-Agent',
                                  DontCare).one()
        assert 'Mozilla' in call.args[1]


class WhenConnected(DingusFixture(Googler)):
    def setup(self):
        super(WhenConnected, self).setup()
        self.connection = googler.urllib2.urlopen.return_value
        self.googler = Googler(['query term'])

    def should_read_result(self):
        assert self.connection.calls('read')

    def should_store_result_in_attribute(self):
        assert self.googler.response is self.connection.read.return_value

