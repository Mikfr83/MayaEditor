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
"""Output toolbar with clear, copy, save and help controls."""

from typing import Any, Optional

import maya.cmds as cmds
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QLabel,
    QPushButton,
    QToolBar,
)


class OutputToolBar(QToolBar):
    """Toolbar for the output window with clear, copy, save, and help controls."""

    def __init__(self, parent: Optional[Any] = None) -> None:
        """Construct the output toolbar.

        Parameters
        ----------
        parent : QDialog or None
            The parent EditorDialog instance.
        """
        super().__init__(parent)
        assert parent is not None
        self.parent: Any = parent
        self.setFloatable(False)
        self.setMovable(False)

        clear_output = QPushButton("Clear")
        clear_output.clicked.connect(parent.output_window.clear)
        self.addWidget(clear_output)

        copy_to_clipboard = QPushButton("Copy")
        copy_to_clipboard.clicked.connect(self.clipboard_copy)
        self.addWidget(copy_to_clipboard)

        save_to_file = QPushButton("Save")
        save_to_file.clicked.connect(self.save_to_file)
        self.addWidget(save_to_file)
        self.addSeparator()

        label = QLabel("Output Level")
        self.addWidget(label)
        output_level = QComboBox()
        output_level.addItem("Echo All")
        output_level.addItem("Normal")
        output_level.setCurrentIndex(1)
        output_level.currentIndexChanged.connect(self.update_output_level)
        self.addWidget(output_level)
        self.addSeparator()

        show_help = QCheckBox("Show Help")
        show_help.setCheckable(True)
        show_help.setChecked(True)
        show_help.toggled.connect(self.show_help)
        self.addWidget(show_help)

        show_lint = QCheckBox("Show Lint")
        show_lint.setCheckable(True)
        show_lint.setChecked(False)
        show_lint.toggled.connect(self.show_lint)
        self.addWidget(show_lint)

        autocomplete_toggle = QCheckBox("Autocomplete")
        autocomplete_toggle.setCheckable(True)
        autocomplete_toggle.setChecked(True)  # Enabled by default
        autocomplete_toggle.toggled.connect(self.toggle_autocomplete)
        self.addWidget(autocomplete_toggle)

        open_web_help = QPushButton("Online Help")
        open_web_help.clicked.connect(lambda x: cmds.help(doc=True))
        self.addWidget(open_web_help)

    @Slot(bool)
    def show_help(self, state: bool) -> None:
        """Toggle the help panel visibility.

        Parameters
        ----------
        state : bool
            True to show, False to hide.
        """
        if self.parent:
            self.parent.help_frame.setVisible(state)

    @Slot(bool)
    def show_lint(self, state: bool) -> None:
        """Toggle the lint panel visibility.

        Parameters
        ----------
        state : bool
            True to show, False to hide.
        """
        if self.parent and hasattr(self.parent, "lint_panel"):
            self.parent.lint_panel.setVisible(state)

    @Slot(bool)
    def toggle_autocomplete(self, state: bool) -> None:
        """Toggle autocomplete popup visibility.

        Parameters
        ----------
        state : bool
            True to show popup, False to hide.
        """
        # Find all PythonTextEdit instances by checking for _popup_enabled
        from .PythonTextEdit import PythonTextEdit

        editors = []

        # Recursively find all PythonTextEdit widgets
        def find_python_editors(widget):
            if isinstance(widget, PythonTextEdit):
                editors.append(widget)
            # Check children
            if hasattr(widget, "children"):
                for child in widget.children():
                    find_python_editors(child)

        if self.parent:
            find_python_editors(self.parent)

        # Toggle all editors
        print(f"[Toggle] Found {len(editors)} PythonTextEdit instances, setting popup to {state}")
        for editor in editors:
            if hasattr(editor, "_popup_enabled"):
                editor._popup_enabled = state
                print(f"[Toggle] Set editor._popup_enabled = {state}")
            # Hide popup immediately if disabling
            if not state and hasattr(editor, "_jedi_popup"):
                editor._jedi_popup.hide()
                print("[Toggle] Hid popup")

    @Slot(int)
    def update_output_level(self, index: int) -> None:
        """Update the Maya command echo level.

        Parameters
        ----------
        index : int
            0 for Echo All, 1 for Normal.
        """
        cmds.commandEcho(state=index)

    def clipboard_copy(self) -> None:
        """Copy the output window content to the clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.clear(mode=clipboard.Clipboard)
        text = self.parent.output_window.toPlainText()
        clipboard.setText(text, mode=clipboard.Clipboard)

    def save_to_file(self) -> None:
        """Save the output window content to a text file."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Output Text", "untitled.txt", "Text (*.txt)")
        if file_name:
            with open(file_name, "w") as output_file:
                output_file.write(self.parent.output_window.toPlainText())
