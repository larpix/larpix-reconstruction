LArPix Reconstruction
===================

We will figure this thing out

Get started with your set of points, how many test directions you want,
and how good your relative position resolution should be.

```python
import numpy as np
from hough import *
points = [(1, 2, 3), (4, 5, 6), ...]
direction_count = 1000
position_bin_count = 100
result = compute_hough(points, trial_directions, position_bin_count)
accumulator, trial_directions, position_bin_edges, translation = result
```

Extract the parameters of the best fit line:

```python
best_params_i = np.unravel_index(np.argmax(accumulator), accumulator.shape)
direction_i, xprime_i, yprime_i = best_params_i

best_direction = trial_directions[direction_i]
theta, phi = best_direction

xprime_low = position_bin_edges[xprime_i]
xprime_high = position_bin_edges[xprime_i + 1]
xprime = (xprime_low + xprime_high)/2

yprime_low = position_bin_edges[yprime_i]
yprime_high = position_bin_edges[yprime_i + 1]
yprime = (yprime_low + yprime_high)/2
```

Form a line object and retrieve some points along that line:

```python
best_line = line(theta, phi, xprime, yprime, translation)

xmin = -10
xmax = 10
npoints = 100
points_along_line = best_line.points('x', xmin, xmax, npoints)
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
