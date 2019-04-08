# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 20XX Joel Graff <monograff76@gmail.com>                         *
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
Exporter for Alignments in LandXML files
'''

import datetime
import re
import math

from shutil import copyfile

from xml.etree import ElementTree as etree
from xml.dom import minidom

import FreeCAD as App

from Project.Support import Units
from Project.XML import LandXml
from Project.XML.KeyMaps import KeyMaps as maps

class AlignmentExporter(object):
    '''
    LandXML exporting class for alignments
    '''

    def __init__(self):

        self.errors = []

    def write_meta_data(self, data, node):
        '''
        Write the project and application data to the file
        '''

        self._write_tree_data(data, LandXml.get_child(node, 'Project'), maps.XML_ATTRIBS['Project'])

        node = LandXml.get_child(node, 'Application')

        node.set('version', ''.join(App.Version()[0:3]))
        node.set('timeStamp', datetime.datetime.utcnow().isoformat())

    def _write_tree_data(self, data, node, keys):
        '''
        Write data to the tree using the passed parameters
        '''

        _key_list = keys[0] + keys[1]

        for _v in _key_list:

            value = data.get(_v[0])

            #assign default if no value in the dictionary
            if value is None:
                value = _v[1]

            if _k in maps.XML_TAGS['angle']:
                value = math.degrees(value)

            elif _k in maps.XML_TAGS['length']:
                value /= Units.scale_factor()

            elif _k == 'rot':

                if value < 0.0:
                    value = 'ccw'

                elif value > 0.0:
                    value = 'cw'

                else:
                    value = ''

            node.set(_k, str(value))

    def write_station_data(self, data, parent):
        '''
        Write station equation information for alignment
        '''

        for sta_eq in data:
            self._write_tree_data(sta_eq, parent, maps.XML_ATTRIBS['StaEquation'])

    def _write_coordinates(self, data, parent):
        '''
        Write coordinate children to parent geometry
        '''

        _sf = 1.0 / Units.scale_factor()

        for _key in maps.XML_TAGS['coordinate']:

            if not _key in data:
                continue

            #scale the coordinates to the document units
            _vec = App.Vector(data[_key])
            _vec.multiply(_sf)

            _child = LandXml.add_child(parent, _key)

            _vec_string = LandXml.get_vector_string(_vec)

            LandXml.set_text(_child, _vec_string)

    def _write_alignment_data(self, data, parent):
        '''
        Write individual alignment to XML
        '''
        _align_node = LandXml.add_child(parent, 'Alignment')

        #write the alignment attributes
        self._write_tree_data(data['meta'], _align_node, maps.XML_ATTRIBS['Alignment'])

        _coord_geo_node = LandXml.add_child(_align_node, 'CoordGeom')

        #write the geo coordinate attributes
        self._write_tree_data(data['meta'], _coord_geo_node, maps.XML_ATTRIBS['CoordGeom'])

        #write the station equation data
        self.write_station_data(data['station'], _align_node)

        #write the alignment geometry data
        for _geo in data['geometry']:

            _node = None

            if _geo['Type'] == 'line':

                _node = LandXml.add_child(_coord_geo_node, 'Line')
                self._write_tree_data(_geo, _node, maps.XML_ATTRIBS['Line'])

            elif _geo['Type'] == 'arc':

                _node = LandXml.add_child(_coord_geo_node, 'Curve')
                self._write_tree_data(_geo, _node, maps.XML_ATTRIBS['Curve'])

            if _node is not None:
                self._write_coordinates(_geo, _node)

    def write(self, data, source_path, target_path):
        '''
        Write the alignment data to a land xml file in the target location
        '''

        root = etree.parse(source_path).getroot()

        for _align in data:
            self._write_alignment_data(_align, LandXml.add_child(root, 'Alignments'))

        LandXml.write_to_file(root, target_path)
