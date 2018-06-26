import h5py
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

    def __init__(self, filename):
        self.filename = filename
        self.datafile = h5py.File(self.filename, 'r')
        self.data = self.datafile['data']
        self.description = self.data.attrs['descripiton']
        self.nrows = self.data.shape[0]
        self.ncols = self.data.shape[1]

    def get_row_data(self, row_idx):
        ''' Fetch 1D array associated with specified row '''
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
        row_dict = dict([(name, row_data[col]) for name, col in HitParser._name2col_map.items()])
        hit = Hit(hid=row_idx, px=row_dict['pixelx'], py=row_dict['pixely'],
                  ts=row_dict['timestamp'], q=(row_dict['v'] - row_dict['pdst_v']),
                  chipid=row_dict['chipid'], channelid=row_dict['channelid'])
        return hit
