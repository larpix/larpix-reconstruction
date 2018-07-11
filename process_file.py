import argparse
from larpixreco.EventBuilder import EventBuilder
from larpixreco.Reconstruction import TrackReconstruction
from larpixreco.RecoFile import RecoFile
from larpixreco.RecoLogging import initializeLogger

parser = argparse.ArgumentParser()
parser.add_argument('infile')
parser.add_argument('outfile')
parser.add_argument('-l', '--logfile', default=None)
args = parser.parse_args()

infile = args.infile
outfile = args.outfile
logger = initializeLogger(level='debug', filename=args.logfile)
eb = EventBuilder(infile, sort_buffer_length=100)
track_reco = TrackReconstruction()
outfile = RecoFile(outfile, opt='o')

curr_event = None
while True:
    curr_event = eb.get_next_event()
    if curr_event is None:
        break
    if curr_event.evid % 100 == 0:
        logger.info('ev {} hit {}/{}'.format(curr_event.evid, eb.data.sort_buffer_idx, eb.data.nrows))

    track_reco.do_reconstruction(curr_event)

    outfile.queue(curr_event)
outfile.flush()
