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

class EventBuilder_t0(EventBuilder):

    def __init__(self, filename, sort_buffer_length=100):
         EventBuilder.__init__(self, filename, sort_buffer_length=100)
         self.t0events = []

    def store_t0_new_event(self, event, t0):
        '''Stores events with external triggers'''
        new_event = Event(evid=event.evid, hits=event.hits, t0=t0)
        self.t0events.append(new_event)
        return new_event


    def get_next_event(self):
        '''Pairs events with external triggers'''
        hits = []
        while len(hits) < EventBuilder.max_ev_len:
            curr_hit = self.data.get_next_sorted_hit()
            if EventBuilder.is_associated(curr_hit, hits):
                # hit should be associated with others -> store and continue
                hits.append(curr_hit)
            elif EventBuilder.is_event(hits):
                # collected hits are an event -> return
                curr_event = self.store_new_event(hits=hits)
                new_t0 = self.t0(curr_event)
                if new_t0 == 1523897644915508880:
                    print(curr_event)
                else:
                    pass
                #print(new_t0)
                if not new_t0 == None:
                    trigger_delay = 997000 #ns
                    max_drift_time = 100000 #ns
                    t0_max = new_t0 - (trigger_delay - max_drift_time)
                    t0_min = new_t0 - trigger_delay
                    for i,event in enumerate(self.events):
                        if event.ts_start >= t0_min and event.ts_start <= t0_max:
                            self.store_t0_new_event(event, new_t0)
                            return self.t0events[-1]
                            hits = []
                        else:
                            hits = []
                            pass
                else:
                    hits = []

            else:
                hits = []

            if curr_hit is None:
                break

        if EventBuilder.is_event(hits):
            # remaining hits are an event -> return
            return self.store_new_event(hits=hits)
        else:
            return None


    def t0(self, event):
        '''Finds external triggers in events'''
        hits = event.hits
        #print(event)
        timestamps = []
        temp_list = []
        i = 0
        while True:
            #print(i, hits[i].channelid,hits[i].chipid)
            if hits[i].channelid == 7:
                if (len(hits) - i) >= 15:
                    temp_list.extend((hits[i].channelid,hits[i+1].channelid,hits[i+2].channelid,hits[i+3].channelid,hits[i+4].channelid,hits[i+5].channelid,hits[i+6].channelid,hits[i+7].channelid,hits[i+8].channelid,hits[i+9].channelid,hits[i+10].channelid,hits[i+11].channelid,hits[i+12].channelid,hits[i+13].channelid,hits[i+14].channelid))
                else:
                    break
            else:
                pass
            if temp_list == [7]*15:
                timestamps.append(hits[i].ts)
                #print(timestamps)
                i += 15
                temp_list = []
            else:
                temp_list = []
            i += 1
            if i >= len(hits): break

        if timestamps == []:
            return None
        else:
            return timestamps[0]



'''TEST'''
'''
if __name__ == '__main__':
    eb = EventBuilder_t0('../../larpix-scripts/datalog_2018_04_16_18_53_30_CEST_.h5',
                         sort_buffer_length=5000)
    event = None
    counter = 0
    while True:
        event = eb.get_next_event()
        #print(eb.t0events)
        if event is None:
            break
        else:
            counter += 1
    #print(eb.events)
    for event in eb.t0events[0:4]:
        print(event)
        #print(event.t0)
    print(len(eb.t0events))
    #print(counter)

'''




