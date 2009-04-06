#!/usr/bin/env python
import sys
import httplib
import itertools
import mwclient

import views
import linkback_reader
import ccquery
from utils import tries 

WIKI_HOST = 'monitor.creativecommons.org'
WIKI_PATH = '/'
BOT_NAME = 'CCStatsBot'
BOT_PASS = 'bhyccstatsbot'

DB_FILE = 'ccdata.sqlite'


class WikiBot(object):
    def __init__(self):
        site = mwclient.Site(WIKI_HOST, WIKI_PATH)
        site.login(BOT_NAME, BOT_PASS)
        self.site = site
        return

    def upload(self, file_name, content, comment=''):
        if isinstance(content, unicode):
            content = content.encode('utf8')
        site = self.site
        try:
            site.upload(content, file_name, comment, ignore=True)
        except httplib.IncompleteRead:
            # The upload is success even we got an IncompleteRead
            pass
        uploaded = site.Images[file_name]
        return uploaded

    def put_page(self, title, content):
        page = self.site.Pages[title]
        page.save(content)
        return page
    
    def get_page(self, title):
        page = self.site.Pages[title]
        return page

def update_wiki(query=None):
    if query is None:
        query = ccquery.CCQuery(DB_FILE)
    bot = WikiBot()
    view = views.View(query)
    filegen = view.all_files()
    for file in filegen:
        print "Uploading file: ", file.title, "...",
        sys.stdout.flush()
        uploaded = bot.upload(file.title, file.text)
        url = uploaded.imageinfo[u'url']
        print "Done. URL: ", url
        view.set_uploaded_url(file.title, url)

    pagegen = view.all_pages()
    for page in pagegen:
        print "Updating page: ", page.title, "...",
        sys.stdout.flush()
        bot.put_page(page.title, page.text)
        print "Done."
    return

def update_db(filter_filename=None):
    data = linkback_reader.most_recent()
    query = ccquery.CCQuery(DB_FILE)

    if filter_filename is not None:
        juris_filter = set(line.strip().lower() for line in open(filter_filename))
        data = itertools.ifilter(lambda x: x[5] in juris_filter, data)
        for juris in juris_filter:
            query.del_linkbacks(juris)
    else:
        query.del_all_linkbacks()
    query.add_linkbacks(data)
    return query

def update_all():
    query = update_db()
    update_wiki(query)
    return

def test():
    bot = WikiBot()
    bot.put_page('Sandbox', 'HIHIHIHIHI')

    TEST_XML = """<?xml version="1.0" encoding="utf-8"?>
#<test33>
#</test33>"""
    uploaded = bot.upload('test88.xml', TEST_XML, 'testing upload.. again.')
    print "Info of uploaded test file:", uploaded.imageinfo

    print "Test OK!"

    return

def usage():
    print """
    ccbot.py [command] [args...]

    With no command, it will fetch most recently data and update both the DB and wiki.

    The followling command is available:

        db: fetch the most recently data and update the DB. An optional jurisdiction
            filter filename can be provided. The filter is a list of jurisdictions
            one per line. Only the jurisdictions listed in this file will be updated.
            If this file is not given, the entire database will be updated.

        wiki: update the wiki from DB data.
        
        test: test the connection to wiki site.
    """

def main(*args):
    if len(args)==0:
        update_all()
    elif args[0]=='db':
        update_db()
    elif args[0]=='wiki':
        update_wiki()
    elif args[0]=='test':
        test()
    else:
        usage()
    return
    

if __name__=='__main__':
    import sys
    main(*sys.argv[1:])
