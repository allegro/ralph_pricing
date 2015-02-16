# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import time
from logging.handlers import TimedRotatingFileHandler


class DirectoryTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    Timed Rotating File Handler with saving files to date / time directory
    instead of adding suffix with date / time to log file.

    Based totally on TimedRotatingFileHandler, instead of rollovering log file.
    """
    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)

        # diff
        dirName, baseName = os.path.split(self.baseFilename)
        time_directory = os.path.join(
            dirName,
            time.strftime(self.suffix, timeTuple)
        )
        dfn = os.path.join(time_directory, baseName)
        if not os.path.exists(time_directory):
            os.mkdir(time_directory)
        # end of diff

        if os.path.exists(dfn):
            os.remove(dfn)
        # Issue 18940: A file may not have been created if delay is True.
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, dfn)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        # python <2.7.6 fix - there is no delay attribute
        if not hasattr(self, 'delay') or not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (
            (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not
            self.utc
        ):
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:
                    addend = -3600
                else:
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt
