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
"""Python editor widget extending TextEdit with highlighting, AST code model and execution."""

import ast
from collections import namedtuple
from typing import Any, Dict, List, Optional

from maya import utils
from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtWidgets import QCompleter, QFileDialog

from .PythonHighlighter import PythonHighlighter
from .TextEdit import TextEdit

is_class: bool = False
code_model_data = namedtuple("code_model_data", "type line_number name")  # noqa: PYI024
class_model_data = namedtuple("class_model_data", "name line_number")  # noqa: PYI024


class PythonTextEdit(TextEdit):
    """QPlainTextEdit customised for Python script editing with highlighting and execution.

    Signals
    -------
    code_model_changed : Signal()
        Emitted when the code model (class/function list) is regenerated.
    """

    completer = QCompleter()
    code_model_changed = Signal()

    def __init__(
        self,
        read_only: bool = True,
        show_line_numbers: bool = True,
        code: Optional[str] = None,
        filename: Optional[str] = None,
        live: bool = False,
        parent: Optional[Any] = None,
    ) -> None:
        """Construct a PythonTextEdit.

        Parameters
        ----------
        read_only : bool
            Whether the editor is read-only.
        show_line_numbers : bool
            Whether to display line numbers.
        code : str or None
            Initial source code.
        filename : str or None
            Associated filename.
        live : bool
            If True, echo output and clear on run (like Maya's script editor).
        parent : QObject or None
            Parent widget.
        """
        super().__init__(read_only, show_line_numbers, code, filename, parent)
        self.highlighter = PythonHighlighter()
        self.highlighter.setDocument(self.document())
        self.execute_selected: bool = False
        self.installEventFilter(self)
        self.live: bool = live
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.copyAvailable.connect(self.selection_changed)
        self.code_model: List[Any] = []
        self.generate_code_model()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Filter key events for Python editor shortcuts.

        Supported shortcuts:
        - Ctrl+Return / F5 : execute code
        - Ctrl+S : save file

        Parameters
        ----------
        obj : QObject
            The object that triggered the event.
        event : QEvent
            The event to process.

        Returns
        -------
        bool
            True if the event was handled, False otherwise.
        """
        if isinstance(obj, PythonTextEdit) and event.type() == QEvent.KeyPress:
            key_event = event
            if (
                key_event.key() == Qt.Key_Return
                and key_event.modifiers() == Qt.ControlModifier
            ) or key_event.key() == Qt.Key_F5:
                self.execute_code()
                return True
            elif (
                key_event.key() == Qt.Key_S
                and key_event.modifiers() == Qt.ControlModifier
            ):
                self.save_file()
                return True
            else:
                return super().eventFilter(obj, event)
        return False

    def event(self, event: QEvent) -> bool:
        """Process events passed directly to the editor.

        Handles tooltip events (currently disabled but reserved).

        Parameters
        ----------
        event : QEvent
            The event to process.

        Returns
        -------
        bool
            True if the event was handled.
        """
        if event.type() == QEvent.ToolTip:
            return True
        return TextEdit.event(self, event)

    def execute_code(self) -> None:
        """Execute the Python code in the editor.

        If text is selected, only the selection is executed.
        In live mode the editor is cleared after execution.
        """
        if self.execute_selected:
            cursor = self.textCursor()
            text = cursor.selectedText()
            text = text.replace("\u2029", "\n")
            if self.live:
                self.update_output.emit(self.toPlainText() + "\n")
                self.draw_line.emit()
            value = utils.executeInMainThreadWithResult(text)
            if self.live and value is not None:
                value = str(value) + "\n"
                self.draw_line.emit()
                self.update_output_html.emit(value)
                self.draw_line.emit()
        else:
            text_to_run = self.toPlainText() + "\n"
            if self.live:
                self.update_output.emit(text_to_run)
                self.draw_line.emit()
                self.clear()
            value = utils.executeInMainThreadWithResult(text_to_run)
            if self.live and value is not None:
                value = str(value)
                self.update_output.emit(value)

    def selection_changed(self, state: bool) -> None:
        """Track whether text is selected for partial execution.

        Parameters
        ----------
        state : bool
            True if text is selected.
        """
        self.execute_selected = state

    def save_file(self) -> bool:
        """Save the current editor content.

        If the filename is ``untitled.py`` a save dialog is shown.

        Returns
        -------
        bool
            True if saved, False if cancelled.
        """
        if self.filename == "untitled.py":
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save As", "", "Python (*.py)"
            )
            if not filename:
                return False
            self.filename = filename
            if self.parent and hasattr(self.parent, "workspace"):
                self.parent.workspace.add_file(filename)
        if self.filename:
            with open(self.filename, "w") as code_file:
                code_file.write(self.toPlainText())
            self.needs_saving = False
            self.generate_code_model()
        return True

    def extract_classes_and_functions(
        self, node_to_traverse: Any, current_object: List[Any]
    ) -> None:
        """Recursively extract class and function definitions from the AST.

        Parameters
        ----------
        node_to_traverse : ast.AST
            The AST node to traverse. Must have a ``body`` attribute.
        current_object : list
            The list to populate with code model entries.
        """
        global is_class
        for node in node_to_traverse.body:
            if isinstance(node, ast.ClassDef):
                is_class = True
                cls_entry: Dict[Any, List[Any]] = {
                    class_model_data(node.name, node.lineno): []
                }
                current_object.append(cls_entry)
                self.extract_classes_and_functions(
                    node,
                    cls_entry[class_model_data(node.name, node.lineno)],
                )
                is_class = False
            if isinstance(node, ast.FunctionDef):
                func = "function"
                if is_class:
                    func = "method"
                current_object.append(
                    code_model_data(type=func, line_number=node.lineno, name=node.name)
                )

    def generate_code_model(self) -> None:
        """Parse the document with AST and rebuild the code model."""
        document = self.document().toRawText()
        document = document.replace("\u2029", "\n")
        node_to_traverse = ast.parse(document)
        self.extract_classes_and_functions(node_to_traverse, self.code_model)
        self.code_model_changed.emit()
