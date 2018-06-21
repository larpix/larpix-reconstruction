'''
Compute the 3D Hough transform from a point cloud.

Based on the algorithm described in Dalitz, Schramke, Jeltsch [2017].

'''

import numpy as np

class line(object):
    '''A line in 3D.'''

    def __init__(self, theta, phi, xp, yp):
        '''
            Define a new line using the "Roberts optimal line
            representation."

            Theta and phi use the usual physics spherical coordinate
            definitions and are in radians. Theta (0 to pi/2) represents
            the angle to the z axis. Phi (-pi to pi) represents the angle
            between the projection on the x-y plane and the x axis, with
            the +y direction at phi = pi/2.

            Theta and phi define the direction of the line, represented
            by the unit vector b. xp and yp define the position of the
            line in the following sense:

            - consider the rotation between the unit vector (0, 0, 1) and
              the direction vector b
            - rotate the xyz coordinate system by the same rotation to
              create the primed coordinate system, so that b is now
              pointing in the z-prime direction.
            - xp and yp are the point of intersection between the line
              and the x-prime / y-prime plane

            Angular ambiguities:
              - Theta is restricted to [0, pi/2]
              - There are additional ambiguities if the line lies exactly
                in the x-y plane but I don't think they are relevant.

        '''
        self.theta = theta
        self.phi = phi
        self.xp = xp
        self.yp = yp

    def points(self, min_coord, max_coord, coord, npoints):
        '''
            Return a list of n Cartesian points along the line ranging
            from coord=min_coord to coord=max_coord, where coord='x',
            'y', or 'z'.

        '''
        #TODO
        pass

    @staticmethod
    def compute_xp_yp(theta, phi, px, py, pz):
        '''
            Compute xp and yp given the direction vector's angles and the
            (unprimed) coordinates of any point on the line, compute xp and
            yp.

        '''
        sintheta = np.sin(theta)
        bx = np.cos(phi)*sintheta
        by = np.sin(phi)*sintheta
        bz = np.cos(theta)

        A = (bx * by)/(1 + bz)
        B = 1 - (bx * bx)/(1 + bz)
        C = 1 - (by * by)/(1 + bz)

        xp = B * px - A * py - bx * pz
        yp = -A * px + C * py - by * pz

        return (xp, yp)

    @classmethod
    def fromDirPoint(cls, theta, phi, px, py, pz):
        '''
            Create a new line given the direction of the line and the
            coordinates of a point on the line.

        '''
        return cls(theta, phi, *compute_xp_yp(theta, phi, px, py, pz))

def fibonacci_hemisphere(samples):
    '''
        Use the Fibonacci sphere method to create a hemisphere of
        (mostly-)evenly spaced points, usable as a set of directions to
        test for the Hough transform. Returns points in Cartesian
        coordinates.

    '''
    points = np.empty((samples, 3))
    samples = samples * 2
    offset = 2./samples
    increment = np.pi * (3. - np.sqrt(5.));

    index = 0
    for i in range(samples):
        y = ((i * offset) - 1) + (offset / 2);
        r = np.sqrt(1 - pow(y,2))

        phi = ((i + 1) % samples) * increment

        x = np.cos(phi) * r
        z = np.sin(phi) * r
        if z >= 0:
            points[index] = [x, y, z]
            index += 1
        if index == samples/2:
            break

    return points

def cartesian_to_spherical(points):
    '''
       Convert the given points into spherical coordinates assuming they
       are unit vectors.

    '''
    phi = np.arctan2(points[:,1], points[:,0])  # arctan(y/x)
    theta = np.arccos(points[:,2])
    return np.vstack((theta, phi)).T

def get_xp_yp_edges(points, nbins):
    '''
        Given the point cloud, return (centered_cloud, xp_edges,
        yp_edges).

    '''
    maxes = points.max(axis=0)
    mins = points.min(axis=0)
    translation = 0.5 * (maxes + mins)
    centered_points = points - translation
    ranges = 0.5 * (maxes - mins)
    range_dist = np.linalg.norm(ranges)
    xp_edges = np.linspace(-range_dist, range_dist, nbins+1)
    yp_edges = xp_edges.copy()
    return centered_points, xp_edges, yp_edges

def get_directions(npoints):
    return cartesian_to_spherical(fibonacci_hemisphere(npoints))

def compute_hough(points, ndirections, npositions):
    '''
        Compute the Hough transformation of the given points and return
        a tuple of (accumulator array, directions, position bin edges).

        The shape of the accumulator array is: (ndirections, npositions,
        npositions).

        The directions are returned as a 2d array of [theta, prime].

        The position bin edges are returned in an array of length
        npositions + 1 and apply to both the x-prime and y-prime axes.

    '''
    input_points = points
    test_directions = get_directions(ndirections)
    points, xp_edges, yp_edges = get_xp_yp_edges(input_points,
            npositions)
    accumulator = np.zeros((
        len(test_directions),
        len(xp_edges) - 1,
        len(yp_edges) - 1))
    max_xp_i = accumulator.shape[1] - 1
    max_yp_i = accumulator.shape[2] - 1

    for point in points:
        for i, (theta, phi) in enumerate(test_directions):
                xp, yp = line.compute_xp_yp(theta, phi, *point)
                xp_i = max(0, min(np.searchsorted(xp_edges, xp)-1, max_xp_i))
                yp_i = max(0, min(np.searchsorted(yp_edges, yp)-1,
                    max_yp_i))
                accumulator[i, xp_i, yp_i] += 1

    return accumulator, test_directions, xp_edges
