'''
Run the 3D Hough transform algorithms conveniently.

'''

import json
import numpy as np

import hough

def load_points(filename):
    '''
        Load the given file and return the (x,y,z) hit points in a numpy
        array.

    '''
    with open(filename, 'r') as f:
        data = json.load(f)
    data = np.array(data, dtype=float)
    points = data[:, (3, 4, 8)]
    points[:,2] -= points[0,2]
    points[:,2] /= 1000.0
    points[:, :2] /= 10.0
    return points

def get_best_tracks(filename, threshold=5):
    '''
        Fit straight lines to the points in the file using an iterative
        Hough transformation and least-squares fit.

        A track must have at least <threshold> points on it.

        Returns ``(lines, points, params)`` where:
         - ``lines`` is a dict mapping ``Line`` ->  [point_index] (list of
           indices of corresponding points in the ``points`` array)
         - ``points`` is a numpy array of shape (npoints, 3) (= x,y,z)
         - ``params`` is the ``HoughParameters`` object associated with the
           fit

    '''
    points = load_points(filename)
    do_point_again = [True for point in points]
    params = hough.HoughParameters()
    params.ndirections = 1000
    params.npositions = 30
    lines = {}
    undo_points = None
    found_good_line = True
    while found_good_line:
        closer, farther, params, mask, best_fit_line = iterate_hough(points,
                params, threshold, undo_points)
        found_good_line = (closer is not None)
        if found_good_line:
            lines[best_fit_line] = np.where(~mask)[0]
            undo_points = points[[i for i in lines[best_fit_line] if
                    do_point_again[i]]]
            print('found good line with %d points' % len(closer))

    return lines, points, params
