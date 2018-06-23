import argparse
from larpixreco.EventBuilder import EventBuilder
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
tracks = []
showers = []
while True:
    curr_event = eb.get_next_event()
    
    track_reco = TrackReconstruction(event)
    shower_reco = ShowerReconstruction(event)

    for track in track_reco:
        tracks.append(track)
    for shower in shower_reco:
        showers.append(shower)

    outfile.queue(tracks, type=TrackReconstruction)
    outfile.queue(showers, type=ShowerReconstruction)

    if curr_event is None:
        break

outfile.flush()
