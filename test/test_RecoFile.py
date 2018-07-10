import pytest
import numpy as np
import larpixreco
from larpixreco.RecoFile import *

def test_larpixreco_type_to_hdf5_hit():
    hit = larpixreco.types.Hit(0,1,2,3,4,5)
    test_kwargs = { 'event_ref' : 63,
                    'test' : 'Dont store this'}
    write_data = RecoFile.larpixreco_type_to_hdf5(hit, **test_kwargs)
    expected = np.array((0,1,2,3,4,5,-9999,-9999,-9999,63,None),
                        dtype=RecoFile.dataset_desc['hits'])
    assert write_data == expected
    
def test_larpixreco_type_to_hdf5_error():
    with pytest.raises(TypeError):
        RecoFile.larpixreco_type_to_hdf5('this is not a valid larpixreco type')
