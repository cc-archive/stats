import pdb
try:
    import psyco
except ImportError:
    pass
import pylab
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from matplotlib.dates import MONDAY, SATURDAY
import datetime
from sqlalchemy.ext.sqlsoup import SqlSoup
import sqlalchemy
import os
import pylab, matplotlib
# Jurisdictions
# for search_engine in 'Yahoo', 'Google', 'All The Web':
# select from simple where search_engine=search_engine
# and language=NULL and country=NULL

# FIXME: My HTML templating is pure evil.

# But how to count jurisidictions?
# I could manually regex against the database results.
# That's hilariously inefficient.

# But it works for now, I suppose.
# Something smarter would be to store this in the database.

# FIXME: This code assumes you're always looking at the "simple"
# table.  That's dumb.

# Note that it should only do this for a particular 
# run, not every single run.  Might as well get the 
# maximum value in that timestamp column to do the 
# latest.  Be sure to get that max separately per 
# search engine.

# FIXME: Move this somewhere I can use it later.
class ListCycle:
    def __init__(self, l):
        self.l = l
        self.index = 0
    def next(self):
        if self.index >= len(self.l):
            self.index = -1
        ret = self.l[self.index]
        self.index += 1
        return ret

BASEDIR='/home/paulproteus/public_html/tmp/'
def fname(s):
    return os.path.join(BASEDIR, s)

db = SqlSoup('mysql://root:@localhost/cc')
 
search_engines = ['Google', 'All The Web', 'Yahoo', 'MSN']
all_html_colors = [k.lower() for k in ['AliceBlue', 'AntiqueWhite', 'Aqua', 'Aquamarine', 'Azure', 'Beige', 'Bisque', 'Black', 'BlanchedAlmond', 'Blue', 'BlueViolet', 'Brown', 'BurlyWood', 'CadetBlue', 'Chartreuse', 'Chocolate', 'Coral', 'CornflowerBlue', 'Cornsilk', 'Crimson', 'Cyan', 'DarkBlue', 'DarkCyan', 'DarkGoldenRod', 'DarkGray', 'DarkGreen', 'DarkKhaki', 'DarkMagenta', 'DarkOliveGreen', 'Darkorange', 'DarkOrchid', 'DarkRed', 'DarkSalmon', 'DarkSeaGreen', 'DarkSlateBlue', 'DarkSlateGray', 'DarkTurquoise', 'DarkViolet', 'DeepPink', 'DeepSkyBlue', 'DimGray', 'DodgerBlue', 'Feldspar', 'FireBrick', 'FloralWhite', 'ForestGreen', 'Fuchsia', 'Gainsboro', 'GhostWhite', 'Gold', 'GoldenRod', 'Gray', 'Green', 'GreenYellow', 'HoneyDew', 'HotPink', 'IndianRed', 'Indigo', 'Ivory', 'Khaki', 'Lavender', 'LavenderBlush', 'LawnGreen', 'LemonChiffon', 'LightBlue', 'LightCoral', 'LightCyan', 'LightGoldenRodYellow', 'LightGrey', 'LightGreen', 'LightPink', 'LightSalmon', 'LightSeaGreen', 'LightSkyBlue', 'LightSlateBlue', 'LightSlateGray', 'LightSteelBlue', 'LightYellow', 'Lime', 'LimeGreen', 'Linen', 'Magenta', 'Maroon', 'MediumAquaMarine', 'MediumBlue', 'MediumOrchid', 'MediumPurple', 'MediumSeaGreen', 'MediumSlateBlue', 'MediumSpringGreen', 'MediumTurquoise', 'MediumVioletRed', 'MidnightBlue', 'MintCream', 'MistyRose', 'Moccasin', 'NavajoWhite', 'Navy', 'OldLace', 'Olive', 'OliveDrab', 'Orange', 'OrangeRed', 'Orchid', 'PaleGoldenRod', 'PaleGreen', 'PaleTurquoise', 'PaleVioletRed', 'PapayaWhip', 'PeachPuff', 'Peru', 'Pink', 'Plum', 'PowderBlue', 'Purple', 'Red', 'RosyBrown', 'RoyalBlue', 'SaddleBrown', 'Salmon', 'SandyBrown', 'SeaGreen', 'SeaShell', 'Sienna', 'Silver', 'SkyBlue', 'SlateBlue', 'SlateGray', 'Snow', 'SpringGreen', 'SteelBlue', 'Tan', 'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'VioletRed', 'Wheat', 'White', 'WhiteSmoke', 'Yellow', 'YellowGreen']]

# Thanks, Will.
# Needs tests.
urlParse_cache = {}
def urlParse(url):
    global urlParse_cache
    if url in urlParse_cache:
        return urlParse_cache[url]
    jurisdiction=''
    elements=url.split('/')
    if len(elements) >= 6:
        which=elements[4]
        if which=='publicdomain':
            which='pd'
        version=elements[5]
        if version=='':
            version='1.0'
        if len(elements)>6:
            jurisdiction=elements[6]
        if jurisdiction=='' or jurisdiction=='us' or jurisdiction=='deed-music':
            jurisdiction='generic'
        # attribs: if it's a CC license, then the list of CC attributes
        if which in ('GPL', 'LGPL', 'devnations', 'sampling', 'pd'): # How to handle PD later in later graphs?
            attribs = []
        else:
            if which in ('sampling+', 'nc-sampling+'):
               attribs = ['by','nc','nd']
            else:
               attribs = which.split('-')
            assert(('by' in attribs) or
                   ('nc' in attribs) or
                   ('nd' in attribs) or
                   ('sa' in attribs))
        # now canonicalize which
        whichparts = which.split('-')
        whichparts.sort()
        which = '-'.join(whichparts)
    else:
        which, version, jurisdiction, attribs = None, None, None, []
    ret = {'which': which, 'version': version, 'jurisdiction': jurisdiction, 'attribs': tuple(attribs)}
    urlParse_cache[url] = ret
    return ret

def get_all_urlParse_results(key, everything):
    ''' Neat for testing! '''
    ret = set()
    for r in [urlParse(k.license_uri)[key] for k in everything]:
        ret.add(r)
    return ret

def bar_chart(data, title,ylabel='',labelfmt='%1.1f'):
    labels = data.keys()
    values = [data[k] for k in labels]
    # Bar supports multiple, well, bars
    # So we could do all search engines at once if we wanted
    # But that's harder to integrate with for_search_engines
    # So forget it.
    ind = pylab.arange(len(values))  # the x locations for the groups
    width = 0.35       # the width of the bars
    pylab.p1 = pylab.bar(ind, values, width, color='r')
    
    pylab.ylabel(ylabel)
    pylab.title(title)
    pylab.xticks(ind+(width/2.0), labels)
    pylab.xlim(-width,len(ind))
    #pylab.yticks(pylab.arange(0,41,10))

    # Labels!
    for x,y in zip(xrange(len(values)), values):
        pylab.text(x+width/2., y, labelfmt % y, va='bottom', ha='center')
    
    pylab.savefig(fname(title))
    pylab.close()
    
    # http://matplotlib.sourceforge.net/screenshots/barchart_demo.py shows how to smarten the legend
    return title

def pie_chart(data, title):
    # make a square figure and axes
    pylab.figure(figsize=(8,8))

    # here's some fun: sort the labels by the values (-:
    data_unpacked = [ (data[key], key) for key in data ]
    data_unpacked.sort()

    fracs = [ datum[0] for datum in data_unpacked ]
    labels= [ datum[1] for datum in data_unpacked ]
    
    explode=[0.05 for k in labels]
    pylab.pie(fracs, explode=explode, labels=labels, autopct='%1.1f%%', shadow=False, colors=('b', 'g', 'r', 'c', 'm', 'y', 'w')) # pctradius=0.85

    ## I would have a legend, but they often overlap with the pie itself.
    #pylab.figlegend()
    #pylab.legend(prop=matplotlib.font_manager.FontProperties('x-small'))
    #leg = pylab.gca().get_legend()
    #ltext  = leg.get_texts()
    #pylab.setp(ltext, fontsize='small')
    #pylab.legend()

    pylab.title(title, bbox={'facecolor':'0.8', 'pad':5})
    pylab.savefig(fname(title))
    pylab.close() # This is key!
    return title

def min_date(engine, table):
    return sqlalchemy.select([sqlalchemy.func.min(table.c.timestamp)],
           table.c.search_engine==engine).execute().fetchone()[0]

def max_date(engine, table):
    return sqlalchemy.select([sqlalchemy.func.max(table.c.timestamp)],
           table.c.search_engine==engine).execute().fetchone()[0]

def date_chart_data(engine, table):
    s = sqlalchemy.select([sqlalchemy.func.sum(table.c.count), table.c.timestamp], table.c.search_engine == engine)
    s.group_by(table.c.timestamp)
    data = s.execute() # sum() returns a string, BEWARE!

    send_this = {}
    for datum in data:
        value, timestamp = datum
        value = int(value) # sqlalchemy bug: SUM() returns a string
        send_this[timestamp] = value
    return send_this

def date_chart(lots_of_data, title):
    """ data is now input as a dict that maps label -> a dict that maps dates to data
    So we can't guarantee the order of keys. """
    ax = pylab.subplot(111) # We're going to have a plot, okay?

    colors = ListCycle( ('b', 'g', 'r', 'c', 'm', 'y', 'k') )

    labels = []
    # We assume the date ranges are the same...
    for label in lots_of_data:
        data = lots_of_data[label]
        data_keys = data.keys()
        data_keys.sort()
        dates = [pylab.date2num(date) for date in data_keys]
        values = [data[date] for date in data_keys]

        # Calculate date delta to decide if later on we'll be in
        # months mode or years mode
        delta = data_keys[-1] - data_keys[0]
        labels.append(label)
        pylab.plot_date(dates, values, colors.next() + '-')
    pylab.legend(labels)

    # There is room for 15 month labels
    # Anything more and it's too squished
    # Meanwhile, want the month labels to happen on some factor of 12
    # So FIXME: let's calculate the smallest factor of 12 we can do this for

    rule = matplotlib.dates.rrulewrapper(matplotlib.dates.MONTHLY, interval=2)
    loc = matplotlib.dates.RRuleLocator(rule)
    formatter = matplotlib.dates.DateFormatter('%m/%y')
    

    years    = YearLocator()   # every year
    yearsFmt = DateFormatter('%Y')
    mondays   = pylab.WeekdayLocator(MONDAY)    # every monday
    months    = MonthLocator(range(1,13), bymonthday=1)           # every month
    monthsFmt = DateFormatter("%m/%y")

    # format the ticks
    if 1: # delta.days < 365:
        # months mode
        ax.xaxis.set_major_locator(loc)
        ax.xaxis.set_major_formatter(formatter)
        #ax.xaxis.set_minor_locator(mondays)
        ax.autoscale_view()
    else:
        # years mode
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(yearsFmt)
        ax.xaxis.set_minor_locator(months)
        ax.autoscale_view()

    locs, labels = pylab.xticks()
    pylab.setp(labels, fontsize=8)

    ax.format_xdata = DateFormatter('%Y-%m-%d')
    ax.format_ydata = lambda f: f
    pylab.title(title)
    pylab.grid(True)
    pylab.savefig(fname(title))
    pylab.close()
    return title

def property_counts(things):
    ''' Input: A subset of everything.
    Output: A hash of prop -> count, plus an extra "total"->total'''
    ret = {}
    for thing in things:
        props = urlParse(thing.license_uri)['attribs']
        for prop in props:
            ret[prop] = ret.get(prop, 0) + thing.count
        if props:
            ret['total'] = ret.get('total',0) + thing.count
            # Only bump total if there were really properties
    return ret

def license_counts(things):
    ''' FIXME: Poorly-named.
    Input: A subset of everything.
    Output: A hash of e.g. "by-sa" -> count, plus an extra "total" -> total'''
    ret = {}
    for thing in things:
        which = urlParse(thing.license_uri)['which']
        attribs = urlParse(thing.license_uri)['attribs']
        if attribs or (which == 'pd'):
            ret[which] = ret.get(which, 0) + thing.count
            ret['total'] = ret.get('total',0) + thing.count
    return ret

def get_all_most_recent(table, engine):
    recent_stamp = sqlalchemy.select([sqlalchemy.func.max(table.c.timestamp)]).execute().fetchone()[0]
    recent = sqlalchemy.select(table.columns, sqlalchemy.and_(table.c.timestamp == recent_stamp, table.c.search_engine == engine)).execute()
    return recent

def for_search_engine(chart_fn, data_fn, table):
    ret = []
    for engine in search_engines:
        data = data_fn(table, engine)
        ret.append(chart_fn(data, engine))
        # FIXME: May die if no hits from this engine?
    return ret

def flatten_small_percents(data, percent_floor):
    ''' Input: a dict that maps keys to number values.
    Output: A dict that has most of the same keys, but combines keys whose percent < percent_floor '''
    # Now flatten out everything < 0.5%
    ret = {}
    ret.update(data) # work on a copy!
    total = sum([ret[k] for k in ret])
    for k in ret.keys():
        if ret[k] <  (0.01 * percent_floor * total):
            ret['Other'] = ret.get('Other', 0) + data[k]
            del ret[k]
    return ret

def percentage_ify(fn, things):
    counts = fn(things)
    if not counts:
        return counts
    # Now flatten into percents
    for thing in counts.keys():
        if thing != 'total':
            # into percent:
            counts[thing] = (100.0 * counts[thing] / counts['total'])
    del counts['total']
    return counts    

def jurisdiction_pie_chart():
    def data_fn(table, engine):
        recent = get_all_most_recent(table, engine)
        # Okay, now gather the data.
        data = {}
        for event in recent:
            jurisdiction = urlParse(event.license_uri)['jurisdiction']
            if jurisdiction:
                data[jurisdiction] = data.get(jurisdiction, 0) + event.count
        data = flatten_small_percents(data, percent_floor=0.5)
        return data
    def chart_fn(data, engine):
        return pie_chart(data, "%s Jurisdiction data" % engine)

    return for_search_engine(chart_fn, data_fn, db.simple)

def exact_license_pie_chart():
    def data_fn(table, engine):
        recent = get_all_most_recent(table, engine)
        percents = percentage_ify(license_counts, recent)
        better = flatten_small_percents(percents, percent_floor=0.2)
        return better
    def chart_fn(data, engine):
        return pie_chart(data, "%s exact license distribution" % engine)
    return for_search_engine(chart_fn, data_fn, db.simple)

def simple_aggregate_date_chart():
    def data_fn(table, engine):
        return {'Total linkbacks': date_chart_data(engine, table)}
    def chart_fn(data, engine):
        return date_chart(data, "%s total linkbacks line graph" % engine)
    return for_search_engine(chart_fn, data_fn, db.simple)

def data2htmltable(data, formatstring = '%1.1f%%'):
    ''' Input: data is a mapping from license identifiers to
    (percent, jurisdiction) pairs.
    Output: HTML. '''
    licenses = data.keys()
    licenses.sort() # 'by' first, etc.
    ret = '' # FIXME: Evil HTML creation
    for l in licenses:
        ret += '<table border=1 style="float: left;">'
        ret += '<caption>%s</caption>' % l
        for percent, jurisdiction in data[l]:
            ret += ('<tr><td>%s</td><td>' + formatstring + '</td></tr>') % (jurisdiction, percent)
        ret += '</table>'
    return ret

def data_for_tables_at_bottom(table, engine):
    engine = 'Yahoo' # FIXME: Hard-coding an engine because otherwise I have to make decisions ASKMIKE
    # about statistics otherwise
    recent = get_all_most_recent(table, engine)
    # Going to implement this the slow way
    # because our database is too dumb

    # Get all known jurisdictions
    all_jurisdictions = get_all_urlParse_results('jurisdiction', recent)

    data = {}
    for jur in all_jurisdictions:
        just_jur = [k for k in recent if urlParse(k.license_uri)['jurisdiction'] == jur]
        jur_percents = percentage_ify(license_counts, just_jur)
        data[jur] = jur_percents

    # Now we turn the data inside-out
    ret = {} # A map from "by-nd" to [(86.7, 'Generic'), (94.2, 'kr'), ...]
    for jur in data:
        for license_tag in data[jur]:
            percent = data[jur][license_tag]
            pair = (percent, jur)
            if license_tag in ret:
                ret[license_tag].append(pair)
            else:
                ret[license_tag] = [pair]

    # Now sort this mess
    for license_tag in ret:
        ret[license_tag].sort()
        ret[license_tag].reverse()
    return ret
    
def property_bar_chart():
    def data_fn(table, engine):
        recent = get_all_most_recent(table, engine)
        return percentage_ify(property_counts, recent)
    
    def chart_fn(data, engine):
        return bar_chart(data, "%s property bar chart" % engine, 'Percent of total','%1.1f%%')
    return for_search_engine(chart_fn, data_fn, db.simple)

def main():
    ''' Current goal: Emulate existing stats pages. '''
    filenames = []
    # First, generate all the graphs
    filenames.extend(simple_aggregate_date_chart())
    filenames.extend(specific_license_date_chart())
    filenames.extend(exact_license_pie_chart())
    filenames.extend(property_bar_chart())
    filenames.extend(jurisdiction_pie_chart())
    filenames.extend(license_versions_date_chart())
    # Now make a trivial HTML page
    filenames.sort()
    html = '<html><body>'
    for f in filenames:
        html += '<img src="%s.png" /><br />' % f

    html += data2htmltable(data_for_tables_at_bottom(db.simple, 'Yahoo'))
    
    html += '</body></html>'
    fd = open(os.path.join(BASEDIR, 'index.html'), 'w')
    fd.write(html)
    fd.close()

def aggregate_for_date_chart(table, engine, fn):
    ''' Input: table and engine, plus a fn for determing keys
    Output: {fn-return-val1: {date: val, date:val, ...} '''
    # It is impossible to implement this fully cleanly because
    # the license tag data we want is not available in the database. :-(
    query = sqlalchemy.select([sqlalchemy.func.sum(table.c.count), table.c.timestamp, table.c.license_uri], table.c.search_engine == engine)
    query.group_by(table.c.license_uri)
    query.group_by(table.c.timestamp)
    data = {} # a mapping of 'by' -> {date: num, date: num, ...}
    for datum in query.execute():
        name = fn(datum)
        if name:
            if name not in data:
                data[name] = {}
            data[name][datum.timestamp] = int(datum[0])
    return data

def license_versions_date_chart():
    def data_fn(table, engine):
        def fn(datum):
            v = urlParse(datum.license_uri)['version']
            if v:
                return v
            #print 'YOW, VERSIONLESS', datum.license_uri
            #print 'on', datum.timestamp
            return None # fall-through for explicitness' sake
        return aggregate_for_date_chart(table, engine, fn)
    def chart_fn(data, engine):
        return date_chart(data, "%s linkbacks per license version" % engine)
    return for_search_engine(chart_fn, data_fn, db.simple)

def specific_license_date_chart():
    def data_fn(table, engine):
        def fn(datum):
            attribs = urlParse(datum.license_uri)['attribs']
            which = urlParse(datum.license_uri)['which']
            if attribs or (which == 'pd'):
                return which
            return None # fall-through for explicitness
        return aggregate_for_date_chart(table, engine, fn)
    def chart_fn(data, engine):
        return date_chart(data, "%s linkbacks per license" % engine)
    return for_search_engine(chart_fn, data_fn, db.simple)

if __name__ == '__main__':
    main()
    

