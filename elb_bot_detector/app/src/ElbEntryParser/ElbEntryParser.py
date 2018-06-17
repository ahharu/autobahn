import logging
import re

class ElbEntryParser():

    @staticmethod
    def parseline(line):
        regex = r'([^ ]*) ([^ ]*) ([^ ]*):([0-9]*) ([^ ]*)[:\-]([0-9]*) ([-.0-9]*) ([-.0-9]*) ([-.0-9]*) (|[-0-9]*) (-|[-0-9]*) ([-0-9]*) ([-0-9]*) \"([^ ]*) ([^ ]*) (- |[^ ]*)\" \"([^$]*)\" ([A-Z0-9-]+) ([A-Za-z0-9.-]*)'
        parsed = re.findall(regex, line.rstrip())
        if len(parsed[0]) < 17:
            logging.getLogger().warning("Could not parse line {}".format(line))
        return parsed[0][2], parsed[0][0], parsed[0][16] , parsed[0][14]