import argparse
from larpixreco.EventBuilder import EventBuilder
from larpixreco.Reconstruction import TrackReconstruction, ShowerReconstruction
from larpixreco.RecoFile import RecoFile

parser = argparse.ArgumentParser()
parser.add_argument('infile')
parser.add_argument('outfile')
args = parser.parse_args()

infile = args.infile
outfile = args.outfile
eb = EventBuilder(infile, sort_buffer_length=100)
outfile = RecoFile(outfile, opt='o')

curr_event = None
while True:
    curr_event = eb.get_next_event()
    if curr_event is None:
        break
    if curr_event.evid % 100 == 0:
        print('ev {} hit {}/{}'.format(curr_event.evid, eb.data.sort_buffer_idx, eb.data.nrows),end='\r')

    track_reco = TrackReconstruction(curr_event)
    track_reco.do_reconstruction()
    shower_reco = ShowerReconstruction(curr_event)
    shower_reco.do_reconstruction()

    outfile.write(curr_event)
