# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2012 by Wilbert Berendsen
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
The Music View's Edit in Place dialog.
"""

from __future__ import unicode_literals

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import app
import autocomplete.analyzer
import autocomplete.completer
import cursordiff
import cursortools
import help.html
import highlighter
import homekey
import indent
import matcher
import metainfo
import qutil
import textformats
import tokeniter
import widgets.dialog

from . import tooltip


def edit(parent, cursor, position=None):
    dlg = Dialog(parent)
    dlg.finished.connect(dlg.deleteLater)
    dlg.edit(cursor)
    dlg.popup(position)


class Dialog(widgets.dialog.Dialog):
    """Dialog containing a short text edit field to edit one line."""
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self._document = None
        self.messageLabel().setWordWrap(True)
        self.document = d = QTextDocument()
        d.setDocumentLayout(QPlainTextDocumentLayout(d))
        self.highlighter = highlighter.highlighter(d)
        self.view = View(d)
        self.matcher = Matcher(self.view)
        self.completer = Completer(self.view)
        self.setMainWidget(self.view)
        help.addButton(self.buttonBox(), help_musicview_editinplace)
        # action for completion popup
        self._showPopupAction = QAction(None, triggered=self.slotCompletionPopup)
        self.addAction(self._showPopupAction)
        # make Ctrl+Return accept the dialog
        self.button("ok").setShortcut(QKeySequence("Ctrl+Return"))
        qutil.saveDialogSize(self, "musicview/editinplace/dialog/size")
        
        self.accepted.connect(self.save)
        app.translateUI(self)
        app.settingsChanged.connect(self.readSettings)
        self.readSettings()
        
    def translateUI(self):
        self.setWindowTitle(app.caption(_("Edit in Place")))
        self.updateMessage()
    
    def readSettings(self):
        self._showPopupAction.setShortcut(
            help.action("autocomplete", "popup_completions").shortcut())
        
    def edit(self, cursor):
        """Edit the block at the specified QTextCursor."""
        if self._document:
            self._document.closed.disconnect(self.reject)
        self._document = cursor.document()
        self._document.closed.connect(self.reject)
        
        # dont change the cursor
        c = self._range = QTextCursor(cursor)
        cursorpos = c.position() - c.block().position()
        cursortools.strip_indent(c)
        indentpos = c.position() - c.block().position()
        c.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        self.view.setPlainText(c.selection().toPlainText())
        
        self.highlighter.setInitialState(tokeniter.state(cursor))
        self.highlighter.setHighlighting(metainfo.info(cursor.document()).highlighting)
        self.highlighter.rehighlight()
        
        # let autocomplete query the real document as if we're at the start
        # of the current block
        self.completer.document_cursor = QTextCursor(cursor.block())
        self.completer.autoComplete = QSettings().value(
                        "autocomplete", True) not in ('false', False)
        
        cursor = self.view.textCursor()
        cursor.setPosition(max(0, cursorpos-indentpos))
        self.view.setTextCursor(cursor)
        
        self.updateMessage()
        
    def popup(self, position):
        """Show the dialog at the specified global QPoint."""
        geom = self.geometry()
        geom.moveCenter(position)
        if position.y() <= geom.height() + 60:
            geom.moveTop(position.y() + 60)
        else:
            geom.moveBottom(position.y() - 60)
        self.setGeometry(geom)
        self.view.setFocus()
        self.show()
    
    def save(self):
        """Called to perform the edits in the document."""
        cursor = QTextCursor(self._range)
        start = cursor.selectionStart()
        with cursortools.compress_undo(cursor):
            # use cursordiff; dont destroy point and click positions
            cursordiff.insert_text(cursor, self.view.toPlainText())
            cursor.setPosition(start, QTextCursor.KeepAnchor)
            # re-indent the inserted line(s)
            indent.re_indent(cursor)
        
    def updateMessage(self):
        """Called when a new cursor is set to edit, updates the message text."""
        if self._document:
            self.setMessage(
              _("Editing line {linenum} of \"{document}\" ({variable})").format(
                linenum = self._range.block().blockNumber() + 1,
                document = self._document.documentName(),
                variable = tooltip.get_definition(self._range) or _("<unknown>"),
            ))
        else:
            self.setMessage("<no document set>") # should never appear
    
    def slotCompletionPopup(self):
        self.completer.showCompletionPopup()


class View(QPlainTextEdit):
    """The text edit in the "Edit in Place" dialog."""
    def __init__(self, document):
        super(View, self).__init__()
        self.setDocument(document)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setCursorWidth(2)
        app.settingsChanged.connect(self.readSettings)
        self.readSettings()
    
    def readSettings(self):
        data = textformats.formatData('editor')
        self.setFont(data.font)
        self.setPalette(data.palette())
    
    def sizeHint(self):
        metrics = self.fontMetrics()
        return QSize(80 * metrics.width(" "),3 * metrics.height())
    
    def event(self, ev):
        """Reimplemented to avoid typing the line separator."""
        if ev == QKeySequence.InsertLineSeparator:
            return False
        return super(View, self).event(ev)


class Matcher(matcher.AbstractMatcher):
    """Looks for matches if the cursor moves."""
    def __init__(self, view):
        super(Matcher, self).__init__(view)
        self._highlighter = MatchHighlighter(view)
    
    def highlighter(self):
        return self._highlighter


class MatchHighlighter(widgets.arbitraryhighlighter.ArbitraryHighlighter):
    """Highlights the matches like { } or << >>."""
    def __init__(self, edit):
        super(MatchHighlighter, self).__init__(edit)
        app.settingsChanged.connect(self.readSettings)
        self.readSettings()
    
    def readSettings(self):
        self._baseColors = textformats.formatData('editor').baseColors
        self.reload()
    
    def textFormat(self, name):
        f = QTextCharFormat()
        f.setBackground(self._baseColors[name])
        return f


class Completer(autocomplete.completer.Completer):
    """A Completer providing completions for the Edit in Place popup.
    
    It can request information from the document specified by the
    document_cursor which can be set as an instance attribute.
    
    """
    document_cursor = None
    def __init__(self, view):
        super(Completer, self).__init__()
        self.setWidget(view)
    
    def analyzer(self):
        return Analyzer(self.document_cursor)


class Analyzer(autocomplete.analyzer.Analyzer):
    """An Analyzer looking at the line of text in the Edit in Place popup.
    
    It takes the document_cursor attribute on init from the Completer,
    so that the document the Edit in Place popup belongs to can be queried
    for information like defined variables, etc.
    
    """
    def __init__(self, cursor):
        self._document_cursor = cursor
    
    def document_cursor(self):
        """Reimplemented to return the cursor of the real document."""
        return self._document_cursor


class help_musicview_editinplace(help.page):
    def title():
        return _("Edit in Place")
    
    def body():
        return help.html.p(
        _("In this dialog you can edit one line of the text document."),
        _("Click OK or press {key} to place the modified text in the document.").format(
        key=QKeySequence("Ctrl+Return").toString(QKeySequence.NativeText)),
        _("You can open the \"Edit in Place\" dialog by Shift-clicking a "
          "clickable object in the Music View or by right-clicking the object "
          "and selecting {menu}.").format(menu=help.menu(_("Edit in Place"))),
        )


