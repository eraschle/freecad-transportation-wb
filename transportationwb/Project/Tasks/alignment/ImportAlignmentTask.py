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
DESCRIPTION
'''

import os

from PySide import QtGui, QtCore

import FreeCAD as App
import FreeCADGui as Gui

from transportationwb.corridor.alignment import HorizontalAlignment

from transportationwb.Project.Tasks.alignment import ImportXmlSubtask
from transportationwb.Project.Tasks.alignment import ImportCsvSubtask

class ImportAlignmentTask:

    def __init__(self, update_callback):

        self.path_base = App.getUserAppDataDir() + 'Mod/freecad-transportation-wb/transportationwb/Project/Tasks/alignment/'
        self.ui = self.path_base + 'import_alignment_task_panel.ui'
        self.form = None
        self.subtask = None

    def accept(self):

        data = self.subtask.import_model()

        if self.subtask.errors:

            print('Errors encountered during import:\n')
            for _e in self.subtask.errors:
                print(_e)

        if not data:
            return None

        errors = []

        for key, value in data['Alignments'].items():

            result = HorizontalAlignment.create(value, value['meta']['ID'] + ' Horiz')

            if result.errors:
                errors += result.errors
                result.errors = []

            App.ActiveDocument.recompute()

        if errors:
            print('Errors encountered during alignment creation:\n')

            for _e in errors:
                print(_e)

        return True

    def reject(self):
        return True

    def clicked(self, index):
        pass

    def open(self):
        pass

    def needsFullSpace(self):
        return False

    def isAllowedAlterSelection(self):
        return True

    def isAllowedAlterView(self):
        return True

    def isAllowedAlterDocument(self):
        return True

    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok)

    def helpRequested(self):
        pass

    def choose_file(self):
        '''
        Open the file picker dialog and open the file that the user chooses
        '''

        open_path = App.getUserAppDataDir() + 'Mod/freecad-transportation-wb/data/alignment/'

        filters = self.form.tr('All files (*.*);; CSV files (*.csv);; LandXML files (*.xml)')
        selected_filter = self.form.tr('LandXML files (*.xml)')
        file_name = QtGui.QFileDialog.getOpenFileName(self.form, 'Select File', open_path, filters, selected_filter)

        if not file_name[0]:
            return

        self.form.file_path.setText(file_name[0])

    def examine_file(self):
        '''
        Examine the file path indicated in the QLineEdit, determine the type,
        and pass parsing on to the appropriate module
        '''

        file_path = self.form.file_path.text()
        filename, extension = os.path.splitext(file_path)
        stream = None

        try:
            stream = open(file_path)
            stream.close()

        except OSError:
            dialog = QtGui.QMessageBox(QtGui.QMessageBox.Critical, 'Unable to open file ', file_path)
            dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            dialog.exec_()
            return

        filename = 'import_alignment_task_xml_subpanel.ui'

        if 'csv' in extension:
            filename = 'import_alignment_task_csv_subpanel.ui'

        subpanel = Gui.PySideUic.loadUi(self.path_base + filename, None)

        #ensure any existing subpanels are removed
        itm_count = self.form.layout().count()

        while itm_count > 1:

            item = self.form.layout().itemAt(itm_count - 1)
            self.form.layout().removeItem(item)
            itm_count = self.form.layout().count()

        self.form.layout().addWidget(subpanel)

        if 'xml' in extension:
            self.subtask = ImportXmlSubtask.create(subpanel, file_path)

        elif '.csv' in extension:
            self.subtask = ImportCsvSubtask.create(subpanel, file_path)

    def setup(self):

        #convert the data to lists of lists

        _mw = self.getMainWindow()

        form = _mw.findChild(QtGui.QWidget, 'TaskPanel')

        form.file_path = form.findChild(QtGui.QLineEdit, 'filename')
        form.pick_file = form.findChild(QtGui.QToolButton, 'pick_file')
        form.pick_file.clicked.connect(self.choose_file)
        form.file_path.textChanged.connect(self.examine_file)

        self.form = form

    def getMainWindow(self):

        top = QtGui.QApplication.topLevelWidgets()

        for item in top:
            if item.metaObject().className() == 'Gui::MainWindow':
                return item

        raise RuntimeError('No main window found')