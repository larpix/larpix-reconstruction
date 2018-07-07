import h5py
import numpy as np
import larpixreco.types as recotypes
import os.path as path
import os

region_ref = h5py.special_dtype(ref=h5py.RegionReference)

class RecoFile(object):
    ''' Class to handle io from reconstruction hdf5 file '''
    dataset_desc = { # describes datasets and datatypes
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
            ('q', 'i8'), ('ts_start', 'i8'), ('ts_end', 'i8')],
        }

    def __init__(self, filename, write_queue_length=0, opt='a'):
        self.filename = filename

        self.queued_bytes = 0
        self.write_queue = dict([(dataset_name, [])
                                 for dataset_name in self.dataset_desc])
        self.write_queue_length = write_queue_length
        self.datafile = None

        self.init_file(opt=opt)

    def init_file(self, opt='a'):
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
                self.datafile.create_dataset(dataset_name, (0,),
                                             maxshape=(None,),
                                             dtype=dataset_dtype)

    def fill_empty_dict(self, data_dict, dataset_name):
        ''' Fill with empty values (if necessary) '''
        for entry_desc in self.dataset_desc[dataset_name]:
            key = entry_desc[0]
            if not key in data_dict:
                if entry_desc[1] == region_ref:
                    data_dict[key] = None
                else:
                    data_dict[key] = -9999
            elif data_dict[key] is None and not entry_desc[1] == region_ref:
                data_dict[key] = -9999

    def hit_data(self, hits, **kwargs):
        '''
        Generate hit data to be stored in file
        '''
        data_list = []
        for idx, hit in enumerate(hits):
            hit_dict = {
                'hid' : hit.hid,
                'px' : hit.px,
                'py' : hit.py,
                'ts' : hit.ts,
                'q' : hit.q,
                'iochain' : hit.iochain,
                'chipid' : hit.chipid,
                'channelid' : hit.channelid,
                'geom' : hit.geom,
                'event_ref' : None,
                'track_ref' : None
                }
            # store references to other data
            for value_name, value in kwargs.items():
                hit_dict[value_name] = value
            self.fill_empty_dict(hit_dict, 'hits')
            hit_tuple = tuple(hit_dict[entry_desc[0]] for entry_desc in \
                                  self.dataset_desc['hits'])
            data_list += [np.array(hit_tuple, \
                                       dtype=self.dataset_desc['hits'])]
        return np.array(data_list)

    def track_data(self, track, **kwargs):
        '''
        Generate track data to be stored in file
        '''
        track_dict = {
            'theta' : track.theta,
            'phi' : track.phi,
            'xp' : track.xp,
            'yp' : track.yp,
            'nhit' : track.nhit,
            'q' : track.q,
            'ts_start' : track.ts_start,
            'ts_end' : track.ts_end,
            }
        # store references to other data
        for value_name, value in kwargs.items():
            track_dict[value_name] = value
        self.fill_empty_dict(track_dict, 'tracks')
        track_tuple = tuple(track_dict[entry_desc[0]] for entry_desc in \
                              self.dataset_desc['tracks'])
        return np.array([np.array(track_tuple, \
                                      dtype=self.dataset_desc['tracks'])])

    def event_data(self, event, **kwargs):
        '''
        Generate event data to be stored in file
        '''
        event_dict = {
            'evid' : event.evid,
            'nhit' : event.nhit,
            'q' : event.q,
            'ts_start' : event.ts_start,
            'ts_end' : event.ts_end,
            }
        # store other data (data_refs, etc)
        for value_name, value in kwargs.items():
            event_dict[value_name] = value
        self.fill_empty_dict(event_dict, 'events')
        event_tuple = tuple(event_dict[entry_desc[0]] for entry_desc in \
                              self.dataset_desc['events'])
        return np.array([np.array(event_tuple, \
                                      dtype=self.dataset_desc['events'])])

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
        dataset[-len(data):] = data

    def write(self, data):
        '''
        Assemble hit collection data into correct file formatting
        Correctly assigns references between parents and daughters
        '''
        dtype = type(data)

        # Initialize data chunks
        hits_write_data = None
        tracks_write_data = None
        events_write_data = None
        if dtype is recotypes.HitCollection:
            # Store hit collection as hits with no associated parents
            self._resize_by(data.nhit, 'hits')
            hits_write_data = self.hit_data(data.hits)

        elif dtype is recotypes.Track:
            track_id = self.datafile['tracks'].shape[0]
            hits_data_start = self.datafile['hits'].shape[0]
            hits_data_end = hits_data_start + data.nhit
            # Store tracks with associated hits and no parent event
            self._resize_by(data.nhit, 'hits')
            self._resize_by(1, 'tracks')
            track_ref = self.datafile['tracks'].regionref[track_id]
            hit_ref = self.datafile['hits'].regionref[hits_data_start:
                                                          hits_data_end]
            hits_write_data = self.hit_data(data.hits, track_ref=track_ref)
            tracks_write_data = self.track_data(data, track_id=track_id,
                                               hit_ref=hit_ref)

        elif dtype is recotypes.Event:
            event_idx = self.datafile['events'].shape[0]
            hits_data_start = self.datafile['hits'].shape[0]
            hits_data_end = hits_data_start + data.nhit
            tracks = [reco_obj for reco_obj in data.reco_objs
                      if isinstance(reco_obj, recotypes.Track)]
            tracks_data_start = self.datafile['tracks'].shape[0]
            tracks_data_end = tracks_data_start + len(tracks)
            # Store event with hits and reconstructed objects referenced
            self._resize_by(data.nhit, 'hits')
            self._resize_by(len(tracks), 'tracks')
            self._resize_by(1, 'events')
            #  Generate references for event
            event_ref = self.datafile['events'].regionref[event_idx]
            hit_ref = self.datafile['hits'].regionref[hits_data_start:
                                                          hits_data_end]
            track_ref = self.datafile['tracks'].regionref[tracks_data_start:
                                                              tracks_data_end]
            curr_hits_data_start = hits_data_start
            for track_idx, track in enumerate(tracks):
                #  Generate references and data for tracks
                track_id = tracks_data_start + track_idx
                curr_track_ref = self.datafile['tracks'].regionref[track_id]
                if hits_write_data is None:
                    hits_write_data = self.hit_data(track.hits,
                                                    track_ref=curr_track_ref,
                                                    event_ref=event_ref)
                else:
                    hits_write_data = np.append(hits_write_data, self.hit_data(
                            track.hits, track_ref=curr_track_ref,
                            event_ref=event_ref))

                curr_hits_data_end = curr_hits_data_start + track.nhit
                curr_hit_ref = self.datafile['hits'].regionref[curr_hits_data_start
                                                               :curr_hits_data_end]
                curr_hits_data_start = curr_hits_data_end
                if tracks_write_data is None:
                    tracks_write_data = self.track_data(track,
                                                        hit_ref=curr_hit_ref,
                                                        track_id=track_id,
                                                        event_ref=event_ref)
                else:
                    tracks_write_data = np.append(\
                        tracks_write_data, self.track_data(track,
                                                           hit_ref=curr_hit_ref,
                                                           track_id=track_id,
                                                           event_ref=event_ref))
            #  Catch any hits in event that are not associated with reco_objs
            orphans = []
            for hit in data.hits:
                if hits_write_data is None or \
                        not hit.hid in hits_write_data['hid']:
                    orphans += [hit]
                    curr_hits_data_start += 1
                    curr_hits_data_end = curr_hits_data_start + 1
            if len(orphans) > 0:
                if hits_write_data is None:
                    hits_write_data = self.hit_data(orphans, event_ref=event_ref)
                else:
                    new_hits_write_data = self.hit_data(orphans, event_ref=event_ref)
                    hits_write_data = np.append(hits_write_data, new_hits_write_data)
            if not curr_hits_data_start == hits_data_end:
                print('Warning: orphaned hits do not add up to total')
                print('N orphan: {}, expected: {}'.format(len(orphans), data.nhit - sum([track.nhit for track in tracks])))
                print('Orphan idx: {}, expected: {}'.format(curr_hits_data_end,
                                                            hits_data_end))
            events_write_data = self.event_data(data, track_ref=track_ref,
                                                hit_ref=hit_ref)
        # Write data to file
        self._fill(hits_write_data, 'hits')
        self._fill(tracks_write_data, 'tracks')
        self._fill(events_write_data, 'events')



