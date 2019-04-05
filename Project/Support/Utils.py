# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2018 Joel Graff <monograff76@gmail.com>                 *
# *                                                                        *
# *  This program is free software; you can redistribute it and/or modify  *
# *  it under the terms of the GNU Lesser General Public License (LGPL)    *
# *  as published by the Free Software Foundation; either version 2 of     *
# *  the License, or (at your option) any later version.                   *
# *  for detail see the LICENCE text file.                                 *
# *                                                                        *
# *  This program is distributed in the hope that it will be useful,       *
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *  GNU Library General Public License for more details.                  *
# *                                                                        *
# *  You should have received a copy of the GNU Library General Public     *
# *  License along with this program; if not, write to the Free Software   *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *  USA                                                                   *
# *                                                                        *
# **************************************************************************

'''
Useful math functions and constants
'''

__title__ = "Math.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

import math

import FreeCAD as App

from Project.Support.Const import Const

    #Regular expressions for detecting stations
    #rex_station = re.compile(r'[0-9]+\+[0-9]{2}\.[0-9]{2,}')
    #rex_near_station = re.compile(r'(?:[0-9]+\+?)?[0-9]{1,2}(?:\.[0-9]*)?')
class Constants(Const):
    '''
    Useful math constants
    '''

    TWO_PI      = math.pi * 2.0             #   2 * pi in radians
    HALF_PI     = math.pi / 2.0             #   1/2 * pi in radians
    ONE_RADIAN  = 180 / math.pi             #   one radian in degrees
    TOLERANCE   = 0.0001                    #   tolerance for differences in measurements
    UP          = App.Vector(0.0, 1.0, 0.0) #   Up vector

def to_float(value):
    '''
    Return value as a float, if possible.
    If value is a list, non-float values are returned as None
    Float 'nan' values are converted to None
    '''

    result = None

    if isinstance(value, list):
        result = []

        for _v in value:
            result.append(to_float(_v))

    else:

        try:
            result = float(value)

        except:
            pass

        if math.isnan(result):
            result = None

    return result

def to_int(value):
    '''
    Return true if string is an integer
    '''

    result = None

    if isinstance(value, list):

        result = []

        for _v in value:

            _f = to_int(_v)

            if not _f:
                return None

            result.append(_f)

        return result

    try:
        result = int(float(value))

    except:
        pass

    return result

def distance_bearing_to_coordinates(distance, bearing):
    '''
    Converts a distance and bearing (in degrees) to cartesian coordinates
    '''

    #convert the bearing to radians, ensuring it falls witin [0.0, 2 * pi)]
    _b = math.radians(bearing) % Constants.two_pi

    return App.Vector(math.sin(_b), math.cos(_b), 0.0).multiply(distance)

def coordinates_to_distance_bearing(prev_coord, next_coord):
    '''
    Given two coordinates in (x,y,z) format, calculate the distance between them
    and the bearing from prev to next
    '''

    distance = (next_coord-prev_coord).Length
    deltas = next_coord - prev_coord

    #calculate the directed bearing of the x and yh deltas
    bearing = math.atan2(deltas[0], deltas[1])

    if bearing < 0.0:
        bearing += math.pi * 2.0

    return (distance, math.degrees(bearing))

def doc_to_radius(value, is_metric=False, station_length=0):
    '''
    Converts degree of curve value to radius
    Assumes a default 100 feet for english units and 1000 meters for metric.
    Custom station lengths can be defined using the station_length parameter
    '''

    if station_length == 0:

        station_length = 100.0

        if is_metric:
            station_length = 1000.0

    return Constants.one_radian * (station_length / value)

def station_to_distance(station, equations):
    '''
    Given a station and equations along an alignment,
    convert the station to the distance from the start of the alignment
    '''

    _s = station

    try:
        _s = float(station)

    except:
        print('Station not floating point value')
        return 0

    start_sta = -1
    end_sta = -1
    distance = 0.0

    for eqn in equations:

        #the equation back is the end of the current range
        end_sta = eqn[0]

        #less than zero - initial station equation
        if not (start_sta < 0.0 or end_sta < 0.0):

            #if the station falls between two values,
            #calculate the final segment length and break out
            if _s <= end_sta and _s >= start_sta:
                distance += _s - start_sta
                break

            #accumulate distance across this station range
            distance += end_sta - start_sta

        #forward is the starting station for the next range
        start = eqn[1]

    return distance

def scrub_stationing(station):
    '''
    Accepts a text string representing a station and
    scrubs it, returning a valid floating point value, -1 if invalid
    '''

    scrub = station.replace('+', '')

    try:
        float(scrub)

    except:
        return -1

    return float(scrub)
