import numpy as np

class Hit(object):
    ''' The basic primitive type used in larpix-reconstruction represents a single trigger of a larpix channel '''

    def __init__(self, px, py, ts, q, iochain=None, chipid=None, channelid=None, geom=None):
        self.px = px
        self.py = py
        self.ts = ts
        self.q = q
        self.iochain = iochain
        self.chipid = chipid
        self.channelid = channelid
        self.geom = geom

    def __str__(self):
        string = 'Hit(px={px}, py={py}, ts={ts}, q={q}, iochain={iochain}, '\
            'chipid={chipid}, channelid={channelid}, geom={geom})'.format(**vars(self))
        return string

class HitCollection(object):
    ''' A base class of collected `Hit` types '''
    def __init__(self, hits):
        self.hits = hits
        self.nhit = len(self.hits)
        self.ts_start = min(self.get_hit_attr('ts'))
        self.ts_end = max(self.get_hit_attr('ts'))
        self.q = sum(self.get_hit_attr('q'))

    def __str__(self):
        string = '{}(hits=[\n\t{}]\n\t)'.format(self.__class__.__name__, \
            ', \n\t'.join(str(hit) for hit in self.hits))
        return string

    def __getitem__(self, key):
        '''
        Access to hits or hit attr.
        If key is an int -> returns hit at that index
        If key in a str -> returns attr value of all hits specified by key
        If key is a dict -> returns hits with attr values that match dict
        If key is a list or tuple -> returns hits at indices
        E.g.
        hc = HitCollection(hits=[Hit(0,0,0,0), Hit(1,0,0,0), Hit(1,1,0,0)])
        hc[0] # Hit(0,0,0,0)
        hc['px'] # [0,1,1]
        hc[{'px' : 1}] # [Hit(1,0,0,0), Hit(1,1,0,0)]
        hc[0,1] # [Hit(0,0,0,0), Hit(1,0,0,0)]
        '''
        if isinstance(key, int):
            return self.hits[key]
        elif isinstance(key, str):
            return self.get_hit_attr(key)
        elif isinstance(key, dict):
            return self.get_hit_match(key)
        elif isinstance(key, list) or isinstance(key, tuple):
            return [self.hits[idx] for idx in key]

    def __len__(self):
        return nhit

    def get_hit_attr(self, attr, default=None):
        ''' Get a list of the specified attribute from event hits '''
        if not default is None:
            return [getattr(hit, attr, default) for hit in self.hits]
        else:
            return [getattr(hit, attr) for hit in self.hits]

    def get_hit_match(self, attr_value_dict):
        '''
        Returns a list of hits that match the attr_value_dict 
        attr_value_dict = { <hit attribute> : <value of attr>, ...}
        '''
        return_list = []
        for hit in self.hits:
            if all([getattr(hit, attr) == value for attr, value in \
                        attr_value_dict.items()]):
                return_list += [hit]
        return return_list

class Event(HitCollection):
    ''' A class for a collection of hits associated by the event builder, contains reconstructed objects '''
    def __init__(self, evid, hits, reco_obj=[]):
        HitCollection.__init__(self, hits)
        self.evid = evid
        self.reco_objs = reco_obj

    def __str__(self):
        string = HitCollection.__str__(self)[:-1]
        string += ', evid={evid}, reco_objs={reco_objs})'.format(\
            **vars(self))
        return string

class Track(HitCollection):
    ''' A class representing a straight line segment and associated hits '''
    def __init__(self, hits, line, hough_params=None, vertices=[]):
        HitCollection.__init__(self, hits)
        self.hough_params = hough_params
        self.line = line
        self.vertices = []

class Shower(HitCollection):
    ''' A class representing a shower '''
    pass
# etc          

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
        return cls(theta, phi, *Line.compute_xp_yp(theta, phi, px, py, pz))

    @classmethod
    def applyTranslation(cls, original, translation):
        '''
            Return a new line which has been translated by the given
            translation vector.
        '''
        point = original.points('x', 0, 1, 2)[0]
        theta, phi = original.theta, original.phi
        px, py, pz = point + translation
        xp, yp = Line.compute_xp_yp(theta, phi, px, py, pz)
        return cls(theta, phi, xp, yp)

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

    @staticmethod
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

