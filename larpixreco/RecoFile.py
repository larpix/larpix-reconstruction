import h5py
from larpixreco.Reconstruction import *
import os.path as path

class RecoFile(object):
    ''' Class to handle io from reconstruction hdf5 file '''
    dataset_name = 'larpixreco'
    ncols = 1 # to be implemented
    dtype = np.int64
    description = '' # to be implemented

    def __init__(self, filename):
        self.filename = filename
        self.queued_bytes = 0
        self.write_queue = []
        self.file = None
        self.dataset = None

        self.init_file()

    def init_file(self):
        # ready file for reading/writing
        pass

    def queue(self, entry, type=Reconstruction):
        # add entry to write queue
        pass

    def flush(self):
        # write remaining entries in write queue
        pass
                                                                                        
        
