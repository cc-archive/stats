import link_counts
import xml.dom.pulldom as pulldom
import datetime

def doTag(saxxer, tag, characters, attrs = {}):
    saxxer.startElement(tag, attrs)
    saxxer.characters(characters)
    saxxer.endElement(tag)

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

class Importer:
    def __init__(self, fd, db = 'mysql://root:@localhost/cc'):
        ''' Takes an fd as an input.
        Creates some internal state and does some SQL queries as a result. '''
        self.lc = link_counts.LinkCounter(db, 'old/api/licenses.xml')
        self.date = "RIGGED TO EXPLODE"
        self.parse(fd)

    def parse(self, fd):
        events = pulldom.parse(fd)
        for (event, node) in events:
            if event == 'START_ELEMENT':
                if node.tagName == 'Dataset':
                    year, month, day = [int(k) for k in node.getAttribute('Date').split('-')]
                    self.date = datetime.datetime(year, month, day)
                    print self.date
                if node.tagName in ('YahooCC', 'Yahoo'):
                    self.engine = 'Yahoo'
                    if 'CC' in node.tagName:
                        self.table = 'complex'
                    else:
                        self.table = 'simple'
                if node.tagName == 'AllTheWeb':
                    self.table = 'simple'
                    self.engine = 'All The Web'
                if node.tagName in ('GoogleCC', 'Google'):
                    self.engine = 'Google'
                    if 'CC' in node.tagName:
                        self.table = 'complex'
                    else:
                        self.table = 'simple'
                if node.tagName == 'Search':
                    events.expandNode(node)
                    hope = getText(node.childNodes)
                    if hope != '!':
                        val = int(hope)
                        license_uri = node.getAttribute('URL')
                        cc_spec = node.getAttribute('Rest')
                        query = node.getAttribute('Term')
                        if cc_spec or query: # This is how I detect YahooCC/GoogleCC
                            assert(query)
                            assert(self.table == 'complex')
                            self.lc.record_complex(license_specifier=cc_spec,
                                                   search_engine=self.engine,
                                                   count=val,
                                                   query=query)
                            # no country, no language
                        else:
                            assert(license_uri)
                            assert(self.table == 'simple')
                            self.lc.record(cc_license_uri=license_uri,
                                           search_engine=self.engine,
                                           count=val)
                            # no country, language
