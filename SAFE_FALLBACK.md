# Safe Fallback Version

If the current implementation continues to crash, we can use this minimal, safe version:

## Minimal Safe Version

Replace the completion code with this simpler approach:

### In `keyPressEvent`:
```python
def keyPressEvent(self, event) -> None:
    # Process the key normally first
    super().keyPressEvent(event)
    
    # Then update completions DIRECTLY (no QTimer)
    if _JEDI_AVAILABLE:
        try:
            ch = event.text()
            if ch and (ch.isalnum() or ch == "_" or ch == "."):
                self._update_completions_safe()
        except Exception as e:
            print(f"[Jedi] Error: {e}")
```

### Simpler `_update_completions_safe`:
```python
def _update_completions_safe(self) -> None:
    """Minimal safe version of completion updates."""
    try:
        if not _JEDI_AVAILABLE or Script is None:
            return
        
        # Get source and position
        source = self.document().toPlainText()
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.positionInBlock()
        
        # Get completions from Jedi
        script = Script(source, path=self.filename or "")
        completions = script.complete(line, col)
        
        # Extract names
        names = []
        for c in completions:
            nm = getattr(c, "name", None)
            if nm and nm not in names:
                names.append(nm)
        
        print(f"[Jedi] Found {len(names)} completions")
        
        # Update model (but DON'T try to show popup yet)
        if names:
            self._completions_model.setStringList(names)
            print(f"[Jedi] Model updated with {len(names)} items")
            # Only update model, no popup manipulation
    except Exception as e:
        print(f"[Jedi] Safe completion error: {e}")
```

## Testing the Fallback

1. Try the current version first to see the error
2. If it crashes on `QTimer.singleShot` or popup operations, apply the fallback
3. The fallback only updates the model, doesn't try to show the popup
4. This will help isolate whether the issue is with Jedi or with the popup display

## Common Crash Causes

### 1. QTimer.singleShot in Maya
Some Qt operations don't work well in Maya's thread model. If the crash happens on `QTimer.singleShot(0, ...)`, remove it and call `_update_completions()` directly.

### 2. Popup Show/Raise/SetFocus
Maya's windowing might not support these operations on QCompleter's popup. Remove:
```python
popup.show()
popup.raise_()
popup.setFocus()
```

### 3. Model/View Thread Issues
If updating the model causes crashes, we might need to defer it differently or use signals/slots.

## If All Else Fails: Custom Popup

If QCompleter continues to be problematic, implement a simple custom popup:

```python
class SimpleCompletionPopup(QListWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFocusPolicy(Qt.NoFocus)
        
    def show_at_cursor(self, editor, items):
        self.clear()
        self.addItems(items)
        rect = editor.cursorRect()
        pos = editor.mapToGlobal(rect.bottomLeft())
        self.move(pos)
        self.show()
```

This gives full control and avoids QCompleter's complexity.
