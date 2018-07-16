import numpy as np
from larpixreco.types import Track, Shower
import larpixreco.algorithms.hough as hough
from functools import wraps
import sys
import traceback
from larpixreco.RecoLogging import getLogger
logger = getLogger(__name__)

def safe_failure(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as expt:
            logger.error('Error encountered in {}: {}'.format(func.__name__, expt))
            logger.error(traceback.format_exc())
            return None
    return new_func

class Reconstruction(object):
    ''' Base class for reconstruction methods '''
    def __init__(self):
        pass

    @safe_failure
    def do_reconstruction(self, event):
        pass

class TrackReconstruction(Reconstruction):
    ''' Class for reconstructing events into straight line segments '''
    def __init__(self, hough_threshold=5, hough_ndir=1000, hough_npos=30):
        Reconstruction.__init__(self)
        self.hough_ndir = hough_ndir
        self.hough_npos = hough_npos
        self.hough_threshold = hough_threshold
        self.cache = hough.setup_fit_errors()

    @safe_failure
    def do_reconstruction(self, event):
        ''' Perform hough transform algorithm and add Track reco objects to event '''
        x = np.array(event['px'])/10 # convert to mm
        y = np.array(event['py'])/10 # "
        z = (np.array(event['ts']) - event.ts_start)/1000 # convert to us
        points = np.array(list(zip(x,y,z)))
        params = hough.HoughParameters()
        params.ndirections = self.hough_ndir
        params.npositions = self.hough_npos
        lines, points, params = hough.run_iterative_hough(points,
                params, self.hough_threshold, self.cache)

        tracks = []
        for line, hit_idcs in lines.items():
            hits = event[list(hit_idcs)]
            tracks += [Track(hits=hits, theta=line.theta, phi=line.phi,
                xp=line.xp, yp=line.yp, cov=line.cov)]
        event.reco_objs += tracks
        return tracks

class ShowerReconstruction(Reconstruction):
    ''' Class for reconstructing events into showers '''
    def __init__(self):
        Reconstruction.__init__(self)

    @safe_failure
    def do_reconstruction(self, event):
        # Split up event into showers (not implemented)
        pass

