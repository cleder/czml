# -*- coding: utf-8 -*-
#    Copyright (C) 2013  Christian Ledermann
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
try:
    from itertools import izip_longest
except ImportError:
    from itertools import zip_longest as izip_longest
try:
    import simplejson as json
except ImportError:
    import json

from datetime import datetime, date
import dateutil.parser


try:
    unicode
except NameError:
    # Python 3
    basestring = unicode = str


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return izip_longest(*args, fillvalue=fillvalue)



class CZML(object):
    """ CZML is a subset of JSON, meaning that a valid CZML document
    is also a valid JSON document. Specifically, a CZML document contains
    a single JSON array where each object-literal element in the array is
    a CZML packet."""

    packets = None

    def __init__(self, packets=None):
        if packets:
            self.packets = packets
        else:
            self.packets = []

    def dumps(self):
        if self.packets:
            json.dumps(packets)
        else:
            return '[]'

    def dump(self):
        return self.packets


    def loads(self, data):
        packets = json.loads(data)
        self.load(pakets)

    def load(self, data):
        self.packets = data


class _DateTimeAware(object):
    """ A baseclass for Date time aware objects """

    _epoch = None
    _nextTime = None
    _previousTime = None

    def __init__(self, epoch=None, nextTime=None, previousTime=None):
        self.epoch = epoch
        self.nextTime = nextTime
        self.previousTime = previousTime

    @property
    def epoch(self):
        """ Specifies the epoch to use for times specifies as seconds
        since an epoch. """
        if self._epoch:
            return self._epoch.isoformat()

    @epoch.setter
    def epoch(self, dt):
        if dt is None:
            self._epoch = None
        elif isinstance(dt, (date,datetime)):
            self._epoch = dt
        elif isinstance(dt, basestring):
            self._epoch = dateutil.parser.parse(dt)
        else:
            raise ValueError

    @property
    def nextTime(self):
        """The time of the next sample within this interval, specified as
        either an ISO 8601 date and time string or as seconds since epoch.
        This property is used to determine if there is a gap between samples
        specified in different packets."""
        if isinstance(self._nextTime, (date,datetime)):
            return self._nextTime.isoformat()
        elif isinstance(self._nextTime, (int, long, float)):
            return self._nextTime

    @nextTime.setter
    def nextTime(self, dt):
        if dt is None:
            self._nextTime = None
        elif isinstance(dt, (date,datetime)):
            self._nextTime = dt
        elif isinstance(dt, (int, long, float)):
            self._nextTime = dt
        elif isinstance(dt, basestring):
            try:
                self._nextTime = float(dt)
            except ValueError:
                self._nextTime = dateutil.parser.parse(dt)
        else:
            raise ValueError


    @property
    def previousTime(self):
        """The time of the previous sample within this interval, specified
        as either an ISO 8601 date and time string or as seconds since epoch.
        This property is used to determine if there is a gap between samples
        specified in different packets."""
        if isinstance(self._previousTime, (date,datetime)):
            return self._previousTime.isoformat()
        elif isinstance(self._previousTime, (int, long, float)):
            return self._previousTime

    @previousTime.setter
    def previousTime(self, dt):
        if dt is None:
            self._previousTime = None
        elif isinstance(dt, (date,datetime)):
            self._previousTime = dt
        elif isinstance(dt, (int, long, float)):
            self._previousTime = dt
        elif isinstance(dt, basestring):
            try:
                self._previousTime = float(dt)
            except ValueError:
                self._previousTime = dateutil.parser.parse(dt)
        else:
            raise ValueError


    def loads(self, data):
        d = json.loads(data)
        self.epoch = d.get('epoch', None)
        self.nextTime = d.get('nextTime', None)
        self.previousTime = d.get('previousTime', None)


    def data(self):
        return {'epoch': self.epoch,
            'nextTime': self.nextTime,
            'previousTime': self.previousTime,
            }

    def dumps(self):
        return json.dumps(self.data())


class _Coordinate(object):
    """ [Longitude, Latitude, Height] or [X, Y, Z] or
    [Time, Longitude, Latitude, Height] or [Time, X, Y, Z]
    """
    x = y = z = 0
    t = None

    def __init__(self, x, y, z=0, t=None):
        self.x = x
        self.y = y
        self.z = z
        self.t = t


class _Coordinates(object):

    coords = None

    def __init__(self, coords):
        if len(coords) < 3:
            self.coords = [_Coordinate(coords[0], coords[1])]
        elif len(coords) < 4:
            self.coords = [_Coordinate(coords[0], coords[1], coords[2])]
        elif len(coords) == 4:
            self.coords = [_Coordinate(coords[1], coords[2], coords[3], coords[0])]
        elif len(coords) >= 4:
            self.coords = []
            for coord in grouper(coords, 4):
                self.coords.append(_Coordinate(coord[1], coord[2],
                                        coord[3], coord[0]))
        else:
            raise ValueError







class Position(_DateTimeAware):
    """ The position of the object in the world. The position has no
    direct visual representation, but it is used to locate billboards,
    labels, and other primitives attached to the object. """


    # The reference frame in which cartesian positions are specified.
    # Possible values are "FIXED" and "INERTIAL". In addition, the value
    # of this property can be a hash (#) symbol followed by the ID of
    # another object in the same scope whose "position" and "orientation"
    # properties define the reference frame in which this position is defined.
    # This property is ignored when specifying position with any type other
    # than cartesian. If this property is not specified,
    # the default reference frame is "FIXED".
    referenceFrame = None

    # The position represented as a Cartesian [X, Y, Z] in the meters
    # relative to the referenceFrame. If the array has three elements,
    # the position is constant. If it has four or more elements, they
    # are time-tagged samples arranged as
    # [Time, X, Y, Z, Time, X, Y, Z, Time, X, Y, Z, ...],
    # where Time is an ISO 8601 date and time string or seconds since epoch.
    cartesian = None

    # The position represented as a WGS 84 Cartographic
    # [Longitude, Latitude, Height] where longitude and latitude are in
    # radians and height is in meters. If the array has three elements,
    # the position is constant. If it has four or more elements, they are
    # time-tagged samples arranged as
    # [Time, Longitude, Latitude, Height, Time, Longitude, Latitude, Height, ...],
    # where Time is an ISO 8601 date and time string or seconds since epoch.
    cartographicRadians = None

    # The position reprsented as a WGS 84 Cartographic
    # [Longitude, Latitude, Height] where longitude and latitude are in
    # degrees and height is in meters. If the array has three elements,
    # the position is constant. If it has four or more elements, they are
    # time-tagged samples arranged as
    # [Time, Longitude, Latitude, Height, Time, Longitude, Latitude, Height, ...],
    # where Time is an ISO 8601 date and time string or seconds since epoch.
    cartographicDegrees = None

    def data(self):
        d = super(Position, self).data()


class Billboard (object):
    """A billboard, or viewport-aligned image. The billboard is positioned
    in the scene by the position property.
    A billboard is sometimes called a marker."""

    pass

class VertexPositions(object):
    """The world-space positions of vertices.
    The vertex positions have no direct visual representation, but they
    are used to define polygons, polylines, and other objects attached
    to the object."""

    pass


class Orientation(object):
    """The orientation of the object in the world.
    The orientation has no direct visual representation, but it is used
    to orient models, cones, and pyramids attached to the object."""

    pass

class Point(object):
    """A point, or viewport-aligned circle.
    The point is positioned in the scene by the position property. """

    pass

class Label(object):
    """ A string of text.
    The label is positioned in the scene by the position property."""

    pass

class Polyline(object):
    """ A polyline, which is a line in the scene composed of multiple segments.
    The vertices of the polyline are specified by the vertexPositions property.
    """
    pass

class Path(object):
    """A path, which is a polyline defined by the motion of an object over
    time. The possible vertices of the path are specified by the position
    property."""
    pass

class Polygon(object):
    """A polygon, which is a closed figure on the surface of the Earth.
    The vertices of the polygon are specified by the vertexPositions property.
    """
    pass

class Cone(object):
    """ A cone starts at a point or apex and extends in a circle of
    directions which all have the same angular separation from the Z-axis
    of the object to which the cone is attached. The cone may be capped
    at a radial limit, it may have an inner hole, and it may be only a
    part of a complete cone defined by clock angle limits. The apex
    point of the cone is defined by the position property and extends in
    the direction of the Z-axis as defined by the orientation property.
    """
    pass

class Pyramid(object):
    """A pyramid starts at a point or apex and extends in a specified list
    of directions from the apex. Each pair of directions forms a face of
    the pyramid. The pyramid may be capped at a radial limit.
    """
    pass


class Camera(object):
    """A camera."""
    pass



class CZMLPacket(object):
    """  A CZML packet describes the graphical properties for a single
    object in the scene, such as a single aircraft.
    """

    # Each packet has an id property identifying the object it is describing.
    # IDs do not need to be GUIDs - URIs make good IDs - but they do need
    # to uniquely identify a single object within a CZML source and any
    # other CZML sources loaded into the same scope.
    # If an id is not specified, the client will automatically generate
    # a unique one. However, this prevents later packets from referring
    # to this object in order to, for example, add more data to it.
    # A single CZML stream or document can contain multiple packets with
    # the same id, describing different aspects of the same object.
    id = None

    # The availability property indicates when data for an object is available.
    # If data for an object is known to be available at the current animation
    # time, but the client does not yet have that data (presumably because
    # it will arrive in a later packet), the client will pause with a message
    # like "Buffering..." while it waits to receive the data. The property
    # can be a single string specifying a single interval, or an array
    # of strings representing intervals.
    availability = None

    # The position of the object in the world. The position has no direct
    # visual representation, but it is used to locate billboards, labels,
    # and other primitives attached to the object.
    position = None

    # A billboard, or viewport-aligned image. The billboard is positioned
    # in the scene by the position property. A billboard is sometimes
    # called a marker.
    billboard = None

    # The world-space positions of vertices. The vertex positions have no
    # direct visual representation, but they are used to define polygons,
    # polylines, and other objects attached to the object.
    vertexPositions = None

    # The orientation of the object in the world. The orientation has no
    # direct visual representation, but it is used to orient models,
    # cones, and pyramids attached to the object.
    orientation = None

    # A point, or viewport-aligned circle. The point is positioned in
    # the scene by the position property.
    point = None

    # A string of text. The label is positioned in the scene by the
    # position property.
    label = None

    # A polyline, which is a line in the scene composed of multiple segments.
    # The vertices of the polyline are specified by the vertexPositions
    # property.
    polyline = None

    # A path, which is a polyline defined by the motion of an object over
    # time. The possible vertices of the path are specified by the
    # position property.
    path = None

    # A polygon, which is a closed figure on the surface of the Earth.
    # The vertices of the polygon are specified by the vertexPositions
    # property.
    polygon = None

    # A cone. A cone starts at a point or apex and extends in a circle of
    # directions which all have the same angular separation from the Z-axis
    # of the object to which the cone is attached. The cone may be capped
    # at a radial limit, it may have an inner hole, and it may be only a
    # part of a complete cone defined by clock angle limits. The apex point
    # of the cone is defined by the position property and extends in the
    # direction of the Z-axis as defined by the orientation property.
    cone = None

    # A pyramid. A pyramid starts at a point or apex and extends in a
    # specified list of directions from the apex. Each pair of directions
    # forms a face of the pyramid. The pyramid may be capped at a radial limit.
    pyramid = None

    # A camera.
    camera = None




    def __init__(self, id=None, availability = None):
        self.id = id
        self.availability = availability

    def dumps(self):
        d = {'id': self.id, 'availability': self.availability}
        json.dumps(d)


    def loads(self, data):
        d = json.loads(data)
        self.load(d)

    def load(self, data):
        self.id = data.get('id', None)
        self.availability = data.get('availability', None)
