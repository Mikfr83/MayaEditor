# Copyright (C) 2022  Jonathan Macey
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Custom QUiLoader subclass for better event handling.

Modified from:
https://stackoverflow.com/questions/27603350/how-do-i-load-children-from-ui-file-in-pyside/27610822#27610822
"""
from typing import Optional

from PySide6 import QtCore, QtUiTools, QtWidgets


class UiLoader(QtUiTools.QUiLoader):
    """QUiLoader subclass that assigns created widgets as attributes of a base instance."""

    _baseinstance: Optional[QtWidgets.QWidget] = None

    def createWidget(
        self, classname: str, parent: Optional[QtWidgets.QWidget] = None, name: str = ""
    ) -> QtWidgets.QWidget:
        """Create a new widget from classname and assign it to the base instance.

        Parameters
        ----------
        classname : str
            Name of the class to create.
        parent : QWidget or None
            Parent widget for the new widget.
        name : str
            Object name for the new widget.

        Returns
        -------
        QWidget
            The newly created widget.
        """
        if parent is None and self._baseinstance is not None:
            widget = self._baseinstance
        else:
            widget = super().createWidget(classname, parent, name)
            if self._baseinstance is not None:
                setattr(self._baseinstance, name, widget)
        return widget

    def loadUi(self, uifile: str, baseinstance: Optional[QtWidgets.QWidget] = None) -> QtWidgets.QWidget:
        """Load a .ui file and associate widgets with a base instance.

        Parameters
        ----------
        uifile : str
            Full path to the .ui file.
        baseinstance : QWidget or None
            Parent widget to associate the loaded widgets with.

        Returns
        -------
        QWidget
            The loaded widget.
        """
        self._baseinstance = baseinstance
        widget = self.load(uifile)
        QtCore.QMetaObject.connectSlotsByName(widget)
        return widget
