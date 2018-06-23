from larpixreco.types import Track, Shower

class Reconstruction(object):
    ''' Base class for reconstruction methods '''
    def __init__(self, event):
        self.event = event

    def do_reconstruction(self):
        pass

class TrackReconstruction(Reconstruction):
    ''' Class for reconstructing events into straight line segments '''
    def __init__(self, event, tracks=[]):
        Reconstruction.__init__(self, event)
        self.tracks = tracks

    def do_reconstruction(self):
        # Split up event into tracks (not implemented)
        self.tracks = [Track(pos=[0,0,0], dir=[0,0,1], hits=self.event.hits)]
        return self.tracks

class ShowerReconstruction(Reconstruction):
    ''' Class for reconstructing events into showers '''
    def __init__(self, event, showers=[]):
        Reconstruction.__init__(self, event)
        self.showers = showers

    def do_reconstruction(self):
        # Split up event into showers (not implemented)
        self.showers = [Shower(hits=self.event.hits)]
        return self.showers

