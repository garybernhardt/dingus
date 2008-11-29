import urllib2


class Googler(object):
    BASE_QUERY_URL = 'http://www.google.com/search?q='
    USER_AGENT = ('Mozilla/5.0' +
                  '(X11; U; Linux i686; en-US; rv:1.7.8)' +
                  'Gecko/20050524 Fedora/1.5 Firefox/1.5')

    def __init__(self, terms):
        query_string = '+'.join(terms)
        request = urllib2.Request('%s%s' % (self.BASE_QUERY_URL,
                                            query_string))
        request.add_header('User-Agent', self.USER_AGENT)
        connection = urllib2.urlopen(request)
        self.response = connection.read()


if __name__ == '__main__':
    print Googler(['lulz', 'megalulz']).response

