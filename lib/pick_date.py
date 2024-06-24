import datetime
import lib.posting_config

default_config = lib.posting_config.default_config

def next_meetup_date(config=default_config):
    return next_meetup_date_testable(config, datetime.datetime.now())

def next_meetup_date_testable(config, dt):
    d = dt.date()
    if dt.time() > datetime.time(hour=18): # if it's 6 PM or later
        d += datetime.timedelta(days=1) # then don't schedule it for today
    day_number = config.get("weekday_number")
    if day_number is None:
        raise Exception("Day of the week must be specified")
    return next_weekday(d, day_number)

def next_weekday(d, weekday):
    target_day = d.weekday()+1
    days_ahead = weekday - target_day
    if days_ahead < 0:  # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


