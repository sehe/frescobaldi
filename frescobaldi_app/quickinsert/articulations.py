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
The Quick Insert panel Articulations Tool.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import app
import symbols

import tool
import buttongroup


# a dict mapping long articulation names to their short sign
shorthands = {
    'marcato': '^',
    'stopped': '+',
    'tenuto': '-',
    'staccatissimo': '|',
    'accent': '>',
    'staccato': '.',
    'portato': '_',
}


class Articulations(tool.Tool):
    """Articulations tool in the quick insert panel toolbox.
    
    """
    def __init__(self, panel):
        super(Articulations, self).__init__(panel)
        self.shorthands = QCheckBox(self)
        self.shorthands.setChecked(True)
        self.layout().addWidget(self.shorthands)
        for cls in (
                ArticulationsGroup,
                OrnamentsGroup,
                SignsGroup,
                OtherGroup,
            ):
            self.layout().addWidget(cls(self))
        app.translateUI(self)
        
    def translateUI(self):
        self.shorthands.setText(_("Allow shorthands"))
        self.shorthands.setToolTip(_(
            "Use short notation for some articulations like staccato."))

    def icon(self):
        """Should return an icon for our tab."""
        return symbols.icon("articulation_prall")
    
    def title(self):
        """Should return a title for our tab."""
        return _("Articulations")
  
    def tooltip(self):
	"""Returns a tooltip"""
	return _("Different kinds of articulations and other signs.")


class Group(buttongroup.ButtonGroup):
    def actionData(self):
        for name, title in self.actionTexts():
            yield name, symbols.icon('articulation_'+name), None

    def actionTriggered(self, name):
        print "Articulation",name,"triggered"#DEBUG
        

class ArticulationsGroup(Group):
    def translateUI(self):
        self.setTitle(_("Articulations"))
        
    def actionTexts(self):
        yield 'accent', _("Accent")
        yield 'marcato', _("Marcato")
        yield 'staccatissimo', _("Staccatissimo")
        yield 'staccato', _("Staccato")
        yield 'portato', _("Portato")
        yield 'tenuto', _("Tenuto")
        yield 'espressivo', _("Espressivo")


class OrnamentsGroup(Group):
    def translateUI(self):
        self.setTitle(_("Ornaments"))
        
    def actionTexts(self):
        yield 'trill', _("Trill")
        yield 'prall', _("Prall")
        yield 'mordent', _("Mordent")
        yield 'turn', _("Turn")
        yield 'prallprall', _("Prall prall")
        yield 'prallmordent', _("Prall mordent")
        yield 'upprall', _("Up prall")
        yield 'downprall', _("Down prall")
        yield 'upmordent', _("Up mordent")
        yield 'downmordent', _("Down mordent")
        yield 'prallup', _("Prall up")
        yield 'pralldown', _("Prall down")
        yield 'lineprall', _("Line prall")
        yield 'reverseturn', _("Reverse turn")


class SignsGroup(Group):
    def translateUI(self):
        self.setTitle(_("Signs"))
        
    def actionTexts(self):
        yield 'fermata', _("Fermata")
        yield 'shortfermata', _("Short fermata")
        yield 'longfermata', _("Long fermata")
        yield 'verylongfermata', _("Very long fermata")
        yield 'segno', _("Segno")
        yield 'coda', _("Coda")
        yield 'varcoda', _("Varcoda")
        yield 'signumcongruentiae', _("Signumcongruentiae")


class OtherGroup(Group):
    def translateUI(self):
        self.setTitle(_("Other"))
    
    def actionTexts(self):
        yield 'upbow', _("Upbow")
        yield 'downbow', _("Downbow")
        yield 'snappizzicato', _("Snappizzicato")
        yield 'open', _("Open (e.g. brass)")
        yield 'stopped', _("Stopped (e.g. brass)")
        yield 'flageolet', _("Flageolet")
        yield 'thumb', _("Thumb")
        yield 'lheel', _("Left heel")
        yield 'rheel', _("Right heel")
        yield 'ltoe', _("Left toe")
        yield 'rtoe', _("Right toe")
        yield 'halfopen', _("Half open (e.g. hi-hat)")

