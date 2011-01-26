# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008, 2009, 2010 by Wilbert Berendsen
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

from __future__ import unicode_literals

"""
A QGroupBox in the Quick Insert Panel that auto-layouts its buttons.
"""

import weakref

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import actioncollection
import actioncollectionmanager
import app
import widgets.shortcuteditdialog


class ButtonGroup(QGroupBox):
    """Inherit this class to create a group of buttons.
    
    You should implement:
    - translateUI() to set the title
    - actionData() to yield name, icon, function for every button
    - actionTexts() to yield name, text for every button
    - actionTriggered() (if you don't supply a function) to implement the
      handler for the action.
    
    """
      
    def __init__(self, tool):
        super(ButtonGroup, self).__init__(tool)
        self._tool = weakref.ref(tool)
        grid = QGridLayout()
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(grid)
        self.createActions()
        self.setActionTexts()
        self.createButtons()
        app.translateUI(self)
        app.languageChanged.connect(self.setActionTexts)
        
    def translateUI(self):
        """Should set our title."""
        pass
    
    def tool(self):
        return self._tool()
    
    def actionDict(self):
        """Returns the Quick Insert action dictionary."""
        return self.tool().panel().actionDict
        
    def direction(self):
        """ The value of the generic direction widget.
        
        -1 == Down
         0 == Neutral
         1 == Up
         
        """
        return 1 - self.panel().direction.currentIndex()
        
    def createActions(self):
        actionDict = self.actionDict()
        self._names = []
        for name, icon, function in self.actionData():
            if function is None:
                function = (lambda name: lambda: self.actionTriggered(name))(name)
            actionDict[name] = QAction(None, icon=icon, triggered=function)
            self._names.append(name)
    
    def setActionTexts(self):
        actionDict = self.actionDict()
        for name, text in self.actionTexts():
            actionDict[name].setText(text)
            actionDict[name].setToolTip(text)
    
    def createButtons(self):
        actionDict = self.actionDict()
        layout = self.layout()
        row = layout.rowCount()
        columns = 5
        for num, name in enumerate(self._names, row*columns):
            b = Button(self, name, actionDict[name])
            layout.addWidget(b, *divmod(num, columns))
            
    def actionData(self):
        """Should yield name, icon, function (may be None) for every action."""
        pass
    
    def actionTexts(self):
        """Should yield name, text for very action."""
        pass
    
    def actionTriggered(self, name):
        """Called by default when a button is activated."""
        print "Action triggered:", name # DEBUG
        

class Button(QToolButton):
    def __init__(self, group, name, action):
        super(Button, self).__init__(group)
        self.setObjectName(name)
        self.setDefaultAction(action)
        self.setAutoRaise(True)
        self.setIconSize(QSize(22, 22))
    
    def actionCollection(self):
        return self.parent().tool().panel().parent().actionCollection
    
    def key(self):
        """Returns a textual representation of the configured shortcut if it exists."""
        shortcuts = self.actionCollection().shortcuts(self.objectName())
        if shortcuts:
            key = shortcuts[0].toString()
            if len(shortcuts) > 1:
                key += "..."
            return key
    
    def event(self, ev):
        if ev.type() == QEvent.ToolTip:
            text = self.defaultAction().text()
            key = self.key()
            if key:
                text = _("{name} ({key})").format(name=text, key=key)
            QToolTip.showText(ev.globalPos(), text)
            return True
        return super(Button, self).event(ev)
    
    def contextMenuEvent(self, ev):
        m = QMenu(self)
        a = m.addAction(_("Configure Keyboard Shortcut ({key})").format(key = self.key() or "None"))
        a.triggered.connect(self.editShortcut)
        m.exec_(ev.globalPos())
        m.deleteLater()

    def editShortcut(self):
        """Edit our shortcut."""
        mainwindow = self.parent().tool().panel().parent().mainwindow()
        action = QAction(self.defaultAction().icon(), self.defaultAction().text(), None)
        action.setShortcuts(self.actionCollection().shortcuts(self.objectName()) or [])
        if actioncollectionmanager.manager(mainwindow).editAction(self, action,
                self.actionCollection().defaults().get(self.objectName()),
                self.defaultAction()):
            self.actionCollection().setShortcuts(self.objectName(), action.shortcuts())

