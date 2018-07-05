import numpy as np
from larpixreco.types import Track, Shower
import larpixreco.hough as hough

class Reconstruction(object):
    ''' Base class for reconstruction methods '''
    def __init__(self, event):
        self.event = event

    def do_reconstruction(self):
        pass

class TrackReconstruction(Reconstruction):
    ''' Class for reconstructing events into straight line segments '''
    def __init__(self, event):
        Reconstruction.__init__(self, event)

    def do_reconstruction(self, hough_threshold=5, hough_ndir=1000, hough_npos=30):
        ''' Perform hough transform algorithm and add Track reco objects to event '''
        x = np.array(self.event['px'])/10 # convert to mm
        y = np.array(self.event['py'])/10 # "
        z = (np.array(self.event['ts']) - self.event.ts_start)/1000 # convert to us
        points = np.array(list(zip(x,y,z)))
        params = hough.HoughParameters()
        params.ndirections = hough_ndir
        params.npositions = hough_npos
        lines, points, params = hough.run_iterative_hough(points, params,
            hough_threshold)

        tracks = []
        for line, hit_idcs in lines.items():
            hits = self.event[list(hit_idcs)]
            tracks += [Track(hits=hits, line=line, hough_params=params)]
        self.event.reco_objs += tracks
        return tracks

class ShowerReconstruction(Reconstruction):
    ''' Class for reconstructing events into showers '''
    def __init__(self, event):
        Reconstruction.__init__(self, event)

    def do_reconstruction(self):
        # Split up event into showers (not implemented)
        pass

