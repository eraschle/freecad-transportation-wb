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
Manages Horizontal curve data
'''

__title__ = "HorizontalCurve.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

import FreeCAD as App
import Draft
import Part
from transportationwb import ScriptedObjectSupport as Sos

if App.Gui:
    import FreeCADGui as Gui

def createHorizontalCurve(data, units):
    '''
    Creates a Horizontal curve alignment object

    data - dictionary containing horizontal curve geometry
    meta - dictionary containing hc metadata
    '''

    obj = App.ActiveDocument.addObject("App::FeaturePython", 'Sta ' + data['PC_station'])

    #obj.Label = translate("Transportation", OBJECT_TYPE)
    hc = _HorizontalCurve(obj)

    print("Processing curve...")
    print(data)
    radius = float(data.get('radius', 0.0))

    obj.PC_Station = data['PC_station'] + "'"
    obj.Delta = data['central_angle']
    obj.Bearing = data['bearing']
    obj.Quadrant = data['quadrant']
    obj.Direction = data['direction']
    obj.Radius = str(radius) + "'"

    if obj.Bearing < 0.0:
        obj.Bearing = 0.0

#    obj.A = abs(obj.Grade_In - obj.Grade_Out)
#    obj.K = lngth / obj.A

#    obj.PI_Station = float(data['pi'])
#    obj.PI_Elevation = float(data['elevation']) * conv

    _ViewProviderHorizontalCurve(obj.ViewObject)

    return hc

class _HorizontalCurve():

    def __init__(self, obj):
        """
        Default Constructor
        """

        obj.Proxy = self
        self.Type = 'HorizontalCurve'
        self.Object = obj

        Sos._add_property('Angle', 'General.Bearing', 'Angle of PC tangent at start of curve', 0.00)
        Sos._add_property('String','General.Quadrant', 'Bearing quadrant of the PC tangent', '')
        Sos._add_property('Length', 'General.PC_Station', 'Station of the Horizontal Point of Curvature', 0.00, True)
        Sos._add_property('Length', 'General.PI_Station', 'Station of the Horizontal Point of Intersection', 0.00)
        Sos._add_property('Length', 'General.PT_Station', 'Station of the Horizontal Point of Tangency', 0.00, True)
        Sos._add_property('Angle', 'General.Delta', 'Central angle of the curve', 0.00)
        Sos._add_property('String', 'General.Direction', 'Curve direction', '')
        Sos._add_property('Length', 'General.Radius', 'Curve radius', 0.00)        
        Sos._add_property('Length', 'General.Length', 'Curve length', 0.00)
        Sos._add_property('Float', 'General.E', 'External distance', 0.00, True)
        Sos._add_property('Float', 'General.T', 'Tangent length', 0.00, True)
        Sos._add_property('Float', 'General.D', 'Degree of Curvature', True, True)

        self.doRecalc = False

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def _recalc_curve(self):


        pi = self.Object.PI_Station.Value
        elev = self.Object.PI_Elevation.Value
        g1 = self.Object.Grade_In
        g2 = self.Object.Grade_Out
        lngth = self.Object.Length.Value

        half_length = lngth / 2.0

        self.Object.PC_Station = pi - half_length
        self.Object.PT_Station = pi + half_length

        self.Object.PC_Elevation = elev - g1 * half_length
        self.Object.PT_Elevation = elev + g2 * half_length

        self.Object.A = abs(g1 - g2)
        self.Object.K = lngth / self.Object.A

    def execute(self, fpy):

        self._recalc_curve()

class _ViewProviderHorizontalCurve:

    def __init__(self, obj):
        """
        Initialize the view provider
        """
        obj.Proxy = self

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def attach(self, obj):
        """
        View provider scene graph initialization
        """
        self.Object = obj.Object

    def updateData(self, fp, prop):
        """
        Property update handler
        """
        pass

    def getDisplayMode(self, obj):
        """
        Valid display modes
        """
        return ["Wireframe"]

    def getDefaultDisplayMode(self):
        """
        Return default display mode
        """
        return "Wireframe"

    def setDisplayMode(self, mode):
        """
        Set mode - wireframe only
        """
        return "Wireframe"

    def onChanged(self, vp, prop):
        """
        Handle individual property changes
        """
        pass

    def getIcon(self):
        return ""