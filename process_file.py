import argparse
from larpixreco.EventBuilder import EventBuilder
from larpixreco.Reconstruction import TrackReconstruction
from larpixreco.RecoFile import RecoFile
from larpixreco.RecoLogging import initializeLogger

parser = argparse.ArgumentParser()
parser.add_argument('infile')
parser.add_argument('outfile')
parser.add_argument('-l', '--logfile', default=None)
parser.add_argument('-n', '--num', default=-1, type=int, help='num events to process')
args = parser.parse_args()

infile = args.infile
outfile = args.outfile
n_events = args.num
logger = initializeLogger(level='debug', filename=args.logfile)
eb = EventBuilder(infile, sort_buffer_length=100)
track_reco = TrackReconstruction()
outfile = RecoFile(outfile, opt='o')

curr_event = None
n_processed = 0
while True:
    if n_events >= 0 and n_processed >= n_events:
        break

    curr_event = eb.get_next_event()
    if curr_event is None:
        break
    if curr_event.evid % 100 == 0:
        logger.info('ev {} hit {}/{}'.format(curr_event.evid, eb.data.sort_buffer_idx, eb.data.nrows))

    # track_reco.do_reconstruction(curr_event)

    outfile.queue(curr_event)
    n_processed += 1
outfile.flush()
