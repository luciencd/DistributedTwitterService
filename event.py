
class EventTypes:
    BLOCK="block"
    UNBLOCK="unblock"
    TWEET="tweet"

class event:
    DELIM = ","
    def __init__(self,site,op,body,truetime,timestamp=-1):
        self.site = site
        self.op = op
        self.data = body
        ##need to change timestamp to actual time.
        self.timestamp = timestamp
        self.truetime = truetime

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

    def related_unblock_exists(self, event_list):
        linked_unblocks = list(filter(lambda e: e.site == self.site \
            and e.data == self.data \
            and e.op == EventTypes.UNBLOCK \
            and self.op == EventTypes.BLOCK, event_list))

        return len(linked_unblocks) > 0


    def __str__(self):
        return "{} by {} at {}:\n   {}".format(self.op.title(),self.site,self.truetime,self.data)
