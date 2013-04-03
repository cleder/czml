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

def hexcolor_to_rgba(color, opacity='3c'):
    """ convert a web hexadecimal [#]RRGGBB[AA] color to an (R, G, B, A) tuple """
    color = color.strip()
    if color.startswith('#'):
        color = color[1:]
    tc = int(color, 16) # this raises a value error  if color contains illegal chars
    if len(color)==3:
        color =''.join([b*2 for b in color]) + opacity
    elif len(color)==4:
        color =''.join([b*2 for b in color])
    elif len(color)==6:
        color = color + opacity
    elif len(color)==8:
        pass
    else:
        raise ValueError("input #%s is not in #RRGGBB[AA] format" % color)
    r, g, b, a = color[0:2], color[2:4], color[4:6], color[6:8]
    r, g, b, a = [int(n, 16) for n in (r, g, b, a)]
    return (r, g, b, a)
