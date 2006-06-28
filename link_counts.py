from lxml import etree
import urllib2
import urllib
import re
import time
import BeautifulSoup
import datetime

## ADDME: MSN Search E389A2EC44FFB3F5748A9AEF7CCFED7AD82690DA and 
## API?  Screen-scrape?
## They have some SOAP thing that is only documented in an MSI.  What a freaking pain.

DEBUG = 1
def debug(s):
    if DEBUG:
        print s

import google
google.setLicense('8cJjiPdQFHK2T3LGWq+Ro04dyJr0fyZs')

from simpleyahoo import legitimate_yahoo_count
import simpleyahoo

from sqlalchemy.ext.sqlsoup import SqlSoup

## THINKME: Google and Yahoo both have different ways to encode CC license types.  Later on, it's probably worth standardizing this somehow, or else their trash gets shoved into our DB.

## FIXME: Maybe I could loop over the URIs somewhere else so that I pass a URI
## in to the search-engine-specific things

## The count_* functions could totally be turned into a "templated" function

## FIXME: The bigger Yahoo and Google query stuff seems fairly separate from
## the count_* functions.  Maybe jam it into a different class?

class LinkCounter:
    dumb_queries = ['license', '-license', 'work', '-work', 'html', '-html']
    ## TRYME: ccTLDs?
    def __init__(self, dburl, xmlpath):
        self.timestamp = datetime.datetime.now()
        self.db = SqlSoup(dburl) # open this with sqlsoup or something
        self.uris = self.parse(xmlpath)
        # We need to get a list of URIs to search for
        assert(self.uris) # These should not be empty.

    def parse(self, xmlpath):
        # FIXME: Add urls (after checking for duplicates) from old/
        ret = []
        tree2=etree.parse(xmlpath)
        root2=tree2.getroot()
        for element in root2.getiterator('version'):
            ret.append(element.get('uri'))
        return ret # I'm not sorting.  So there.

    def record(self, cc_license_uri, search_engine, count):
        self.db.simple.insert(license_uri=cc_license_uri, search_engine=search_engine,count=count,timestamp = self.timestamp)
        self.db.flush()

    def count_google(self):
        ## Once from webtrawl
        for uri in self.uris:
            result = google.doGoogleSearch("link:%s" % uri)
            count = result.meta.estimatedTotalResultsCount

            # We record the specific uri, count pair in the DB
            self.record(cc_license_uri=uri, search_engine='Google', count=count)

    def count_alltheweb(self):
        # These guys seem to get mad at us if we query them too fast.
        # To avoid "HTTP Error 999" (!), let's sleep(0.1) between
        # queries.  They seem to block the IP, not just the
        # user-agent.  Oops.
        for uri in self.uris:
            self.record(cc_license_uri=uri, search_engine="All The Web", count=atw_count("link:" + uri))
            time.sleep(0.1) # "And, breathe."

    def count_yahoo(self):
        # No sleep here because we're APIing it up.
        for uri in self.uris:
            for language in [None] + simpleyahoo.langauges.keys():
                for country in [None] + simpleyahoo.countries.keys():
                    countryid = simpleyahoo.countries.get(country, None) # None as default
                    langid = simpleyahoo.countries.get(language, None) # None as default
                    count = legitimate_yahoo_count(uri, 'InlinkData', country=countryid, language=langid)
                    self.record(cc_license_uri=uri,
                                search_engine='Yahoo',
                                count = count,
                                language = language,
                                country = country)

    def specific_google_counter(self):
        """ Now instead of searching for links to a license URI,
        we use Google's built-in CC search.

        Unfortunately, it doesn't let you do a raw count, so we hack
        around that by adding up queries like -license and +license."""
        
        ## The is Google's idea of how to encode CC stuff.
        licenses = ["cc_publicdomain", "cc_attribute", "cc_sharealike", "cc_noncommercial", "cc_nonderived", "cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived"]
        for license in licenses:
            for dumb_query in self.dumb_queries:
                result = google.doGoogleSearch(dumb_query, restrict=license)
                count = result.meta.estimatedTotalResultsCount
                self.record_complex(license_specifier=license,
                                    search_engine='Google',
                                    count=count,
                                    query=dumb_query)
    
    def specific_yahoo_counter(self):
        """ Similar deal here as for Google's specific_counter.
        FIXME: Abstract Yahoo queries. """
        licenses = [['cc_any'],['cc_commercial'],['cc_modifiable'],['cc_commercial', 'cc_modifiable']]
        for license in licenses:
            for dumb_query in self.dumb_queries:
                # Now, let's add languages
                for language in [None] + simpleyahoo.languages.keys():
                    for country in [None] + simpleyahoo.countries.keys():
                        countryid = simpleyahoo.countries.get(country, None) # None as default
                        langid = simpleyahoo.countries.get(language, None) # None as default
                        count = legitimate_yahoo_count(query=dumb_query, cc_spec=license, country=countryid, language=langid) # Query with the terse form
                        self.record_complex(license_specifier='&'.join(license),
                                            search_engine='Yahoo',
                                            count=count,
                                            query=dumb_query,
                                            language=language,
                                            country=country) # but store the human forms
                        

    def record_complex(self, license_specifier, search_engine, count, query, country, language):
        self.db.complex.insert(license_specifier=license_specifier, count = count, query = query, timestamp = self.timestamp, search_engine=search_engine, country=country, language=language)
        self.db.flush()
        debug("%s gave us %d hits via %s" % (license_specifier, count, search_engine))
        
def main():
    lc = LinkCounter(dburl='mysql://root:@localhost/cc', xmlpath='old/api/licenses.xml')
    lc.count_google()
    lc.count_alltheweb()
    lc.count_yahoo()
    lc.specific_google_counter()
    lc.specific_yahoo_counter()
