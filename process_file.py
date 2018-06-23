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
eb = EventBuilder(infile)
outfile = RecoFile(outfile)

curr_event = None
while True:
    curr_event = eb.get_next_event()
    if curr_event is None:
        break

    track_reco = TrackReconstruction(curr_event)
    tracks = track_reco.do_reconstruction()
    shower_reco = ShowerReconstruction(curr_event)
    showers = shower_reco.do_reconstruction()

    outfile.queue(tracks, type=TrackReconstruction)
    outfile.queue(showers, type=ShowerReconstruction)

outfile.flush()
