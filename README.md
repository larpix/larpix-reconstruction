LArPix Reconstruction
===================

This module is a collection of classes and methods to assist reading in LArPix
data files, applying reconstruction algorithms, and storing reconstructed objects.

## Getting started

An example script for processing a LArPix hdf5 file is been provided in
`process_file.py`. This script demonstrates the process of initializing an
`EventBuilder`, looping through a data file, and applying a series of
reconstruction algorithms to the events. The reconstructed objects are then stored
using a `RecoFile` for further analysis.

The processing occurs like this:
- An `EventBuilder` is created on the data file of interest. The `EventBuilder`
(and the underlying `HitParser`) will scan through the data file. The `HitParser`
implements a sorted buffer to accommodate the nearly-serialized data from LArPix.
The length of this buffer can be adjusted using the `sort_buffer_length` keyword
argument of the `EventBuilder`.
- A `RecoFile` is created to handle the buffering of output data. To save
reconstruction objects, use `recofile.queue(reco_obj, type=type(reco_obj))`,
which will put the current object into the write queue of the `RecoFile`.
Once the number of bytes in the write queue passes `recofile.write_queue_length`,
the queue is flushed to file. To insure that all reco objects are written, be
sure to perform a `recofile.flush()` after queuing objects.
- In an 'infinite' loop, events are consecutively extracted from the data
using the `eventbuilder.get_next_event()`. This method returns an `Event`
type until the end of the file is reached, at which point a `None` is returned.
- A reconstruction is created using each event and is performed using
`<reconstruction type>.do_reconstruction()`.
- Reconstructed objects are stored in the `event.reco_objs` list and can be
accessed by any subsequent reconstruction. This facilitates a multi-algorithm
approach in which reconstructed objects can be merged, extended, or split.
- After the complete reconstruction chain has been performed, the final
recontructed objects are added to the `RecoFile` write queue for storage.

## Hough transform algorithm

Get started with your set of points saved in a JSON file. The output of
larpix-scripts/h52json.py will do nicely. The default direction and
position resolution supplied in this framework work fine for now.

Run the iterative Hough transform algorithm on the points in the file,
using the threshold to determine how many Hough-space votes are needed
to accept a track.

```python
import run_hough
lines, points, params = run_hough.get_best_tracks('myfile.json', threshold=15)
```

The ``lines`` dict maps ``hough.Line`` objects to a numpy array of the
points identified as part of the line (using a simple Euclidean distance
cut). ``points`` is a numpy array of all the points in the file.
``params`` is a ``hough.HoughParameters`` object which records the basic
parameters of the Hough transformation.

Note: due to the least-squares fit, the final number
of points on the track may in principle be below the threshold, or there
may be a true line which exceeds the threshold but which may not be
found. These cases are assumed to be rare.

From here you can plot the reconstructed lines:

```python
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = Axes3D(fig)

lines_list = list(lines.keys())
points_list = list(lines.values())
for line, points_near_line in zip(lines_list, points_list):
    points_on_line = line.points('x', 50, 150, 50)
    ax.scatter(*(points_near_line.T))
    ax.scatter(*(points_on_line.T))
```

### Line parametrization

While the parametrization of a line on the plane is straightforward, it
is more complicated in 3D. I use the parametrization advocated for by
the paper below. This parametrization is also known as Roberts's optimal
line representation. A direction vector is chosen to lie along the line
such that the z coordinate is positive. (There are rules to resolve the
ambiguity when the z coordinate is 0.) A primed coordinate system is
then constructed with the direction vector as the z-prime axis. The
point of intersection of the line with the x-prime/y-prime plane,
coupled with the unprimed coordinates of the direction vector, is
sufficient to uniquely identify the line.

### Choice of trial directions

Trial directions are chosen using the Fibonacci spiral technique for
identifying approximately-equidistant points on the unit sphere.


Hough transform algorithm adapted from:

Christoph Dalitz, Tilman Schramke, and Manuel Jeltsch, _Iterative Hough
Transform for Line Detection in 3D Point Clouds_, Image Processing On
Line, 7 (2017), pp. 184–196. https://doi.org/10.5201/ipol.2017.208