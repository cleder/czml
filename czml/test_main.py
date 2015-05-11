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

import unittest, os
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

    def testDateTimeAware(self):

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
        with self.assertRaises(ValueError):
            dtob.epoch = 1
        self.assertRaises(ValueError, setattr, dtob, 'epoch', 1)
        # Cannot assign a float to epoch (no offsets allowed)
        with self.assertRaises(ValueError):
            dtob.epoch = 2.0
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

    def testCoordinates(self):

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

    def testDocument(self):

        # Create a new document packet
        doc_packet1 = czml.CZMLPacket(id='document', version='1.0')
        self.assertEqual(doc_packet1.data(), {'id': 'document', 'version': '1.0'})

        # Modify an existing document packet
        doc_packet1.version = '1.1'
        self.assertEqual(doc_packet1.data(), {'id': 'document', 'version': '1.1'})

        # Create a new document packet from an existing document packet
        doc_packet2 = czml.CZMLPacket()
        doc_packet2.loads(doc_packet1.dumps())
        self.assertEqual(doc_packet1.data(), doc_packet2.data())

        # Test that version can only be added to the document packet (id='document')
        with self.assertRaises(Exception):
            doc_packet1 = czml.CZMLPacket(id='foo', version='1.0')
        doc_packet1 = czml.CZMLPacket(id='foo')
        self.assertRaises(Exception, setattr, doc_packet1, 'version', '1.0')

        # Test the writing of CZML using the write() method and the reading of that CZML using the loads() method
        doc = czml.CZML()
        doc.packets.append(doc_packet2)
        label_packet = czml.CZMLPacket(id='label')
        label = czml.Label()
        label.text = 'test label'
        label.show = True
        label_packet.label = label
        doc.packets.append(label_packet)
        test_filename = 'test.czml'
        doc.write(test_filename)
        with open(test_filename, 'r') as test_file:
            doc2 = czml.CZML()
            doc2.loads(test_file.read())
            self.assertEqual(doc.dumps(), doc2.dumps())
        os.remove(test_filename)

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

        # Create a new point
        point = czml.Point()
        point.color = {'rgba': [0, 255, 127, 55]}
        self.assertEqual(point.data(), {'color':
                {'rgba': [0, 255, 127, 55]},
                'show': False})

        point.outlineColor = {'rgbaf': [0.0, 0.255, 0.127, 0.55]}
        self.assertEqual(point.data(), {'color': {'rgba': [0, 255, 127, 55]},
                                        'outlineColor': {'rgbaf': [0.0, 0.255, 0.127, 0.55]},
                                        'show': False})

        # Modify an existing point
        point.pixelSize = 10
        point.outlineWidth = 2
        point.show = True
        self.assertEqual(point.data(), {'color': {'rgba': [0, 255, 127, 55]},
                                        'pixelSize': 10,
                                        'outlineColor': {'rgbaf': [0.0, 0.255, 0.127, 0.55]},
                                        'outlineWidth': 2,
                                        'show': True})

        # Create a new point from an existing point
        p2 = czml.Point()
        p2.loads(point.dumps())
        self.assertEqual(point.data(), p2.data())

        # Add a point to a CZML packet
        packet = czml.CZMLPacket(id='abc')
        packet.point = p2
        self.assertEqual(packet.data(), {'id': 'abc',
                                         'point': {'color': {'rgba': [0, 255, 127, 55]},
                                                   'pixelSize': 10,
                                                   'outlineColor': {'rgbaf': [0.0, 0.255, 0.127, 0.55]},
                                                   'outlineWidth': 2,
                                                   'show': True},
                                         })

    def testLabel(self):

        # Create a new label
        l = czml.Label()
        l.text = 'test label'
        l.show = False
        self.assertEqual(l.data(), {'text': 'test label', 'show': False})

        # Modify an existing label
        l.show = True
        self.assertEqual(l.data(), {'text': 'test label', 'show': True})

        # Create a new label from an existing label
        l2 = czml.Label()
        l2.loads(l.dumps())
        self.assertEqual(l.data(), l2.data())

        # Add a label toa CZML packet
        packet = czml.CZMLPacket(id='abc')
        packet.label = l2
        self.assertEqual(packet.data(), {'id': 'abc',
                                         'label': {'text': 'test label', 'show': True},
                                         })

    def testBillboard(self):

        # Create a new billboard
        bb = czml.Billboard(show=True, scale=0.7)
        bb.image = 'http://localhost/img.png'
        bb.color = {'rgba': [0, 255, 127, 55]}
        self.assertEqual(bb.data(), {'image': 'http://localhost/img.png',
                                     'scale': 0.7,
                                     'color': {'rgba': [0, 255, 127, 55]},
                                     'show': True})

        # Modify an existing billboard
        bb.image = 'http://localhost/img2.png'
        bb.scale = 1.3
        bb.color = {'rgba': [127, 0, 255, 160]}
        bb.show = False
        self.assertEqual(bb.data(), {'image': 'http://localhost/img2.png',
                                     'scale': 1.3,
                                     'color': {'rgba': [127, 0, 255, 160]},
                                     'show': False})

        # Create a new billboard from an existing billboard
        bb2 = czml.Billboard()
        bb2.loads(bb.dumps())
        self.assertEqual(bb.data(), bb2.data())

        # Add a billboard to a CZML packet
        packet = czml.CZMLPacket(id='abc')
        packet.billboard = bb2
        self.assertEqual(packet.data(), {'id': 'abc',
                                         'billboard': {'image': 'http://localhost/img2.png',
                                                       'scale': 1.3,
                                                       'color': {'rgba': [127, 0, 255, 160]},
                                                       'show': False},
                                         })

    def testClock(self):

        # Create a new clock (inside a document packet)
        doc = czml.CZMLPacket(id='document', version='1.0')
        c = czml.Clock()
        c.currentTime = '2017-08-21T16:50:00Z'
        c.multiplier = 3
        c.range = 'UNBOUNDED'
        c.step = 'SYSTEM_CLOCK_MULTIPLIER'
        self.assertEqual(c.data(),
            {'currentTime': '2017-08-21T16:50:00Z',
             'multiplier': 3,
             'range': 'UNBOUNDED',
             'step': 'SYSTEM_CLOCK_MULTIPLIER'})
        doc.clock = c
        self.assertEqual(doc.data(),
                         {'id': 'document',
                          'version': '1.0',
                          'clock': {'currentTime': '2017-08-21T16:50:00Z',
                                    'multiplier': 3,
                                    'range': 'UNBOUNDED',
                                    'step': 'SYSTEM_CLOCK_MULTIPLIER'},
                          })

        # Test that clock can only be added to the document object (id='document')
        doc = czml.CZMLPacket(id='foo')
        c = czml.Clock()
        self.assertRaises(Exception, setattr, doc, 'clock', c)

    def testMaterial(self):

        # Create a new material
        red = czml.Color(rgba=(255, 0, 0, 64))
        mat = czml.Material()
        mat.solidColor = {'color': red}
        self.assertEqual(mat.data(), {'solidColor': {'color': {'rgba': [255, 0, 0, 64]}}})

        # Create a new material from an existing material
        mat2 = czml.Material()
        mat2.loads(mat.dumps())
        self.assertEqual(mat.data(), mat2.data())

    def testGrid(self):

        # Create a new grid
        red = czml.Color(rgba=(255, 0, 0, 64))
        g = czml.Grid()
        g.color = red
        g.cellAlpha = 0.5
        g.lineCount = 4
        g.lineThickness = 1.5
        g.lineOffset = 0.75
        self.assertEqual(g.data(), {'color': {'rgba': [255, 0, 0, 64]},
                                    'cellAlpha': 0.5,
                                    'lineCount': 4,
                                    'lineThickness': 1.5,
                                    'lineOffset': 0.75})

        # Create a new grid from an existing grid
        g2 = czml.Grid()
        g2.loads(g.dumps())
        self.assertEqual(g.data(), g2.data())

    def testImage(self):

        # Create a new image
        i = czml.Image(image='http://localhost/img.png')
        i.repeat = 3
        self.assertEqual(i.data(), {'image': 'http://localhost/img.png',
                                    'repeat': 3})

        # Create a new image from an existing image
        i2 = czml.Image()
        i2.loads(i.dumps())
        self.assertEqual(i.data(), i2.data())

    def testStripe(self):

        # Create a new stripe
        red = czml.Color(rgba=(255, 0, 0, 64))
        grn = czml.Color(rgba=(0, 255, 0, 64))
        s = czml.Stripe()
        s.orientation = 'HORIZONTAL'
        s.evenColor = red
        s.oddColor = grn
        s.offset = 1.5
        s.repeat = 3.6
        self.assertEqual(s.data(), {'orientation': 'HORIZONTAL',
                                    'evenColor': {'rgba': [255, 0, 0, 64]},
                                    'oddColor': {'rgba': [0, 255, 0, 64]},
                                    'offset': 1.5,
                                    'repeat': 3.6})

        # Create a new stripe from an existing stripe
        s2 = czml.Stripe()
        s2.loads(s.dumps())
        self.assertEqual(s.data(), s2.data())

    def testSolidColor(self):

        # Create a new solidcolor
        red = czml.Color(rgba=(255, 0, 0, 64))
        sc = czml.SolidColor()
        sc.color = red
        self.assertEqual(sc.data(), {'color': {'rgba': [255, 0, 0, 64]}})

        # Create a new solidcolor from an existing solidcolor
        sc2 = czml.SolidColor()
        sc2.loads(sc.dumps())
        self.assertEqual(sc.data(), sc2.data())

    def testPolylineGlow(self):

        # Create a new polylineglow
        red = czml.Color(rgba=(255, 0, 0, 64))
        pg = czml.PolylineGlow()
        pg.color = red
        pg.glowPower = 0.25
        self.assertEqual(pg.data(), {'color': {'rgba': [255, 0, 0, 64]},
                                     'glowPower': 0.25})

        # Create a new polylineglow from an existing polylineglow
        pg2 = czml.PolylineGlow()
        pg2.loads(pg.dumps())
        self.assertEqual(pg.data(), pg2.data())

    def testPolylineOutline(self):

        # Create a new polylineoutline
        red = czml.Color(rgba=(255, 0, 0, 64))
        grn = czml.Color(rgba=(0, 255, 0, 64))
        po = czml.PolylineOutline()
        po.color = red
        po.outlineColor = grn
        po.outlineWidth = 4
        self.assertEqual(po.data(), {'color': {'rgba': [255, 0, 0, 64]},
                                     'outlineColor': {'rgba': [0, 255, 0, 64]},
                                     'outlineWidth': 4})

        # Create a new polylineoutline from an existing polylineoutline
        po2 = czml.PolylineOutline()
        po2.loads(po.dumps())
        self.assertEqual(po.data(), po2.data())

    def testPositions(self):

        # Create a new positions
        v = czml.Positions()
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

        # Modify an existing positions
        v.cartesian = None
        v.cartographicDegrees = None
        v.cartographicRadians = [0.0, 0.0, .0, 1.0, 1.0, 1.0]
        self.assertEqual(v.data(), {'cartographicRadians':
            [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]})

        # Create a new positions from an existing positions
        v2 = czml.Positions()
        v2.loads(v.dumps())
        self.assertEqual(v.data(), v2.data())

    def testPath(self):

        # Create a new path
        sc = czml.SolidColor(color={'rgba': [0, 255, 127, 55]})
        m1 = czml.Material(solidColor=sc)
        c1 = [0, -62, 141, 0,
              2, -51, 143, 0,
              4, -40, 145, 0]
        v1 = czml.Position(cartographicDegrees=c1)
        p1 = czml.Path(show=True, width=5, leadTime=2, trailTime=6,
                       resolution=3, material=m1, position=v1)
        self.assertEqual(p1.data(), {'show': True, 'width': 5, 'leadTime': 2,
                                     'trailTime': 6, 'resolution': 3,
                                     'material':
                                         {'solidColor':
                                              {'color': {'rgba': [0, 255, 127, 55]}},
                                          },
                                     'position':
                                         {'cartographicDegrees': [0, -62, 141, 0,
                                                                  2, -51, 143, 0,
                                                                  4, -40, 145, 0]},

                                     })

        # Create a new path from an existing path
        p2 = czml.Path()
        p2.loads(p1.dumps())
        self.assertEqual(p2.data(), p1.data())

        # Modify an existing path
        po = czml.PolylineOutline(color={'rgba': [0, 255, 127, 55]},
                                  outlineColor={'rgba': [0, 55, 127, 255]},
                                  outlineWidth=4)
        m2 = czml.Material(polylineOutline=po)
        c2 = [0, 1000, 7500, 90,
              4, 2000, 6500, 50,
              8, 3000, 5500, 20]
        v2 = czml.Position(cartesian=c2)
        p2.show = False
        p2.material = m2
        p2.position = v2
        self.assertEqual(p2.data(), {'show': False, 'width': 5, 'leadTime': 2,
                                     'trailTime': 6, 'resolution': 3,
                                     'material':
                                         {'polylineOutline':
                                              {'color': {'rgba': [0, 255, 127, 55]},
                                               'outlineColor': {'rgba': [0, 55, 127, 255]},
                                               'outlineWidth': 4},
                                          },
                                     'position':
                                         {'cartesian': [0, 1000, 7500, 90,
                                                        4, 2000, 6500, 50,
                                                        8, 3000, 5500, 20]},
                                     })

        # Add a path to a CZML packet
        packet = czml.CZMLPacket(id='abc')
        packet.path = p2
        self.assertEqual(packet.data(), {'id': 'abc',
                                         'path': {'show': False, 'width': 5, 'leadTime': 2,
                                                  'trailTime': 6, 'resolution': 3,
                                                  'material':
                                                      {'polylineOutline':
                                                           {'color': {'rgba': [0, 255, 127, 55]},
                                                            'outlineColor': {'rgba': [0, 55, 127, 255]},
                                                            'outlineWidth': 4},
                                                       },
                                                  'position':
                                                      {'cartesian': [0, 1000, 7500, 90,
                                                                     4, 2000, 6500, 50,
                                                                     8, 3000, 5500, 20]},
                                                  },
                                         })


    def testPolyline(self):

        # Create a new polyline
        sc = czml.SolidColor(color={'rgba': [0, 255, 127, 55]})
        m1 = czml.Material(solidColor=sc)
        c1 = geometry.LineString([(-162, 41, 0), (-151, 43, 0), (-140, 45, 0)])
        v1 = czml.Positions(cartographicDegrees=c1)
        p1 = czml.Polyline(show=True, width=5, followSurface=False, material=m1, positions=v1)
        self.assertEqual(p1.data(), {'show': True, 'width': 5, 'followSurface': False,
                                     'material':
                                         {'solidColor':
                                              {'color': {'rgba': [0, 255, 127, 55]}},
                                          },
                                     'positions':
                                         {'cartographicDegrees': [-162, 41, 0,
                                                                  -151, 43, 0,
                                                                  -140, 45, 0]},

                                     })

        # Create a new polyline
        pg = czml.PolylineGlow(color={'rgba': [0, 255, 127, 55]}, glowPower=0.25)
        m2 = czml.Material(polylineGlow=pg)
        c2 = geometry.LineString([(1.6, 5.3, 10), (2.4, 4.2, 20), (3.8, 3.1, 30)])
        v2 = czml.Positions(cartographicRadians=c2)
        p2 = czml.Polyline(show=False, width=7, followSurface=True, material=m2, positions=v2)
        self.assertEqual(p2.data(), {'show': False, 'width': 7, 'followSurface': True,
                                     'material':
                                         {'polylineGlow':
                                              {'color': {'rgba': [0, 255, 127, 55]},
                                               'glowPower': 0.25},
                                          },
                                     'positions':
                                         {'cartographicRadians': [1.6, 5.3, 10,
                                                                  2.4, 4.2, 20,
                                                                  3.8, 3.1, 30]},
                                     })

        # Create a polyline from an existing polyline
        p3 = czml.Polyline()
        p3.loads(p2.dumps())
        self.assertEqual(p3.data(), p2.data())

        # Modify an existing polyline
        po = czml.PolylineOutline(color={'rgba': [0, 255, 127, 55]},
                                  outlineColor={'rgba': [0, 55, 127, 255]},
                                  outlineWidth=4)
        m3 = czml.Material(polylineOutline=po)
        c3 = geometry.LineString([(1000, 7500, 90), (2000, 6500, 50), (3000, 5500, 20)])
        v3 = czml.Positions(cartesian=c3)
        p3.material = m3
        p3.positions = v3
        self.assertEqual(p3.data(), {'show': False, 'width': 7, 'followSurface': True,
                                     'material':
                                         {'polylineOutline':
                                              {'color': {'rgba': [0, 255, 127, 55]},
                                               'outlineColor': {'rgba': [0, 55, 127, 255]},
                                               'outlineWidth': 4},
                                          },
                                     'positions':
                                         {'cartesian': [1000, 7500, 90,
                                                        2000, 6500, 50,
                                                        3000, 5500, 20]},
                                     })

        # Add a polyline to a CZML packet
        packet = czml.CZMLPacket(id='abc')
        packet.polyline = p3
        self.assertEqual(packet.data(), {'id': 'abc',
                                         'polyline': {'show': False, 'width': 7, 'followSurface': True,
                                                      'material':
                                                          {'polylineOutline':
                                                               {'color': {'rgba': [0, 255, 127, 55]},
                                                                'outlineColor': {'rgba': [0, 55, 127, 255]},
                                                                'outlineWidth': 4},
                                                           },
                                                      'positions':
                                                          {'cartesian': [1000, 7500, 90,
                                                                         2000, 6500, 50,
                                                                         3000, 5500, 20]},
                                                      },
                                         })


    def testPolygon(self):

        # Create a new polygon
        img = czml.Image(image='http://localhost/img.png', repeat=2)
        mat = czml.Material(image=img)
        pts = geometry.LineString([(50, 20, 2), (60, 30, 3), (50, 30, 4), (60, 20, 5)])
        pos = czml.Positions(cartographicDegrees=pts)
        col = {'rgba': [0, 255, 127, 55]}
        pol = czml.Polygon(show=True, material=mat, positions=pos, perPositionHeight=True,
                           fill=True, outline=True, outlineColor=col)
        self.assertEqual(pol.data(), {'show': True, 'fill': True, 'outline': True,
                                      'perPositionHeight': True,
                                      'outlineColor': {'rgba': [0, 255, 127, 55]},
                                      'material':
                                          {'image':
                                              {'image': 'http://localhost/img.png',
                                               'repeat': 2},
                                          },
                                      'positions':
                                          {'cartographicDegrees': [50, 20, 2,
                                                                   60, 30, 3,
                                                                   50, 30, 4,
                                                                   60, 20, 5]},
                                      })

        # Create a new polygon from an existing polygon
        pol2 = czml.Polygon()
        pol2.loads(pol.dumps())
        self.assertEqual(pol2.data(), pol.data())

        # Modify an existing polygon
        grid = czml.Grid(color={'rgba': [0, 55, 127, 255]}, cellAlpha=0.4,
                         lineCount=5, lineThickness=2, lineOffset=0.3)
        mat2 = czml.Material(grid=grid)
        pts2 = geometry.LineString([(1.5, 1.2, 0), (1.6, 1.3, 0), (1.5, 1.3, 0), (1.6, 1.2, 0)])
        pos2 = czml.Positions(cartographicRadians=pts2)
        pol2.material = mat2
        pol2.positions = pos2
        pol2.perPositionHeight = False
        pol2.height = 7
        pol2.extrudedHeight = 30
        self.assertEqual(pol2.data(), {'show': True, 'fill': True, 'outline': True,
                                       'perPositionHeight': False,
                                       'height': 7, 'extrudedHeight': 30,
                                       'outlineColor': {'rgba': [0, 255, 127, 55]},
                                       'material':
                                           {'grid':
                                                {'color': {'rgba': [0, 55, 127, 255]},
                                                 'cellAlpha': 0.4,
                                                 'lineCount': 5,
                                                 'lineThickness': 2,
                                                 'lineOffset': 0.3},
                                            },
                                       'positions':
                                           {'cartographicRadians': [1.5, 1.2, 0,
                                                                    1.6, 1.3, 0,
                                                                    1.5, 1.3, 0,
                                                                    1.6, 1.2, 0]},
                                       })

        # Add a polygon to a CZML packet
        packet = czml.CZMLPacket(id='abc')
        packet.polygon = pol2
        self.assertEqual(packet.data(), {'id': 'abc',
                                         'polygon': {'show': True, 'fill': True, 'outline': True,
                                                     'perPositionHeight': False,
                                                     'height': 7, 'extrudedHeight': 30,
                                                     'outlineColor': {'rgba': [0, 255, 127, 55]},
                                                     'material':
                                                         {'grid':
                                                              {'color': {'rgba': [0, 55, 127, 255]},
                                                               'cellAlpha': 0.4,
                                                               'lineCount': 5,
                                                               'lineThickness': 2,
                                                               'lineOffset': 0.3},
                                                          },
                                                     'positions':
                                                         {'cartographicRadians': [1.5, 1.2, 0,
                                                                                  1.6, 1.3, 0,
                                                                                  1.5, 1.3, 0,
                                                                                  1.6, 1.2, 0]},
                                                     },
                                         })


    def testEllipse(self):

        # Create a new ellipse
        sc = czml.SolidColor(color={'rgba': [127, 127, 127, 255]})
        mat1 = czml.Material(solidColor=sc)
        pts1 = [50, 20, 2]
        pos1 = czml.Position(cartographicDegrees=pts1)
        ell1 = czml.Ellipse(show=True, fill=True, height=50, extrudedHeight=200,
                            outline=True, outlineColor={'rgba': [0, 255, 127, 55]},
                            semiMajorAxis=150, semiMinorAxis=75, numberOfVerticalLines=800,
                            rotation=1.2, material=mat1, position=pos1)

        self.assertEqual(ell1.data(), {'show': True, 'fill': True, 'outline': True,
                                       'height': 50, 'extrudedHeight': 200, 'rotation': 1.2,
                                       'semiMajorAxis': 150, 'semiMinorAxis': 75,
                                       'numberOfVerticalLines': 800,
                                       'outlineColor': {'rgba': [0, 255, 127, 55]},
                                       'material':
                                           {'solidColor':
                                                {'color': {'rgba': [127, 127, 127, 255]}},
                                            },
                                       'position':
                                           {'cartographicDegrees': [50, 20, 2]},
                                       })

        # Create a new ellipse from an existing ellipse
        ell2 = czml.Ellipse()
        ell2.loads(ell1.dumps())
        self.assertEqual(ell2.data(), ell1.data())

        # Modify an existing ellipse
        strp = czml.Stripe(evenColor={'rgba': [127, 55, 255, 255]},
                           oddColor={'rgba': [127, 255, 55, 127]},
                           offset=1.3, repeat=64, orientation='VERTICAL')
        mat2 = czml.Material(stripe=strp)
        pts2 = [0, 1.5, 1.2, 0,
                2, 1.6, 1.3, 0,
                4, 1.5, 1.3, 0,
                6, 1.6, 1.2, 0]
        pos2 = czml.Position(cartographicRadians=pts2)
        ell2.material = mat2
        ell2.position = pos2
        ell2.perPositionHeight = False
        ell2.height = 7
        ell2.extrudedHeight = 30
        ell2.semiMajorAxis = 600
        ell2.semiMinorAxis = 400
        self.assertEqual(ell2.data(), {'show': True, 'fill': True, 'outline': True,
                                       'height': 7, 'extrudedHeight': 30, 'rotation': 1.2,
                                       'semiMajorAxis': 600, 'semiMinorAxis': 400,
                                       'numberOfVerticalLines': 800,
                                       'outlineColor': {'rgba': [0, 255, 127, 55]},
                                       'material':
                                           {'stripe':
                                                {'evenColor': {'rgba': [127, 55, 255, 255]},
                                                 'oddColor': {'rgba': [127, 255, 55, 127]},
                                                 'offset': 1.3,
                                                 'repeat': 64,
                                                 'orientation': 'VERTICAL'},
                                            },
                                       'position':
                                           {'cartographicRadians': [0, 1.5, 1.2, 0,
                                                                    2, 1.6, 1.3, 0,
                                                                    4, 1.5, 1.3, 0,
                                                                    6, 1.6, 1.2, 0]},
                                       })

        # Add an ellipse to a CZML packet
        packet = czml.CZMLPacket(id='abc')
        packet.ellipse = ell2
        self.assertEqual(packet.data(), {'id': 'abc',
                                         'ellipse': {'show': True, 'fill': True, 'outline': True,
                                                     'height': 7, 'extrudedHeight': 30, 'rotation': 1.2,
                                                     'semiMajorAxis': 600, 'semiMinorAxis': 400,
                                                     'numberOfVerticalLines': 800,
                                                     'outlineColor': {'rgba': [0, 255, 127, 55]},
                                                     'material':
                                                         {'stripe':
                                                              {'evenColor': {'rgba': [127, 55, 255, 255]},
                                                               'oddColor': {'rgba': [127, 255, 55, 127]},
                                                               'offset': 1.3,
                                                               'repeat': 64,
                                                               'orientation': 'VERTICAL'},
                                                          },
                                                     'position':
                                                         {'cartographicRadians': [0, 1.5, 1.2, 0,
                                                                                  2, 1.6, 1.3, 0,
                                                                                  4, 1.5, 1.3, 0,
                                                                                  6, 1.6, 1.2, 0]},
                                                     },
                                         })


    def testEllipsoid(self):

        # Create a new ellipsoid
        ellipsoid_value = {'radii': {'cartesian': [1000.0, 2000.0, 3000.0]},
                           'material': {},
                           'show': True,
                           }
        e = czml.Ellipsoid()
        e.show = True
        e.radii = czml.Radii(cartesian=[1000, 2000, 3000])
        e.material = czml.Material()
        self.assertEqual(e.data(), ellipsoid_value)

        # Create a new ellipsoid from an existing ellipsoid
        e2 = czml.Ellipsoid(**ellipsoid_value)
        self.assertEqual(e.data(), ellipsoid_value)

        # Verify you can't create an ellipsoid with a nonsensical value for material.
        ellipsoid_value['material'] = 2
        with self.assertRaises(TypeError):
            czml.Ellipsoid(**ellipsoid_value)
        self.assertRaises(TypeError, czml.Ellipsoid, **ellipsoid_value)

        # Verify you can't create ellipsoids with nonsensical radii
        ellipsoid_value['material'] = {}
        ellipsoid_value['radii'] = 5
        with self.assertRaises(TypeError):
            czml.Ellipsoid(**ellipsoid_value)
        self.assertRaises(TypeError, czml.Ellipsoid, **ellipsoid_value)

        # Add an ellipsoid to a CZML packet
        packet = czml.CZMLPacket(id='abc')
        packet.ellipsoid = e
        self.assertEqual(packet.data(), {'id': 'abc',
                                         'ellipsoid': {'radii': {'cartesian': [1000.0, 2000.0, 3000.0]},
                                                       'material': {},
                                                       'show': True,
                                                       },
                                         })


    def testCone(self):

        # Create a new cone
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
        self.assertEqual(c.data(), {'outerHalfAngle': 1,
                                    'innerHalfAngle': 2.0,
                                    'outerMaterial': {'solidColor': {'color': {'rgba': [0, 255, 127, 55]}}},
                                    'show': True,
                                    'showIntersection': True,
                                    'capMaterial': {'solidColor': {'color': {'rgba': [0, 255, 127, 55]}}},
                                    'innerMaterial': {'solidColor': {'color': {'rgba': [0, 255, 127, 55]}}}
                                    })

        # Create a new cone from an existing cone
        c2 = czml.Cone()
        c2.loads(c.dumps())
        self.assertEqual(c2.data(), c.data())

        # Verify passing in an unknown value raises a ValueError
        with self.assertRaises(ValueError):
            c3 = czml.Cone(bad_data=None)

        # Add a cone to a CZML packet
        packet = czml.CZMLPacket(id='abc')
        packet.cone = c2
        self.assertEqual(packet.data(), {'id': 'abc',
                                         'cone': {'outerHalfAngle': 1,
                                                  'innerHalfAngle': 2.0,
                                                  'outerMaterial': {'solidColor': {'color': {'rgba': [0, 255, 127, 55]}}},
                                                  'show': True,
                                                  'showIntersection': True,
                                                  'capMaterial': {'solidColor': {'color': {'rgba': [0, 255, 127, 55]}}},
                                                  'innerMaterial': {'solidColor': {'color': {'rgba': [0, 255, 127, 55]}}}
                                                  },
                                         })

    def testDescription(self):

        # Create a new description
        d = czml.Description(string='<h1>Hello World</h1>',
                             reference='the reference'
                            )
        self.assertEqual(d.data(), {'string': '<h1>Hello World</h1>',
                                    'reference': 'the reference'
                                   })

        # Create a new description from an existing description
        d2 = czml.Description()
        d2.loads(d.dumps())
        self.assertEqual(d2.data(), d.data())

        # Change an existing description
        d.string = '<h1>Hello World Again</h1>'
        print(d)

        self.assertEqual(d.data(), {'string': '<h1>Hello World Again</h1>',
                                    'reference': 'the reference'
                                   })

        # Verfy passing unkown value
        with self.assertRaises(Exception):
            d3 = czml.Description(bad_data=None)

        # Add description to CZML packet
        packet = czml.CZMLPacket(id='the_id')
        packet.description = d2
        self.assertEqual(packet.data(), {'id': 'the_id',
                                         'description': {'string': '<h1>Hello World</h1>',
                                                          'reference': 'the reference'
                                                          }
                                         })

        # Add a description as a dict
        packet.description = {'string': 'As a dict'}
        self.assertEqual(packet.data(), {'id': 'the_id',
                                         'description': {'string': 'As a dict'
                                                         }
                                         })


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BaseClassesTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()
