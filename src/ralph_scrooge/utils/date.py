import datetime


def date_range(start, stop, step=datetime.timedelta(days=1)):
    """This function is similar to "normal" `range`, but it operates on dates
    instead of numbers. Taken from "Python Cookbook, 3rd ed.".
    """
    while start < stop:
        yield start
        start += step
