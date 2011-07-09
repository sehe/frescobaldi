# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2011 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
All available part types.
"""

import collections

from PyQt4.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt4.QtGui import QApplication


# instrument / part type categories. Import here ...
from . import strings


# ... and add the categories here to the global list.
categories = [
    strings.category(),
    
]


def model():
    """Returns all available part types as a hierarchical model."""
    m = Model(QApplication.instance())
    global model
    model = lambda: m
    return m


class Model(QAbstractItemModel):
    """Provides the categories and the part types contained therein as a Model.
    
    Simply accesses the global 'categories' variable.
    Don't instantiate directly but use the model() global function.
    
    """
    def index(self, row, column, parent):
        if not parent.isValid():
            return self.createIndex(row, column)
        elif parent.internalPointer() is None:
            return self.createIndex(row, column, categories[parent.row()])
        return QModelIndex()
    
    def parent(self, index):
        if index.internalPointer() is None:
            return QModelIndex()
        return self.createIndex(categories.index(index.internalPointer()), 0)
            
    def columnCount(self, parent):
        return 1
    
    def rowCount(self, parent):
        if not parent.isValid():
            return len(categories)
        elif parent.internalPointer() is None:
            return len(categories[parent.row()].items)
        return 0
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            if index.internalPointer() is None:
                return categories[index.row()].title()
            return index.internalPointer().items[index.row()].title()
        elif role == Qt.DecorationRole:
            if index.internalPointer() is None:
                return categories[index.row()].icon


