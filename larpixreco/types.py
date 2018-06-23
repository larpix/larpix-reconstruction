class Hit(object):
    ''' The basic primitive type used in larpix-reconstruction represents a single trigger of a larpix channel '''

    def __init__(self, hid, px, py, ts, q, iochain=None, chipid=None, channelid=None, geom=None):
        self.hid = hid
        self.px = px
        self.py = py
        self.ts = ts
        self.q = q
        self.iochain = iochain
        self.chipid = chipid
        self.channelid = channelid
        self.geom = geom

    def __str__(self):
        string = 'Hit(hid={hid}, px={px}, py={py}, ts={ts}, q={q}, iochain={iochain}, '\
            'chipid={chipid}, channelid={channelid}, geom={geom})'.format(**vars(self))
        return string

class HitCollection(object):
    ''' A base class of collected `Hit` types '''
    def __init__(self, hits):
        self.hits = hits
        self.nhit = len(self.hits)
        self.hid_start = min(self.get_hit_attr('hid'))
        self.hid_end = max(self.get_hit_attr('hid'))
        self.ts_start = min(self.get_hit_attr('ts'))
        self.ts_end = max(self.get_hit_attr('ts'))
        self.q = sum(self.get_hit_attr('q'))

    def __str__(self):
        string = '{}(hits=[\n\t{}]\n\t)'.format(self.__class__.__name__, \
            ', \n\t'.join(str(hit) for hit in self.hits))
        return string

    def __getitem__(self, key):
        return self.hits[key]

    def __len__(self):
        return nhit

    def get_hit_attr(self, attr, default=None):
        ''' Get a list of the specified attribute from event hits '''
        if not default is None:
            return [getattr(hit, attr, default) for hit in self.hits]
        else:
            return [getattr(hit, attr) for hit in self.hits]

class Event(HitCollection):
    ''' A class for a collection of hits associated by the event builder '''
    def __init__(self, evid, hits):
        HitCollection.__init__(self, hits)
        self.evid = evid

class Track(HitCollection):
    ''' A class representing a straight line segment and associated hits '''
    def __init__(self, pos, dir, hits, vertices=[]):
        HitCollection.__init__(self, hits)
        self.pos = pos
        self.dir = dir
        self.vertices = []

    def prune(self, radius):
        ''' Remove hits outside of specified radius '''
        pass

# etc

class SegmentedTrack(HitCollection):
    ''' A class representing a collection of straight segments and hits '''
    def __init__(self, tracks):
        hits = []
        for track in tracks:
            hits.append(track.hits)
        HitCollection.__init__(self, hits)
        self.tracks = tracks
# etc

class Shower(HitCollection):
    ''' A class representing a shower '''
    pass
# etc          
