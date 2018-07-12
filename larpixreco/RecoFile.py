import h5py
import numpy as np
import larpixreco.types as recotypes
import os.path as path
import os
from larpixreco.RecoLogging import getLogger
logger = getLogger(__name__)

region_ref = h5py.special_dtype(ref=h5py.RegionReference)

class RecoFile(object):
    ''' Class to handle io from reconstruction hdf5 file '''
    larpixreco_type_dataset = { # maps between a larpixreco type (see types.py) and a dataset in file
        recotypes.Hit : 'hits',
        recotypes.Event : 'events',
        recotypes.Track : 'tracks'
        }
    dataset_desc = { # describes datasets and datatypes
        'info' : None,
        'hits' : [
            ('hid', 'i8'),
            ('px', 'i8'), ('py', 'i8'), ('ts', 'i8'), ('q', 'i8'),
            ('iochain', 'i8'), ('chipid', 'i8'), ('channelid', 'i8'),
            ('geom', 'i8'), ('event_ref', region_ref), ('track_ref', region_ref)],
        'events' : [
            ('evid', 'i8'), ('track_ref', region_ref), ('hit_ref', region_ref),
            ('nhit', 'i8'), ('q', 'i8'), ('ts_start', 'i8'), ('ts_end', 'i8')],
        'tracks' : [
            ('track_id','i8'), ('event_ref', region_ref), ('hit_ref', region_ref),
            ('theta', 'f8'),
            ('phi', 'f8'), ('xp', 'f8'), ('yp', 'f8'), ('nhit', 'i8'),
            ('q', 'i8'), ('ts_start', 'i8'), ('ts_end', 'i8'),
            ('sigma_theta', 'f8'), ('sigma_phi', 'f8'), ('sigma_x', 'f8'),
            ('sigma_y', 'f8')],
        }

    def __init__(self, filename, write_queue_length=10, opt='o'):
        self.filename = filename

        self.queued_bytes = 0
        self._write_queue = []
        self.write_queue_length = write_queue_length
        self.datafile = None

        self.init_file(opt=opt)

    def init_file(self, opt):
        # ready file for reading/writing
        if 'o' in opt:
            try:
                os.remove(self.filename)
            except FileNotFoundError:
                pass
            if len(opt) > 1:
                opt = opt.replace('o','')
            else:
                opt = opt.replace('o','a')
        self.datafile = h5py.File(self.filename, opt)
        for dataset_name, dataset_dtype in self.dataset_desc.items():
            if not dataset_name in self.datafile:
                if not dataset_dtype is None:
                    self.datafile.create_dataset(dataset_name, (0,),
                                                 maxshape=(None,),
                                                 dtype=dataset_dtype)
                else:
                    self.datafile.create_group(dataset_name)

    @classmethod
    def fill_empty_dict(cls, data_dict, dataset_name):
        ''' Fill with empty values (if necessary) '''
        for entry_desc in cls.dataset_desc[dataset_name]:
            key = entry_desc[0]
            if not key in data_dict:
                if entry_desc[1] == region_ref:
                    data_dict[key] = None
                else:
                    data_dict[key] = -9999
            elif data_dict[key] is None and not entry_desc[1] == region_ref:
                data_dict[key] = -9999

    @classmethod
    def larpixreco_type_to_hdf5(cls, larpixreco_type_obj, **kwargs):
        '''
        Automatically generate numpy array used by hdf5
        Additional attributes can be set (or overridden by kwargs)
        '''
        if not type(larpixreco_type_obj) in cls.larpixreco_type_dataset.keys():
            raise TypeError('object type is not in list of known types')
        data_dict = vars(larpixreco_type_obj)
        dataset_name = cls.larpixreco_type_dataset[type(larpixreco_type_obj)]
        for value_name, value in kwargs.items():
            data_dict[value_name] = value
        cls.fill_empty_dict(data_dict, dataset_name)
        data_tuple = tuple(data_dict[entry_desc[0]] for entry_desc in \
                               cls.dataset_desc[dataset_name])
        return np.array(data_tuple, dtype=cls.dataset_desc[dataset_name])

    def hit_data(self, hits, **kwargs):
        '''
        Generate hit data to be stored in file
        '''
        data_list = []
        for hit in hits:
            data_list += [self.larpixreco_type_to_hdf5(hit, **kwargs)]
        return np.array(data_list)

    def track_data(self, track, **kwargs):
        '''
        Generate track data to be stored in file
        '''
        if track.cov is not None:
            s_theta, s_phi, s_x, s_y = np.sqrt(np.diag(track.cov))
        else:
            s_theta, s_phi, s_x, s_y = [-1]*4
        new_kwargs = {
            'sigma_theta': s_theta,
            'sigma_phi': s_phi,
            'sigma_x': s_x,
            'sigma_y': s_y,
        }
        return self.larpixreco_type_to_hdf5(track, **kwargs,
                **new_kwargs)

    def event_data(self, event, **kwargs):
        '''
        Generate event data to be stored in file
        '''
        return self.larpixreco_type_to_hdf5(event, **kwargs)

    def _resize_by(self, n, dataset_name):
        ''' Extend dataset by n columns '''
        dataset = self.datafile[dataset_name]
        curr_len = dataset.shape[0]
        dataset.resize(curr_len + n, axis=0)

    def _fill(self, data, dataset_name):
        ''' Fill last chunk of file with new data '''
        if data is None:
            return
        dataset = self.datafile[dataset_name]
        try:
            dataset[-len(data):] = data
        except TypeError:
            dataset[-1:] = data

    def write_attr(self, dataset=None, **kwargs):
        '''
        Write attr to dataset, attr names and values are passed via kwargs
        Can take either a string or class as argument for writing
        '''
        attrs = None
        if isinstance(dataset, type):
            attrs = self.datafile[larpixreco_type_dataset[dataset]].attrs
        elif isinstance(dataset, str):
            attrs = self.datafile[dataset].attrs
        elif dataset is None:
            attrs = self.datafile['info']
        if attrs is None: return
        for key, value in kwargs.items():
            attrs[key] = value

    def queue(self, obj, **kwargs):
        '''
        Add a data object to write queue
        Writes to file if queue is full after new object
        '''
        self._write_queue += [(obj, kwargs)]
        if len(self._write_queue) >= self.write_queue_length:
            self.flush()

    def flush(self):
        '''
        Write remaining object in write queue to file and clear queue
        '''
        for obj, kwargs in self._write_queue:
            self.write(obj, **kwargs)
        self.clear_queue()

    def clear_queue(self):
        '''
        Reset write queue
        '''
        self._write_queue = []

    def write(self, obj, **kwargs):
        '''
        Assemble larpixreco data type into correct file formatting and append to file
        Correctly assigns references between parents and daughters
        Use kwargs to pass additional data fields into the created data
        returns a tuple of (dataset_name, first_row_idx, last_row_idx) such that the data
        written can be accessed via
        RecoFile_instance.datafile[dataset_name][first_row_idx:last_row_idx]

        Due to limitations of the h5py region reference type, data should be stored in
        consecutive blocks.

        To extend the file format, one must do the following:
        - Include the dataset name and dtype description in the class variable dataset_desc
        - Include a map from larpixreco type object to dataset name in the class variable larpixreco_type_dataset
        - Update write statement to specifications above, using your new data type
        '''
        dtype = type(obj)
        return_ref = None

        # Initialize data chunks
        hits_write_data = None
        tracks_write_data = None
        events_write_data = None

        if dtype is recotypes.HitCollection:
            # Store hit collection as hits
            hits_data_start = self.datafile['hits'].shape[0]
            hits_data_end = hits_data_start + obj.nhit
            self._resize_by(obj.nhit, 'hits')
            hits_write_data = self.hit_data(obj.hits, **kwargs)
            return_ref = ('hits', hits_data_start, hits_data_end)

        elif dtype is recotypes.Track:
            # Store track data along with linked hits
            track_id = self.datafile['tracks'].shape[0]
            tracks_data_start = self.datafile['tracks'].shape[0]
            tracks_data_end = tracks_data_start + 1
            self._resize_by(1, 'tracks')
            track_ref = self.datafile['tracks'].regionref[track_id]

            hits_dataset, hits_data_start, hits_data_end = self.write(recotypes.HitCollection(obj.hits),
                                                                      track_ref=track_ref, **kwargs)
            hit_ref = self.datafile['hits'].regionref[hits_data_start:
                                                          hits_data_end]
            tracks_write_data = self.track_data(obj, track_id=track_id,
                                               hit_ref=hit_ref, **kwargs)
            return_ref = ('tracks', tracks_data_start, tracks_data_end)

        elif dtype is recotypes.Event:
            event_idx = self.datafile['events'].shape[0]
            self._resize_by(1, 'events')
            #  Generate references for event
            event_ref = self.datafile['events'].regionref[event_idx]
            # Store sub-objects
            tracks = [reco_obj for reco_obj in obj.reco_objs
                      if isinstance(reco_obj, recotypes.Track)]
            hits_data_start = self.datafile['hits'].shape[0]
            hits_data_end = self.datafile['hits'].shape[0]
            tracks_data_start = self.datafile['tracks'].shape[0]
            tracks_data_end = self.datafile['tracks'].shape[0]
            for track in tracks:
                track_dataset_name, _, tracks_data_end = self.write(track,
                                                                    event_ref=event_ref)
                hits_data_end += track.nhit
            #  Catch any hits in event that are not yet stored
            orphans = []
            for hit in obj.hits:
                if not hit.hid in self.datafile['hits'][hits_data_start:hits_data_end]:
                    orphans += [hit]
            hits_data_end += len(orphans)
            self.write(recotypes.HitCollection(orphans), event_ref=event_ref)
            hit_ref = self.datafile['hits'].regionref[hits_data_start
                                                      :hits_data_end]
            track_ref = self.datafile['tracks'].regionref[tracks_data_start:
                                                              tracks_data_end]
            events_write_data = self.event_data(obj, track_ref=track_ref,
                                                hit_ref=hit_ref)
            return_ref = ('events', event_idx, event_idx+1)
        # Write data to file
        self._fill(hits_write_data, 'hits')
        self._fill(tracks_write_data, 'tracks')
        self._fill(events_write_data, 'events')

        # Return reference to data
        return return_ref
