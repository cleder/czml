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

import unittest
from datetime import datetime, date
import json
from pytz import timezone, utc
eastern = timezone('US/Eastern')

try:
    from czml import czml
except ImportError:
    import czml

try:
    from czml import utils
except ImportError:
    import utils

from pygeoif import geometry


class BaseClassesTestCase(unittest.TestCase):

    def test_DateTimeAware(self):
        dtob = czml._DateTimeAware()
        now = datetime.now()
        est_now = eastern.localize(now)
        utcnow = datetime.utcnow()
        today = now.date()
        dtob.epoch = now
        self.assertEqual(dtob.epoch, now.isoformat())
        dtob.epoch = now.isoformat()
        self.assertEqual(dtob.epoch, now.isoformat())
        dtob.epoch = est_now.isoformat()
        self.assertEqual(dtob.epoch, est_now.isoformat())
        dtob.epoch = today
        self.assertEqual(dtob.epoch, today.isoformat())
        dtob.epoch = utcnow
        self.assertEqual(dtob.epoch, utcnow.isoformat())
        dtob.epoch = None
        self.assertEqual(dtob.epoch, None)
        # Cannot assign an integer to epoch (no offsets allowed)
        #with self.assertRaises(ValueError):
        #    dtob.epoch = 1
        self.assertRaises(ValueError, setattr, dtob, 'epoch', 1)
        # Cannot assign a float to epoch (no offsets allowed)
        #with self.assertRaises(ValueError):
        #    dtob.epoch = 2.0
        self.assertRaises(ValueError, setattr, dtob, 'epoch', 2.0)
        dtob.nextTime = now
        self.assertEqual(dtob.nextTime, now.isoformat())
        dtob.nextTime = now.isoformat()
        self.assertEqual(dtob.nextTime, now.isoformat())
        dtob.nextTime = utcnow
        self.assertEqual(dtob.nextTime, utcnow.isoformat())
        dtob.nextTime = today
        self.assertEqual(dtob.nextTime, today.isoformat())
        dtob.nextTime = 1
        self.assertEqual(dtob.nextTime, 1.0)
        dtob.nextTime = '2'
        self.assertEqual(dtob.nextTime, 2.0)
        dtob.nextTime = None
        self.assertEqual(dtob.nextTime, None)

        dtob.previousTime = now
        self.assertEqual(dtob.previousTime, now.isoformat())
        dtob.previousTime = now.isoformat()
        self.assertEqual(dtob.previousTime, now.isoformat())
        dtob.previousTime = utcnow
        self.assertEqual(dtob.previousTime, utcnow.isoformat())
        dtob.previousTime = today
        self.assertEqual(dtob.previousTime, today.isoformat())
        dtob.previousTime = 1
        self.assertEqual(dtob.previousTime, 1.0)
        dtob.previousTime = '2'
        self.assertEqual(dtob.previousTime, 2.0)
        dtob.previousTime = None
        self.assertEqual(dtob.previousTime, None)

        jst = ('{"nextTime": 2, "previousTime": 1, '
               '"epoch": "2013-02-18T00:00:00"}')
        dtob.loads(jst)
        self.assertEqual(dtob.previousTime, 1.0)
        self.assertEqual(dtob.nextTime, 2.0)
        self.assertEqual(dtob.data(), json.loads(jst))

        # Here's a time that comes in as GMT-5.  The representation should be
        # passed through
        est_jst = ('{"nextTime": 2.0, "previousTime": 1,'
                   ' "epoch": "2013-02-18T01:00:00-05:00"}')
        dtob.loads(est_jst)
        self.assertEqual(dtob.data(), json.loads(est_jst))

    def test_Coordinates(self):
        coord = czml._Coordinates([0, 1])
        self.assertEqual(len(coord.coords), 1)
        self.assertEqual(coord.coords[0].x, 0)
        self.assertEqual(coord.coords[0].y, 1)
        self.assertEqual(coord.coords[0].z, 0)
        self.assertEqual(coord.coords[0].t, None)
        coord = czml._Coordinates([0, 1, 2])
        self.assertEqual(len(coord.coords), 1)
        self.assertEqual(coord.coords[0].x, 0)
        self.assertEqual(coord.coords[0].y, 1)
        self.assertEqual(coord.coords[0].z, 2)
        self.assertEqual(coord.coords[0].t, None)
        now = datetime.now()
        coord = czml._Coordinates([now, 0, 1, 2])
        self.assertEqual(len(coord.coords), 1)
        self.assertEqual(coord.coords[0].x, 0)
        self.assertEqual(coord.coords[0].y, 1)
        self.assertEqual(coord.coords[0].z, 2)
        self.assertEqual(coord.coords[0].t, now)
        y2k = datetime(2000, 1, 1)
        coord = czml._Coordinates([now, 0, 1, 2, y2k, 3, 4, 5])
        self.assertEqual(len(coord.coords), 2)
        self.assertEqual(coord.coords[0].x, 0)
        self.assertEqual(coord.coords[0].y, 1)
        self.assertEqual(coord.coords[0].z, 2)
        self.assertEqual(coord.coords[0].t, now)
        self.assertEqual(coord.coords[1].x, 3)
        self.assertEqual(coord.coords[1].y, 4)
        self.assertEqual(coord.coords[1].z, 5)
        self.assertEqual(coord.coords[1].t, y2k)
        coord = czml._Coordinates([now, 0, 1, 2, 6, 3, 4, 5])
        self.assertEqual(coord.coords[1].t, 6)
        coord = czml._Coordinates([now.isoformat(), 0, 1, 2, '6', 3, 4, 5])
        self.assertEqual(coord.coords[1].t, 6)
        self.assertEqual(coord.coords[0].t, now)
        p = geometry.Point(0, 1)
        coord = czml._Coordinates(p)
        self.assertEqual(coord.coords[0].x, 0)
        self.assertEqual(coord.coords[0].y, 1)
        coord = czml._Coordinates([now, p])
        self.assertEqual(coord.coords[0].x, 0)
        self.assertEqual(coord.coords[0].y, 1)
        self.assertEqual(coord.coords[0].t, now)
        p1 = geometry.Point(0, 1, 2)
        coord = czml._Coordinates([now, p, y2k, p1])
        self.assertEqual(coord.coords[0].x, 0)
        self.assertEqual(coord.coords[0].y, 1)
        self.assertEqual(coord.coords[0].z, 0)
        self.assertEqual(coord.coords[0].t, now)
        self.assertEqual(coord.coords[1].x, 0)
        self.assertEqual(coord.coords[1].y, 1)
        self.assertEqual(coord.coords[1].z, 2)
        self.assertEqual(coord.coords[1].t, y2k)

        self.assertEqual(coord.data(), [now.isoformat(), 0, 1, 0,
                                        y2k.isoformat(), 0, 1, 2])


    def testScale(self):
        pass

    def testColor(self):
        col = czml.Color()
        col.rgba = [0, 255, 127]
        self.assertEqual(col.rgba, [0, 255, 127, 1])
        col.rgba = [0, 255, 127, 55]
        self.assertEqual(col.rgba, [0, 255, 127, 55])
        now = datetime.now()
        col.rgba = [now, 0, 255, 127, 55]
        self.assertEqual(col.rgba, [now.isoformat(), 0, 255, 127, 55])
        y2k = datetime(2000, 1, 1)
        col.rgba = [now, 0, 255, 127, 55, y2k.isoformat(), 5, 6, 7, 8]
        self.assertEqual(col.rgba, [now.isoformat(), 0, 255, 127, 55,
                                    y2k.isoformat(), 5, 6, 7, 8])
        col.rgba = [1, 0, 255, 127, 55, 2, 5, 6, 7, 8]
        self.assertEqual(col.rgba, [1, 0, 255, 127, 55,
                                    2, 5, 6, 7, 8])
        col.rgbaf = [now, 0, 0.255, 0.127, 0.55, y2k.isoformat(), 0.5, 0.6, 0.7, 0.8]
        self.assertEqual(col.rgbaf, [now.isoformat(), 0.0, 0.255, 0.127, 0.55,
                                    y2k.isoformat(), 0.5, 0.6, 0.7, 0.8])
        col2 = czml.Color()
        col2.loads(col.dumps())
        self.assertEqual(col.data(), col2.data())

    def test_hexcolor_to_rgba(self):
        col = '0000'
        ashex = utils.hexcolor_to_rgba
        self.assertEqual(ashex(col), (0, 0, 0, 0))
        col = '0101'
        self.assertEqual(ashex(col), (0, 17, 0, 17))
        col = 'f0f0'
        self.assertEqual(ashex(col), (255, 0, 255, 0))
        col = 'AABBCCDD'
        self.assertEqual(ashex(col), (170, 187, 204, 221))
        col = '3c3c3c'
        self.assertEqual(ashex(col), (60, 60, 60, 60))
        col = 'abc'
        self.assertEqual(ashex(col), (170, 187, 204, 60))
        col = 'ffFF'
        self.assertEqual(ashex(col), (255, 255, 255, 255))
        col = 'ab'
        self.assertRaises(ValueError, ashex, col)
        col = 'rgba'
        self.assertRaises(ValueError, ashex, col)
        col = 'abcde'
        self.assertRaises(ValueError, ashex, col)
        col = ''
        self.assertRaises(ValueError, ashex, col)
        col = None
        self.assertRaises(AttributeError, ashex, col)


class CzmlClassesTestCase(unittest.TestCase):

    def testPosition(self):
        pos = czml.Position()
        now = datetime.now()
        pos.epoch = now
        coords = [7.0, 0.0, 1.0, 2.0, 6.0, 3.0, 4.0, 5.0]
        pos.cartographicRadians = coords
        self.assertEqual(pos.data()['cartographicRadians'],
            coords)
        js = {'epoch': now.isoformat(), 'cartographicRadians': coords}
        self.assertEqual(pos.data(), js)
        self.assertEqual(pos.dumps(), json.dumps(js))
        pos.cartographicDegrees = coords
        self.assertEqual(pos.data()['cartographicDegrees'],
            coords)
        pos.cartesian = coords
        self.assertEqual(pos.data()['cartesian'],
            coords)
        pos2 = czml.Position()
        pos2.loads(pos.dumps())
        self.assertEqual(pos.data(), pos2.data())

    def testRadii(self):
        pos = czml.Radii()
        now = datetime.now()
        pos.epoch = now
        coords = [7.0, 0.0, 1.0, 2.0, 6.0, 3.0, 4.0, 5.0]
        pos.cartesian = coords
        self.assertEqual(pos.data()['cartesian'],
            coords)
        js = {'epoch': now.isoformat(), 'cartesian': coords}
        self.assertEqual(pos.data(), js)
        self.assertEqual(pos.dumps(), json.dumps(js))
        pos.cartographicDegrees = coords
        self.assertEqual(pos.data()['cartesian'],
            coords)
        pos2 = czml.Radii()
        pos2.loads(pos.dumps())
        self.assertEqual(pos.data(), pos2.data())

    def testPoint(self):
        point = czml.Point()
        point.color = {'rgba': [0, 255, 127, 55]}
        self.assertEqual(point.data(), {'color':
                {'rgba': [0, 255, 127, 55]},
                'show': False})
        point.outlineColor = {'rgbaf': [0.0, 0.255, 0.127, 0.55]}
        self.assertEqual(point.data(), {'color':
                    {'rgba': [0, 255, 127, 55]},
                    'outlineColor': {'rgbaf': [0.0, 0.255, 0.127, 0.55]},
                    'show': False})
        point.pixelSize = 10
        point.outlineWidth = 2
        point.show = True
        self.assertEqual(point.data(), {'color':
                        {'rgba': [0, 255, 127, 55]},
                    'pixelSize': 10,
                    'outlineColor':
                        {'rgbaf': [0.0, 0.255, 0.127, 0.55]},
                    'outlineWidth': 2,
                    'show': True})
        p2 = czml.Point()
        p2.loads(point.dumps())
        self.assertEqual(point.data(), p2.data())

    def testLabel(self):
        l = czml.Label()
        l.text = 'test label'
        l.show = False
        self.assertEqual(l.data(), {'text': 'test label', 'show': False})
        l.show = True
        self.assertEqual(l.data(), {'text': 'test label', 'show': True})
        l2 = czml.Label()
        l2.loads(l.dumps())
        self.assertEqual(l.data(), l2.data())

    def testBillboard(self):
        bb = czml.Billboard()
        bb.image = 'http://localhost/img.png'
        bb.scale = 0.7
        bb.show = True
        bb.color = {'rgba': [0, 255, 127, 55]}
        self.assertEqual(bb.data(),
            {'image': 'http://localhost/img.png', 'scale': 0.7,
            'color': {'rgba': [0, 255, 127, 55]},
            'show': True})
        bb2 = czml.Billboard()
        bb2.loads(bb.dumps())
        self.assertEqual(bb.data(), bb2.data())

    def testMaterial(self):
        red = czml.Color(rgba=(255, 0, 0, 64))
        mat = czml.Material(solidColor={'color': red})
        mat.solidColor = {'color': red}
        mat_dict = {'solidColor': {'color': {'rgba': [255, 0, 0, 64]}}}
        self.assertEqual(mat.data(), mat_dict)

        mat2 = czml.Material(**mat_dict)
        self.assertEqual(mat.data(), mat2.data())

    def testVertexPositions(self):
        v = czml.VertexPositions()
        l = geometry.LineString([(0, 0), (1, 1)])
        r = geometry.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])
        ext = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        int_1 = [(0.5, 0.25), (1.5, 0.25), (1.5, 1.25), (0.5, 1.25), (0.5, 0.25)]
        int_2 = [(0.5, 1.25), (1, 1.25), (1, 1.75), (0.5, 1.75), (0.5, 1.25)]
        p = geometry.Polygon(ext, [int_1, int_2])
        v.cartesian = l
        v.cartographicDegrees = r
        v.cartographicRadians = p
        self.assertEqual(v.data(),
            {'cartesian': [0.0, 0.0, 0, 1.0, 1.0, 0],
            'cartographicRadians':
            [0.0, 0.0, 0, 0.0, 2.0, 0, 2.0, 2.0, 0, 2.0, 0.0, 0, 0.0, 0.0, 0],
            'cartographicDegrees':
            [0.0, 0.0, 0, 1.0, 1.0, 0, 1.0, 0.0, 0, 0.0, 0.0, 0]})
        v2 = czml.VertexPositions()
        v2.loads(v.dumps())
        self.assertEqual(v.data(), v2.data())
        v.cartesian = None
        v.cartographicDegrees = None
        v.cartographicRadians = [0.0, 0.0, .0, 1.0, 1.0, 1.0]
        self.assertEqual(v.data(), {'cartographicRadians':
            [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]})

    def testPolyline(self):
        p = czml.Polyline()
        p.color = {'rgba': [0, 255, 127, 55]}
        self.assertEqual(p.data(), {'color':
                {'rgba': [0, 255, 127, 55]},
                'show': False})
        p.outlineColor = {'rgbaf': [0.0, 0.255, 0.127, 0.55]}
        self.assertEqual(p.data(), {'color':
                    {'rgba': [0, 255, 127, 55]},
                    'outlineColor': {'rgbaf': [0.0, 0.255, 0.127, 0.55]},
                    'show': False})
        p.width = 10
        p.outlineWidth = 2
        p.show = True
        self.assertEqual(p.data(), {'color':
                        {'rgba': [0, 255, 127, 55]},
                    'width': 10,
                    'outlineColor':
                        {'rgbaf': [0.0, 0.255, 0.127, 0.55]},
                    'outlineWidth': 2,
                    'show': True})
        p2 = czml.Polyline()
        p2.loads(p.dumps())
        self.assertEqual(p.data(), p2.data())

    def testPolygon(self):
        p = czml.Polygon()
        m = czml.Material()
        sc = czml.SolidColor(color={'rgba': [0, 255, 127, 55]})
        m.solidColor = sc
        p.material = m
        self.assertEqual(p.data(),
            {'material':
                {'solidColor':
                    {'color': {'rgba': [0, 255, 127, 55]}}
            }   }
            )
        p2 = czml.Polygon()
        p2.loads(p.dumps())
        self.assertEqual(p.data(), p2.data())
        p3 = czml.Polygon(color={'rgba': [0, 255, 127, 55]})
        self.assertEqual(p.data(), p3.data())

    def testEllipsoid(self):
        ellipsoid_value = {'radii': {'cartesian': [1000.0, 2000.0, 3000.0]},
                           'material': {},
                           'show': True,
                           }
        e = czml.Ellipsoid()
        e.show = True
        e.radii = czml.Radii(cartesian=[1000, 2000, 3000])
        e.material = czml.Material()
        self.assertEqual(e.data(), ellipsoid_value)
        e2 = czml.Ellipsoid(**ellipsoid_value)
        self.assertEqual(e.data(), ellipsoid_value)

        # You can't create an ellipsoid with a nonsensical value for material.
        ellipsoid_value['material'] = 2
        #with self.assertRaises(TypeError):
        #    czml.Ellipsoid(**ellipsoid_value)
        self.assertRaises(TypeError, czml.Ellipsoid, **ellipsoid_value)

        ellipsoid_value['material'] = {}
        ellipsoid_value['radii'] = 5
        # Can't create ellipsoids with nonsensical radii
        #with self.assertRaises(TypeError):
        #    czml.Ellipsoid(**ellipsoid_value)
        self.assertRaises(TypeError, czml.Ellipsoid, **ellipsoid_value)


    def testCone(self):
        sc = czml.SolidColor(color={'rgba': [0, 255, 127, 55]})
        mat = czml.Material(solidColor=sc)

        c = czml.Cone(show=True,
                      innerMaterial=mat,
                      outerMaterial=mat,
                      capMaterial=mat,
                      showIntersection=True,
                      outerHalfAngle=1,
                      innerHalfAngle=2.0,
                      )

        czml_dict = {'outerHalfAngle': 1,
                     'innerHalfAngle': 2.0,
                     'outerMaterial': {'solidColor': {'color': {'rgba': [0, 255, 127, 55]}}},
                     'show': True,
                     'showIntersection': True,
                     'capMaterial': {'solidColor': {'color': {'rgba': [0, 255, 127, 55]}}},
                     'innerMaterial': {'solidColor': {'color': {'rgba': [0, 255, 127, 55]}}}
                     }

        self.assertEqual(czml_dict, c.data())

        # Passing in an unknown value raises a ValueError
        #with self.assertRaises(ValueError):
        #    czml.Cone(bad_data=None, **czml_dict)
        self.assertRaises(ValueError, czml.Cone, bad_data=None, **czml_dict)

    def testCZMLPacket(self):
        p = czml.CZMLPacket(id='abc')
        self.assertEqual(p.dumps(), '{"id": "abc"}')
        bb = czml.Billboard()
        bb.image = 'http://localhost/img.png'
        bb.scale = 0.7
        bb.show = True
        p.billboard = bb
        self.assertEqual(p.data(),
            {'billboard': {'image': 'http://localhost/img.png',
            'scale': 0.7, 'show': True}, 'id': 'abc'})
        p2 = czml.CZMLPacket(id='abc')
        p2.loads(p.dumps())
        self.assertEqual(p.data(), p2.data())
        pos = czml.Position()
        coords = [7.0, 0.0, 1.0, 2.0, 6.0, 3.0, 4.0, 5.0]
        pos.cartesian = coords
        p.position = pos
        l = czml.Label()
        l.text = 'test label'
        l.show = False
        p.label = l
        self.assertEqual(p.data(),
            {'billboard': {'image': 'http://localhost/img.png',
            'scale': 0.7, 'show': True}, 'id': 'abc',
            'label': {'show': False, 'text': 'test label'},
            'position': {'cartesian': [7.0, 0.0, 1.0, 2.0, 6.0, 3.0, 4.0, 5.0]},
            })
        p2.loads(p.dumps())
        self.assertEqual(p.data(), p2.data())
        p3 = czml.CZMLPacket(id='cde')
        p3.point = {'color':
                    {'rgba': [0, 255, 127, 55]},
                    'show': True}
        self.assertEqual(p3.data(), {'id': 'cde',
                                    'point': {'color':
                                        {'rgba': [0, 255, 127, 55]},
                                        'show': True}})
        p32 = czml.CZMLPacket(id='abc')
        p32.loads(p3.dumps())
        self.assertEqual(p3.data(), p32.data())
        p4 = czml.CZMLPacket(id='defg')

        pl = czml.Polyline()
        pl.color = {'rgba': [0, 255, 127, 55]}
        pl.width = 10
        pl.outlineWidth = 2
        pl.show = True
        v = czml.VertexPositions()
        v.cartographicDegrees = [0.0, 0.0, .0, 1.0, 1.0, 1.0]
        p4.vertexPositions = v
        p4.polyline = pl
        self.assertEqual(p4.data(),
             {'polyline':
                {'color': {'rgba': [0, 255, 127, 55]},
                'width': 10,
                'outlineWidth': 2,
                'show': True},
            'id': 'defg',
            'vertexPositions':
                {'cartographicDegrees':
                    [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]}
            })
        p42 = czml.CZMLPacket(id='abc')
        p42.loads(p4.dumps())
        self.assertEqual(p4.data(), p42.data())
        p5 = czml.CZMLPacket(id='efgh')
        p5.vertexPositions = v
        poly = czml.Polygon(color={'rgba': [0, 255, 127, 55]})
        p5.polygon = poly
        self.assertEqual(p5.data(),
            {'polygon':
                {'material':
                    {'solidColor':
                        {'color':
                            {'rgba': [0, 255, 127, 55]}}}},
                    'id': 'efgh',
                    'vertexPositions':
                        {'cartographicDegrees':
                            [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]}})
        p52 = czml.CZMLPacket(id='abc')
        p52.loads(p5.dumps())
        self.assertEqual(p5.data(), p52.data())
        return p

    def testCZML(self):
        cz = czml.CZML()
        self.assertEqual(list(cz.data()), [])
        p = self.testCZMLPacket()
        cz.packets.append(p)
        self.assertEqual(list(cz.data()),
            [{'billboard': {'image': 'http://localhost/img.png',
            'scale': 0.7, 'show': True}, 'id': 'abc',
            'label': {'show': False, 'text': 'test label'},
            'position': {'cartesian': [7.0, 0.0, 1.0, 2.0, 6.0, 3.0, 4.0, 5.0]}}])
        cz1 = czml.CZML()
        cz1.loads(cz.dumps())
        self.assertEqual(list(cz.data()), list(cz1.data()))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BaseClassesTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()
