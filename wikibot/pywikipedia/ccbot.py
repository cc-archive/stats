#!/usr/bin/env python
import sys
import os.path
sys.path.append( os.path.dirname( os.path.dirname(__file__) ) ) #parent dir of this file

import itertools
import wikipedia

import views


def run():
    site = wikipedia.getSite()
    view = views.View()
    pagegen = view.all_pages()
    for page in pagegen:
        print "Updating page: ", page.title, "...",
        sys.stdout.flush()
        wikipage = wikipedia.Page(site, page.title)
        oldpage = wikipage.get()
        if page.text <> oldpage:
            wikipage.put(page.text, "Updated by ccbot.py - testing.")
            print "Done."
        else:
            print "Same as old page, skipped."
    return

def test():
    site = wikipedia.getSite()
    page = wikipedia.Page(site, u'Sandbox')    
    page.put(u'Hello, world! This is from ccbot.py')
    return

if __name__=='__main__':
    #test()
    run()

