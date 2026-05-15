#!/usr/bin/env python3
"""Custom Jedi autocomplete popup for MayaEditor."""

from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem

try:
    from jedi import Script  # type: ignore

    _JEDI_AVAILABLE = True
except Exception:
    Script = None  # type: ignore
    _JEDI_AVAILABLE = False


class JediCompletionPopup(QListWidget):
    """Custom autocomplete popup using Jedi for Python code completion.

    This is a simpler alternative to QCompleter that gives us full control
    over the popup behavior in Maya's environment.
    """

    completion_selected = Signal(str)  # Emitted when user selects a completion

    def __init__(self, parent=None):
        """Initialize the completion popup.

        Parameters
        ----------
        parent : QWidget, optional
            Parent widget (typically the text editor)
        """
        super().__init__(parent)

        # Configure as a popup window
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFocusPolicy(Qt.NoFocus)

        # Styling
        self.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid #4a90d9;
                selection-background-color: #4a90d9;
                selection-color: #ffffff;
                font-size: 12px;
                padding: 2px;
            }
            QListWidget::item {
                padding: 4px 8px;
            }
        """)

        # Set size constraints
        self.setMinimumWidth(200)
        self.setMaximumWidth(400)
        self.setMaximumHeight(300)

        # Connect selection signal
        self.itemClicked.connect(self._on_item_clicked)

        print("[JediCompletionPopup] Initialized")

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        """Handle item selection from the popup.

        Parameters
        ----------
        item : QListWidgetItem
            The selected item
        """
        text = item.text()
        print(f"[JediCompletionPopup] Item clicked: {text}")
        self.completion_selected.emit(text)
        self.hide()

    def show_completions(self, editor, completions: List[str]) -> None:
        """Show the completion popup with the given items.

        Parameters
        ----------
        editor : QWidget
            The text editor widget
        completions : List[str]
            List of completion strings to display
        """
        if not completions:
            self.hide()
            return

        # Clear and populate
        self.clear()
        for comp in completions[:50]:  # Limit to 50 items for performance
            self.addItem(comp)

        # Select first item
        if self.count() > 0:
            self.setCurrentRow(0)

        # Calculate position below cursor
        cursor_rect = editor.cursorRect()
        global_pos = editor.mapToGlobal(cursor_rect.bottomLeft())

        # Adjust size based on content
        self.adjustSize()

        # Position the popup
        self.move(global_pos)

        # Show it
        self.show()
        self.raise_()

        print(f"[JediCompletionPopup] Showing {self.count()} items at {global_pos}")

    def keyPressEvent(self, event):
        """Handle key events in the popup.

        Parameters
        ----------
        event : QKeyEvent
            The key event
        """
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Accept current selection
            current_item = self.currentItem()
            if current_item:
                self._on_item_clicked(current_item)
            event.accept()
        elif event.key() == Qt.Key_Escape:
            # Cancel
            self.hide()
            event.accept()
        elif event.key() in (Qt.Key_Up, Qt.Key_Down):
            # Navigate
            super().keyPressEvent(event)
        else:
            # Send other keys back to the editor
            self.hide()
            if self.parent():
                self.parent().keyPressEvent(event)


def get_jedi_completions(source: str, line: int, col: int, filename: str = "") -> List[str]:
    """Get completions from Jedi.

    Parameters
    ----------
    source : str
        The source code
    line : int
        Line number (1-based)
    col : int
        Column number (0-based)
    filename : str, optional
        Filename for context

    Returns
    -------
    List[str]
        List of completion strings
    """
    if not _JEDI_AVAILABLE or Script is None:
        return []

    try:
        script = Script(source, path=filename)
        completions = script.complete(line, col)
        names = []
        for c in completions:
            nm = getattr(c, "name", None) or getattr(c, "complete", None)
            if isinstance(nm, str) and nm not in names:
                names.append(nm)
        return names
    except Exception as e:
        print(f"[Jedi] Error getting completions: {e}")
        return []
