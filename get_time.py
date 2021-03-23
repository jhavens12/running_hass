#v3.0 - updated for multi-year support
import time
import datetime
import calendar
from datetime import date
from dateutil.relativedelta import relativedelta, MO, SU
##

def now():
    return datetime.datetime.now()

def forever():
    return datetime.datetime(year=2016, month=1, day=1)

def FOM(x): #updated #0 is this month?
    #first of month
    #start of day
    now = datetime.datetime.now()
    months_ago = now - relativedelta(months=x) #subtract x months
    return datetime.datetime(months_ago.year, months_ago.month, 1) #returns months ago year and month, but day 1

def LOM(x): #updated
    #last of month
    #end of day
    now = datetime.datetime.now()
    months_ago = now - relativedelta(months=x-1) #subtract x months + 1
    return datetime.datetime(months_ago.year, months_ago.month, 1, hour=23, minute=59, second=59) - (datetime.timedelta(days=1))

def FOY(): #should be good
    #first of year
    #start of day
    now = datetime.datetime.now()
    return datetime.datetime(now.year, 1, 1)

def LM(x): #updated
    #last monday
    #start of day
    now = datetime.datetime.now()
    now2 = datetime.datetime(now.year, now.month, now.day, hour=00, minute=00, second=00)
    past = now2 - relativedelta(weeks=x)
    return past - datetime.timedelta(days=now2.weekday())

def LS(x): #works
    #last sunday
    #end of day
    now = datetime.datetime.now()
    date = datetime.datetime(now.year, now.month, now.day, hour=23, minute=59, second=59)
    return date - datetime.timedelta(weeks=x, days=now.weekday()+1,)

def LS_S(x): #works
    #last sunday
    #start of day
    now = datetime.datetime.now()
    date = datetime.datetime(now.year, now.month, now.day, hour=0, minute=0, second=0)
    return date - datetime.timedelta(weeks=x, days=now.weekday()+1,)

def running_week(x): #updated to show 0 is 0 weeks, not 1 week
    #running week start
    #down to hour
    w = x-1
    now = datetime.datetime.now()
    return now - datetime.timedelta(weeks=w, days=+7)

def running_thirty(x): #updated to show 0 is 0 30 days, not 1 30 days
    #30 days ago start
    #down to hour
    w = x-1
    now = datetime.datetime.now()
    return now - datetime.timedelta(weeks=(4*w), days=+30)

def add_day(given_date,x):
    #adds x days to given day
    return given_date + datetime.timedelta(days=1*x)

def day(x):
    #x days ago
    #down to hour
    now = datetime.datetime.now()
    return now - datetime.timedelta(days=x)

def weekday(x):
    return calendar.day_name[x.weekday()]

def what_month(x): #takes 1-12 as input, not datetime
    return calendar.month_name[x]

def difference_days(time1,time2):
    if time1 > time2:
        newer_time = time1
        older_time = time2
    if time2 > time1:
        older_time = time1
        newer_time = time2
    delta = newer_time - older_time
    return delta.days

def difference_minutes(time1,time2):
    if time1 > time2:
        newer_time = time1
        older_time = time2
    if time2 > time1:
        older_time = time1
        newer_time = time2
    delta = newer_time - older_time
    return delta

def convert_weekday_full(i):
    return str(calendar.day_name[i.weekday()])+" "+str(calendar.month_name[i.month])+" "+str(i.day)

def convert_weekday_short(i): #pulled from get_data - used to create activity short dates
    return str(calendar.day_abbr[i.weekday()])+" "+str(calendar.month_abbr[i.month])+" "+str(i.day)

def convert_month_name(i):
    return str(calendar.month_name[i.month])

def convert_year_name(i):
    return str(i.year)

def PFOY():
    #first of last year
    #start of day
    now = datetime.datetime.now()
    return datetime.datetime((now.year-1), 1, 1)
