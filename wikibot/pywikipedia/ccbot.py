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
    pagegens = itertools.chain(
            view.stats_world(),
            view.stats_juris(),
            view.list_juris(),
            )
    for page in pagegens:
        print "Updating page: ", page.title
        wikipage = wikipedia.Page(site, page.title)
        wikipage.put(page.text, "Updated by ccbot.py - testing.")
    return

def test():
    site = wikipedia.getSite()
    page = wikipedia.Page(site, u'Sandbox')
    page.put(u'Hello, world! This is from ccbot.py')
    return

if __name__=='__main__':
    #test()
    run()

