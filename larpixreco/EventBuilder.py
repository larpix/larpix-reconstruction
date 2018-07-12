from larpixreco.types import Hit, Event
from larpixreco.HitParser import HitParser
from larpixreco.RecoLogging import getLogger
logger = getLogger(__name__)

class EventBuilder(object):
    max_ev_len = 5000
    min_ev_len = 5
    dt_cut = int(10e3) # ns

    def __init__(self, filename, sort_buffer_length=100):
        self.filename = filename
        self.data = HitParser(filename, sort_buffer_length=sort_buffer_length)
        self.curr_evid = 0
        self.events = []

    @staticmethod
    def is_associated(hit, hits_to_compare):
        ''' Check if hit should be associated with a list of hits '''
        if not EventBuilder.is_consecutive(hit, hits_to_compare):
            return False
        return True

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

    @staticmethod
    def is_event(hits):
        if len(hits) < EventBuilder.min_ev_len:
            return False
        return True

    def reset(self):
        ''' Resets internal loop to start of file '''
        self.curr_evid = 0
        self.events = []

    def clear(self):
        ''' Resets the events list without changing the position in the file '''
        self.events = []

    def store_new_event(self, hits):
        event = Event(evid=self.curr_evid, hits=hits)
        self.events += [event]
        self.curr_evid += 1
        return event

    def get_next_event(self):
        ''' Parse data file until a new event is found '''
        hits = []
        while len(hits) < EventBuilder.max_ev_len:
            curr_hit = self.data.get_next_sorted_hit()
            if EventBuilder.is_associated(curr_hit, hits):
                # hit should be associated with others -> store and continue
                hits.append(curr_hit)
            elif EventBuilder.is_event(hits):
                # collected hits are an event -> return
                return self.store_new_event(hits=hits)
            else:
                hits = []
            
            if curr_hit is None:
                break

        if EventBuilder.is_event(hits):
            # remaining hits are an event -> return
            return self.store_new_event(hits=hits)
        else:
            return None

