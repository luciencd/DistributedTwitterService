from datetime import datetime
from dateutil import tz
from dateutil.parser import parse

class EventTypes:
    BLOCK="block"
    UNBLOCK="unblock"
    TWEET="tweet"

class event:
    DELIM = ","
    def __init__(self,site,op,body,truetime,name,timestamp=-1):
        self.site = site
        self.op = op
        self.data = body
        self.timestamp = timestamp
        #when constructing this, assume the tweet's time is in UTC, and should be converted in the __str__ "view"
        self.truetime = truetime
        self.name = name

    def get_tweet(self):
        if(self.op == EventTypes.TWEET):
            return self.data
        else:
            return None

    def get_blocker(self):
        if(self.op == EventTypes.BLOCK or self.op == EventTypes.UNBLOCK):
            return int(self.data.split(event.DELIM)[0])
        else:
            return None

    def get_blocked(self):
        if(self.op == EventTypes.BLOCK or self.op == EventTypes.UNBLOCK):
            return int(self.data.split(event.DELIM)[1])
        else:
            return None

    def superceding_unblock_exists(self, event_list):
        linked_unblocks = list(filter(lambda e: e.site == self.site \
            and e.data == self.data \
            and e.op == EventTypes.UNBLOCK \
            and e.timestamp > self.timestamp \
            and self.op == EventTypes.BLOCK, event_list))

        return len(linked_unblocks) > 0

    def superceding_block_exists(self, event_list):
        linked_unblocks = list(filter(lambda e: e.site == self.site \
            and e.data == self.data \
            and e.op == EventTypes.BLOCK \
            and e.timestamp > self.timestamp \
            and self.op == EventTypes.UNBLOCK, event_list))

        return len(linked_unblocks) > 0



    def __str__(self):
        localtime = parse(self.truetime).astimezone(tz.tzlocal())
        return "{} by {} at {}:\n   {}".format(self.op.title(),self.name,localtime.strftime('%Y-%m-%d %H:%M:%S'),self.data)
