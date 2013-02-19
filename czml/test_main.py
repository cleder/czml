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

try:
    from czml import czml
except ImportError:
    import czml

from pygeoif import geometry

class BaseClassesTestCase( unittest.TestCase ):

    def test_DateTimeAware(self):
        dtob = czml._DateTimeAware()
        now = datetime.now()
        today = now.date()
        dtob.epoch = now
        self.assertEqual(dtob.epoch, now.isoformat())
        dtob.epoch = now.isoformat()
        self.assertEqual(dtob.epoch, now.isoformat())
        dtob.epoch = today
        self.assertEqual(dtob.epoch, today.isoformat())
        dtob.epoch = None
        self.assertEqual(dtob.epoch, None)

        dtob.nextTime = now
        self.assertEqual(dtob.nextTime, now.isoformat())
        dtob.nextTime = now.isoformat()
        self.assertEqual(dtob.nextTime, now.isoformat())
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
        dtob.previousTime = today
        self.assertEqual(dtob.previousTime, today.isoformat())
        dtob.previousTime = 1
        self.assertEqual(dtob.previousTime, 1.0)
        dtob.previousTime = '2'
        self.assertEqual(dtob.previousTime, 2.0)
        dtob.previousTime = None
        self.assertEqual(dtob.previousTime, None)

        jst = '{"nextTime": 2, "previousTime": 1, "epoch": "2013-02-18T00:00:00"}'
        dtob.loads(jst)
        self.assertEqual(dtob.previousTime, 1.0)
        self.assertEqual(dtob.nextTime, 2.0)
        self.assertEqual(dtob.data(), json.loads(jst))


    def test_Coordinates(self):
        coord = czml._Coordinates([0,1])
        self.assertEqual(len(coord.coords), 1)
        self.assertEqual(coord.coords[0].x, 0)
        self.assertEqual(coord.coords[0].y, 1)
        self.assertEqual(coord.coords[0].z, 0)
        self.assertEqual(coord.coords[0].t, None)
        coord = czml._Coordinates([0,1,2])
        self.assertEqual(len(coord.coords), 1)
        self.assertEqual(coord.coords[0].x, 0)
        self.assertEqual(coord.coords[0].y, 1)
        self.assertEqual(coord.coords[0].z, 2)
        self.assertEqual(coord.coords[0].t, None)
        now = datetime.now()
        coord = czml._Coordinates([now, 0,1,2])
        self.assertEqual(len(coord.coords), 1)
        self.assertEqual(coord.coords[0].x, 0)
        self.assertEqual(coord.coords[0].y, 1)
        self.assertEqual(coord.coords[0].z, 2)
        self.assertEqual(coord.coords[0].t, now)
        y2k = datetime(2000,1,1)
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



class CzmlClassesTestCase( unittest.TestCase ):

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



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BaseClassesTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()
