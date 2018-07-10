from larpixreco.types import Hit, Event
from larpixreco.HitParser import HitParser


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

    def store_t0_new_event(self, hits):
        event = Event(evid=self.curr_evid, hits=hits)
        self.t0events.append(event)
        self.curr_evid += 1
        return event


    def get_next_event(self, with_t0=False):
        '''
        hits = []
        while len(hits) < EventBuilder.max_ev_len:
            curr_hit = self.data.get_next_sorted_hit()
            if EventBuilder.is_associated(curr_hit, hits):
                # hit should be associated with others -> store and continue
                hits.append(curr_hit)
            elif EventBuilder.is_event(hits):
                # collected hits are an event -> return
                self.store_new_event(hits=hits)
                return self.events[-1]
                #self.events # a large list of every previous event
                if with_t0:
                    if self.t0 == True:
                        self.store_t0_new_event #kind of, associate w/ previous event first
                    else:
                        pass

                # is recent event ext trig?
                # if yes look through previous events and associate (NO)
                # if can associate -> return associated event
            else:
                hits = []

            if curr_hit is None:
                break

        if EventBuilder.is_event(hits):
            # remaining hits are an event -> return
            return self.store_new_event(hits=hits)
        else:
            return None
            '''
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

    def t0(self, event):
            hits = event.hits
            print(event)
            timestamps = []
            temp_list = []
            i = 0
            while True:
                print(i, hits[i].channelid,hits[i].chipid)
                if hits[i].channelid == 15:
                    if (len(hits) - i) >= 15:
                        temp_list.extend((hits[i].channelid,hits[i+1].channelid,hits[i+2].channelid,hits[i+3].channelid,hits[i+4].channelid,hits[i+5].channelid,hits[i+6].channelid,hits[i+7].channelid,hits[i+8].channelid,hits[i+9].channelid,hits[i+10].channelid,hits[i+11].channelid,hits[i+12].channelid,hits[i+13].channelid,hits[i+14].channelid))
                    else:
                        break
                else:
                    pass
                if temp_list == [7]*15:
                    timestamps.append(hits[i].ts)
                    print(timestamps)
                    i += 15
                    temp_list = []
                else:
                    temp_list = []
                i += 1
                if i >= len(hits): break

            print('timestamps=',timestamps)
            if timestamps == []:
                return None
            else:
                pass #return timestamps


'''
TEST
import h5py
from numpy import array

h5file = h5py.File('../larpix-scripts/datalog_2018_04_16_18_53_30_CEST_.h5',)
data = h5file['data']
mylist = data[4119:4180]
extra = data[4119:4220, 0]

eb = EventBuilder_t0('../larpix-scripts/datalog_2018_04_16_18_53_30_CEST_.h5',
                     sort_buffer_length=5000)
event = None
counter = 0
while True:
    event = eb.get_next_event()
    if event is None: break
    if not eb.t0(event) is None:
        print(eb.t0(event))
    if counter > 5: break
    counter += 1
'''



