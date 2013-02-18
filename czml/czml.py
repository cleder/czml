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
    import simplejson as json
except ImportError:
    import json

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

    def loads(self, data):
        packets = json.loads(data)
        self.load(pakets)

    def load(self, data):
        self.packets = data


class Position(object):
    """ The position of the object in the world. The position has no
    direct visual representation, but it is used to locate billboards,
    labels, and other primitives attached to the object. """

    pass

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
