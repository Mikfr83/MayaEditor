#!/usr/bin/env python3
"""Custom Jedi autocomplete popup for MayaEditor."""

import sys
from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem

try:
    from jedi import Interpreter, Project, Script  # type: ignore

    _JEDI_AVAILABLE = True
except Exception:
    Script = None  # type: ignore
    Project = None  # type: ignore
    Interpreter = None  # type: ignore
    _JEDI_AVAILABLE = False

# Cache the Jedi project to avoid recreating it every time
_jedi_project = None


def _get_jedi_project():
    """Get or create a Jedi project configured with Maya's sys.path."""
    global _jedi_project
    if _jedi_project is None and _JEDI_AVAILABLE and Project is not None:
        # Create a project with Maya's current sys.path
        # This allows Jedi to find Maya modules
        _jedi_project = Project(path=".", added_sys_path=sys.path)
        print(f"[Jedi] Created project with {len(sys.path)} sys.path entries")
        print(f"[Jedi] Sample paths: {sys.path[:3]}")

        # Check if maya is actually in sys.path
        maya_paths = [p for p in sys.path if "maya" in p.lower()]
        if maya_paths:
            print(f"[Jedi] Found {len(maya_paths)} Maya-related paths")
            print(f"[Jedi] Maya paths: {maya_paths[:2]}")
        else:
            print("[Jedi] WARNING: No Maya paths found in sys.path!")

    return _jedi_project


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

        # Dark mode styling
        self.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: #d4d4d4;
                border: 2px solid #007acc;
                selection-background-color: #007acc;
                selection-color: #ffffff;
                font-size: 12px;
                padding: 2px;
            }
            QListWidget::item {
                padding: 4px 8px;
                border-bottom: 1px solid #3c3c3c;
            }
            QListWidget::item:hover {
                background-color: #3c3c3c;
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
        # Get the project configured with Maya's sys.path
        project = _get_jedi_project()

        # Debug: show what we're analyzing
        context_lines = source.split("\n")
        if line - 1 < len(context_lines):
            current_line = context_lines[line - 1]
            print(f"[Jedi] Analyzing: '{current_line}' at col {col}")

        # Execute the code up to the cursor to get real runtime context
        # This allows Jedi to see actual imported modules
        try:
            # Create a namespace and execute imports
            namespace = {}

            # Execute all lines before the current line to populate namespace
            lines_before = context_lines[: line - 1]
            code_before = "\n".join(lines_before)

            if code_before.strip():
                print(f"[Jedi] Executing {len(lines_before)} lines to build namespace...")
                try:
                    exec(code_before, namespace)
                    imported_items = [k for k in namespace.keys() if not k.startswith("_")]
                    print(f"[Jedi] Namespace has: {imported_items}")

                    # Debug: Check what cmds actually is
                    if "cmds" in namespace:
                        cmds_obj = namespace["cmds"]
                        print(f"[Jedi] cmds type: {type(cmds_obj)}")
                        print(f"[Jedi] cmds module: {getattr(cmds_obj, '__name__', 'unknown')}")
                        # Try to get some attributes
                        if hasattr(cmds_obj, "polyCube"):
                            print(f"[Jedi] cmds.polyCube exists: {cmds_obj.polyCube}")
                        else:
                            print("[Jedi] WARNING: cmds.polyCube NOT found!")
                        # Show first few attributes
                        attrs = [a for a in dir(cmds_obj) if not a.startswith("_")][:10]
                        print(f"[Jedi] cmds attributes: {attrs}")
                except Exception as exec_error:
                    print(f"[Jedi] Error executing code: {exec_error}")
                    import traceback

                    traceback.print_exc()
                    namespace = {}

            # Add Maya's main namespace as well
            import __main__

            combined_namespace = {**__main__.__dict__, **namespace}

            print(f"[Jedi] Combined namespace has {len(combined_namespace)} items")
            print("[Jedi] Using Interpreter mode with executed namespace")

            # Debug: What does Interpreter see?
            interpreter = Interpreter(source, namespaces=[combined_namespace], project=project)

            print(f"[Jedi] Calling complete(line={line}, col={col})")
            completions = interpreter.complete(line, col)
            print(f"[Jedi] Complete returned {len(completions)} items")
        except Exception as interp_error:
            print(f"[Jedi] Interpreter failed, falling back to Script: {interp_error}")
            import traceback

            traceback.print_exc()
            # Fallback to Script mode
            script = Script(source, path=filename, project=project)
            completions = script.complete(line, col)

        # Debug: show what Jedi found
        print(f"[Jedi] Jedi returned {len(completions)} raw completions")
        if len(completions) > 0:
            print(f"[Jedi] First completion: {completions[0].name if completions else 'none'}")

        # Fallback: If Jedi returns few/no completions but we're completing on a module,
        # use dir() directly (better for dynamically generated modules like maya.cmds)
        if len(completions) < 10 and "." in current_line:
            # Check if we're completing on a known object
            parts = current_line.split(".")
            if len(parts) >= 2:
                obj_name = parts[0].strip()
                if obj_name in combined_namespace:
                    obj = combined_namespace[obj_name]
                    # If it's a module or has many attributes, use dir()
                    if hasattr(obj, "__name__") or len(dir(obj)) > 50:
                        print(f"[Jedi] Using dir() fallback for '{obj_name}'")

                        # Get all attributes
                        all_attrs = dir(obj)

                        # Filter to callables (functions) and non-private
                        callables = []
                        non_callables = []
                        for attr in all_attrs:
                            if attr.startswith("_"):
                                continue
                            try:
                                attr_obj = getattr(obj, attr)
                                if callable(attr_obj):
                                    callables.append(attr)
                                else:
                                    non_callables.append(attr)
                            except:
                                # If we can't get it, skip it
                                pass

                        print(f"[Jedi] dir() found {len(callables)} callables, {len(non_callables)} non-callables")

                        # Prefer callables but include non-callables too
                        direct_completions = callables + non_callables

                        # If user has typed something after the dot, filter by prefix
                        if len(parts) > 1 and parts[-1].strip():
                            prefix = parts[-1].strip()
                            print(f"[Jedi] Filtering {len(direct_completions)} items by prefix '{prefix}'")
                            direct_completions = [c for c in direct_completions if c.startswith(prefix)]
                            print(f"[Jedi] {len(direct_completions)} items match prefix")

                        if len(direct_completions) > len(completions):
                            print(
                                f"[Jedi] Using dir() results instead of Jedi ({len(direct_completions)} vs {len(completions)})"
                            )
                            print(f"[Jedi] First 10 completions: {direct_completions[:10]}")
                            return direct_completions

        names = []
        for c in completions:
            nm = getattr(c, "name", None) or getattr(c, "complete", None)
            if isinstance(nm, str) and nm not in names:
                # Filter out private/dunder unless explicitly typed
                if nm.startswith("__") and not current_line.strip().endswith("__"):
                    continue
                names.append(nm)
            # Debug first few completions
            if len(names) <= 5:
                comp_type = getattr(c, "type", "unknown")
                print(f"[Jedi]   - {nm} (type: {comp_type})")

        if names:
            print(f"[Jedi] Returned {len(names)} completions: {names[:10]}...")
        else:
            print("[Jedi] WARNING: No useful completions found!")
            # Additional debug when no completions
            print(f"[Jedi] Source length: {len(source)} chars")
            print(f"[Jedi] Current line: '{current_line}'")
            print(f"[Jedi] Line {line}, Col {col}")

        return names
    except Exception as e:
        print(f"[Jedi] Error getting completions: {e}")
        import traceback

        traceback.print_exc()
        return []
