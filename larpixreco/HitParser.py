import h5py
import numpy as np
from larpixreco.types import Hit

class HitParser(object):
    ''' A helper for parsing data files into `Hit` types '''
    _col2name_map = { # col : name
        0 : 'channelid',
        1 : 'chipid',
        2 : 'pixelid',
        3 : 'pixelx',
        4 : 'pixely',
        5 : 'raw_adc',
        6 : 'raw_timestamp',
        7 : 'adc',
        8 : 'timestamp',
        9 : 'serialblock',
        10 : 'v',
        11 : 'pdst_v'
        }
    _name2col_map = dict([(name, col) for col, name in _col2name_map.items()])

    def __init__(self, filename, sort_buffer_length=1):
        self.filename = filename
        self.datafile = h5py.File(self.filename, 'r')
        self.data = self.datafile['data']
        self.description = self.data.attrs['descripiton']
        self.nrows = self.data.shape[0]
        self.ncols = self.data.shape[1]

        self._sort_buffer = None
        self.sort_buffer_length = sort_buffer_length
        self.sort_buffer_idx = 0

    @staticmethod
    def convert_row_to_hit(row_data):
        row_dict = dict([(name, row_data[col]) for name, col in HitParser._name2col_map.items()])
        hit = Hit(px=row_dict['pixelx'], py=row_dict['pixely'],
                  # FIXME: row index is not currently stored
                  ts=row_dict['timestamp'], q=(row_dict['v'] - row_dict['pdst_v']),
                  chipid=row_dict['chipid'], channelid=row_dict['channelid'])
        return hit

    def get_row_data(self, row_idx):
        ''' Fetch 1D array associated with specified row, last column is row_idx '''
        if row_idx >= self.nrows:
            return None
        return self.data[row_idx]

    def get_row_attr(self, row_idx, attr):
        ''' Fetch value in data specified by row and column name '''
        if row_idx >= self.nrows:
            return None
        return self.get_row_data(row_idx)[HitParser._name2col_map[attr]]

    def get_hit(self, row_idx):
        ''' Create a hit corresponding to the specified row '''
        row_data = self.get_row_data(row_idx)
        if row_data is None:
            return None
        return HitParser.convert_row_to_hit(row_data)

    def _load_next_sorted(self, sort_field='timestamp'):
        ''' Load next row into sorted array buffer '''
        buffer_length = min(self.sort_buffer_length, self.nrows)
        sort_col = HitParser._name2col_map[sort_field]
        if not self._sort_buffer is None:
            # sort buffer has been initialized
            self.sort_buffer_idx += 1
            new_row = None
            if self.sort_buffer_idx < self.nrows:
                new_row = self.get_row_data(self.sort_buffer_idx)
            if not new_row is None:
                sort_data = np.vstack((self._sort_buffer[1:], new_row))
                self._sort_buffer = sort_data[sort_data[:,sort_col].argsort()]
            else:
                self._sort_buffer = self._sort_buffer[1:]
        else:
            # sort buffer has not been initialized
            sort_data = self.data[:buffer_length]
            self.sort_buffer_idx = buffer_length - 1
            self._sort_buffer = sort_data[sort_data[:,sort_col].argsort()]

    def get_next_sorted_hit(self, sort_field='timestamp'):
        ''' Returns first row in sorted buffer '''
        self._load_next_sorted(sort_field)
        if len(self._sort_buffer) == 0:
            return None
        return HitParser.convert_row_to_hit(self._sort_buffer[0])

