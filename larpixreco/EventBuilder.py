from larpixreco.types import Hit, Event
from larpixreco.HitParser import HitParser

class EventBuilder(object):
    max_ev_len = 5000
    min_ev_len = 5
    dt_cut = int(10e3) # ns

    def __init__(self, filename):
        self.filename = filename
        self.data = HitParser(filename)
        self.curr_idx = 0
        self.curr_evid = 0
        self.events = []

    @staticmethod
    def is_consecutive(hit, hits_to_compare):
        ''' Check if hit is within `EventBuilder.dt_cut` of any hit in list '''
        if hit is None:
            return False
        elif len(hits_to_compare) == 0:
            return True
        for comp_hit in hits_to_compare:
            if abs(hit.ts - comp_hit.ts) < EventBuilder.dt_cut:
                return True
        return False

    def get_next_event(self):
        ''' Parse data file until a new event is found '''
        hits = []
        while len(hits) < EventBuilder.max_ev_len:
            curr_hit = self.data.get_hit(self.curr_idx)
            if EventBuilder.is_consecutive(curr_hit, hits):
                # hit is near others (in time) -> store and continue
                hits.append(curr_hit)
            elif len(hits) >= EventBuilder.min_ev_len:
                # collected hits are an event -> return
                event = Event(evid=self.curr_evid, hits=hits)
                self.events.append(event)
                self.curr_evid += 1
                return event
            else:
                hits = []
            
            if curr_hit is None:
                break
            self.curr_idx += 1

        if len(hits) >= EventBuilder.min_ev_len:
            event = Event(evid=self.curr_evid, hits=hits)
            self.events.append(event)
            self.curr_evid += 1
            return event
        else:
            return None

