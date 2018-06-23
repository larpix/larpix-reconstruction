from larpixreco.types import Track, Shower

class Reconstruction(object):
    ''' Base class for reconstruction methods '''
    def __init__(self, event):
        self.event = event

class TrackReconstruction(Reconstruction):
    ''' Class for reconstructing events into straight line segments '''
    def do_reconstruction(self):
        # Split up event into tracks (not implemented)
        return Track(pos=[0,0,0], dir=[0,0,1], hits=self.event.hits)

class ShowerReconstruction(Reconstruction):
    ''' Class for reconstructing events into showers '''
    def do_reconstruction(self):
        # Split up event into showers (not implemented)
        return Shower(hits=self.event.hits)
        
