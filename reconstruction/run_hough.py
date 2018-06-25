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
    data = np.array(data)
    points = data[:, (3, 4, 8)]
    points[:,2] -= points[0,2]
    return points

def get_best_line(accumulator, directions, bins, translation, scale):
    '''
        Return the line specified by the maximum bin in the accumulator.

    '''
    indices = np.unravel_index(np.argmax(accumulator),
            accumulator.shape)
    dir_i, xp_i, yp_i = indices
    line = hough.get_line(dir_i, xp_i, yp_i, directions, bins, bins,
            translation, scale)
    return line

def points_close_to_line(points, line, dr):
    '''
        Return the indices of the points which are within dr of the
        specified line.

        Indices refer to the "axis 0" index in the points array.

    '''
    is_close = []
    for i, point in enumerate(points):
        if line.distance_to(point) < dr:
            is_close.append(i)
    return is_close
