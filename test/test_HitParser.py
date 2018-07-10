import pytest
import larpixreco
from larpixreco.HitParser import *
import os.path

test_datafile = os.path.dirname(__file__) + '/test_datafile.h5'

def test_get_next_sorted_hit():
    n_to_test = 1e4
    hp = HitParser(test_datafile, sort_buffer_length=2000)
    prev_hits = []
    curr_hit = None
    counter = 0
    while True:
        curr_hit = hp.get_next_sorted_hit()
        if curr_hit is None or counter > n_to_test: break
        prev_hits += [curr_hit]
        counter += 1
    dts = [prev_hits[i+1].ts - prev_hits[i].ts for i in range(len(prev_hits)-1)]
    incorrect_packets = [(i, dt) for i,dt in enumerate(dts) if dt < 0]
    assert len(incorrect_packets) == 0, '{}/{} incorrectly sorted packets (idx, dt): {}'.format(len(incorrect_packets),
                                                                                                int(n_to_test),
                                                                                                incorrect_packets)

        
