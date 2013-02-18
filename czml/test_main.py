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






def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BaseClassesTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()
