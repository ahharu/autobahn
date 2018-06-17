import calendar

def UTC_time_to_epoch(timestamp):
    epoch = calendar.timegm(timestamp.utctimetuple())
    return epoch