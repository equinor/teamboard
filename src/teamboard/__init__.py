import calendar
import datetime
import logging
import pytz
import dateutil.parser
import os

# create logger

logger = logging.getLogger('teamboard_logger')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

logger.addHandler(ch)

logger.info("Logging initialized!")


def teamboard_logger():
    """
    :rtype: logging.Logger
    """
    return logging.getLogger('teamboard_logger')


def get_env(name, default_value):
    value = os.getenv(name)

    if value is None:
        teamboard_logger().info("%s not set! Using '%s' as default." % (name, default_value))
        value = default_value
    else:
        teamboard_logger().info("%s set to '%s'" % (name, value))

    return value


# Borrowed from Django

TIMESINCE_CHUNKS = (
    (60 * 60 * 24 * 365, ('%d year', '%d years')),
    (60 * 60 * 24 * 30, ('%d month', '%d months')),
    (60 * 60 * 24 * 7, ('%d week', '%d weeks')),
    (60 * 60 * 24, ('%d day', '%d days')),
    (60 * 60, ('%d hour', '%d hours')),
    (60, ('%d minute', '%d minutes'))
)

# UTC time zone as a tzinfo instance.
utc = pytz.utc


def is_aware(value):
    """
    Determine if a given datetime.datetime is aware.
    The concept is defined in Python's docs:
    http://docs.python.org/library/datetime.html#datetime.tzinfo
    Assuming value.tzinfo is either None or a proper datetime.tzinfo,
    value.utcoffset() implements the appropriate logic.
    """
    return value.utcoffset() is not None


def avoid_wrapping(value):
    """
    Avoid text wrapping in the middle of a phrase by adding non-breaking
    spaces where there previously were normal spaces.
    """
    return value.replace(" ", "\xa0")


def timesince(d, now=None, reversed=False):
    """
    Take two datetime objects and return the time between d and now as a nicely
    formatted string, e.g. "10 minutes". If d occurs after now, return
    "0 minutes".
    Units used are years, months, weeks, days, hours, and minutes.
    Seconds and microseconds are ignored.  Up to two adjacent units will be
    displayed.  For example, "2 weeks, 3 days" and "1 year, 3 months" are
    possible outputs, but "2 weeks, 3 hours" and "1 year, 5 days" are not.
    Adapted from
    http://web.archive.org/web/20060617175230/http://blog.natbat.co.uk/archive/2003/Jun/14/time_since
    """
    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    if not now:
        now = datetime.datetime.now(utc if is_aware(d) else None)

    if reversed:
        d, now = now, d
    delta = now - d

    # Deal with leapyears by subtracing the number of leapdays
    leapdays = calendar.leapdays(d.year, now.year)
    if leapdays != 0:
        if calendar.isleap(d.year):
            leapdays -= 1
        elif calendar.isleap(now.year):
            leapdays += 1
    delta -= datetime.timedelta(leapdays)

    # ignore microseconds
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        # d is in the future compared to now, stop processing.
        return avoid_wrapping('0 minutes')

    for i, (seconds, name) in enumerate(TIMESINCE_CHUNKS):
        count = since // seconds
        if count != 0:
            break


    result = avoid_wrapping(name[1] % count if count > 1 else name[0] % count)
    if i + 1 < len(TIMESINCE_CHUNKS):
        # Now get the second item
        seconds2, name2 = TIMESINCE_CHUNKS[i + 1]
        count2 = (since - (seconds * count)) // seconds2
        if count2 != 0:
            result += ', ' + avoid_wrapping(name2[1] % count2 if count2 > 1 else name2[0] % count2)
    return result


def timeuntil(d, now=None):
    """
    Like timesince, but return a string measuring the time until the given time.
    """
    return timesince(d, now, reversed=True)


def pretty_date_since(isodatestr):
    return timesince(dateutil.parser.parse(isodatestr))
