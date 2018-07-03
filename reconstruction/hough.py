'''
Compute the 3D Hough transform from a point cloud.

Based on the algorithm described in Dalitz, Schramke, Jeltsch [2017].

'''

import numpy as np

class Line(object):
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

    def points(self, coord, min_coord, max_coord, npoints):
        '''
            Return a list of n Cartesian points along the line ranging
            from coord=min_coord to coord=max_coord, where coord='x',
            'y', or 'z'.

        '''
        theta = self.theta
        phi = self.phi
        xp = self.xp
        yp = self.yp
        sintheta = np.sin(theta)
        bx = np.cos(phi)*sintheta
        by = np.sin(phi)*sintheta
        bz = np.cos(theta)
        b = np.array([bx, by, bz])
        A = -(bx * by)/(1 + bz)
        B = 1 - (bx * bx)/(1 + bz)
        C = 1 - (by * by)/(1 + bz)

        p0 = xp * np.array([B, A, -bx]) + yp * np.array([A, C, -by])
        distance = None
        num_bs_in_range = None
        if coord == 'x':
            distance = (p0[0] - min_coord)/bx
            num_bs_in_range = (max_coord - min_coord)/bx
        elif coord == 'y':
            distance = (p0[1] - min_coord)/by
            num_bs_in_range = (max_coord - min_coord)/by
        elif coord == 'z':
            distance = (p0[2] - min_coord)/bz
            num_bs_in_range = (max_coord - min_coord)/bz
        else:
            raise ValueError('Bad coord')

        p1 = p0 - distance * b
        prefactor = num_bs_in_range/(npoints-1)
        prefactor_array = (prefactor *
                np.arange(npoints).reshape((npoints, 1)))
        jumps = prefactor_array * np.tile(b, (npoints, 1))
        points = p1 + jumps
        return points

    def distance_to(self, point):
        '''
            Return the perpendicular distance of this line to the given
            point.

        '''
        point_on_line = self.points('x', point[0], point[0] + 10, 2)[0]
        theta = self.theta
        phi = self.phi
        sintheta = np.sin(theta)
        bx = np.cos(phi)*sintheta
        by = np.sin(phi)*sintheta
        bz = np.cos(theta)
        direction = np.array([bx, by, bz])
        first_part = point_on_line - point
        second_part = np.dot(direction, first_part) * direction
        vector = first_part - second_part
        distance = np.linalg.norm(vector)
        return distance

    @classmethod
    def fromDirPoint(cls, theta, phi, px, py, pz):
        '''
            Create a new line given the direction of the line and the
            coordinates of a point on the line.

        '''
        return cls(theta, phi, *compute_xp_yp(theta, phi, px, py, pz))

    @classmethod
    def applyTranslation(cls, original, translation):
        '''
            Return a new line which has been translated by the given
            translation vector.

        '''
        point = original.points('x', 0, 1, 2)[0]
        theta, phi = original.theta, original.phi
        px, py, pz = point + translation
        xp, yp = compute_xp_yp(theta, phi, px, py, pz)
        return cls(theta, phi, xp, yp)


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

def center_translate(points):
    '''
        Apply a constant translation so the point cloud is centered at
        the origin (judging by the distance between xmin and xmax, ymin
        and ymax, and zmin and zmax).

        The translation vector is computed and then applied according to
        ``new_points = old_points - translation``.

        Return the translated points, the translation vector, and a
        function to undo the translation, e.g. ``lambda points: points +
        translation``.

    '''
    maxes = points.max(axis=0)
    mins = points.min(axis=0)
    translation = 0.5 * (maxes + mins)
    centered_points = points - translation
    def undo_translation(new_points):
        return new_points + translation

    return (centered_points, translation, undo_translation)

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
        Given the point cloud, return (xp_edges, yp_edges).

    '''
    maxes = points.max(axis=0)
    mins = points.min(axis=0)
    ranges = 0.5 * (maxes - mins)
    range_dist = np.linalg.norm(ranges)
    xp_edges = np.linspace(-range_dist, range_dist, nbins+1)
    yp_edges = xp_edges.copy()
    return xp_edges, yp_edges

def get_directions(npoints):
    return cartesian_to_spherical(fibonacci_hemisphere(npoints))

def get_line(dir_i, xp_i, yp_i, dirs, xp, yp, translation):
    '''
        Return the Line specified by the given direction, xprime,
        yprime, and translation.

    '''
    theta, phi = dirs[dir_i]
    xp, yp = xp[xp_i], yp[yp_i]
    raw_line = Line(theta, phi, xp, yp)
    line = Line.applyTranslation(raw_line, translation)
    return line

def cov_evals_evecs(points):
    '''
        Return the eigenvalues and eigenvectors of the covariance matrix
        for the specified points.

        Returns (evals, evecs) sorted in descending order by eigenvalue.
        Note that the numpy convention is that the eigenvector array
        has shape (ndims, neigenvecs) so that the columns specify
        eigenvectors and the rows specify x-y-z. This is the opposite
        convention from the points array where the rows specify the
        points.

    '''
    x = points - np.mean(points, axis=0)
    cov = np.cov(x, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    evecs = evecs[:, order]
    evals = evals[order]
    return evals, evecs

class HoughParameters(object):
    '''
        Keep track of the parameters used for a series of Hough
        transforms.

    '''
    def __init__(self):
        self.ndirections = None
        self.npositions = None
        self.directions = None
        self.position_bins = None
        self.translation = None
        self.accumulator = None
        self.dr = None

def compute_hough(points, params, op='+'):
    '''
        Compute the Hough transformation of the given points and return
        an updated Parameters object.

        The input points should have all 3 axes using the same
        units/dimensions.

        The shape of the accumulator array is: (ndirections, npositions,
        npositions).

        The directions are returned as a 2d array of [theta, prime].

        The position bin edges are returned in an array of length
        npositions + 1 and apply to both the x-prime and y-prime axes.

        The translation is a constant vector which describes how the
        input points are translated to simplify the Hough transformation
        computation. To ensure the lines extracted from the accumulator
        are accurate, you must displace the line specified by
        (direction, xprime, yprime) by adding the
        translation vector to each of its points. This is handled
        by the ``Line.applyTranslation`` function.

    '''
    input_points = points
    test_directions = None
    if params.directions is None:
        test_directions = get_directions(params.ndirections)
        params.directions = test_directions
    else:
        test_directions = params.directions

    if params.translation is None:
        points, translation, undo_translation = center_translate(input_points)
        params.translation = translation
    else:
        points = input_points - params.translation
    xp_edges = None
    yp_edges = None
    if params.position_bins is None:
        xp_edges, yp_edges = get_xp_yp_edges(points, params.npositions)
        params.position_bins = xp_edges
        params.dr = xp_edges[1] - xp_edges[0]
    else:
        xp_edges = params.position_bins
        yp_edges = params.position_bins
    accumulator = None
    if params.accumulator is None:
        params.accumulator = np.zeros((
            len(test_directions),
            len(xp_edges) - 1,
            len(yp_edges) - 1))
        accumulator = params.accumulator
    else:
        accumulator = params.accumulator
    max_xp_i = accumulator.shape[1] - 1
    max_yp_i = accumulator.shape[2] - 1

    for point in points:
        for i, (theta, phi) in enumerate(test_directions):
                xp, yp = compute_xp_yp(theta, phi, *point)
                xp_i = max(0, min(np.searchsorted(xp_edges, xp)-1, max_xp_i))
                yp_i = max(0, min(np.searchsorted(yp_edges, yp)-1,
                    max_yp_i))
                if op == '+':
                    accumulator[i, xp_i, yp_i] += 1
                elif op == '-':
                    accumulator[i, xp_i, yp_i] -= 1
                else:
                    raise ValueError('Invalid op (must be "+" or "-")')

    return params
