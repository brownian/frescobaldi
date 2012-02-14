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
Manages widgets in the borders of a QScrollArea.
"""

from PyQt4.QtCore import QEvent, QObject, QPoint, QRect, QSize


LEFT, TOP, RIGHT, BOTTOM = 0, 1, 2, 3

class BorderLayout(QObject):
    
    # order in which the widget spaces are filled.
    # if top and bottom are first, they get the full width.
    order = TOP, BOTTOM, LEFT, RIGHT
    
    def __init__(self, scrollarea):
        super(BorderLayout, self).__init__(scrollarea)
        self._resizing = False
        self._widgets = ([], [], [], [])
        scrollarea.viewport().installEventFilter(self)
    
    @classmethod
    def get(cls, scrollarea):
        """Gets the BorderLayout for the given scrollarea.
        
        If None exists, creates and returns a new instance.
        
        """
        for c in scrollarea.children():
            if type(c) is cls:
                return c
        return cls(scrollarea)
    
    def scrollarea(self):
        return self.parent()
    
    def eventFilter(self, obj, ev):
        if self._resizing:
            return False
        elif ev.type() == QEvent.Resize and obj is self.scrollarea().viewport():
            self.updateGeometry()
        elif ev.type() in (QEvent.Resize, QEvent.ShowToParent, QEvent.HideToParent):
            self.updateGeometry()
        return False
    
    def addWidget(self, widget, side):
        """Adds a widget to our scrollarea."""
        self.insertWidget(widget, side, -1)
        
    def insertWidget(self, widget, side, position):
        """Inserts a widget in a specific position."""
        assert side in (LEFT, TOP, RIGHT, BOTTOM)
        new = False
        for l in self._widgets:
            if widget in l:
                l.remove(widget)
                break
        else:
            new = True
            widget.installEventFilter(self)
            widget.setParent(self.scrollarea())
            widget.setAutoFillBackground(True)
        if position == -1:
            self._widgets[side].append(widget)
        else:
            self._widgets[side].insert(widget, position)
        if new:
            widget.show()
        self.updateGeometry()
            
    def removeWidget(self, widget):
        for side in LEFT, TOP, RIGHT, BOTTOM:
            if widget in self._widgets[side]:
                self._widgets[side].remove(widget)
                widget.removeEventFilter(self)
                widget.setParent(None)
                return True
        self.updateGeometry()
    
    def updateGeometry(self):
        """Positions all widgets in the scrollarea edges."""
        self._resizing = True
        self.scrollarea().setViewportMargins(0, 0, 0, 0)
        pos = self.scrollarea().viewport().pos()
        size = self.scrollarea().viewport().size()
        left, right, top, bottom = 0, 0, 0, 0
        
        for side in self.order:
            def widgets():
                for w in self._widgets[side][::-1]:
                    if w.isVisible():
                        yield w
            if side is LEFT:
                for widget in widgets():
                    w = widget.sizeHint().width()
                    h = size.height() - top - bottom
                    x = left
                    y = top
                    g = QRect(pos + QPoint(x, y), QSize(w, h))
                    widget.setGeometry(g)
                    left += w
            elif side is RIGHT:
                for widget in widgets():
                    w = widget.sizeHint().width()
                    h = size.height() - top - bottom
                    x = size.width() - right - w
                    y = top
                    g = QRect(pos + QPoint(x, y), QSize(w, h))
                    widget.setGeometry(g)
                    right += w
            elif side is TOP:
                for widget in widgets():
                    w = size.width() - left - right
                    h = widget.heightForWidth(w)
                    if h == -1:
                        h = widget.sizeHint().height()
                    x = left
                    y = top
                    g = QRect(pos + QPoint(x, y), QSize(w, h))
                    widget.setGeometry(g)
                    top += h
            elif side is BOTTOM:
                for widget in widgets():
                    w = size.width() - left - right
                    h = widget.heightForWidth(w)
                    if h == -1:
                        h = widget.sizeHint().height()
                    x = left
                    y = size.height() - bottom - h
                    g = QRect(pos + QPoint(x, y), QSize(w, h))
                    widget.setGeometry(g)
                    bottom += h
        self.scrollarea().setViewportMargins(left, top, right, bottom)
        self._resizing = False



