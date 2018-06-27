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

def get_best_line(accumulator, directions, bins, translation):
    '''
        Return the line specified by the maximum bin in the accumulator.

    '''
    indices = np.unravel_index(np.argmax(accumulator),
            accumulator.shape)
    dir_i, xp_i, yp_i = indices
    line = hough.get_line(dir_i, xp_i, yp_i, directions, bins, bins,
            translation)
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

def split_by_distance(points, line, dr):
    '''
        Return two new arrays and a list, containing the points closer to and
        farther from the line than the given dr, as well as a boolean
        mask array where True means "farther than dr".

        Returned as a tuple (closer, farther, mask).

    '''
    close_to_line_index = points_close_to_line(points, line, dr)
    mask = np.ones(len(points), dtype=bool)
    mask[close_to_line_index] = False
    closer = np.empty((len(close_to_line_index), 3))
    farther = np.empty((len(mask) - len(closer), 3))
    closer[:] = points[~mask]
    farther[:] = points[mask]
    return closer, farther, mask

def get_fit_line(points, start_line, dr):
    '''
        Return the best fit line determined by least-squares fit to the
        points within dr of start_line.

        Specific algorithm used is:
         - direction is the eigenvector corresponding to the largest
           eigenvalue of the covariance matrix
         - anchor point is the average position of the relevant points

    '''
    closer, farther, mask = split_by_distance(points, start_line, dr)
    anchor = np.mean(closer, axis=0)
    evals, evecs = hough.cov_evals_evecs(closer)
    direction_unnorm = (evecs.T)[0]
    direction_norm = direction_unnorm/np.linalg.norm(direction_unnorm)
    directions = hough.cartesian_to_spherical(direction_norm.reshape((1,
        3)))
    theta, phi = directions[0]
    fit_line = hough.Line.fromDirPoint(theta, phi, *anchor)
    return fit_line

def get_best_track(filename):
    '''
        Fit a straight line to the points in the file using a Hough
        transformation and least-squares fit.

        Returns (Line, points, close_points, mask).

    '''
    points = load_points(filename)
    result = hough.compute_hough(points, 1000, 30)
    guess_line = get_best_line(*result)
    bins = result[2]
    dr = bins[1] - bins[0]
    fit_line = get_fit_line(points, guess_line, dr)
    closer, farther, mask = split_by_distance(points, fit_line, dr)
    return fit_line, points, closer, mask
