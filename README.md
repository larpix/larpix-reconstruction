LArPix Reconstruction
===================

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
