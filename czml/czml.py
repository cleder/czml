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
    long
except NameError:
    # Python 3
    long = int

try:
    unicode
except NameError:
    # Python 3
    basestring = unicode = str

# XXX Import the geometries from shapely if it is installed
# or otherwise from Pygeoif

from pygeoif import geometry

from pygeoif.geometry import as_shape as asShape


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return izip_longest(*args, fillvalue=fillvalue)


def class_property(cls, name, doc=None):
    """Returns a property function that checks to be sure
    the value being assigned is a certain class before assigning it to a hidden
    variable defined by "_" + name.  Also transparently returns the data()
    method when the object value is requested.
    """

    def getter(self):
        val = getattr(self, '_' + name)
        if val is not None:
            return val.data()

    def setter(self, val):
        hidden_attribute = '_' + name
        if isinstance(val, cls):
            setattr(self, hidden_attribute, val)
        elif isinstance(val, dict):
            m = cls()
            m.load(val)
            setattr(self, hidden_attribute, m)
        elif val is None:
            setattr(self, hidden_attribute, None)
        else:
            # See if this value works as the only input to cls
            try:
                setattr(self, hidden_attribute, cls(val))
            except TypeError:
                raise TypeError('Property %s must be of class %s. %s was provided.' %
                                (name, cls.__name__, val.__class__.__name__))

    return property(getter, setter, doc=doc)

from pytz import utc

def datetime_property(name, allow_offset=False, doc=None):
    """Generates a datetime property that handles strings and timezones.
    """
    reserved_name = '_' + name

    def getter(self):
        val = getattr(self, reserved_name)
        if isinstance(val, (date, datetime)):
            return val.isoformat()
        elif allow_offset and isinstance(val, (int, long, float)):
            return val

    def setter(self, dt):
        if dt is None:
            setattr(self, reserved_name, None)
        elif isinstance(dt, (date, datetime)):
            setattr(self, reserved_name, dt)
        elif allow_offset and isinstance(dt, (int, long, float)):
            setattr(self, reserved_name, dt)
        elif isinstance(dt, basestring):
            if allow_offset:
                try:
                    dt = float(dt)
                except ValueError:
                    dt = dateutil.parser.parse(dt)
            else:
                dt = dateutil.parser.parse(dt)
            setattr(self, reserved_name, dt)
        else:
            raise ValueError

    return property(getter, setter, doc=doc)

# Many classes will have material and position properties.
material_property = lambda x: class_property(Material, x)
position_property = lambda x: class_property(Position, x)


class _CZMLBaseObject(object):
    _properties = ()

    def __init__(self, **kwargs):
        """Default init functionality is to load kwargs
        """
        self.load(kwargs)

    @property
    def properties(self):
        return self._properties

    def write(self, filename):
        with open(filename, 'w') as outfile:
            json.dump(list(self.data()), outfile)

    def dumps(self, **kwargs):
        d = self.data()
        return json.dumps(d, **kwargs)

    def data(self):
        d = {}
        for attr in self.properties:
            a = getattr(self, attr)
            if a is not None:
                # These classes have a data method that should be called.
                if isinstance(a, (_CZMLBaseObject, _Colors,
                                  _Coordinates, _Positions)):
                    d[attr] = a.data()
                else:
                    d[attr] = a
        return d

    def loads(self, data):
        packets = json.loads(data)
        self.load(packets)

    def load(self, data):
        if hasattr(data, 'iteritems'):
            # python 2
            iterator = data.iteritems
        elif hasattr(data, 'items'):
            # python 3
            iterator = data.items
        for k, v in iterator():
            if k in self.properties:
                setattr(self, k, v)
            else:
                raise ValueError


class CZML(_CZMLBaseObject):
    """ CZML is a subset of JSON, meaning that a valid CZML document
    is also a valid JSON document. Specifically, a CZML document contains
    a single JSON array where each object-literal element in the array is
    a CZML packet."""

    packets = None

    def __init__(self, packets=None):
        if packets:
            for p in packets:
                self.append(p)
        else:
            self.packets = []

    def data(self):
        for p in self.packets:
            yield p.data()

    def dumps(self, **kwargs):
        d = list(self.data())
        return json.dumps(d, **kwargs)

    def load(self, data):
        self.packets = []
        for packet in data:
            p = CZMLPacket()
            p.load(packet)
            self.packets.append(p)

    def append(self, packet):
        if self.packets is None:
            self.packets = []
        if isinstance(packet, CZMLPacket):
            self.packets.append(packet)
        else:
            raise ValueError

class _DateTimeAware(_CZMLBaseObject):
    """ A baseclass for Date time aware objects """

    _epoch = None
    _nextTime = None
    _previousTime = None
    _properties = ('epoch', 'nextTime', 'previousTime')

    epoch = datetime_property('epoch', doc=
        """ Specifies the epoch to use for times specifies as seconds
        since an epoch. """)
    nextTime = datetime_property('nextTime', allow_offset=True, doc=
        """The time of the next sample within this interval, specified as
        either an ISO 8601 date and time string or as seconds since epoch.
        This property is used to determine if there is a gap between samples
        specified in different packets.""")
    previousTime = datetime_property('previousTime', allow_offset=True, doc=
        """The time of the previous sample within this interval, specified
        as either an ISO 8601 date and time string or as seconds since epoch.
        This property is used to determine if there is a gap between samples
        specified in different packets.""")


class _Coordinate(object):
    """ [Longitude, Latitude, Height] or [X, Y, Z] or
    [Time, Longitude, Latitude, Height] or [Time, X, Y, Z]
    """
    x = y = z = 0
    t = None

    def __init__(self, x, y=None, z=0, t=None):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        if t is None:
            self.t = None
        elif isinstance(t, (date, datetime)):
            self.t = t
        elif isinstance(t, (int, long, float)):
            self.t = float(t)
        elif isinstance(t, basestring):
            try:
                self.t = float(t)
            except ValueError:
                self.t = dateutil.parser.parse(t)
        else:
            raise ValueError


class _Coordinates(object):

    coords = None

    def __init__(self, coords):
        if isinstance(coords, (list, tuple)):
            try:
                float(coords[1])
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
            except TypeError:
                self.coords = []
                for coord in grouper(coords, 2):
                    geom = asShape(coord[1])
                    assert(isinstance(geom, geometry.Point))
                    self.coords.append(_Coordinate(*geom.coords[0], t=coord[0]))
        else:
            geom = asShape(coords)
            if isinstance(geom, geometry.Point):
                self.coords = [_Coordinate(*geom.coords[0])]

    def data(self):
        d = []
        if self.coords:
            for coord in self.coords:
                if isinstance(coord.t, (date, datetime)):
                     d.append(coord.t.isoformat())
                elif coord.t is None:
                    pass
                else:
                    d.append(coord.t)
                d.append(coord.x)
                d.append(coord.y)
                d.append(coord.z)
        return d


class Number(_DateTimeAware):
    """Represents numbers"""
    number = None

    def __init__(self, number=number, **kwargs):
        self._properties += ('number',)
        super(Number, self).__init__(number=number, **kwargs)

    def data(self):
        data = super(Number, self).data()
        if (('number' in data) and (len(data.keys()) == 1) and
            isinstance(data['number'], (int, float, str, long))):
            return data['number']
        return super(Number, self).data()



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

    _cartesian = None
    _cartographicRadians = None
    _cartographicDegrees = None
    interpolationAlgorithm = None
    interpolationDegree = None

    def __init__(self, **kwargs):
        self._properties += ('cartesian', 'cartographicRadians',
                             'cartographicDegrees', 'interpolationAlgorithm',
                             'interpolationDegree', 'referenceFrame')
        super(Position, self).__init__(**kwargs)

    @property
    def cartesian(self):
        """ The position represented as a Cartesian [X, Y, Z] in the meters
        relative to the referenceFrame. If the array has three elements,
        the position is constant. If it has four or more elements, they
        are time-tagged samples arranged as
        [Time, X, Y, Z, Time, X, Y, Z, Time, X, Y, Z, ...],
        where Time is an ISO 8601 date and time string or seconds since epoch.
        """
        return self._cartesian

    @cartesian.setter
    def cartesian(self, geom):
        if geom is not None:
            self._cartesian = _Coordinates(geom)
        else:
            self._cartesian = None

    @property
    def cartographicDegrees(self):
        """The position represented as a WGS 84 Cartographic
        [Longitude, Latitude, Height] where longitude and latitude are in
        degrees and height is in meters. If the array has three elements,
        the position is constant. If it has four or more elements, they are
        time-tagged samples arranged as
        [Time, Longitude, Latitude, Height, Time, Longitude, Latitude, Height, ...],
        where Time is an ISO 8601 date and time string or seconds since epoch.
        """
        return self._cartographicDegrees

    @cartographicDegrees.setter
    def cartographicDegrees(self, geom):
        if geom is not None:
            self._cartographicDegrees = _Coordinates(geom)
        else:
            self._cartographicDegrees = None


    @property
    def cartographicRadians(self):
        """The position represented as a WGS 84 Cartographic
        [Longitude, Latitude, Height] where longitude and latitude are in
        radians and height is in meters. If the array has three elements,
        the position is constant. If it has four or more elements, they are
        time-tagged samples arranged as
        [Time, Longitude, Latitude, Height, Time, Longitude, Latitude, Height, ...],
        where Time is an ISO 8601 date and time string or seconds since epoch.
        """
        return self._cartographicRadians

    @cartographicRadians.setter
    def cartographicRadians(self, geom):
        if geom is not None:
            self._cartographicRadians = _Coordinates(geom)
        else:
            self._cartographicRadians = None


class Radii(_DateTimeAware):
    """ Radii is in support of ellipsoids.  This class is nearly an identical
    copy of the Position class since its behavior is almost the same.
    """


    # The reference frame in which cartesian positions are specified.
    # Possible values are "FIXED" and "INERTIAL". In addition, the value
    # of this property can be a hash (#) symbol followed by the ID of
    # another object in the same scope whose "position" and "orientation"
    # properties define the reference frame in which this position is defined.
    # This property is ignored when specifying position with any type other
    # than cartesian. If this property is not specified,
    # the default reference frame is "FIXED".
    referenceFrame = None
    _cartesian = None

    def __init__(self, **kwargs):
        self._properties += ('cartesian', 'referenceFrame')
        super(_DateTimeAware, self).__init__(**kwargs)

    @property
    def cartesian(self):
        """ The position represented as a Cartesian [X, Y, Z] in the meters
        relative to the referenceFrame. If the array has three elements,
        the position is constant. If it has four or more elements, they
        are time-tagged samples arranged as
        [Time, X, Y, Z, Time, X, Y, Z, Time, X, Y, Z, ...],
        where Time is an ISO 8601 date and time string or seconds since epoch.
        """
        return self._cartesian

    @cartesian.setter
    def cartesian(self, geom):
        if geom is not None:
            self._cartesian = _Coordinates(geom)
        else:
            self._cartesian = None

    def load(self, data):
        super(Radii, self).load(data)
        self.cartesian = data.get('cartesian', None)

class _Color(object):
    r = g = b = a = 0
    t = None

    def __init__(self, r, g, b, a=1, t=None, num=float):
        self.r = num(r)
        self.g = num(g)
        self.b = num(b)
        self.a = num(a)
        if t is None:
            self.t = None
        elif isinstance(t, (date, datetime)):
            self.t = t
        elif isinstance(t, (int, long, float)):
            self.t = float(t)
        elif isinstance(t, basestring):
            try:
                self.t = float(t)
            except ValueError:
                self.t = dateutil.parser.parse(t)
        else:
            raise ValueError



class _Colors(object):
    """ The color specified as an array of color components
    [Red, Green, Blue, Alpha].
    If the array has four elements, the color is constant.
    If it has five or more elements, they are time-tagged samples arranged as
    [Time, Red, Green, Blue, Alpha, Time, Red, Green, Blue, Alpha, ...],
    where Time is an ISO 8601 date and time string or seconds since epoch.
    """
    colors = None

    def __init__(self, colors, num=float):
        if isinstance(colors, (list, tuple)):
            if len(colors) == 3:
                self.colors = [_Color(colors[0], colors[1], colors[2], num=num)]
            elif len(colors) == 4:
                self.colors = [_Color(colors[0], colors[1], colors[2], colors[3], num=num)]
            elif len(colors) == 5:
                self.colors = [_Color(colors[1], colors[2], colors[3], colors[4], colors[0], num=num)]
            elif len(colors) >= 5:
                self.colors = []
                for color in grouper(colors, 5):
                    self.colors.append(_Color(color[1], color[2],
                                            color[3], color[4] , color[0], num=num))
            else:
                raise ValueError
        elif colors is None:
            self.colors = None
        else:
            raise ValueError

    def data(self):
        d = []
        if self.colors:
            for color in self.colors:
                if isinstance(color.t, (date, datetime)):
                     d.append(color.t.isoformat())
                elif color.t is None:
                    pass
                else:
                    d.append(color.t)
                d.append(color.r)
                d.append(color.g)
                d.append(color.b)
                d.append(color.a)
        return d


class Color(_DateTimeAware):

    _rgba = None
    _rgbaf = None

    def __init__(self, **kwargs):
        self._properties += ('rgba', 'rgbaf')
        super(_DateTimeAware, self).__init__(**kwargs)

    @property
    def rgba(self):
        """The color specified as an array of color components
        [Red, Green, Blue, Alpha] where each component is in the
        range 0-255. If the array has four elements, the color is constant.
        If it has five or more elements, they are time-tagged samples arranged as
        [Time, Red, Green, Blue, Alpha, Time, Red, Green, Blue, Alpha, ...],
        where Time is an ISO 8601 date and time string or seconds since epoch.
        """
        if self._rgba is not None:
            return self._rgba.data()

    @rgba.setter
    def rgba(self, colors):
        if colors is None:
            self._rgba = None
        else:
            self._rgba = _Colors(colors, num=int)

    @property
    def rgbaf(self):
        """The color specified as an array of color components
        [Red, Green, Blue, Alpha] where each component is in the
        range 0.0-1.0. If the array has four elements, the color is constant.
        If it has five or more elements, they are time-tagged samples
        arranged as
        [Time, Red, Green, Blue, Alpha, Time, Red, Green, Blue, Alpha, ...],
        where Time is an ISO 8601 date and time string or seconds since epoch.
        """
        if self._rgbaf is not None:
            return self._rgbaf.data()

    @rgbaf.setter
    def rgbaf(self, colors):
        if colors is None:
            self._rgbaf = None
        else:
            self._rgbaf = _Colors(colors, num=float)

class Scale(_DateTimeAware):
    """ The scale of the billboard. The scale is multiplied with the
    pixel size of the billboard's image. For example, if the scale is 2.0,
    the billboard will be rendered with twice the number of pixels,
    in each direction, of the image."""

    _number = None


    @property
    def number(self):
        """ The floating-point value. The value may be a single number,
        in which case the value is constant over the interval, or it may
        be an array. If it is an array and the array has one element,
        the value is constant over the interval. If it has two or more
        elements, they are time-tagged samples arranged as
        [Time, Value, Time, Value, ...], where Time is an ISO 8601 date
        and time string or seconds since epoch."""
        if isinstance(self._number, alist):
            val = []
            for d in grouper(self._number, 2):
                if isinstance(d[0], (int, long, float)):
                     val.append(d[0])
                else:
                     val.append(d[0].isoformat())
            return val
        else:
            return self._number

    @number.setter
    def number(self, data):
        self._number = []
        if isinstance(data, (list, tuple)):
            if len(data) > 1:
                for d in grouper(data, 2):
                    v = float(d[1])
                    t = d[0]
                    if isinstance(t, (date, datetime)):
                       t = t
                    elif isinstance(t, (int, long, float)):
                        t = float(t)
                    elif isinstance(t, basestring):
                        try:
                            t = float(t)
                        except ValueError:
                            t = dateutil.parser.parse(t)
                    else:
                        raise ValueError
                    self._number.append((t, v))
            else:
                self._number = float(data[0])
        else:
            self._number = float(data)

    def data(self):
        d = super(Scale, self).data()
        if self.number:
            d['number'] = self.number
        return d

class Billboard(_CZMLBaseObject):
    """A billboard, or viewport-aligned image. The billboard is positioned
    in the scene by the position property.
    A billboard is sometimes called a marker."""

    # Whether or not the billboard is shown.
    show = None

    # The image displayed on the billboard, expressed as a URL.
    # For broadest client compatibility, the URL should be accessible
    # via Cross-Origin Resource Sharing (CORS).
    # The URL may also be a data URI.
    image = None

    _color = None

    scale = None

    _properties = ('show','image','color','scale')




class Clock(_CZMLBaseObject):
    """The clock settings for the entire data set.
       Only valid on the document object."""

    interval = None

    _currentTime = None
    _multiplier = None
    _range = None
    _step = None
    _properties = ('currentTime', 'multiplier', 'interval', 'range', 'step',)


class _Positions(object):
    """ The list of positions [X, Y, Z, X, Y, Z, ...] """

    coords = None

    def __init__(self, coords):
        if isinstance(coords, (list, tuple)):
            assert(len(coords) % 3 == 0)
            assert(len(coords) >= 6)
            for coord in coords:
                if isinstance(coord, (int, long, float)):
                    continue
                else:
                    raise ValueError
            self.coords = coords
        else:
            geom = asShape(coords)
            if isinstance(geom, geometry.Polygon):
                geom = geom.exterior
            if isinstance(geom, (geometry.LineString, geometry.LinearRing)):
                self.coords = []
                for coord in geom.coords:
                    if len(coord) == 2:
                        self.coords += [coord[0], coord[1], 0]
                    elif len(coord) == 3:
                        self.coords += coord
                    else:
                        raise ValueError

    def data(self):
        return self.coords


class Positions(_CZMLBaseObject):
    """The world-space positions of vertices.
    The vertex positions have no direct visual representation, but they
    are used to define polygons, polylines, and other objects attached
    to the object."""

    # The reference frame in which cartesian positions are specified.
    # Possible values are "FIXED" and "INERTIAL".
    # In addition, the value of this property can be a hash (#) symbol
    # followed by the ID of another object in the same scope
    # whose "position" and "orientation" properties define the reference
    # frame in which this position is defined.
    # This property is ignored when specifying position with any type
    # other than cartesian. If this property is not specified,
    # the default reference frame is "FIXED".
    referenceFrame = None

    # The list of positions specified as references. Each reference is
    # to a property that defines a single position,
    # possible as it changes with time.
    references = None

    _cartesian = None
    _cartographicRadians = None
    _cartographicDegrees = None


    def __init__(self, referenceFrame=None,
            cartesian=None, cartographicRadians=None,
            cartographicDegrees=None, references=None):
        self.cartesian = cartesian
        self.cartographicRadians = cartographicRadians
        self.cartographicDegrees = cartographicDegrees
        self.referenceFrame = referenceFrame
        self.references = references


    @property
    def cartesian(self):
        """The list of positions represented as Cartesian
        [X, Y, Z, X, Y, Z, ...] in the meters
        relative to the referenceFrame.
        """
        return self._cartesian

    @cartesian.setter
    def cartesian(self, geom):
        if geom is not None:
            self._cartesian = _Positions(geom)
        else:
            self._cartesian = None

    @property
    def cartographicDegrees(self):
        """The list of positions represented as WGS 84
        [Longitude, Latitude, Height, Longitude, Latitude, Height, ...]
        where longitude and latitude are in degrees and height is in meters.
        """
        return self._cartographicDegrees

    @cartographicDegrees.setter
    def cartographicDegrees(self, geom):
        if geom is not None:
            self._cartographicDegrees = _Positions(geom)
        else:
            self._cartographicDegrees = None


    @property
    def cartographicRadians(self):
        """The list of positions represented as WGS 84
        [Longitude, Latitude, Height, Longitude, Latitude, Height, ...]
        where longitude and latitude are in radians and height is in meters.
        """
        return self._cartographicRadians

    @cartographicRadians.setter
    def cartographicRadians(self, geom):
        if geom is not None:
            self._cartographicRadians = _Positions(geom)
        else:
            self._cartographicRadians = None

    def load(self, data):
        self.cartographicDegrees = data.get('cartographicDegrees', None)
        self.cartographicRadians = data.get('cartographicRadians', None)
        self.cartesian = data.get('cartesian', None)


    def data(self):
        d = {}
        if self.cartographicDegrees:
            d['cartographicDegrees'] = self.cartographicDegrees.data()
        if self.cartographicRadians:
            d['cartographicRadians'] = self.cartographicRadians.data()
        if self.cartesian:
            d['cartesian'] = self.cartesian.data()
        if self.references:
            d["references"] = self.references
        return d



class Orientation(_DateTimeAware):
    """The orientation of the object in the world.
    The orientation has no direct visual representation, but it is used
    to orient models, cones, and pyramids attached to the object.

    TODO: check the quaternions to be sure they're valid.

    https://github.com/AnalyticalGraphicsInc/cesium/wiki/CZML-Content#orientation

    """

    unitQuaternion = None
    axes = None
    interpolationAlgorithm = None
    interpolationDegree = None

    def __init__(self, **kwargs):
        self._properties += ('axes', 'unitQuaternion',
                             'interpolationAlgorithm', 'interpolationDegree')
        super(Orientation, self).__init__(**kwargs)


class Point(_CZMLBaseObject):
    """A point, or viewport-aligned circle.
    The point is positioned in the scene by the position property. """

    show = False
    _color = None
    _outlineColor = None

    # The width of the outline of the point.
    outlineWidth = None

    # The size of the point, in pixels.
    pixelSize = None

    def __init__(self, show=False, color=None, pixelSize=None,
                outlineColor=None, outlineWidth=None):
        self.show = show
        self.color = color
        self.pixelSize = pixelSize
        self.outlineColor = outlineColor
        self.outlineWidth = outlineWidth


    @property
    def color(self):
        """ The color of the point."""
        if self._color is not None:
            return self._color.data()

    @color.setter
    def color(self, color):
        if isinstance(color, Color):
            self._color = color
        elif isinstance(color, dict):
            col = Color()
            col.load(color)
            self._color = col
        elif color is None:
            self._color = None
        else:
            raise TypeError

    @property
    def outlineColor(self):
        """ The color of the outline of the point."""
        if self._outlineColor is not None:
            return self._outlineColor.data()

    @outlineColor.setter
    def outlineColor(self, color):
        if isinstance(color, Color):
            self._outlineColor = color
        elif isinstance(color, dict):
            col = Color()
            col.load(color)
            self._outlineColor = col
        elif color is None:
            self._outlineColor = None
        else:
            raise TypeError




    def data(self):
        d = {}
        if self.show:
            d['show'] = True
        if self.show == False:
            d['show'] = False
        if self.color:
            d['color'] = self.color
        if self.pixelSize:
            d['pixelSize'] = self.pixelSize
        if self.outlineColor:
            d['outlineColor'] = self.outlineColor
        if self.outlineWidth:
            d['outlineWidth'] = self.outlineWidth

        return d

    def load(self, data):
        self.show = data.get('show', None)
        self.color = data.get('color', None)
        self.outlineColor = data.get('outlineColor', None)
        self.pixelSize = data.get('pixelSize', None)
        self.outlineWidth = data.get('outlineWidth', None)



class Label(_CZMLBaseObject):
    """ A string of text.
    The label is positioned in the scene by the position property."""

    text = None
    show = False
    horizontalOrigin = None
    scale = None
    pixelOffset = None

    def __init__(self, text=None, show=False):
        self.text = text
        self.show = show

    def data(self):
        d = {}
        if self.show:
            d['show'] = True
        if self.show == False:
            d['show'] = False
        if self.text:
            d['text'] = self.text
        if self.horizontalOrigin:
            d['horizontalOrigin'] = self.horizontalOrigin
        if self.scale:
            d['scale'] = self.scale
        if self.pixelOffset:
            d['pixelOffset'] = self.pixelOffset
        return d

    def load(self, data):
        self.show = data.get('show', None)
        self.text = data.get('text', None)


class Grid(_CZMLBaseObject):
    """Fills the surface with a grid."""
    _color = None
    _cellAlpha = None
    _lineCount = None
    _lineThickness = None
    _lineOffset = None
    _properties = ('color', 'cellAlpha', 'lineCount', 'lineThickness', 'lineOffset',)


class Image(_CZMLBaseObject):
    """Fills the surface with an image."""
    _image = None
    _repeat = None
    _properties = ('image', 'repeat',)


class Stripe(_CZMLBaseObject):
    """Fills the surface with alternating colors."""
    _orientation = None
    _evenColor = None
    _oddColor = None
    _offset = None
    _repeat = None
    _properties = ('orientation', 'evenColor', 'oddColor', 'offset', 'repeat',)


class SolidColor(_CZMLBaseObject):
    """Fills the surface with a solid color, which may be translucent."""
    _color = None
    _properties = ('color',)


class PolylineGlow(_CZMLBaseObject):
    """Colors the line with a glowing color."""
    _color = None
    _glowPower = None
    _properties = ('color', 'glowPower',)


class PolylineOutline(_CZMLBaseObject):
    """Colors the line with a color and outline."""
    _color = None
    _outlineColor = None
    _outlineWidth = None
    _properties = ('color', 'outlineColor', 'outlineWidth',)


class Material(_CZMLBaseObject):
    """The material to use to fill the polygon."""
    _grid = None
    _image = None
    _stripe = None
    _solidColor = None
    _polylineGlow = None
    _polylineOutline = None

    _properties = ('grid', 'image', 'stripe', 'solidColor', 'polylineGlow', 'polylineOutline')

    grid = class_property(Grid, 'grid',
                          doc="""Fills the surface with a grid.
                          """)
    image = class_property(Image, 'image',
                           doc="""The image to display on the surface.
                           """)
    stripe = class_property(Stripe, 'stripe',
                            doc="""Fills the surface with alternating colors.
                            """)
    solidColor = class_property(SolidColor, 'solidColor',
                                doc="""Fills the surface with a solid color, which may be translucent.
                                """)
    polylineGlow = class_property(PolylineGlow, 'polylineGlow',
                                  doc="""Colors the line with a glowing color.
                                  """)
    polylineOutline = class_property(PolylineOutline, 'polylineOutline',
                                     doc="""Colors the line with a color and outline.
                                     """)


class Path(_DateTimeAware, _CZMLBaseObject):
    """A path, which is a polyline defined by the motion of an object over
    time. The possible vertices of the path are specified by the position
    property."""
    show = None

    _width = None
    width = class_property(Number, 'width');

    _leadTime = None
    leadTime = class_property(Number, 'leadTime');

    _trailTime = None
    trailTime = class_property(Number, 'trailTime');

    _resolution = None
    resolution = class_property(Number, 'resolution');

    _material = None
    material = class_property(Material, 'material')

    _position = None
    position = class_property(Position, 'position');

    _properties = ('show', 'width', 'leadTime', 'trailTime',
                   'resolution', 'material', 'position')


class Polyline(_DateTimeAware, _CZMLBaseObject):
    """ A polyline, which is a line in the scene composed of multiple segments.
    """
    show = None
    followSurface = None

    _width = None
    width = class_property(Number, 'width');

    _material = None
    material = class_property(Material, 'material')

    _positions = None
    positions = class_property(Positions, 'positions');

    _properties = ('show', 'followSurface', 'width', 'material', 'positions')


class Polygon(_DateTimeAware, _CZMLBaseObject):
    """A polygon, which is a closed figure on the surface of the Earth.
    """
    show = None
    fill = None
    outline = None
    perPositionHeight = None
    closeTop = None
    closeBottom = None

    _height = None
    height = class_property(Number, 'height')

    _stRotation = None
    stRotation = class_property(Number, 'stRotation')

    _granularity = None
    granularity = class_property(Number, 'granularity')

    _extrudedHeight = None
    extrudedHeight = class_property(Number, 'extrudedHeight')

    _outlineColor = None
    outlineColor = class_property(Color, 'outlineColor')

    _outlineWidth = None
    outlineWidth = class_property(Number, 'outlineWidth')

    _material = None
    material = class_property(Material, 'material')

    _positions = None
    positions = class_property(Positions, 'positions');

    _properties = ('show', 'fill', 'height', 'outline', 'stRotation',
                   'granularity', 'extrudedHeight', 'perPositionHeight',
                   'outlineColor', 'outlineWidth', 'material', 'positions',
                   'closeTop', 'closeBottom')


class Ellipse(_DateTimeAware, _CZMLBaseObject):
    """An ellipse, which is a closed curve on the surface of the Earth.
       The ellipse is positioned using the position property.
    """
    show = None
    fill = None
    outline = None

    _height = None
    height = class_property(Number, 'height')

    _rotation = None
    rotation = class_property(Number, 'rotation')

    _stRotation = None
    stRotation = class_property(Number, 'stRotation')

    _granularity = None
    granularity = class_property(Number, 'granularity')

    _semiMajorAxis = None
    semiMajorAxis = class_property(Number, 'semiMajorAxis')

    _semiMinorAxis = None
    semiMinorAxis = class_property(Number, 'semiMinorAxis')

    _extrudedHeight = None
    extrudedHeight = class_property(Number, 'extrudedHeight')

    _numberOfVerticalLines = None
    numberOfVerticalLines = class_property(Number, 'numberOfVerticalLines')

    _outlineColor = None
    outlineColor = class_property(Color, 'outlineColor')

    _outlineWidth = None
    outlineWidth = class_property(Number, 'outlineWidth')

    _material = None
    material = class_property(Material, 'material')

    _position = None
    position = class_property(Position, 'position');

    _properties = ('show', 'fill', 'outline', 'height', 'rotation', 'stRotation',
                   'granularity', 'extrudedHeight', 'semiMajorAxis', 'semiMinorAxis',
                   'numberOfVerticalLines', 'outlineColor', 'outlineWidth', 'material', 'position')


class Ellipsoid(_DateTimeAware):
    show = True
    _radii = None
    _material = None

    material = material_property('material')
    radii = class_property(Radii, 'radii')

    def data(self):
        d = super(Ellipsoid, self).data()

        for attr in ('show', 'material', 'radii'):
            a = getattr(self, attr)
            if a is not None:
                if isinstance(a, _CZMLBaseObject):
                    d[attr] = a.data()
                else:
                    d[attr] = a
        return d

    def load(self, data):
        self.material = data.get('material', None)
        self.radii = data.get('radii', None)

class Cone(_DateTimeAware, _CZMLBaseObject):
    """ A cone starts at a point or apex and extends in a circle of
    directions which all have the same angular separation from the Z-axis
    of the object to which the cone is attached. The cone may be capped
    at a radial limit, it may have an inner hole, and it may be only a
    part of a complete cone defined by clock angle limits. The apex
    point of the cone is defined by the position property and extends in
    the direction of the Z-axis as defined by the orientation property.
    """
    show = True
    innerHalfAngle = None
    outerHalfAngle = None
    radius = None

    minimumClockAngle = None
    maximumClockAngle = None

    showIntersection = None
    intersectionColor = None

    # Materials
    _capMaterial = None
    _innerMaterial = None
    _outerMaterial = None
    _silhouetteMaterial = None

    capMaterial = material_property('capMaterial')
    innerMaterial = material_property('innerMaterial')
    outerMaterial = material_property('outerMaterial')
    silhouetteMaterial = material_property('silhouetteMaterial')

    def __init__(self, epoch=None, nextTime=None, previousTime=None, **kwargs):

        _DateTimeAware.__init__(self, epoch=epoch,
                                nextTime=nextTime,
                                previousTime=previousTime)

        self._properties += ('show', 'innerHalfAngle', 'outerHalfAngle', 'radius',
                             'minimumClockAngle', 'maximumClockAngle',
                             'showIntersection', 'intersectionColor',
                             'capMaterial', 'innerMaterial', 'outerMaterial',
                             'silhouetteMaterial')
        for param in kwargs:
            if param in self._properties:
                setattr(self, param, kwargs[param])
            else:
                raise ValueError('Unknown parameter: %s', param)

    def data(self):
        d = _DateTimeAware.data(self)
        d['show'] = self.show

        for attr in self._properties:
            a = getattr(self, attr)
            if a is not None:
                if isinstance(a, _CZMLBaseObject):
                    d[attr] = a.data()
                else:
                    d[attr] = a
            # TODO: Finish entering these.
        return d

class Pyramid(_CZMLBaseObject):
    """A pyramid starts at a point or apex and extends in a specified list
    of directions from the apex. Each pair of directions forms a face of
    the pyramid. The pyramid may be capped at a radial limit.
    """
    pass


class Camera(_CZMLBaseObject):
    """A camera."""
    pass

class Description(_CZMLBaseObject):
    string = None
    reference = None
    
    def __init__(self, string=None, reference=None):
        self.string = string
        self.reference = reference
    
    def data(self):
        d = {}
        if self.string:
            d['string'] = self.string
        if self.reference:
            d['reference'] = self.reference
        return d
    
    def load(self, data):
        self.string = data.get('string', None)
        self.reference = data.get('reference', None)

class CZMLPacket(_CZMLBaseObject):
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
    _id = None

    # The availability property indicates when data for an object is available.
    # If data for an object is known to be available at the current animation
    # time, but the client does not yet have that data (presumably because
    # it will arrive in a later packet), the client will pause with a message
    # like "Buffering..." while it waits to receive the data. The property
    # can be a single string specifying a single interval, or an array
    # of strings representing intervals.
    availability = None

    # The CZML version being written. Only valid on the document object.
    _version = None

    # The clock settings for the entire data set. Only valid on the document object.
    _clock = None

    _position = None

    _billboard = None

    # The world-space positions of vertices. The vertex positions have no
    # direct visual representation, but they are used to define polygons,
    # polylines, and other objects attached to the object.
    _positions = None

    # The orientation of the object in the world. The orientation has no
    # direct visual representation, but it is used to orient models,
    # cones, and pyramids attached to the object.
    _orientation = None

    _point = None

    _label = None

    # A polyline, which is a line in the scene composed of multiple segments.
    # The vertices of the polyline are specified by the positions
    # property.
    _polyline = None

    # A path, which is a polyline defined by the motion of an object over
    # time. The possible vertices of the path are specified by the
    # position property.
    _path = None
    path = class_property(Path, 'path')

    # A polygon, which is a closed figure on the surface of the Earth.
    # The vertices of the polygon are specified by the positions
    # property.
    _polygon = None

    # A cone. A cone starts at a point or apex and extends in a circle of
    # directions which all have the same angular separation from the Z-axis
    # of the object to which the cone is attached. The cone may be capped
    # at a radial limit, it may have an inner hole, and it may be only a
    # part of a complete cone defined by clock angle limits. The apex point
    # of the cone is defined by the position property and extends in the
    # direction of the Z-axis as defined by the orientation property.
    _cone = None

    # A pyramid. A pyramid starts at a point or apex and extends in a
    # specified list of directions from the apex. Each pair of directions
    # forms a face of the pyramid. The pyramid may be capped at a radial limit.
    pyramid = None

    # A camera.
    camera = None

    # An ellipsoid
    _ellipsoid = None
    # Ensure ellipsoids are Ellipsoid objects and handle them appropriately.
    ellipsoid = class_property(Ellipsoid, 'ellipsoid')

    # ellipse
    _ellipse = None
    ellipse = class_property(Ellipse, 'ellipse')

    # try adding description
    _description = None

    _properties = ('id', 'description', 'version', 'availability', 'billboard', 'clock', 'position', 'label', 'point', 'positions', 'polyline', 'polygon', 'path', 'orientation', 'ellipse', 'ellipsoid', 'cone', 'pyramid')

    # TODO: Figure out how to set __doc__ from here.
    # position = class_property(Position, 'position')
    
    @property
    def description(self):
      if self._description is not None:
        return self._description.data()
    
    @description.setter
    def description(self, description):
        if isinstance(description, Description):
            self._description = description
        elif isinstance(description, dict):
            d = Description()
            d.load(description)
            self._description = d
        elif description is None:
            self._description = None
        else:
            raise TypeError
    
    @property
    def position(self):
        """The position of the object in the world. The position has no direct
        visual representation, but it is used to locate billboards, labels,
        and other primitives attached to the object.
        """
        if self._position is not None:
            return self._position.data()

    @position.setter
    def position(self, position):
        if isinstance(position, Position):
            self._position = position
        elif isinstance(position, dict):
            pos = Position()
            pos.load(position)
            self._position = pos
        elif position is None:
            self._position = None
        else:
            raise TypeError


    @property
    def label(self):
        """A string of text. The label is positioned in the scene by the
        position property."""
        if self._label is not None:
            return self._label.data()

    @label.setter
    def label(self, label):
        if isinstance(label, Label):
            self._label = label
        elif isinstance(label, dict):
            l = Label()
            l.load(label)
            self._label = l
        elif label is None:
            self._label = None
        else:
            raise TypeError



    @property
    def billboard(self):
        """A billboard, or viewport-aligned image. The billboard is positioned
        in the scene by the position property. A billboard is sometimes
        called a marker."""
        if self._billboard is not None:
            return self._billboard.data()

    @billboard.setter
    def billboard(self, billboard):
        if isinstance(billboard, Billboard):
            self._billboard = billboard
        elif isinstance(billboard, dict):
            bb = Billboard()
            bb.load(billboard)
            self._billboard = bb
        elif billboard is None:
            self._billboard = None
        else:
            raise TypeError

    @property
    def version(self):
        """The CZML version being written. Only valid on the document object."""
        if self._version is not None:
            return self._version

    @version.setter
    def version(self, version):
        if self.id != 'document':
            raise Exception('(2) version can only be set on the document object')
        if isinstance(version, str):
            self._version = version
        elif isinstance(version, basestring):
            self._version = version
        else:
            raise TypeError

    @property
    def clock(self):
        """The clock settings for the entire data set. Only valid on the
        document object."""
        if self._clock is not None:
            return self._clock.data()

    @clock.setter
    def clock(self, clock):
        if self.id != 'document':
            raise Exception('Clock object is only valid on the document object')
        if isinstance(clock, Clock):
            self._clock = clock
        elif isinstance(clock, dict):
            c = Clock()
            c.load(clock)
            self._clock = c
        elif clock is None:
            self._clock = None
        else:
            raise TypeError

    @property
    def orientation(self):
        """An orientation"""
        if self._orientation is not None:
            return self._orientation.data()

    @orientation.setter
    def orientation(self, orientation):
        if isinstance(orientation, Orientation):
            self._orientation = orientation
        elif isinstance(orientation, dict):
            p = Orientation()
            p.load(orientation)
            self._orientation = p
        elif orientation is None:
            self._orientation = None
        else:
            raise TypeError

    @property
    def point(self):
        """A point, or viewport-aligned circle. The point is positioned in
        the scene by the position property."""
        if self._point is not None:
            return self._point.data()

    @point.setter
    def point(self, point):
        if isinstance(point, Point):
            self._point = point
        elif isinstance(point, dict):
            p = Point()
            p.load(point)
            self._point = p
        elif point is None:
            self._point = None
        else:
            raise TypeError

    @property
    def positions(self):
        """The world-space positions of vertices.
        The vertex positions have no direct visual representation,
        but they are used to define polygons, polylines,
        and other objects attached to the object."""
        if self._positions is not None:
            return self._positions.data()

    @positions.setter
    def positions(self, vpositions):
        if isinstance(vpositions, Positions):
            self._positions = vpositions
        elif isinstance(vpositions, dict):
            p = Positions()
            p.load(vpositions)
            self._positions = p
        elif vpositions is None:
            self._positions = None
        else:
            raise TypeError


    @property
    def polyline(self):
        """A polyline, which is a line in the scene composed of multiple segments.
        The vertices of the polyline are specified by the positions
        property."""
        if self._polyline is not None:
            return self._polyline.data()

    @polyline.setter
    def polyline(self, polyline):
        if isinstance(polyline, Polyline):
            self._polyline = polyline
        elif isinstance(polyline, dict):
            p = Polyline()
            p.load(polyline)
            self._polyline = p
        elif polyline is None:
            self._polyline = None
        else:
            raise TypeError

    @property
    def polygon(self):
        """A polygon, which is a closed figure on the surface of the Earth.
        The vertices of the polygon are specified by the positions
        property."""

        if self._polygon is not None:
            return self._polygon.data()

    @polygon.setter
    def polygon(self, polygon):
        if isinstance(polygon, Polygon):
            self._polygon = polygon
        elif isinstance(polygon, dict):
            p = Polygon()
            p.load(polygon)
            self._polygon = p
        elif polygon is None:
            self._polygon = None
        else:
            raise TypeError

    @property
    def cone(self):
        """A polygon, which is a closed figure on the surface of the Earth.
        The vertices of the polygon are specified by the positions
        property."""

        if self._cone is not None:
            return self._cone.data()

    @cone.setter
    def cone(self, cone):
        if isinstance(cone, Cone):
            self._cone = cone
        elif isinstance(cone, dict):
            p = Cone()
            p.load(cone)
            self._cone = p
        elif cone is None:
            self._cone = None
        else:
            raise TypeError

    def data(self):
        d = {}
        for property_name in self._properties:
            property_value = getattr(self, property_name)
            if property_value is not None:
                d[property_name] = property_value
        return d

    def load(self, data):
        for property_name in self._properties:
            property_value = data.get(property_name, None)
            if property_value is not None:
                setattr(self, property_name, property_value)


