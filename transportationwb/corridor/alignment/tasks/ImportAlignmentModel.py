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
QAbstractTableModel class for Task QTableView
'''

import re
import operator

from PySide import QtCore

class ImportAlignmentModel(QtCore.QAbstractTableModel):

    rex_station = re.compile(r'[0-9]+\+[0-9]{2}\.[0-9]{2,}')
    rex_near_station = re.compile(r'(?:[0-9]+\+?)?[0-9]{1,2}(?:\.[0-9]*)?')
    default_flags = QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def __init__(self, nam, headers, data, parent=None):

        QtCore.QAbstractTableModel.__init__(self, parent)

        self.data_model = data
        self.headers = headers
        self.model_name = nam

    def rowCount(self, parent=QtCore.QModelIndex()):
        '''
        Number of rows currently in the model
        '''

        if self.data_model:
            return len(self.data_model)

        #default
        return 0

    def columnCount(self, parent=QtCore.QModelIndex()):
        '''
        Number of columns currently in the model
        '''
        if self.data_model:
            return len(self.data_model[0])

        #default
        return 0

    def data(self, index, role):
        '''
        Return data for valid indices and display role
        '''
        if not index.isValid():
            return None

        if not role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
            return None

        if not 0 <= index.row() < len(self.data_model):
            return None

        return self.data_model[index.row()][index.column()]

    def setData(self, index, value, role):
        '''
        Update existing model data
        '''

        self.data_model[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)

        return True

        if role != QtCore.Qt.EditRole:
            return False

        if index.isValid() and 0 <= index.row() < len(self.data_model):

            raw_value = None

            #test for valid data types on a per-column basis
            if index.column() == 0:
                value = self.validate_station(value)

            else:

                try:
                    value = float(value)

                except:
                    return False

            #set the value
            self.data_model[index.row()][index.column()] = value

            self.dataChanged.emit(index, index)

            return True

        return False

    def headerData(self, col, orientation, role):
        '''
        Headers to be displated
        '''

        print('model ', self.model_name)

        if not self.headers:
            return None

        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.headers[col]

        return None

    def flags(self, index):

        flags = ImportAlignmentModel.default_flags

        if index.row() > 0:
            flags = flags & ~QtCore.Qt.ItemIsEditable

        return flags
