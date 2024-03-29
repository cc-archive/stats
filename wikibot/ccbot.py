#!/usr/bin/env python
import sys
import os
import traceback
import httplib
import itertools
import mwclient

import config
import views
import linkback_reader
import ccquery
from utils import tries 

WIKI_HOST = 'monitor.creativecommons.org'
WIKI_PATH = '/'

BOT_NAME = 'CCStatsBot'
BOT_PASS = 'bhyccstatsbot'

DB_FILE = config.DB_FILE

class WikiBot(object):
    def __init__(self, filter = None):
        site = mwclient.Site(WIKI_HOST, WIKI_PATH)
        self.site = site
        self.login()
        if filter is None:
            filter = lambda x: True
        self.filter = filter
        return

    def login(self):
        self.site.login(BOT_NAME, BOT_PASS)
        return

    def upload(self, file_name, content, comment=''):
        
        print "Uploading file: ", file_name, "...",
        sys.stdout.flush()

        if isinstance(content, unicode):
            content = content.encode('utf8')
        site = self.site
        try:
            tries( 3, lambda: site.upload(content, file_name, comment, ignore=True) )
        except httplib.IncompleteRead:
            # The upload is success even we got an IncompleteRead
            pass
        try:
            uploaded = site.Images[file_name]
        except:
            # This will be failed... don't know why.
            pass
        uploaded = site.Images[file_name]

        print 'Done.'

        return uploaded

    def put_page(self, title, content):
        page = self.site.Pages[title]
        page.save(content)
        return page
    
    def get_page(self, title):
        page = self.site.Pages[title]
        return page

    def update_pages(self, pages):
        for page in pages:
            if not page.text:
                # Do nothing if the page content is empty
                continue
            if not self.filter(page):
                continue
            print "Updating page: ", page.title, "...",
            sys.stdout.flush()
            try:
                self.put_page(page.title, page.text)
                print "Done."
            #except mwclient.MwClientError:
            except:
                print "Error when updating page:"
                print '-'*60
                traceback.print_exc()
                print '-'*60
                # reset connection pool and continue to next task
                del self.site.connection[:]
                self.login()
        return

    def upload_files(self, files, seturl_callback):
        for file in files:
            if self.filter(file):
                uploaded = self.upload(file.title, file.text)
            else:
                uploaded = self.site.Images[file.title]
            url = uploaded.imageinfo[u'url']
            seturl_callback(file.title, url)
        return



def update_wiki(args = (), query=None):
    if query is None:
        query = ccquery.CCQuery(DB_FILE)

    # setup filter
    if args:
        if args[0]=='-x':
            exclude = True
            args = args[1:]
        else:
            exclude = False
        args = [a.lower() for a in args]
        def _filter(x):
            title = x.title.lower()
            for a in args:
                if a in title:
                    # return True if '-x' not set, otherwise False
                    return not exclude
            return exclude
    else:
        _filter = lambda x: True
    
    bot = WikiBot(filter=_filter)

    view = views.View(query)
    filegen = view.all_files()
    bot.upload_files(filegen, view.set_uploaded_url)

    pagegen = view.all_pages()
    bot.update_pages(pagegen)
    
    def new_userpages():
        pagegen = view.all_userpages()
        for page in pagegen:
            wikipage = bot.get_page(page.title)
            if not wikipage.exists:
                yield page
            else:
                print "Purging ", page.title
                wikipage.purge()
        return

    bot.update_pages(new_userpages())
    return

def update_wikiuserpages(query=None):
    if query is None:
        query = ccquery.CCQuery(DB_FILE)
    view = views.View(query)
    bot = WikiBot()
    print "WARNING: This operation is dangerous because it will overwite all existing user content. Please input 'YES I KNOW' to continue."
    know = raw_input()
    if know != 'YES I KNOW':
        return
    pagegen = view.all_userpages()
    bot.update_pages(pagegen)
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
    update_wiki(query = query)
    return

def _get_table_file(name):
    if name[-4:].lower()=='.csv':
        name = name[:-4]
    return name, name+'.csv'

def upload(*files):
    bot = WikiBot()
    for file in files:
        content = open(file, 'rb').read()
        upload_name = os.path.basename(file)

        bot.upload(upload_name, content)
    return

def export_db(table, file=None):
    if file is None:
        table, file = _get_table_file(table)
    q = ccquery.CCQuery(DB_FILE)
    q.export_table(table, open(file,'w'))
    return

def import_db(table, file=None):
    if file is None:
        table, file = _get_table_file(table)
    q = ccquery.CCQuery(DB_FILE)
    q.import_table(table, open(file))
    return

def test():
    bot = WikiBot()
    bot.put_page('Sandbox', 'Testing Sandbox.. by ccbot.py')

    TEST_XML = """<?xml version="1.0" encoding="utf-8"?>
<test123>
</test123>"""
    uploaded = bot.upload('test999.xml', TEST_XML, 'testing upload.. again and agina.')
    print "Info of uploaded test file:", uploaded.imageinfo

    print "Test OK!"

    return

def usage():
    print """
    ccbot.py [command] [args...]

    With no command, it will fetch most recently data and update both the DB and wiki.

    The followling command is available:

        db [<filter_filename>]: fetch the most recently data and update the DB. An optional
            jurisdiction filter filename can be provided. The filter is a list of
            jurisdictions one per line. Only the jurisdictions listed in this file will
            be updated. If this file is not given, the entire database will be updated.

        wiki [-x] [<keywords>...]: update the wiki pages from DB data. Only the pages which
            is used for robot produced contents will be updated. User produced contents will
            be untouched. If <keywords> is present, then only pages that contain at least one
            of the given keywords in title will be updated. If -x option is given, pages that
            contain given keywords in title will be excluded from update.

        upload: upload files to wiki.

        wikiuserpages: initialize all the user content pages. Warning: This will clean
            all the existing user contents.
        
        import <table> [<filename>]: import DB table from CSV file.

        export <table> [<filename>]: export DB table from CSV file.
        
        test: test the connection to wiki site.
    """

def main(*args):
    if len(args)==0:
        update_all()
    elif args[0]=='db':
        update_db(*args[1:])
    elif args[0]=='wiki':
        update_wiki(args[1:])
    elif args[0]=='upload':
        upload(*args[1:])
    elif args[0]=='wikiuserpages':
        update_wikiuserpages()
    elif args[0]=='import':
        import_db(*args[1:])
    elif args[0]=='export':
        export_db(*args[1:])
    elif args[0]=='test':
        test()
    else:
        usage()
    return
    

if __name__=='__main__':
    import sys
    main(*sys.argv[1:])
