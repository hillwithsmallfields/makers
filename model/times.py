from __future__ import print_function

if __name__ == "__main__":
    import sys
    sys.path.append('..')    # for running tests

from datetime import datetime, timedelta, timezone
import model.configuration
import pytz
import re

# todo: event templates to have after-effect fields, so that cancellation of membership can schedule cancellation of equipment training

# Use this version on Python >= 3.7:
# def as_time(clue):
#     # todo: parse it as a local time, but return result in UTC
#     return (clue
#             if isinstance(clue, datetime)
#             else (datetime.fromordinal(clue)
#                   if isinstance(clue, int)
#                   else (datetime.fromisoformat(clue)
#                         if isinstance(clue, str)
#                         else None)))

organizational_timezone = pytz.timezone(model.configuration.get_config('organization', 'timezone'))

fulltime = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}")

def as_time(clue):
    # print("as_time parsing", clue)
    if clue is None or clue == "":
        return now() + timedelta(1, 0) # default to this time tomorrow, just so there is a default
    return (clue
            if isinstance(clue, datetime)
            else (datetime.fromordinal(clue)
                  if isinstance(clue, int)
                  else (datetime.strptime(clue, "%Y-%m-%dT%H:%M"
                                          if fulltime.match(clue)
                                          else "%Y-%m-%d").replace(tzinfo=organizational_timezone)
                        if isinstance(clue, str)
                        else None)))

def in_minutes(clue):
    if type(clue) == int:
        return clue
    parts = clue.split(':')
    return int(parts[0]) if len(parts) == 1 else ((int(parts[0]) * 60) + int(parts[1]))

def in_seconds(clue):
    return in_minutes(clue) * 60

def timestring(when):
    # print("timestring called with", when)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
        # print("timestring set tz to utc, producing", when)
    if when.hour == 0 and when.minute == 0 and when.second == 0:
        # print("timestring returning", str(when.date()))
        return str(when.date())
    else:
        when.replace(microsecond=0)
        if when.second >= 59:
            when.replace(minute=when.minute + 1)
            when.replace(second=0)
        # print("timestring returning", when.astimezone(organizational_timezone).isoformat()[:16])
        return when.astimezone(organizational_timezone).isoformat()[:16]

def now():
    return datetime.utcnow().replace(tzinfo=timezone.utc)

def format_now(fmt):
    """Apply datetime.strftime to the current time."""
    return now().strftime(fmt)

def as_utc(when):
    return (when
            if when.tzinfo
            else when.replace(tzinfo=timezone.utc)).astimezone(pytz.timezone('utc'))

def test_times():
    our_now = now()
    print("our now is", our_now)
    our_now_output = timestring(our_now)
    print("as timestring, that is", our_now_output)
    print("")
    sample_input = "2018-04-18T18:00"
    sample_as_time = as_time(sample_input)
    print("sample_as_time is", sample_as_time)
    sample_as_utc = as_utc(sample_as_time)
    print("sample_as_utc is", sample_as_time)
    sample_timestring = timestring(sample_as_time)
    print("sample_timestring is", sample_timestring)
    print("")
    for dur_string in ["20", "60", "80", "1:00", "1:20", "1:00:00", "1:20:00"]:
        dur = in_minutes(dur_string)
        print("string", dur_string, "reads as", dur, "minutes")
    pass

if __name__ == "__main__":
    test_times()
