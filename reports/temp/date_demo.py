#!/usr/bin/env python
"""
Show how to make date plots in matplotlib using date tick locators and
formatters.  See major_minor_demo1.py for more information on
controlling major and minor ticks

All matplotlib date plotting is done by converting date instances into
days since the 0001-01-01 UTC.  The conversion, tick locating and
formatting is done behind the scenes so this is most transparent to
you.  The dates module provides several converter functions date2num
and num2date

This example requires an active internet connection since it uses
yahoo finance to get the data for plotting
"""

# Set up data
from sqlalchemy.ext.sqlsoup import SqlSoup
from sqlalchemy import *
db = SqlSoup('mysql://root:@localhost/cc')

ENGINE='Yahoo'
def min_date():
    return select([func.min(db.simple.c.timestamp)],
           db.simple.c.search_engine==ENGINE).execute().fetchone()[0]

def max_date():
    return select([func.max(db.simple.c.timestamp)],
           db.simple.c.search_engine==ENGINE).execute().fetchone()[0]

def get_data():
    s = select([func.sum(db.simple.c.count), db.simple.c.timestamp])
    s.group_by(db.simple.c.timestamp)
    return s.execute().fetchall() # sum() returns a string, BEWARE!

everything = db.simple.select(
    and_(db.simple.c.timestamp != None,
         db.simple.c.search_engine == ENGINE))

from pylab import *
from matplotlib.finance import quotes_historical_yahoo
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from matplotlib.dates import MONDAY, SATURDAY
import datetime
date1 = min_date()
date2 = max_date()

assert(date2 >= date1)
delta = date2 - date1

years    = YearLocator()   # every year
yearsFmt = DateFormatter('%Y')
mondays   = WeekdayLocator(MONDAY)    # every monday
months    = MonthLocator(range(1,13), bymonthday=1)           # every month
monthsFmt = DateFormatter("%b '%y")

data = get_data()

quotes = quotes_historical_yahoo(
    'INTC', date1, date2)
if not quotes:
    raise SystemExit

dates = [date2num(q[1]) for q in data]
opens = [int(q[0]) for q in data]

print dates
print opens
ax = subplot(111)
plot_date(dates, opens, '-')

# format the ticks
if delta.days < 365:
    # months mode
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(monthsFmt)
    ax.xaxis.set_minor_locator(mondays)
    ax.autoscale_view()
else:
    # years mode
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)
    ax.autoscale_view()

# format the coords message box
def price(x): return '$%1.2f'%x
ax.format_xdata = DateFormatter('%Y-%m-%d')
ax.format_ydata = price

grid(True)
show()
